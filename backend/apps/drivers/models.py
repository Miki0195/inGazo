"""
Driver models for InGazo application.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Driver(models.Model):
    """
    Driver profile extending the base User model.
    Contains driver-specific information like license and ratings.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        verbose_name=_('User')
    )

    license_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('License Number'),
        help_text=_('Driver\'s license number')
    )

    license_expiry = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('License Expiry Date')
    )

    license_photo_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('License Photo URL')
    )

    rating = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ],
        verbose_name=_('Rating'),
        help_text=_('Average rating from 0 to 5')
    )

    total_trips = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Trips'),
        help_text=_('Total number of completed trips')
    )

    total_reviews = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Reviews'),
        help_text=_('Total number of reviews received')
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified Driver'),
        help_text=_('Whether the driver has been verified by admin')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Whether the driver is currently active')
    )

    bio = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Bio'),
        help_text=_('Short description about the driver')
    )

    # Preferences
    accepts_smoking = models.BooleanField(
        default=False,
        verbose_name=_('Accepts Smoking')
    )

    accepts_pets = models.BooleanField(
        default=False,
        verbose_name=_('Accepts Pets')
    )

    accepts_luggage = models.BooleanField(
        default=True,
        verbose_name=_('Accepts Luggage')
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
        db_table = 'drivers'
        verbose_name = _('Driver')
        verbose_name_plural = _('Drivers')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['license_number']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_verified', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.full_name or self.user.email} - Driver"

    def update_rating(self, new_rating: float) -> None:
        """
        Update the driver's average rating with a new review.
        Uses weighted average calculation.
        """
        if self.total_reviews == 0:
            self.rating = new_rating
        else:
            total_rating = self.rating * self.total_reviews
            self.rating = (total_rating + new_rating) / (self.total_reviews + 1)
        
        self.total_reviews += 1
        self.save(update_fields=['rating', 'total_reviews', 'updated_at'])

    def increment_trips(self) -> None:
        """
        Increment the total trips counter.
        """
        self.total_trips += 1
        self.save(update_fields=['total_trips', 'updated_at'])

    @property
    def full_name(self) -> str:
        """Return the driver's full name."""
        return self.user.full_name or self.user.email


class DriverDocument(models.Model):
    """
    Documents uploaded by drivers for verification.
    """

    class DocumentType(models.TextChoices):
        LICENSE = 'license', _('Driver License')
        INSURANCE = 'insurance', _('Insurance')
        VEHICLE_REGISTRATION = 'registration', _('Vehicle Registration')
        ID_CARD = 'id_card', _('ID Card')
        OTHER = 'other', _('Other')

    class DocumentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending Review')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
        EXPIRED = 'expired', _('Expired')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Driver')
    )

    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        verbose_name=_('Document Type')
    )

    document_url = models.URLField(
        max_length=500,
        verbose_name=_('Document URL')
    )

    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.PENDING,
        verbose_name=_('Status')
    )

    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Expiry Date')
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_('Rejection Reason')
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Reviewed At')
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_documents',
        verbose_name=_('Reviewed By')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        db_table = 'driver_documents'
        verbose_name = _('Driver Document')
        verbose_name_plural = _('Driver Documents')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.driver} - {self.get_document_type_display()}"

