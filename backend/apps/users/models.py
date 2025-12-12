"""
User models for InGazo application.
Custom User model with UUID primary key and phone number authentication support.
"""

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user manager for User model.
    Supports creating users with email or phone number.
    """

    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        """
        Create and return a regular user.
        """
        if not email and not phone_number:
            raise ValueError(_('User must have either an email or phone number'))

        if email:
            email = self.normalize_email(email)

        user = self.model(
            email=email,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, phone_number=None, password=None, **extra_fields):
        """
        Create and return a superuser.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for InGazo application.
    
    Supports authentication via email or phone number.
    Uses UUID as primary key for better scalability and security.
    """

    # Phone number validator (Hungarian/Austrian format)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be in format: '+999999999'. Up to 15 digits allowed.")
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_('Phone Number'),
        db_index=True
    )
    
    email = models.EmailField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_('Email Address'),
        db_index=True
    )
    
    full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Full Name')
    )
    
    profile_photo_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Profile Photo URL')
    )
    
    # Status flags
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Designates whether this user should be treated as active.')
    )
    
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('Staff Status'),
        help_text=_('Designates whether the user can log into the admin site.')
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified'),
        help_text=_('Designates whether the user has verified their account.')
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
    
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Login')
    )

    objects = UserManager()

    # Use email as the primary identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active', 'is_verified']),
        ]

    def __str__(self):
        return self.email or self.phone_number or str(self.id)

    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name or self.email or self.phone_number or ''

    def get_short_name(self):
        """Return the short name for the user."""
        if self.full_name:
            return self.full_name.split()[0]
        return self.email.split('@')[0] if self.email else str(self.id)[:8]

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

