from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from functools import wraps

from users.models import User
from users.serializer import UserSerializer
from users.forms import UserCreateForm, UserEditForm


def superadmin_required(view_func):
    """Decorator: only SUPERADMIN can access."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'SUPERADMIN':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# Create your views here.
def signup(request):

    email = request.POST['email']
    password = request.POST['password']
    if email:
        return JsonResponse({
            "message":"Please enter your email address",
            "success":False,
        })
    user = User.objects.filter(email=email)
    if user:
        User.objects.create_user(email,password)
        return JsonResponse({
            "message": "Successfully created user",
            "success":True,
        })
    else:
        return JsonResponse({
            "message": "Something went wrong",
        })

def profile(request):
    user = request.user
    return JsonResponse({
        "user":UserSerializer(user).data,
    })


@login_required
def user_settings(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'profile':
            request.user.email = request.POST.get('email', request.user.email)
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_settings')

        elif action == 'password':
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            if not request.user.check_password(old_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password1 != new_password2:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password1) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')
            return redirect('user_settings')

    return render(request, 'users/settings.html')


@login_required
def playback_control(request):
    from devices.models import Device
    from django.db.models import Count
    devices = Device.objects.annotate(ad_count=Count('assigned_ads')).order_by('device_name')
    for device in devices:
        device.assigned_ads_list = device.assigned_ads.all()
    return render(request, 'playback/control.html', {'devices': devices})


# =====================
# User Management CRUD (SUPERADMIN only)
# =====================

@superadmin_required
def user_list(request):
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    users = User.objects.exclude(pk=request.user.pk).annotate(
        device_count=Count('owned_devices'),
    ).order_by('-date_joined')

    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
    if role_filter:
        users = users.filter(role=role_filter)

    paginator = Paginator(users, 10)
    page = request.GET.get('page')
    users = paginator.get_page(page)

    return render(request, 'users/list.html', {
        'users': users,
        'query': query,
        'role_filter': role_filter,
    })


@superadmin_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.created_by = request.user
            user.save()
            messages.success(request, f'User "{user.username}" created successfully.')
            return redirect('user_list')
    else:
        form = UserCreateForm()
    return render(request, 'users/create.html', {'form': form})


@superadmin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.role == 'SUPERADMIN' and user.pk != request.user.pk:
        messages.error(request, 'Cannot edit another Super Admin.')
        return redirect('user_list')
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" updated successfully.')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'users/edit.html', {'form': form, 'edit_user': user})


@superadmin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.role == 'SUPERADMIN':
        messages.error(request, 'Cannot delete a Super Admin account.')
    elif request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully.')
    return redirect('user_list')

