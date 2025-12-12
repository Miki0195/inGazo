"""
Custom permissions for the Bookings app.
"""

from rest_framework import permissions


class IsBookingOwner(permissions.BasePermission):
    """
    Custom permission to only allow booking owner (passenger) to modify.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsBookingParticipant(permissions.BasePermission):
    """
    Custom permission to allow booking owner or ride driver to view.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access all
        if request.user.is_staff:
            return True
        
        # Booking owner (passenger) can access
        if obj.user == request.user:
            return True
        
        # Ride driver can access
        if hasattr(request.user, 'driver_profile'):
            if obj.ride.driver == request.user.driver_profile:
                return True
        
        return False


class IsRideDriver(permissions.BasePermission):
    """
    Custom permission for ride driver actions on bookings.
    """

    def has_object_permission(self, request, view, obj):
        if not hasattr(request.user, 'driver_profile'):
            return False
        return obj.ride.driver == request.user.driver_profile

