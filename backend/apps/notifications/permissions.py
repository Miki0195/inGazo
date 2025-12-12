"""
Custom permissions for the Notifications app.
"""

from rest_framework import permissions


class IsNotificationOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a notification to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff

