from django.contrib import admin
from django.utils.html import format_html
from accounts.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'display_avatar', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)

    def display_avatar(self, obj):
        """عرض صورة المستخدم في لوحة تحكم Django."""
        if obj.avatar:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%;" />', obj.avatar.url)
        return "No Avatar"

    display_avatar.short_description = "Avatar"

admin.site.register(User, UserAdmin)
