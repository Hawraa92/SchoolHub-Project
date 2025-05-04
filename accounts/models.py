from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import default_storage

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png",
        blank=True,
        null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username or self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split("@")[0]

        if not self.avatar:
            default_path = "avatars/default.png"
            if default_storage.exists(default_path):
                self.avatar = default_path

        super().save(*args, **kwargs)
