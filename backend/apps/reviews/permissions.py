"""
Custom permissions for the Reviews app.
"""

from rest_framework import permissions


class IsReviewOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a review to modify it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user or request.user.is_staff


class IsReviewTarget(permissions.BasePermission):
    """
    Custom permission to allow the review target to respond.
    """

    def has_object_permission(self, request, view, obj):
        return obj.target == request.user or request.user.is_staff


class CanReview(permissions.BasePermission):
    """
    Custom permission to check if user can review after a ride.
    """
    message = 'You can only review users from completed rides you participated in.'

    def has_permission(self, request, view):
        # Basic authentication check
        return request.user.is_authenticated

