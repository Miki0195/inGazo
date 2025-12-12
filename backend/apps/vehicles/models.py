"""
Vehicle models for InGazo application.
"""

import uuid
from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.drivers.models import Driver


class Vehicle(models.Model):
    """
    Vehicle model representing a car registered by a driver.
    """

    class VehicleColor(models.TextChoices):
        BLACK = 'black', _('Black')
        WHITE = 'white', _('White')
        SILVER = 'silver', _('Silver')
        GRAY = 'gray', _('Gray')
        RED = 'red', _('Red')
        BLUE = 'blue', _('Blue')
        GREEN = 'green', _('Green')
        YELLOW = 'yellow', _('Yellow')
        BROWN = 'brown', _('Brown')
        ORANGE = 'orange', _('Orange')
        OTHER = 'other', _('Other')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name='vehicles',
        verbose_name=_('Driver')
    )

    make = models.CharField(
        max_length=100,
        verbose_name=_('Make'),
        help_text=_('Vehicle manufacturer (e.g., Toyota, BMW)')
    )

    model = models.CharField(
        max_length=100,
        verbose_name=_('Model'),
        help_text=_('Vehicle model (e.g., Corolla, 3 Series)')
    )

    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1990),
            MaxValueValidator(date.today().year + 1)
        ],
        verbose_name=_('Year'),
        help_text=_('Manufacturing year')
    )

    license_plate = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('License Plate'),
        db_index=True
    )

    color = models.CharField(
        max_length=20,
        choices=VehicleColor.choices,
        default=VehicleColor.OTHER,
        verbose_name=_('Color')
    )

    seats = models.PositiveIntegerField(
        default=4,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9)
        ],
        verbose_name=_('Available Seats'),
        help_text=_('Number of passenger seats available (excluding driver)')
    )

    photo_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Photo URL')
    )

    # Vehicle features
    has_air_conditioning = models.BooleanField(
        default=True,
        verbose_name=_('Air Conditioning')
    )

    has_wifi = models.BooleanField(
        default=False,
        verbose_name=_('WiFi')
    )

    has_usb_charger = models.BooleanField(
        default=False,
        verbose_name=_('USB Charger')
    )

    trunk_space = models.CharField(
        max_length=20,
        choices=[
            ('small', _('Small')),
            ('medium', _('Medium')),
            ('large', _('Large')),
        ],
        default='medium',
        verbose_name=_('Trunk Space')
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Whether the vehicle is currently available for rides')
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified'),
        help_text=_('Whether the vehicle has been verified by admin')
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
        db_table = 'vehicles'
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['license_plate']),
            models.Index(fields=['driver']),
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['make', 'model']),
        ]

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.license_plate})"

    @property
    def full_name(self) -> str:
        """Return the full vehicle name."""
        return f"{self.year} {self.make} {self.model}"

    @property
    def driver_name(self) -> str:
        """Return the driver's name."""
        return self.driver.full_name

