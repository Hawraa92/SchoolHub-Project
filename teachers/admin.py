from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'mobile', 'get_age', 'list_subjects')
    search_fields = ('full_name', 'email', 'mobile')
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'full_name', 'date_of_birth', 'gender', 'email', 'mobile', 'address', 'subjects')
        }),
    )
    readonly_fields = ('get_age',)

    @admin.display(description="Age")
    def get_age(self, obj):
        return obj.age or "-"

    @admin.display(description="Subjects")
    def list_subjects(self, obj):
        return ", ".join(subject.name for subject in obj.subjects.all())
