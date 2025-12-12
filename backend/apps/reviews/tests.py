"""
Tests for the Reviews app.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.bookings.models import Booking
from apps.drivers.models import Driver
from apps.rides.models import Ride
from apps.vehicles.models import Vehicle

from .models import Review

User = get_user_model()


class ReviewModelTests(TestCase):
    """
    Tests for the Review model.
    """

    def setUp(self):
        # Create driver
        self.driver_user = User.objects.create_user(
            email='driver@example.com',
            password='testpass123',
            full_name='Test Driver'
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
            departure_time=timezone.now() - timedelta(days=1),
            seats_total=3,
            start_location=Point(16.3738, 48.2082),
            end_location=Point(19.0402, 47.4979),
            start_city='Vienna',
            end_city='Budapest',
            price_per_seat=Decimal('25.00'),
            status=Ride.RideStatus.FINISHED
        )
        
        # Create passenger
        self.passenger = User.objects.create_user(
            email='passenger@example.com',
            password='testpass123',
            full_name='Test Passenger'
        )

    def test_create_review(self):
        """Test creating a review."""
        review = Review.objects.create(
            ride=self.ride,
            reviewer=self.passenger,
            target=self.driver_user,
            review_type=Review.ReviewType.DRIVER_REVIEW,
            rating=5,
            comment='Great driver!'
        )
        
        self.assertEqual(review.reviewer, self.passenger)
        self.assertEqual(review.target, self.driver_user)
        self.assertEqual(review.rating, 5)
        self.assertTrue(review.is_visible)

    def test_add_response(self):
        """Test adding a response to a review."""
        review = Review.objects.create(
            ride=self.ride,
            reviewer=self.passenger,
            target=self.driver_user,
            review_type=Review.ReviewType.DRIVER_REVIEW,
            rating=4,
            comment='Good ride'
        )
        
        review.add_response('Thank you!')
        
        self.assertEqual(review.response, 'Thank you!')
        self.assertIsNotNone(review.response_at)


class ReviewAPITests(APITestCase):
    """
    Tests for the Review API endpoints.
    """

    def setUp(self):
        # Create driver
        self.driver_user = User.objects.create_user(
            email='driver@example.com',
            password='testpass123',
            full_name='Test Driver'
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
        
        # Create finished ride
        self.ride = Ride.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            departure_time=timezone.now() - timedelta(days=1),
            seats_total=3,
            start_location=Point(16.3738, 48.2082),
            end_location=Point(19.0402, 47.4979),
            start_city='Vienna',
            end_city='Budapest',
            price_per_seat=Decimal('25.00'),
            status=Ride.RideStatus.FINISHED
        )
        
        # Create passenger with completed booking
        self.passenger = User.objects.create_user(
            email='passenger@example.com',
            password='testpass123',
            full_name='Test Passenger'
        )
        
        self.booking = Booking.objects.create(
            ride=self.ride,
            user=self.passenger,
            seats_reserved=1,
            status=Booking.BookingStatus.COMPLETED
        )

    def test_create_review(self):
        """Test creating a review via API."""
        self.client.force_authenticate(user=self.passenger)
        
        data = {
            'ride_id': str(self.ride.id),
            'target_id': str(self.driver_user.id),
            'rating': 5,
            'comment': 'Excellent ride!',
        }
        response = self.client.post('/api/v1/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.filter(reviewer=self.passenger).exists())

    # Add more tests as needed

