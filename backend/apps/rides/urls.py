"""
URL configuration for the Rides app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RideRecurringViewSet, RideViewSet

app_name = 'rides'

router = DefaultRouter()
router.register(r'recurring', RideRecurringViewSet, basename='ride-recurring')
router.register(r'', RideViewSet, basename='ride')

urlpatterns = [
    path('', include(router.urls)),
]

