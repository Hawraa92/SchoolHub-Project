from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, login_view

app_name = 'accounts'

urlpatterns = [
    path('register/', register, name='register'),

    path('login/', login_view, name='login'),

    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
]
