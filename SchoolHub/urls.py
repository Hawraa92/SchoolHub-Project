"""
URL configuration for the SchoolHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for the SchoolHub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home  # If you have a home view, keep it; otherwise, remove or adjust.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Home view placeholder
    path('students/', include('students.urls')),
    path('accounts/', include('accounts.urls')),
    path('teachers/', include('teachers.urls')),

    # IMPORTANT: include the reports app URLs
    path('reports/', include('reports.urls')),
]

# Serving media and static files in development (optional)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
