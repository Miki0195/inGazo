"""
Pytest configuration for InGazo backend.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client instance."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def create_user():
    """Factory fixture for creating users."""
    def _create_user(
        email='test@example.com',
        password='testpass123',
        **kwargs
    ):
        return User.objects.create_user(
            email=email,
            password=password,
            **kwargs
        )
    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return an authenticated API client."""
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user

