"""
Tests for the Rides app.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.drivers.models import Driver
from apps.vehicles.models import Vehicle

from .models import Ride, RideRecurring, RideStop

User = get_user_model()


class RideModelTests(TestCase):
    """
    Tests for the Ride model.
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
        self.vehicle = Vehicle.objects.create(
            driver=self.driver,
            make='Toyota',
            model='Corolla',
            year=2020,
            license_plate='ABC-123',
            seats=4
        )

    def test_create_ride(self):
        """Test creating a ride with geographic points."""
        ride = Ride.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            departure_time=timezone.now() + timedelta(days=1),
            seats_total=3,
            start_location=Point(16.3738, 48.2082),  # Vienna
            end_location=Point(19.0402, 47.4979),    # Budapest
            start_city='Vienna',
            end_city='Budapest',
            price_per_seat=Decimal('25.00')
        )
        
        self.assertEqual(ride.driver, self.driver)
        self.assertEqual(ride.seats_available, 3)
        self.assertEqual(ride.status, Ride.RideStatus.SCHEDULED)

    def test_reserve_seats(self):
        """Test seat reservation."""
        ride = Ride.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            departure_time=timezone.now() + timedelta(days=1),
            seats_total=3,
            start_location=Point(16.3738, 48.2082),
            end_location=Point(19.0402, 47.4979),
            start_city='Vienna',
            end_city='Budapest',
            price_per_seat=Decimal('25.00')
        )
        
        # Reserve 2 seats
        result = ride.reserve_seats(2)
        self.assertTrue(result)
        self.assertEqual(ride.seats_available, 1)
        
        # Try to reserve more than available
        result = ride.reserve_seats(2)
        self.assertFalse(result)


class RideAPITests(APITestCase):
    """
    Tests for the Ride API endpoints.
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
        self.vehicle = Vehicle.objects.create(
            driver=self.driver,
            make='Toyota',
            model='Corolla',
            year=2020,
            license_plate='ABC-123',
            seats=4
        )
        self.client.force_authenticate(user=self.user)

    def test_create_ride(self):
        """Test creating a ride via API."""
        data = {
            'vehicle_id': str(self.vehicle.id),
            'departure_time': (timezone.now() + timedelta(days=1)).isoformat(),
            'seats_total': 3,
            'start_location': {'latitude': 48.2082, 'longitude': 16.3738},
            'end_location': {'latitude': 47.4979, 'longitude': 19.0402},
            'start_city': 'Vienna',
            'end_city': 'Budapest',
            'price_per_seat': '25.00',
        }
        response = self.client.post('/api/v1/rides/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ride.objects.filter(driver=self.driver).exists())

    # Add more tests as needed

