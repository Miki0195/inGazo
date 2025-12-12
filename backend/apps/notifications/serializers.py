"""
Serializers for the Notifications app.
"""

from rest_framework import serializers

from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'type_display',
            'title',
            'message',
            'reference_type',
            'reference_id',
            'is_read',
            'read_at',
            'priority',
            'priority_display',
            'action_url',
            'metadata',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'type',
            'title',
            'message',
            'reference_type',
            'reference_id',
            'priority',
            'action_url',
            'metadata',
            'created_at',
        ]


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications (admin/system use).
    """

    class Meta:
        model = Notification
        fields = [
            'user',
            'type',
            'title',
            'message',
            'reference_type',
            'reference_id',
            'priority',
            'action_url',
            'metadata',
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationPreference model.
    """

    class Meta:
        model = NotificationPreference
        fields = [
            'email_booking_updates',
            'email_ride_reminders',
            'email_promotional',
            'push_booking_updates',
            'push_ride_reminders',
            'push_chat_messages',
            'push_promotional',
        ]


class MarkReadSerializer(serializers.Serializer):
    """
    Serializer for marking notifications as read.
    """
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text='List of notification IDs to mark as read. If empty, marks all as read.'
    )

