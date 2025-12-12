"""
Admin configuration for the Users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for the User model.
    """
    list_display = [
        'email',
        'phone_number',
        'full_name',
        'is_verified',
        'is_active',
        'is_staff',
        'created_at',
    ]
    list_filter = [
        'is_verified',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at',
    ]
    search_fields = [
        'email',
        'phone_number',
        'full_name',
    ]
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']

    fieldsets = (
        (None, {
            'fields': ('id', 'email', 'phone_number', 'password')
        }),
        (_('Personal Info'), {
            'fields': ('full_name', 'profile_photo_url')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_verified',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        (_('Important Dates'), {
            'fields': ('created_at', 'updated_at', 'last_login'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'phone_number',
                'full_name',
                'password1',
                'password2',
                'is_active',
                'is_verified',
                'is_staff',
            ),
        }),
    )

