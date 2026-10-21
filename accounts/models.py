from django.db import models
from django.contrib.auth.models import AbstractUser


class AuthUserModel(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="users/profile/",
        blank=True,
        null=True
        )
    is_customer = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username}"