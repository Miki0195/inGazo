"""
Admin configuration for the Notifications app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for Notification model.
    """
    list_display = [
        'id_short',
        'user_link',
        'type',
        'title_short',
        'is_read',
        'priority_badge',
        'created_at',
    ]
    list_filter = [
        'type',
        'is_read',
        'priority',
        'push_sent',
        'email_sent',
        'created_at',
    ]
    search_fields = [
        'user__email',
        'user__full_name',
        'title',
        'message',
    ]
    readonly_fields = [
        'id',
        'read_at',
        'push_sent_at',
        'email_sent_at',
        'created_at',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'type', 'priority')
        }),
        (_('Content'), {
            'fields': ('title', 'message', 'action_url', 'metadata')
        }),
        (_('Reference'), {
            'fields': ('reference_type', 'reference_id')
        }),
        (_('Status'), {
            'fields': ('is_read', 'read_at')
        }),
        (_('Delivery'), {
            'fields': (
                'push_sent',
                'push_sent_at',
                'email_sent',
                'email_sent_at',
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )

    def id_short(self, obj):
        """Short ID display."""
        return str(obj.id)[:8]
    id_short.short_description = _('ID')

    def user_link(self, obj):
        """Link to user admin page."""
        from django.urls import reverse
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.full_name or obj.user.email
        )
    user_link.short_description = _('User')

    def title_short(self, obj):
        """Truncated title."""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = _('Title')

    def priority_badge(self, obj):
        """Display priority with color badge."""
        colors = {
            'low': 'gray',
            'normal': 'blue',
            'high': 'orange',
            'urgent': 'red',
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = _('Priority')

    actions = ['mark_as_read', 'mark_as_unread', 'send_push_notification']

    @admin.action(description=_('Mark selected as read'))
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notification(s) marked as read.')

    @admin.action(description=_('Mark selected as unread'))
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notification(s) marked as unread.')

    @admin.action(description=_('Send push notification'))
    def send_push_notification(self, request, queryset):
        # TODO: Implement push notification sending
        self.message_user(
            request,
            'Push notification sending not yet implemented.',
            level='warning'
        )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """
    Admin configuration for NotificationPreference model.
    """
    list_display = [
        'user',
        'email_booking_updates',
        'email_ride_reminders',
        'push_booking_updates',
        'push_ride_reminders',
        'updated_at',
    ]
    list_filter = [
        'email_booking_updates',
        'email_promotional',
        'push_booking_updates',
        'push_promotional',
    ]
    search_fields = [
        'user__email',
        'user__full_name',
    ]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        (_('Email Preferences'), {
            'fields': (
                'email_booking_updates',
                'email_ride_reminders',
                'email_promotional',
            )
        }),
        (_('Push Notification Preferences'), {
            'fields': (
                'push_booking_updates',
                'push_ride_reminders',
                'push_chat_messages',
                'push_promotional',
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

