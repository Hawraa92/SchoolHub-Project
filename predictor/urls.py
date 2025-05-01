# file: predictor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.performance_dashboard, name='performance_dashboard'),
]
