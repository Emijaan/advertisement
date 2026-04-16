from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import profile, user_settings, playback_control, user_list, user_create, user_edit, user_delete
from devices.views import device_login, device_ads, device_play_log, device_list, device_detail, device_create, device_edit, device_delete, group_list, group_create, group_detail, group_edit, group_delete
from ads.views import ad_list, ad_create, ad_edit, ad_delete, ad_toggle, kill_switch_toggle
from analytics.views import analytics_dashboard
from adAgency.views import dashboard, branding_settings

router = DefaultRouter()

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth (login/, logout/, password_change/, etc.)
    path('', include('django.contrib.auth.urls')),

    # Dashboard
    path('', dashboard, name='dashboard'),

    # Ads CRUD
    path('ads/', ad_list, name='ad_list'),
    path('ads/create/', ad_create, name='ad_create'),
    path('ads/<int:pk>/edit/', ad_edit, name='ad_edit'),
    path('ads/<int:pk>/delete/', ad_delete, name='ad_delete'),
    path('ads/<int:pk>/toggle/', ad_toggle, name='ad_toggle'),
    path('kill-switch/', kill_switch_toggle, name='kill_switch_toggle'),

    # Devices CRUD
    path('devices/', device_list, name='device_list'),
    path('devices/create/', device_create, name='device_create'),
    path('devices/<int:pk>/', device_detail, name='device_detail'),
    path('devices/<int:pk>/edit/', device_edit, name='device_edit'),
    path('devices/<int:pk>/delete/', device_delete, name='device_delete'),

    # Device Groups
    path('groups/', group_list, name='group_list'),
    path('groups/create/', group_create, name='group_create'),
    path('groups/<int:pk>/', group_detail, name='group_detail'),
    path('groups/<int:pk>/edit/', group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', group_delete, name='group_delete'),

    # Analytics
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),

    # Playback
    path('playback/', playback_control, name='playback_control'),

    # Settings
    path('settings/', user_settings, name='user_settings'),
    path('settings/branding/', branding_settings, name='branding_settings'),

    # User Management (SUPERADMIN only)
    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_create'),
    path('users/<int:pk>/edit/', user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', user_delete, name='user_delete'),

    # API endpoints (for Android app)
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/profile/', profile),
    path('api/device/login/', device_login, name='device_login'),
    path('api/device/<str:device_id>/ads/', device_ads, name='device_ads'),
    path('api/device/<str:device_id>/play-log/', device_play_log, name='device_play_log'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
