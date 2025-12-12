"""
Booking models for InGazo application.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.rides.models import Ride


class Booking(models.Model):
    """
    Booking model for ride reservations.
    Connects passengers with rides.
    """

    class BookingStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        CANCELLED = 'cancelled', _('Cancelled')
        COMPLETED = 'completed', _('Completed')
        REJECTED = 'rejected', _('Rejected')
        NO_SHOW = 'no_show', _('No Show')

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PAID = 'paid', _('Paid')
        REFUNDED = 'refunded', _('Refunded')
        FAILED = 'failed', _('Failed')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Ride')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Passenger')
    )

    seats_reserved = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9)
        ],
        verbose_name=_('Seats Reserved'),
        help_text=_('Number of seats booked')
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name=_('Status'),
        db_index=True
    )

    # Payment information
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Total Price'),
        help_text=_('Total price for all seats')
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_('Payment Status')
    )

    payment_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Payment Reference'),
        help_text=_('External payment system reference')
    )

    # Pickup/dropoff preferences
    pickup_note = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Pickup Note'),
        help_text=_('Additional info for pickup location')
    )

    # Communication
    passenger_message = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Message to Driver'),
        help_text=_('Message from passenger to driver')
    )

    driver_message = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Message from Driver'),
        help_text=_('Message from driver to passenger')
    )

    # Status timestamps
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Confirmed At')
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Cancelled At')
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )

    cancellation_reason = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Cancellation Reason')
    )

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_bookings',
        verbose_name=_('Cancelled By')
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
        db_table = 'bookings'
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ride', 'user']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
        # Prevent duplicate bookings for same ride by same user
        constraints = [
            models.UniqueConstraint(
                fields=['ride', 'user'],
                condition=models.Q(status__in=['pending', 'confirmed']),
                name='unique_active_booking_per_user_ride'
            )
        ]

    def __str__(self):
        return f"{self.user.full_name or self.user.email} - {self.ride}"

    def save(self, *args, **kwargs):
        # Calculate price if not set
        if not self.price:
            self.price = self.ride.price_per_seat * self.seats_reserved
        super().save(*args, **kwargs)

    @property
    def is_cancellable(self) -> bool:
        """Check if booking can still be cancelled."""
        return self.status in [
            self.BookingStatus.PENDING,
            self.BookingStatus.CONFIRMED
        ]

    def confirm(self) -> bool:
        """
        Confirm the booking and reserve seats on the ride.
        """
        from django.utils import timezone
        
        if self.status != self.BookingStatus.PENDING:
            return False
        
        # Try to reserve seats
        if not self.ride.reserve_seats(self.seats_reserved):
            return False
        
        self.status = self.BookingStatus.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save(update_fields=['status', 'confirmed_at', 'updated_at'])
        return True

    def cancel(self, cancelled_by=None, reason: str = '') -> bool:
        """
        Cancel the booking and release seats.
        """
        from django.utils import timezone
        
        if not self.is_cancellable:
            return False
        
        # Release seats if booking was confirmed
        if self.status == self.BookingStatus.CONFIRMED:
            self.ride.release_seats(self.seats_reserved)
        
        self.status = self.BookingStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason
        self.save(update_fields=[
            'status',
            'cancelled_at',
            'cancelled_by',
            'cancellation_reason',
            'updated_at'
        ])
        return True

    def complete(self) -> bool:
        """
        Mark booking as completed after ride finishes.
        """
        from django.utils import timezone
        
        if self.status != self.BookingStatus.CONFIRMED:
            return False
        
        self.status = self.BookingStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])
        return True

    def reject(self, reason: str = '') -> bool:
        """
        Reject a pending booking request.
        """
        if self.status != self.BookingStatus.PENDING:
            return False
        
        self.status = self.BookingStatus.REJECTED
        self.cancellation_reason = reason
        self.save(update_fields=['status', 'cancellation_reason', 'updated_at'])
        return True

