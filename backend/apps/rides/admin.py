"""
Admin configuration for the Rides app.
"""

from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Ride, RideRecurring, RideStop


class RideStopInline(admin.TabularInline):
    """
    Inline admin for ride stops.
    """
    model = RideStop
    extra = 0
    fields = ['order', 'name', 'address', 'estimated_arrival', 'price_from_start']


@admin.register(Ride)
class RideAdmin(GISModelAdmin):
    """
    Admin configuration for Ride model with map support.
    """
    list_display = [
        'id_short',
        'route_display',
        'driver_link',
        'departure_time',
        'seats_display',
        'price_per_seat',
        'status_badge',
        'created_at',
    ]
    list_filter = [
        'status',
        'instant_booking',
        'allows_detours',
        'departure_time',
        'created_at',
    ]
    search_fields = [
        'start_city',
        'end_city',
        'driver__user__email',
        'driver__user__full_name',
        'vehicle__license_plate',
    ]
    readonly_fields = [
        'id',
        'seats_available',
        'created_at',
        'updated_at',
    ]
    ordering = ['-departure_time']
    inlines = [RideStopInline]
    date_hierarchy = 'departure_time'

    fieldsets = (
        (None, {
            'fields': ('id', 'driver', 'vehicle', 'status')
        }),
        (_('Schedule'), {
            'fields': ('departure_time',)
        }),
        (_('Seats'), {
            'fields': ('seats_total', 'seats_available')
        }),
        (_('Route'), {
            'fields': (
                'start_location',
                'start_city',
                'start_address',
                'end_location',
                'end_city',
                'end_address',
            )
        }),
        (_('Pricing & Duration'), {
            'fields': (
                'price_per_seat',
                'estimated_duration_minutes',
                'estimated_distance_km',
            )
        }),
        (_('Options'), {
            'fields': ('notes', 'allows_detours', 'instant_booking')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def id_short(self, obj):
        """Short ID display."""
        return str(obj.id)[:8]
    id_short.short_description = _('ID')

    def route_display(self, obj):
        """Display route."""
        return f"{obj.start_city} → {obj.end_city}"
    route_display.short_description = _('Route')

    def driver_link(self, obj):
        """Link to driver admin page."""
        from django.urls import reverse
        url = reverse('admin:drivers_driver_change', args=[obj.driver.id])
        return format_html('<a href="{}">{}</a>', url, obj.driver.full_name)
    driver_link.short_description = _('Driver')

    def seats_display(self, obj):
        """Display seats available/total."""
        return f"{obj.seats_available}/{obj.seats_total}"
    seats_display.short_description = _('Seats')

    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'scheduled': 'blue',
            'ongoing': 'green',
            'finished': 'gray',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')

    actions = ['cancel_rides', 'finish_rides']

    @admin.action(description=_('Cancel selected rides'))
    def cancel_rides(self, request, queryset):
        updated = queryset.filter(status='scheduled').update(status='cancelled')
        self.message_user(request, f'{updated} ride(s) cancelled.')

    @admin.action(description=_('Mark selected rides as finished'))
    def finish_rides(self, request, queryset):
        updated = queryset.filter(status='ongoing').update(status='finished')
        self.message_user(request, f'{updated} ride(s) finished.')


@admin.register(RideStop)
class RideStopAdmin(GISModelAdmin):
    """
    Admin configuration for RideStop model.
    """
    list_display = [
        'ride',
        'order',
        'name',
        'estimated_arrival',
        'price_from_start',
    ]
    list_filter = ['ride__status']
    search_fields = ['name', 'ride__start_city', 'ride__end_city']
    ordering = ['ride', 'order']


@admin.register(RideRecurring)
class RideRecurringAdmin(GISModelAdmin):
    """
    Admin configuration for RideRecurring model.
    """
    list_display = [
        'route_display',
        'driver_link',
        'days_display',
        'time_of_day',
        'seats_total',
        'price_per_seat',
        'is_active',
        'valid_from',
        'valid_until',
    ]
    list_filter = [
        'is_active',
        'days_of_week',
        'valid_from',
        'created_at',
    ]
    search_fields = [
        'start_city',
        'end_city',
        'driver__user__email',
        'driver__user__full_name',
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('id', 'driver', 'vehicle', 'is_active')
        }),
        (_('Schedule'), {
            'fields': ('days_of_week', 'time_of_day', 'valid_from', 'valid_until')
        }),
        (_('Route'), {
            'fields': (
                'start_location',
                'start_city',
                'start_address',
                'end_location',
                'end_city',
                'end_address',
            )
        }),
        (_('Capacity & Pricing'), {
            'fields': ('seats_total', 'price_per_seat')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def route_display(self, obj):
        """Display route."""
        return f"{obj.start_city} → {obj.end_city}"
    route_display.short_description = _('Route')

    def driver_link(self, obj):
        """Link to driver admin page."""
        from django.urls import reverse
        url = reverse('admin:drivers_driver_change', args=[obj.driver.id])
        return format_html('<a href="{}">{}</a>', url, obj.driver.full_name)
    driver_link.short_description = _('Driver')

    def days_display(self, obj):
        """Display days of week."""
        return obj.get_days_display()
    days_display.short_description = _('Days')

    actions = ['activate_recurring', 'deactivate_recurring']

    @admin.action(description=_('Activate selected recurring rides'))
    def activate_recurring(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} recurring ride(s) activated.')

    @admin.action(description=_('Deactivate selected recurring rides'))
    def deactivate_recurring(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} recurring ride(s) deactivated.')

