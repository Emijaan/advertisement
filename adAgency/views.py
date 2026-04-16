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
    total_ads = Ad.objects.count()
    active_ads = Ad.objects.filter(is_active=True).count()
    total_devices = Device.objects.count()
    online_devices = Device.objects.filter(is_online=True).count()
    total_plays = PlayLog.objects.count()

    devices = Device.objects.all()[:5]
    recent_ads = Ad.objects.all().order_by('-created_at')[:5]

    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_plays = (
        PlayLog.objects.filter(played_at__gte=thirty_days_ago)
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
