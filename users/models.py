from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
    ("SUPERADMIN", "Super Admin"),
        ("ADMIN", "Admin"),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)