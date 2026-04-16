from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
import json

from devices.models import Device, DeviceGroup
from devices.forms import DeviceForm, DeviceAssignAdsForm, DeviceGroupForm, DeviceGroupDevicesForm, DeviceGroupAssignAdsForm
from analytics.models import PlayLog
from ads.models import Ad
from ads.models import KillSwitch


def _get_all_ads_for_device(device):
    """Get all active ads for a device: direct + from all groups. Returns deduplicated queryset."""
    if KillSwitch.is_killed():
        return Ad.objects.none()
    direct_ads = device.assigned_ads.filter(is_active=True)
    group_ads = Ad.objects.filter(is_active=True, device_groups__devices=device)
    return (direct_ads | group_ads).distinct()


@csrf_exempt
def device_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    device_id = data.get('username', '')
    secret_key = data.get('password', '')

    try:
        device = Device.objects.get(device_id=device_id, secret_key=secret_key)
        device.is_online = True
        device.last_active = timezone.now()
        device.save()

        ads = _get_all_ads_for_device(device).order_by('priority')
        ads_data = []
        for ad in ads:
            ads_data.append({
                'id': ad.pk,
                'title': ad.title,
                'description': ad.description,
                'video_url': request.build_absolute_uri(ad.video.url) if ad.video else '',
                'duration': ad.duration,
                'play_limit': ad.play_limit,
                'priority': ad.priority,
                'is_active': ad.is_active,
            })

        return JsonResponse({
            'device_name': device.device_name,
            'device_id': device.device_id,
            'location': device.location,
            'ads': ads_data,
            'success': True,
        })
    except Device.DoesNotExist:
        return JsonResponse({'error': 'Invalid Device ID or Secret Key', 'success': False}, status=401)


@csrf_exempt
def device_ads(request, device_id):
    """API endpoint for Android app to fetch assigned ads for a device."""
    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)

    device.last_active = timezone.now()
    device.save()

    ads = _get_all_ads_for_device(device).order_by('priority')
    ads_data = []
    for ad in ads:
        # Enforce play_limit: count how many times this ad played on this device
        play_count = PlayLog.objects.filter(device=device, ad=ad).count()
        if ad.play_limit > 0 and play_count >= ad.play_limit:
            continue  # skip ads that have reached their play limit
        ads_data.append({
            'id': ad.pk,
            'title': ad.title,
            'description': ad.description,
            'video_url': request.build_absolute_uri(ad.video.url) if ad.video else '',
            'duration': ad.duration,
            'play_limit': ad.play_limit,
            'play_count': play_count,
            'priority': ad.priority,
            'is_active': ad.is_active,
        })

    return JsonResponse({'ads': ads_data, 'device_name': device.device_name})


