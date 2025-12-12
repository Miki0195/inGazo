"""
Admin configuration for the Vehicles app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Vehicle model.
    """
    list_display = [
        'license_plate',
        'full_name_display',
        'driver_link',
        'seats',
        'color',
        'is_verified',
        'is_active',
        'created_at',
    ]
    list_filter = [
        'is_verified',
        'is_active',
        'color',
        'make',
        'year',
        'created_at',
    ]
    search_fields = [
        'license_plate',
        'make',
        'model',
        'driver__user__email',
        'driver__user__full_name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('id', 'driver', 'is_verified', 'is_active')
        }),
        (_('Vehicle Information'), {
            'fields': ('make', 'model', 'year', 'license_plate', 'color', 'seats')
        }),
        (_('Features'), {
            'fields': (
                'has_air_conditioning',
                'has_wifi',
                'has_usb_charger',
                'trunk_space',
            )
        }),
        (_('Media'), {
            'fields': ('photo_url',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name_display(self, obj):
        """Display full vehicle name."""
        return obj.full_name
    full_name_display.short_description = _('Vehicle')

    def driver_link(self, obj):
        """Link to driver admin page."""
        from django.urls import reverse
        url = reverse('admin:drivers_driver_change', args=[obj.driver.id])
        return format_html('<a href="{}">{}</a>', url, obj.driver.full_name)
    driver_link.short_description = _('Driver')

    actions = ['verify_vehicles', 'unverify_vehicles', 'activate_vehicles', 'deactivate_vehicles']

    @admin.action(description=_('Verify selected vehicles'))
    def verify_vehicles(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} vehicle(s) verified.')

    @admin.action(description=_('Unverify selected vehicles'))
    def unverify_vehicles(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} vehicle(s) unverified.')

    @admin.action(description=_('Activate selected vehicles'))
    def activate_vehicles(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} vehicle(s) activated.')

    @admin.action(description=_('Deactivate selected vehicles'))
    def deactivate_vehicles(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} vehicle(s) deactivated.')

