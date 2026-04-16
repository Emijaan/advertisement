from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone

from analytics.models import PlayLog
from ads.models import Ad
from devices.models import Device


@login_required
def analytics_dashboard(request):
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)

    # Filter data by ownership for non-SUPERADMIN
    if request.user.role == 'SUPERADMIN':
        plays_qs = PlayLog.objects.all()
    else:
        plays_qs = PlayLog.objects.filter(device__created_by=request.user)

    total_plays = plays_qs.count()
    plays_today = plays_qs.filter(played_at__date=today.date()).count()
    plays_30d = plays_qs.filter(played_at__gte=thirty_days_ago).count()

    top_ads = (
        plays_qs.values('ad__title')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    top_devices = (
        plays_qs.values('device__device_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    daily_plays = (
        plays_qs.filter(played_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('played_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    chart_labels = [d['date'].strftime('%b %d') for d in daily_plays]
    chart_data = [d['count'] for d in daily_plays]

    recent_logs = plays_qs.select_related('ad', 'device').order_by('-played_at')[:20]

    return render(request, 'analytics/dashboard.html', {
        'total_plays': total_plays,
        'plays_today': plays_today,
        'plays_30d': plays_30d,
        'top_ads': top_ads,
        'top_devices': top_devices,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'recent_logs': recent_logs,
    })
