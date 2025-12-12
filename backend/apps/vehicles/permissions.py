"""
Custom permissions for the Vehicles app.
"""

from rest_framework import permissions


class IsVehicleOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a vehicle to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow staff to edit any vehicle
        if request.user.is_staff:
            return True
        
        # Check if user owns the vehicle through their driver profile
        return (
            hasattr(request.user, 'driver_profile') and
            obj.driver == request.user.driver_profile
        )


class IsVehicleOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to all,
    but write access only to the vehicle owner.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow staff to edit any vehicle
        if request.user.is_staff:
            return True
        
        # Write permissions are only allowed to the owner
        return (
            hasattr(request.user, 'driver_profile') and
            obj.driver == request.user.driver_profile
        )

