"""
Tests for the Bookings app.
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
from apps.rides.models import Ride
from apps.vehicles.models import Vehicle

from .models import Booking

User = get_user_model()


class BookingModelTests(TestCase):
    """
    Tests for the Booking model.
    """

    def setUp(self):
        # Create driver
        self.driver_user = User.objects.create_user(
            email='driver@example.com',
            password='testpass123'
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
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
        
        # Create ride
        self.ride = Ride.objects.create(
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
        
        # Create passenger
        self.passenger = User.objects.create_user(
            email='passenger@example.com',
            password='testpass123'
        )

    def test_create_booking(self):
        """Test creating a booking."""
        booking = Booking.objects.create(
            ride=self.ride,
            user=self.passenger,
            seats_reserved=2
        )
        
        self.assertEqual(booking.user, self.passenger)
        self.assertEqual(booking.seats_reserved, 2)
        self.assertEqual(booking.price, Decimal('50.00'))
        self.assertEqual(booking.status, Booking.BookingStatus.PENDING)

    def test_confirm_booking(self):
        """Test confirming a booking reserves seats."""
        booking = Booking.objects.create(
            ride=self.ride,
            user=self.passenger,
            seats_reserved=2
        )
        
        initial_seats = self.ride.seats_available
        result = booking.confirm()
        
        self.assertTrue(result)
        self.assertEqual(booking.status, Booking.BookingStatus.CONFIRMED)
        
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.seats_available, initial_seats - 2)

    def test_cancel_booking_releases_seats(self):
        """Test cancelling a confirmed booking releases seats."""
        booking = Booking.objects.create(
            ride=self.ride,
            user=self.passenger,
            seats_reserved=2
        )
        booking.confirm()
        
        self.ride.refresh_from_db()
        seats_after_confirm = self.ride.seats_available
        
        booking.cancel()
        
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.seats_available, seats_after_confirm + 2)


class BookingAPITests(APITestCase):
    """
    Tests for the Booking API endpoints.
    """

    def setUp(self):
        # Create driver
        self.driver_user = User.objects.create_user(
            email='driver@example.com',
            password='testpass123'
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
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
        
        # Create ride
        self.ride = Ride.objects.create(
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
        
        # Create passenger
        self.passenger = User.objects.create_user(
            email='passenger@example.com',
            password='testpass123'
        )

    def test_create_booking(self):
        """Test creating a booking via API."""
        self.client.force_authenticate(user=self.passenger)
        
        data = {
            'ride_id': str(self.ride.id),
            'seats_reserved': 2,
            'passenger_message': 'Hello!',
        }
        response = self.client.post('/api/v1/bookings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Booking.objects.filter(user=self.passenger).exists())

    # Add more tests as needed

