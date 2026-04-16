from django.db import models
from django.conf import settings


class Device(models.Model):
    device_name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=100, unique=True)
    secret_key = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    is_online = models.BooleanField(default=False)
    last_active = models.DateTimeField(null=True, blank=True)
    assigned_ads = models.ManyToManyField('ads.Ad', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='owned_devices')

    def __str__(self):
        return self.device_name


class DeviceGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    devices = models.ManyToManyField(Device, blank=True, related_name='groups')
    assigned_ads = models.ManyToManyField('ads.Ad', blank=True, related_name='device_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='owned_groups')

    def __str__(self):
        return self.name