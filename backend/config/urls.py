"""
URL configuration for BioAI Hub project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/', include([
        path('auth/', include('apps.authentication.urls')),
        path('resources/', include('apps.resources.urls')),  # US-05, US-06, US-07, US-08
        # path('notifications/', include('apps.notifications.urls')),  # TODO: Implementar US-18
        path('users/', include('apps.authentication.urls_users')),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
