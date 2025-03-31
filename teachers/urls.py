from django.urls import path
from . import views  # Import views from teachers app

urlpatterns = [
    path('dashboard/', views.dashboard, name='teachers_dashboard'),  # Keep only valid views
]
