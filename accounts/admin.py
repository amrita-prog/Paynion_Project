from django.contrib import admin
from .models import CustomUser, Notification
from django.utils.html import format_html


# Register your models here.

# superuser = admin (amrita@gmail.com)
# password = admin

admin.site.site_header = "Admin"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Welcome to Admin Panel"

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('profile_image_tag', 'full_name', 'email', 'phone', 'upi_id')
    search_fields = ('full_name', 'email', 'phone')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                                obj.profile_image.url)
        return "No Image"