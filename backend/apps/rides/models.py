"""
Ride models for InGazo application.
Includes single trips, recurring rides, and ride stops using GeoDjango.
"""

import uuid

from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.drivers.models import Driver
from apps.vehicles.models import Vehicle


class Ride(models.Model):
    """
    Single trip ride model with geographic locations.
    Uses PostGIS PointField for spatial data.
    """

    class RideStatus(models.TextChoices):
        SCHEDULED = 'scheduled', _('Scheduled')
        ONGOING = 'ongoing', _('Ongoing')
        FINISHED = 'finished', _('Finished')
        CANCELLED = 'cancelled', _('Cancelled')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name='rides',
        verbose_name=_('Driver')
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='rides',
        verbose_name=_('Vehicle')
    )

    # Departure information
    departure_time = models.DateTimeField(
        verbose_name=_('Departure Time'),
        db_index=True
    )

    # Seat management
    seats_total = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9)
        ],
        verbose_name=_('Total Seats'),
        help_text=_('Total number of seats available for passengers')
    )

    seats_available = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(9)
        ],
        verbose_name=_('Available Seats'),
        help_text=_('Number of seats currently available')
    )

    # Geographic locations using GeoDjango PointField
    # SRID 4326 is WGS 84 (standard GPS coordinates)
    start_location = gis_models.PointField(
        srid=4326,
        verbose_name=_('Start Location'),
        spatial_index=True,
        help_text=_('Geographic point for pickup location')
    )

    end_location = gis_models.PointField(
        srid=4326,
        verbose_name=_('End Location'),
        spatial_index=True,
        help_text=_('Geographic point for dropoff location')
    )

    # Human-readable location names
    start_city = models.CharField(
        max_length=255,
        verbose_name=_('Start City'),
        db_index=True
    )

    start_address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Start Address')
    )

    end_city = models.CharField(
        max_length=255,
        verbose_name=_('End City'),
        db_index=True
    )

    end_address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('End Address')
    )

    # Pricing
    price_per_seat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Price per Seat'),
        help_text=_('Price in EUR for one seat')
    )

    # Estimated trip info
    estimated_duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Estimated Duration (minutes)')
    )

    estimated_distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Estimated Distance (km)')
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=RideStatus.choices,
        default=RideStatus.SCHEDULED,
        verbose_name=_('Status'),
        db_index=True
    )

    # Ride preferences
    notes = models.TextField(
        blank=True,
        max_length=1000,
        verbose_name=_('Notes'),
        help_text=_('Additional information about the ride')
    )

    allows_detours = models.BooleanField(
        default=False,
        verbose_name=_('Allows Detours'),
        help_text=_('Whether the driver can make small detours for pickups')
    )

    instant_booking = models.BooleanField(
        default=False,
        verbose_name=_('Instant Booking'),
        help_text=_('Allow passengers to book without driver approval')
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
        db_table = 'rides'
        verbose_name = _('Ride')
        verbose_name_plural = _('Rides')
        ordering = ['-departure_time']
        indexes = [
            models.Index(fields=['departure_time']),
            models.Index(fields=['status']),
            models.Index(fields=['start_city', 'end_city']),
            models.Index(fields=['driver']),
            models.Index(fields=['seats_available']),
            models.Index(fields=['price_per_seat']),
        ]

    def __str__(self):
        return f"{self.start_city} → {self.end_city} ({self.departure_time.strftime('%Y-%m-%d %H:%M')})"

    def save(self, *args, **kwargs):
        # Initialize seats_available if not set
        if self.seats_available is None:
            self.seats_available = self.seats_total
        super().save(*args, **kwargs)

    @property
    def is_full(self) -> bool:
        """Check if the ride is fully booked."""
        return self.seats_available == 0

    @property
    def has_seats(self) -> bool:
        """Check if there are seats available."""
        return self.seats_available > 0

    def reserve_seats(self, count: int) -> bool:
        """
        Reserve seats for a booking.
        Returns True if successful, False if not enough seats.
        """
        if count <= self.seats_available:
            self.seats_available -= count
            self.save(update_fields=['seats_available', 'updated_at'])
            return True
        return False

    def release_seats(self, count: int) -> None:
        """
        Release seats when a booking is cancelled.
        """
        self.seats_available = min(self.seats_available + count, self.seats_total)
        self.save(update_fields=['seats_available', 'updated_at'])


class RideStop(models.Model):
    """
    Intermediate stops for a ride.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='stops',
        verbose_name=_('Ride')
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_('Stop Name')
    )

    location = gis_models.PointField(
        srid=4326,
        verbose_name=_('Location'),
        spatial_index=True
    )

    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Address')
    )

    order = models.PositiveIntegerField(
        verbose_name=_('Order'),
        help_text=_('Order of the stop in the route (1 = first stop)')
    )

    estimated_arrival = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Estimated Arrival')
    )

    price_from_start = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Price from Start'),
        help_text=_('Price per seat from ride start to this stop')
    )

    class Meta:
        db_table = 'ride_stops'
        verbose_name = _('Ride Stop')
        verbose_name_plural = _('Ride Stops')
        ordering = ['ride', 'order']
        unique_together = [['ride', 'order']]

    def __str__(self):
        return f"{self.ride} - Stop {self.order}: {self.name}"


class RideRecurring(models.Model):
    """
    Recurring weekly ride template.
    Used to automatically create rides on specified days.
    """

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, _('Monday')
        TUESDAY = 1, _('Tuesday')
        WEDNESDAY = 2, _('Wednesday')
        THURSDAY = 3, _('Thursday')
        FRIDAY = 4, _('Friday')
        SATURDAY = 5, _('Saturday')
        SUNDAY = 6, _('Sunday')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name='recurring_rides',
        verbose_name=_('Driver')
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='recurring_rides',
        verbose_name=_('Vehicle')
    )

    # Days of week when this ride occurs (stored as array of integers 0-6)
    days_of_week = ArrayField(
        models.IntegerField(choices=DayOfWeek.choices),
        verbose_name=_('Days of Week'),
        help_text=_('Days when this recurring ride is active (0=Monday, 6=Sunday)')
    )

    # Time of departure
    time_of_day = models.TimeField(
        verbose_name=_('Time of Day'),
        help_text=_('Departure time')
    )

    # Geographic locations
    start_location = gis_models.PointField(
        srid=4326,
        verbose_name=_('Start Location'),
        spatial_index=True
    )

    end_location = gis_models.PointField(
        srid=4326,
        verbose_name=_('End Location'),
        spatial_index=True
    )

    start_city = models.CharField(
        max_length=255,
        verbose_name=_('Start City')
    )

    start_address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Start Address')
    )

    end_city = models.CharField(
        max_length=255,
        verbose_name=_('End City')
    )

    end_address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('End Address')
    )

    # Seat and pricing
    seats_total = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9)
        ],
        verbose_name=_('Total Seats')
    )

    price_per_seat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Price per Seat')
    )

    # Template validity
    valid_from = models.DateField(
        verbose_name=_('Valid From'),
        help_text=_('Start date for generating rides')
    )

    valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Valid Until'),
        help_text=_('End date for generating rides (null = indefinite)')
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
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
        db_table = 'ride_recurring'
        verbose_name = _('Recurring Ride')
        verbose_name_plural = _('Recurring Rides')
        ordering = ['-created_at']

    def __str__(self):
        days = ', '.join([self.DayOfWeek(d).label for d in self.days_of_week])
        return f"{self.start_city} → {self.end_city} ({days} at {self.time_of_day})"

    def get_days_display(self) -> str:
        """Return human-readable days string."""
        return ', '.join([self.DayOfWeek(d).label for d in sorted(self.days_of_week)])

