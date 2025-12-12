"""
URL configuration for the Users app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomTokenObtainPairView,
    UserDetailByEmailView,
    UserDetailByPhoneView,
    UserProfileView,
    UserRegistrationView,
    UserViewSet,
)

app_name = 'users'

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # Authentication
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    
    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Check availability
    path('check/email/<str:email>/', UserDetailByEmailView.as_view(), name='check-email'),
    path('check/phone/<str:phone_number>/', UserDetailByPhoneView.as_view(), name='check-phone'),
    
    # ViewSet routes
    path('', include(router.urls)),
]

