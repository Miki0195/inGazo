"""
Notification models for InGazo application.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    Notification model for user alerts and messages.
    """

    class NotificationType(models.TextChoices):
        # Booking related
        BOOKING_REQUEST = 'booking_request', _('New Booking Request')
        BOOKING_CONFIRMED = 'booking_confirmed', _('Booking Confirmed')
        BOOKING_CANCELLED = 'booking_cancelled', _('Booking Cancelled')
        BOOKING_REJECTED = 'booking_rejected', _('Booking Rejected')
        
        # Ride related
        RIDE_STARTING = 'ride_starting', _('Ride Starting Soon')
        RIDE_STARTED = 'ride_started', _('Ride Started')
        RIDE_CANCELLED = 'ride_cancelled', _('Ride Cancelled')
        RIDE_COMPLETED = 'ride_completed', _('Ride Completed')
        
        # Driver related
        DRIVER_VERIFIED = 'driver_verified', _('Driver Verified')
        DOCUMENT_APPROVED = 'document_approved', _('Document Approved')
        DOCUMENT_REJECTED = 'document_rejected', _('Document Rejected')
        
        # Review related
        NEW_REVIEW = 'new_review', _('New Review')
        
        # System
        SYSTEM = 'system', _('System Notification')
        PROMOTIONAL = 'promotional', _('Promotional')

    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        NORMAL = 'normal', _('Normal')
        HIGH = 'high', _('High')
        URGENT = 'urgent', _('Urgent')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('User')
    )

    type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        verbose_name=_('Type'),
        db_index=True
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_('Title')
    )

    message = models.TextField(
        max_length=1000,
        verbose_name=_('Message')
    )

    # Optional reference to related objects
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Reference Type'),
        help_text=_('Type of related object (e.g., "booking", "ride")')
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Reference ID'),
        help_text=_('ID of related object')
    )

    # Status
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Read'),
        db_index=True
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Read At')
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
        verbose_name=_('Priority')
    )

    # Push notification status
    push_sent = models.BooleanField(
        default=False,
        verbose_name=_('Push Sent')
    )

    push_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Push Sent At')
    )

    # Email notification status
    email_sent = models.BooleanField(
        default=False,
        verbose_name=_('Email Sent')
    )

    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Email Sent At')
    )

    # Action URL for deep linking
    action_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Action URL'),
        help_text=_('URL or deep link for notification action')
    )

    # Metadata for additional info
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Metadata')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Expires At'),
        help_text=_('When the notification expires and should be auto-deleted')
    )

    class Meta:
        db_table = 'notifications'
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.title}"

    def mark_as_read(self) -> None:
        """Mark notification as read."""
        from django.utils import timezone
        
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    @classmethod
    def create_notification(
        cls,
        user,
        notification_type: str,
        title: str,
        message: str,
        reference_type: str = '',
        reference_id=None,
        priority: str = 'normal',
        action_url: str = '',
        metadata: dict = None
    ):
        """
        Helper method to create a notification.
        """
        return cls.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id,
            priority=priority,
            action_url=action_url,
            metadata=metadata or {}
        )


class NotificationPreference(models.Model):
    """
    User preferences for notification delivery.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('User')
    )

    # Email preferences
    email_booking_updates = models.BooleanField(
        default=True,
        verbose_name=_('Email: Booking Updates')
    )

    email_ride_reminders = models.BooleanField(
        default=True,
        verbose_name=_('Email: Ride Reminders')
    )

    email_promotional = models.BooleanField(
        default=False,
        verbose_name=_('Email: Promotional')
    )

    # Push notification preferences
    push_booking_updates = models.BooleanField(
        default=True,
        verbose_name=_('Push: Booking Updates')
    )

    push_ride_reminders = models.BooleanField(
        default=True,
        verbose_name=_('Push: Ride Reminders')
    )

    push_chat_messages = models.BooleanField(
        default=True,
        verbose_name=_('Push: Chat Messages')
    )

    push_promotional = models.BooleanField(
        default=False,
        verbose_name=_('Push: Promotional')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')

    def __str__(self):
        return f"{self.user} - Notification Preferences"

