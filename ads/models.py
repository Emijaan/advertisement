from django.db import models
from django.conf import settings

# Create your models here.
class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to='ads/')
    duration = models.IntegerField()  # in seconds
    play_limit = models.IntegerField()
    priority = models.IntegerField(default=1)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='owned_ads')

    def __str__(self):
        return self.title


class KillSwitch(models.Model):
    """Singleton model: when active=True, ALL ads are stopped immediately across all devices."""
    is_active = models.BooleanField(default=False)
    activated_at = models.DateTimeField(null=True, blank=True)
    activated_by = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = 'Kill Switch'
        verbose_name_plural = 'Kill Switch'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def is_killed(cls):
        obj = cls.objects.filter(pk=1).first()
        return obj.is_active if obj else False

    def __str__(self):
        return f"Kill Switch ({'ACTIVE' if self.is_active else 'Inactive'})"
