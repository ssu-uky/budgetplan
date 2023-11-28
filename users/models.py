from django.db import models
from .manager import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid


class User(AbstractBaseUser, PermissionsMixin):
    # id = models.UUIDField(
    #     primary_key=True, default=uuid.uuid4, editable=False, unique=True
    # )
    username = models.CharField(max_length=50, unique=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    name = models.CharField(max_length=50, blank=False)

    objects = CustomUserManager()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
