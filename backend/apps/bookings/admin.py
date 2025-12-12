"""
Admin configuration for the Bookings app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for Booking model.
    """
    list_display = [
        'id_short',
        'passenger_link',
        'ride_link',
        'seats_reserved',
        'price',
        'status_badge',
        'payment_status',
        'created_at',
    ]
    list_filter = [
        'status',
        'payment_status',
        'created_at',
        'confirmed_at',
    ]
    search_fields = [
        'user__email',
        'user__full_name',
        'ride__start_city',
        'ride__end_city',
        'ride__driver__user__email',
    ]
    readonly_fields = [
        'id',
        'price',
        'confirmed_at',
        'cancelled_at',
        'completed_at',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('id', 'ride', 'user', 'status')
        }),
        (_('Booking Details'), {
            'fields': ('seats_reserved', 'price', 'pickup_note')
        }),
        (_('Payment'), {
            'fields': ('payment_status', 'payment_reference')
        }),
        (_('Communication'), {
            'fields': ('passenger_message', 'driver_message')
        }),
        (_('Cancellation'), {
            'fields': ('cancellation_reason', 'cancelled_by'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': (
                'created_at',
                'confirmed_at',
                'cancelled_at',
                'completed_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def id_short(self, obj):
        """Short ID display."""
        return str(obj.id)[:8]
    id_short.short_description = _('ID')

    def passenger_link(self, obj):
        """Link to user admin page."""
        from django.urls import reverse
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.full_name or obj.user.email
        )
    passenger_link.short_description = _('Passenger')

    def ride_link(self, obj):
        """Link to ride admin page."""
        from django.urls import reverse
        url = reverse('admin:rides_ride_change', args=[obj.ride.id])
        return format_html(
            '<a href="{}">{} → {}</a>',
            url,
            obj.ride.start_city,
            obj.ride.end_city
        )
    ride_link.short_description = _('Ride')

    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
            'completed': 'blue',
            'rejected': 'gray',
            'no_show': 'purple',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')

    actions = ['confirm_bookings', 'cancel_bookings', 'complete_bookings']

    @admin.action(description=_('Confirm selected bookings'))
    def confirm_bookings(self, request, queryset):
        confirmed = 0
        for booking in queryset.filter(status='pending'):
            if booking.confirm():
                confirmed += 1
        self.message_user(request, f'{confirmed} booking(s) confirmed.')

    @admin.action(description=_('Cancel selected bookings'))
    def cancel_bookings(self, request, queryset):
        cancelled = 0
        for booking in queryset.filter(status__in=['pending', 'confirmed']):
            if booking.cancel(cancelled_by=request.user, reason='Cancelled by admin'):
                cancelled += 1
        self.message_user(request, f'{cancelled} booking(s) cancelled.')

    @admin.action(description=_('Complete selected bookings'))
    def complete_bookings(self, request, queryset):
        completed = 0
        for booking in queryset.filter(status='confirmed'):
            if booking.complete():
                completed += 1
        self.message_user(request, f'{completed} booking(s) completed.')

