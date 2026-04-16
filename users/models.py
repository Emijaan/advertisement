from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("SUPERADMIN", "Super Admin"),
        ("ADMIN", "Admin"),
        ("USER", "User"),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='USER')
    device_limit = models.IntegerField(default=10, help_text='Max devices this user can create. 0 = unlimited. Only applies to USER role.')
    created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_users')

    def __str__(self):
        return self.username