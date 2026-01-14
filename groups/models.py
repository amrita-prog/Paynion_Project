from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL

class Group(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)

    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name="group_members")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups")
    created_at = models.DateTimeField(auto_now_add=True)
    last_settled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title




class GroupInvite(models.Model):
    email = models.EmailField()
    group = models.ForeignKey("Group", on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} → {self.group.title}"
