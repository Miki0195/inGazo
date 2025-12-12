"""
Tests for the Notifications app.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Notification, NotificationPreference

User = get_user_model()


class NotificationModelTests(TestCase):
    """
    Tests for the Notification model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_create_notification(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            user=self.user,
            type=Notification.NotificationType.BOOKING_CONFIRMED,
            title='Booking Confirmed',
            message='Your booking has been confirmed.'
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.priority, Notification.Priority.NORMAL)

    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            user=self.user,
            type=Notification.NotificationType.SYSTEM,
            title='Test',
            message='Test message'
        )
        
        notification.mark_as_read()
        
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

    def test_create_notification_helper(self):
        """Test the create_notification helper method."""
        notification = Notification.create_notification(
            user=self.user,
            notification_type=Notification.NotificationType.RIDE_STARTING,
            title='Ride Starting Soon',
            message='Your ride starts in 30 minutes',
            priority='high',
            metadata={'ride_id': 'test-123'}
        )
        
        self.assertEqual(notification.priority, 'high')
        self.assertEqual(notification.metadata['ride_id'], 'test-123')


class NotificationAPITests(APITestCase):
    """
    Tests for the Notification API endpoints.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create some notifications
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                type=Notification.NotificationType.SYSTEM,
                title=f'Test Notification {i}',
                message=f'Test message {i}'
            )

    def test_list_notifications(self):
        """Test listing notifications."""
        response = self.client.get('/api/v1/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_unread_count(self):
        """Test getting unread count."""
        response = self.client.get('/api/v1/notifications/unread_count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 5)

    def test_mark_all_read(self):
        """Test marking all notifications as read."""
        response = self.client.post('/api/v1/notifications/mark_read/', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        
        # Verify all are read
        unread_count = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)

    # Add more tests as needed

