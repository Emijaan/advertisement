from django.db import models

# Create your models here.
class PlayLog(models.Model):
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE)
    ad = models.ForeignKey('ads.Ad', on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)
