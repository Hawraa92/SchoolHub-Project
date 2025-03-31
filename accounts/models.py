from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django.core.files.storage import default_storage

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.png", blank=True, null=True)  # Improved avatar field

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username or self.email

    def save(self, *args, **kwargs):
        if not self.username:
            email_username, _ = self.email.split("@")
            self.username = email_username
        
        # Ensure the default avatar exists
        if not self.avatar:
            default_path = "avatars/default.png"
            if default_storage.exists(default_path):
                self.avatar = default_path

        super(User, self).save(*args, **kwargs)
