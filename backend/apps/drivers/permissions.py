"""
Custom permissions for the Drivers app.
"""

from rest_framework import permissions


class IsDriverOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a driver profile to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsDriverOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to all, 
    but write access only to the driver profile owner.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user or request.user.is_staff


class IsDriver(permissions.BasePermission):
    """
    Custom permission to only allow users with driver profiles.
    """
    message = 'You must be a registered driver to perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'driver_profile')
        )


class IsVerifiedDriver(permissions.BasePermission):
    """
    Custom permission to only allow verified drivers.
    """
    message = 'You must be a verified driver to perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'driver_profile') and
            request.user.driver_profile.is_verified
        )

