"""
Tests for the Vehicles app.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.drivers.models import Driver

from .models import Vehicle

User = get_user_model()


class VehicleModelTests(TestCase):
    """
    Tests for the Vehicle model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='driver@example.com',
            password='testpass123'
        )
        self.driver = Driver.objects.create(
            user=self.user,
            license_number='ABC123456'
        )

    def test_create_vehicle(self):
        """Test creating a vehicle."""
        vehicle = Vehicle.objects.create(
            driver=self.driver,
            make='Toyota',
            model='Corolla',
            year=2020,
            license_plate='ABC-123',
            seats=4
        )
        
        self.assertEqual(vehicle.driver, self.driver)
        self.assertEqual(vehicle.make, 'Toyota')
        self.assertEqual(vehicle.full_name, '2020 Toyota Corolla')


class VehicleAPITests(APITestCase):
    """
    Tests for the Vehicle API endpoints.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='driver@example.com',
            password='testpass123'
        )
        self.driver = Driver.objects.create(
            user=self.user,
            license_number='ABC123456'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_vehicle(self):
        """Test creating a vehicle via API."""
        data = {
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'license_plate': 'ABC-123',
            'seats': 4,
        }
        response = self.client.post('/api/v1/vehicles/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Vehicle.objects.filter(license_plate='ABC-123').exists())

    # Add more tests as needed

