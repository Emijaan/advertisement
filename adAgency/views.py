from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import json

from ads.models import Ad
from devices.models import Device
from analytics.models import PlayLog


@login_required
def dashboard(request):
    # Filter data by ownership for non-SUPERADMIN
    if request.user.role == 'SUPERADMIN':
        ads_qs = Ad.objects.all()
        devices_qs = Device.objects.all()
        plays_qs = PlayLog.objects.all()
    else:
        ads_qs = Ad.objects.filter(created_by=request.user)
        devices_qs = Device.objects.filter(created_by=request.user)
        plays_qs = PlayLog.objects.filter(device__created_by=request.user)

    total_ads = ads_qs.count()
    active_ads = ads_qs.filter(is_active=True).count()
    total_devices = devices_qs.count()
    online_devices = devices_qs.filter(is_online=True).count()
    total_plays = plays_qs.count()

    devices = devices_qs[:5]
    recent_ads = ads_qs.order_by('-created_at')[:5]

    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_plays = (
        plays_qs.filter(played_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('played_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    chart_labels = json.dumps([d['date'].strftime('%b %d') for d in daily_plays])
    chart_data = json.dumps([d['count'] for d in daily_plays])

    return render(request, 'dashboard.html', {
        'total_ads': total_ads,
        'active_ads': active_ads,
        'total_devices': total_devices,
        'online_devices': online_devices,
        'total_plays': total_plays,
        'devices': devices,
        'recent_ads': recent_ads,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    })
