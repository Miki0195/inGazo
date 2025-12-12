"""
Custom permissions for the Rides app.
"""

from rest_framework import permissions


class IsRideOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a ride to modify it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.driver.user == request.user or request.user.is_staff


class IsRideOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to all,
    but write access only to the ride owner.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.driver.user == request.user or request.user.is_staff


class CanBookRide(permissions.BasePermission):
    """
    Custom permission to check if user can book a ride.
    Users cannot book their own rides.
    """
    message = 'You cannot book your own ride.'

    def has_object_permission(self, request, view, obj):
        # Check that user is not the driver
        if hasattr(request.user, 'driver_profile'):
            if obj.driver == request.user.driver_profile:
                return False
        return True

