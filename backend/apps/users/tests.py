"""
Tests for the Users app.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserModelTests(TestCase):
    """
    Tests for the User model.
    """

    def test_create_user_with_email(self):
        """Test creating a user with email."""
        email = 'test@example.com'
        password = 'testpass123'
        user = User.objects.create_user(email=email, password=password)
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_phone(self):
        """Test creating a user with phone number."""
        phone = '+36301234567'
        password = 'testpass123'
        user = User.objects.create_user(phone_number=phone, password=password)
        
        self.assertEqual(user.phone_number, phone)
        self.assertTrue(user.check_password(password))

    def test_create_superuser(self):
        """Test creating a superuser."""
        email = 'admin@example.com'
        password = 'adminpass123'
        user = User.objects.create_superuser(email=email, password=password)
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_verified)


class UserAPITests(APITestCase):
    """
    Tests for the User API endpoints.
    """

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'full_name': 'Test User',
        }

    def test_user_registration(self):
        """Test user registration endpoint."""
        response = self.client.post('/api/v1/users/auth/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

    # Add more tests as needed