@csrf_exempt
def device_play_log(request, device_id):
    """API endpoint for Android app to report an ad play completion."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    ad_id = data.get('ad_id')
    if not ad_id:
        return JsonResponse({'error': 'ad_id required'}, status=400)

    try:
        ad = Ad.objects.get(pk=ad_id)
    except Ad.DoesNotExist:
        return JsonResponse({'error': 'Ad not found'}, status=404)

    PlayLog.objects.create(device=device, ad=ad)

    device.last_active = timezone.now()
    device.save()

    play_count = PlayLog.objects.filter(device=device, ad=ad).count()
    return JsonResponse({'success': True, 'play_count': play_count, 'play_limit': ad.play_limit})


@login_required
def device_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    devices = Device.objects.all().annotate(ad_count=Count('assigned_ads')).order_by('device_name')

    if query:
        devices = devices.filter(Q(device_name__icontains=query) | Q(location__icontains=query) | Q(device_id__icontains=query))
    if status_filter == 'online':
        devices = devices.filter(is_online=True)
    elif status_filter == 'offline':
        devices = devices.filter(is_online=False)

    paginator = Paginator(devices, 10)
    page = request.GET.get('page')
    devices = paginator.get_page(page)

    return render(request, 'devices/list.html', {
        'devices': devices,
        'query': query,
        'status_filter': status_filter,
    })


@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    play_logs = PlayLog.objects.filter(device=device).select_related('ad').order_by('-played_at')[:20]

    if request.method == 'POST':
        form = DeviceAssignAdsForm(request.POST)
        if form.is_valid():
            device.assigned_ads.set(form.cleaned_data['ads'])
            messages.success(request, 'Assigned ads updated.')
            return redirect('device_detail', pk=pk)
    else:
        form = DeviceAssignAdsForm(initial={'ads': device.assigned_ads.all()})

    return render(request, 'devices/detail.html', {
        'device': device,
        'form': form,
        'play_logs': play_logs,
        'all_ads': Ad.objects.all().order_by('title'),
        'assigned_ad_ids': set(device.assigned_ads.values_list('pk', flat=True)),
    })


@login_required
def device_create(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            groups = form.cleaned_data.get('groups')
            if groups:
                for group in groups:
                    group.devices.add(device)
            messages.success(request, 'Device created successfully.')
            return redirect('device_list')
    else:
        form = DeviceForm()
    return render(request, 'devices/create.html', {'form': form})


@login_required
def device_edit(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            device = form.save()
            # Update group memberships
            current_groups = set(device.groups.all())
            selected_groups = set(form.cleaned_data.get('groups', []))
            for g in current_groups - selected_groups:
                g.devices.remove(device)
            for g in selected_groups - current_groups:
                g.devices.add(device)
            messages.success(request, 'Device updated successfully.')
            return redirect('device_detail', pk=pk)
    else:
        form = DeviceForm(instance=device)
    return render(request, 'devices/edit.html', {'form': form, 'device': device})


@login_required
def device_delete(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        device.delete()
        messages.success(request, 'Device deleted successfully.')
    return redirect('device_list')


# =====================
# Device Group CRUD
# =====================

@login_required
def group_list(request):
    query = request.GET.get('q', '')
    groups = DeviceGroup.objects.all().annotate(
        device_count=Count('devices', distinct=True),
        ad_count=Count('assigned_ads', distinct=True),
    ).order_by('name')

    if query:
        groups = groups.filter(Q(name__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(groups, 10)
    page = request.GET.get('page')
    groups = paginator.get_page(page)

    return render(request, 'devices/group_list.html', {
        'groups': groups,
        'query': query,
    })


@login_required
def group_create(request):
    if request.method == 'POST':
        form = DeviceGroupForm(request.POST)
        devices_form = DeviceGroupDevicesForm(request.POST)
        if form.is_valid() and devices_form.is_valid():
            group = form.save()
            group.devices.set(devices_form.cleaned_data['devices'])
            messages.success(request, 'Group created successfully.')
            return redirect('group_detail', pk=group.pk)
    else:
        form = DeviceGroupForm()
        devices_form = DeviceGroupDevicesForm()
    return render(request, 'devices/group_create.html', {'form': form, 'devices_form': devices_form})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(DeviceGroup, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'assign_ads':
            ads_form = DeviceGroupAssignAdsForm(request.POST)
            if ads_form.is_valid():
                group.assigned_ads.set(ads_form.cleaned_data['ads'])
                messages.success(request, 'Assigned ads updated for group.')
                return redirect('group_detail', pk=pk)
        elif action == 'assign_devices':
            devices_form = DeviceGroupDevicesForm(request.POST)
            if devices_form.is_valid():
                group.devices.set(devices_form.cleaned_data['devices'])
                messages.success(request, 'Group devices updated.')
                return redirect('group_detail', pk=pk)

    ads_form = DeviceGroupAssignAdsForm(initial={'ads': group.assigned_ads.all()})
    devices_form = DeviceGroupDevicesForm(initial={'devices': group.devices.all()})
    all_ads = Ad.objects.all().order_by('title')
    assigned_ad_ids = set(group.assigned_ads.values_list('pk', flat=True))

    return render(request, 'devices/group_detail.html', {
        'group': group,
        'ads_form': ads_form,
        'devices_form': devices_form,
        'all_ads': all_ads,
        'assigned_ad_ids': assigned_ad_ids,
    })


@login_required
def group_edit(request, pk):
    group = get_object_or_404(DeviceGroup, pk=pk)
    if request.method == 'POST':
        form = DeviceGroupForm(request.POST, instance=group)
        devices_form = DeviceGroupDevicesForm(request.POST)
        if form.is_valid() and devices_form.is_valid():
            form.save()
            group.devices.set(devices_form.cleaned_data['devices'])
            messages.success(request, 'Group updated successfully.')
            return redirect('group_detail', pk=pk)
    else:
        form = DeviceGroupForm(instance=group)
        devices_form = DeviceGroupDevicesForm(initial={'devices': group.devices.all()})
    return render(request, 'devices/group_edit.html', {'form': form, 'devices_form': devices_form, 'group': group})


@login_required
def group_delete(request, pk):
    group = get_object_or_404(DeviceGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Group deleted successfully.')
    return redirect('group_list')
