from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

def user_profile_path(instance, filename):
    return f"profile_pics/{instance.full_name}/{filename}"

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10, blank=True, null=True)
    profile_image = models.ImageField(upload_to=user_profile_path, default='default_profile.png')
    bio = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']   # keep username but don't use for login

    def __str__(self):
        return self.email
