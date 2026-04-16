from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from users.models import User
from users.serializer import UserSerializer


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

