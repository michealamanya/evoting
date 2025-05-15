"""
URL configuration for voting_project project.

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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add electronic_voting app URLs
    path('voting/', include('electronic_voting.urls')),
    # Add analytics app URLs
    path('analytics/', include('analytics.urls')),
    # Add notification app URLs
    path('notifications/', include('notification.urls')),
    # Add user_management app URLs
    path('accounts/', include('user_management.urls')),
    # Include Django authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),
    # Redirect root URL to voting app
    path('', RedirectView.as_view(url='/voting/', permanent=True)),
    # Include new page URLs
    path('', include('pages.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

