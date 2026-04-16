from django.contrib import admin
from devices.models import Device, DeviceGroup


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_id', 'secret_key', 'location', 'is_online', 'last_active')
    search_fields = ('device_name', 'device_id', 'location')
    list_filter = ('is_online',)


@admin.register(DeviceGroup)
class DeviceGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('devices', 'assigned_ads')
