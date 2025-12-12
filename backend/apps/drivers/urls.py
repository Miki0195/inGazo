"""
URL configuration for the Drivers app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BecomeDriverView,
    DriverDocumentViewSet,
    DriverProfileView,
    DriverViewSet,
)

app_name = 'drivers'

router = DefaultRouter()
router.register(r'', DriverViewSet, basename='driver')
router.register(r'documents', DriverDocumentViewSet, basename='driver-document')

urlpatterns = [
    # Become a driver
    path('become/', BecomeDriverView.as_view(), name='become-driver'),
    
    # Current user's driver profile
    path('profile/', DriverProfileView.as_view(), name='driver-profile'),
    
    # ViewSet routes
    path('', include(router.urls)),
]

