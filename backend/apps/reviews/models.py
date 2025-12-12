"""
Review models for InGazo application.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.rides.models import Ride


class Review(models.Model):
    """
    Review model for rating drivers and passengers after rides.
    """

    class ReviewType(models.TextChoices):
        DRIVER_REVIEW = 'driver', _('Driver Review')  # Passenger reviews driver
        PASSENGER_REVIEW = 'passenger', _('Passenger Review')  # Driver reviews passenger

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Ride')
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        verbose_name=_('Reviewer')
    )

    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        verbose_name=_('Target User')
    )

    review_type = models.CharField(
        max_length=20,
        choices=ReviewType.choices,
        verbose_name=_('Review Type')
    )

    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        verbose_name=_('Rating'),
        help_text=_('Rating from 1 to 5 stars')
    )

    comment = models.TextField(
        blank=True,
        max_length=1000,
        verbose_name=_('Comment')
    )

    # Response from the reviewed user
    response = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Response'),
        help_text=_('Response from the reviewed user')
    )

    response_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Response At')
    )

    # Moderation
    is_visible = models.BooleanField(
        default=True,
        verbose_name=_('Visible'),
        help_text=_('Whether the review is publicly visible')
    )

    is_flagged = models.BooleanField(
        default=False,
        verbose_name=_('Flagged'),
        help_text=_('Whether the review has been flagged for moderation')
    )

    flagged_reason = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Flagged Reason')
    )

    moderated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Moderated At')
    )

    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_reviews',
        verbose_name=_('Moderated By')
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
        db_table = 'reviews'
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['reviewer']),
            models.Index(fields=['target']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
        # Prevent duplicate reviews for same ride by same reviewer
        constraints = [
            models.UniqueConstraint(
                fields=['ride', 'reviewer', 'target'],
                name='unique_review_per_ride_reviewer_target'
            )
        ]

    def __str__(self):
        return f"{self.reviewer} → {self.target} ({self.rating}★)"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # Update driver rating if this is a new driver review
        if is_new and self.review_type == self.ReviewType.DRIVER_REVIEW:
            if hasattr(self.target, 'driver_profile'):
                self.target.driver_profile.update_rating(self.rating)

    def add_response(self, response_text: str) -> None:
        """Add a response from the reviewed user."""
        from django.utils import timezone
        
        self.response = response_text
        self.response_at = timezone.now()
        self.save(update_fields=['response', 'response_at', 'updated_at'])

    def flag(self, reason: str) -> None:
        """Flag the review for moderation."""
        self.is_flagged = True
        self.flagged_reason = reason
        self.save(update_fields=['is_flagged', 'flagged_reason', 'updated_at'])

    def moderate(self, moderator, is_visible: bool) -> None:
        """Moderate the review."""
        from django.utils import timezone
        
        self.is_visible = is_visible
        self.is_flagged = False
        self.moderated_at = timezone.now()
        self.moderated_by = moderator
        self.save(update_fields=[
            'is_visible',
            'is_flagged',
            'moderated_at',
            'moderated_by',
            'updated_at'
        ])

