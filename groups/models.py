from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Group(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)

    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name="group_members")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
