from django.contrib import admin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'display_avatar', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)

    def display_avatar(self, obj):
        """Display the user's avatar as a circular thumbnail."""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%;" />',
                obj.avatar.url
            )
        # Fallback to default avatar if none uploaded
        default_url = '/static/avatars/default.png'
        return format_html(
            '<img src="{}" width="40" height="40" style="border-radius:50%;" />',
            default_url
        )
    display_avatar.short_description = "Avatar"
