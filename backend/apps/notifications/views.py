"""
Views for the Notifications app.
"""

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Notification, NotificationPreference
from .serializers import (
    MarkReadSerializer,
    NotificationPreferenceSerializer,
    NotificationSerializer,
)


class NotificationViewSet(ModelViewSet):
    """
    ViewSet for Notification CRUD operations.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'delete']  # No create/update from API

    def get_queryset(self):
        """
        Return notifications for the current user.
        """
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Filter by type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(type=notification_type)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications.
        """
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Mark notifications as read.
        """
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data.get('notification_ids', [])
        
        queryset = Notification.objects.filter(
            user=request.user,
            is_read=False
        )
        
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        updated = queryset.update(is_read=True, read_at=timezone.now())
        
        return Response({
            'message': f'{updated} notification(s) marked as read.',
            'count': updated
        })

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        """
        Mark a single notification as read.
        """
        notification = self.get_object()
        notification.mark_as_read()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """
        Delete all read notifications for the user.
        """
        deleted, _ = Notification.objects.filter(
            user=request.user,
            is_read=True
        ).delete()
        
        return Response({
            'message': f'{deleted} notification(s) deleted.',
            'count': deleted
        })


class NotificationPreferenceView(APIView):
    """
    API endpoint for managing notification preferences.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get current user's notification preferences.
        """
        preferences, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationPreferenceSerializer(preferences)
        return Response(serializer.data)

    def put(self, request):
        """
        Update notification preferences.
        """
        preferences, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationPreferenceSerializer(
            preferences,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        """
        Partially update notification preferences.
        """
        return self.put(request)

