from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'SUPERADMIN')
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ("SUPERADMIN", "Super Admin"),
        ("ADMIN", "Admin"),
        ("USER", "User"),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='USER')

    objects = CustomUserManager()
    device_limit = models.IntegerField(default=10, help_text='Max devices this user can create. 0 = unlimited. Only applies to USER role.')
    created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_users')

    def __str__(self):
        return self.username