from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from ads.models import Ad, KillSwitch
from ads.forms import AdForm


@login_required
def ad_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    ads = Ad.objects.all().order_by('-created_at')

    if query:
        ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if status_filter == 'active':
        ads = ads.filter(is_active=True)
    elif status_filter == 'inactive':
        ads = ads.filter(is_active=False)

    paginator = Paginator(ads, 10)
    page = request.GET.get('page')
    ads = paginator.get_page(page)

    return render(request, 'ads/list.html', {
        'ads': ads,
        'query': query,
        'status_filter': status_filter,
    })


@login_required
def ad_create(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ad created successfully.')
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/create.html', {'form': form})


@login_required
def ad_edit(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ad updated successfully.')
            return redirect('ad_list')
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/edit.html', {'form': form, 'ad': ad})


@login_required
def ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Ad deleted successfully.')
    return redirect('ad_list')


@login_required
def ad_toggle(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        ad.is_active = not ad.is_active
        ad.save()
        status = 'activated' if ad.is_active else 'deactivated'
        messages.success(request, f'Ad "{ad.title}" {status}.')
    return redirect('ad_list')


@login_required
def kill_switch_toggle(request):
    if request.method == 'POST':
        ks, _ = KillSwitch.objects.get_or_create(pk=1)
        ks.is_active = not ks.is_active
        ks.activated_at = timezone.now() if ks.is_active else None
        ks.activated_by = request.user.username if ks.is_active else ''
        ks.save()
        if ks.is_active:
            messages.warning(request, 'KILL SWITCH ACTIVATED — All ads stopped immediately across all devices.')
        else:
            messages.success(request, 'Kill switch deactivated — Ads are now playing normally.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
