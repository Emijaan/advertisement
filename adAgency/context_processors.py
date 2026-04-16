def page_title(request):
    """Add page_title to template context based on URL name."""
    titles = {
        'dashboard': 'Dashboard',
        'ad_list': 'Ads',
        'ad_create': 'Create Ad',
        'ad_edit': 'Edit Ad',
        'device_list': 'Devices',
        'device_create': 'Add Device',
        'device_detail': 'Device Details',
        'device_edit': 'Edit Device',
        'group_list': 'Device Groups',
        'group_create': 'Create Group',
        'group_detail': 'Group Details',
        'group_edit': 'Edit Group',
        'analytics_dashboard': 'Analytics',
        'playback_control': 'Playback Control',
        'user_settings': 'Settings',
        'user_list': 'Users',
        'user_create': 'Create User',
        'user_edit': 'Edit User',
        'branding_settings': 'Branding',
    }
    url_name = ''
    if request.resolver_match:
        url_name = request.resolver_match.url_name or ''
    return {'page_title': titles.get(url_name, 'Dashboard')}


def kill_switch_status(request):
    """Add kill switch status to every template."""
    from ads.models import KillSwitch
    ks = KillSwitch.objects.filter(pk=1).first()
    return {
        'kill_switch_active': ks.is_active if ks else False,
        'kill_switch': ks,
    }


def site_branding(request):
    """Add site branding (logo, favicon, site_name) to every template."""
    from ads.models import SiteBranding
    branding = SiteBranding.get_solo()
    return {'site_branding': branding}
