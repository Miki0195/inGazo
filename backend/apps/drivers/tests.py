"""
Tests for the Drivers app.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Driver, DriverDocument

User = get_user_model()


class DriverModelTests(TestCase):
    """
    Tests for the Driver model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='driver@example.com',
            password='testpass123'
        )

    def test_create_driver(self):
        """Test creating a driver profile."""
        driver = Driver.objects.create(
            user=self.user,
            license_number='ABC123456'
        )
        
        self.assertEqual(driver.user, self.user)
        self.assertEqual(driver.license_number, 'ABC123456')
        self.assertEqual(driver.rating, 0.0)
        self.assertEqual(driver.total_trips, 0)

    def test_update_rating(self):
        """Test updating driver rating."""
        driver = Driver.objects.create(
            user=self.user,
            license_number='ABC123456'
        )
        
        driver.update_rating(4.0)
        self.assertEqual(driver.rating, 4.0)
        self.assertEqual(driver.total_reviews, 1)
        
        driver.update_rating(5.0)
        self.assertEqual(driver.rating, 4.5)
        self.assertEqual(driver.total_reviews, 2)


class DriverAPITests(APITestCase):
    """
    Tests for the Driver API endpoints.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_become_driver(self):
        """Test becoming a driver."""
        data = {
            'license_number': 'ABC123456',
            'bio': 'Experienced driver',
        }
        response = self.client.post('/api/v1/drivers/become/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Driver.objects.filter(user=self.user).exists())

    # Add more tests as needed

