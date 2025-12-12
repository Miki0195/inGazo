"""
URL configuration for InGazo project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# API v1 URL patterns
api_v1_patterns = [
    # Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App URLs
    path('users/', include('apps.users.urls')),
    path('drivers/', include('apps.drivers.urls')),
    path('vehicles/', include('apps.vehicles.urls')),
    path('rides/', include('apps.rides.urls')),
    path('bookings/', include('apps.bookings.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('reviews/', include('apps.reviews.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include((api_v1_patterns, 'api-v1'))),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site configuration
admin.site.site_header = 'InGazo Administration'
admin.site.site_title = 'InGazo Admin'
admin.site.index_title = 'Welcome to InGazo Admin Panel'

