
from django.contrib import admin
from django.shortcuts import redirect
from .models import PredictionConfig

try:
    admin.site.unregister(PredictionConfig)
except admin.sites.NotRegistered:
    pass

@admin.register(PredictionConfig)
class PredictionConfigAdmin(admin.ModelAdmin):
    list_display = ("name",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return redirect('performance_dashboard')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return redirect('performance_dashboard')
