from django.contrib import admin
from .models import Group, GroupInvite

# Register your models here.

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'last_settled_at')
    search_fields = ('title', 'description', 'created_by__full_name', 'members__full_name')
    list_filter = ('created_at', 'last_settled_at')
    ordering = ('-created_at',)
    filter_horizontal = ('members',)

@admin.register(GroupInvite)
class GroupInviteAdmin(admin.ModelAdmin):
    list_display = ('email', 'group', 'invited_by', 'is_accepted', 'created_at')
    search_fields = ('email', 'group__title', 'invited_by__full_name')
    list_filter = ('is_accepted', 'created_at')
    ordering = ('-created_at',)