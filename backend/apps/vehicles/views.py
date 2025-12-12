"""
Views for the Vehicles app.
"""

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.drivers.permissions import IsDriver

from .models import Vehicle
from .permissions import IsVehicleOwner
from .serializers import (
    VehicleCreateSerializer,
    VehicleSerializer,
    VehicleUpdateSerializer,
)


class VehicleViewSet(ModelViewSet):
    """
    ViewSet for Vehicle CRUD operations.
    """
    queryset = Vehicle.objects.select_related('driver', 'driver__user').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return VehicleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VehicleUpdateSerializer
        return VehicleSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsDriver()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsVehicleOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Filter queryset based on query parameters.
        """
        queryset = Vehicle.objects.select_related(
            'driver', 'driver__user'
        ).filter(is_active=True)
        
        user = self.request.user
        
        # Filter by driver
        driver_id = self.request.query_params.get('driver_id')
        if driver_id:
            queryset = queryset.filter(driver_id=driver_id)
        
        # If user is a driver, they can see all their vehicles
        if hasattr(user, 'driver_profile'):
            mine_only = self.request.query_params.get('mine')
            if mine_only and mine_only.lower() == 'true':
                queryset = queryset.filter(driver=user.driver_profile)
        
        # Filter by seats
        min_seats = self.request.query_params.get('min_seats')
        if min_seats:
            queryset = queryset.filter(seats__gte=int(min_seats))
        
        # Filter by verification status (admin only)
        if user.is_staff:
            is_verified = self.request.query_params.get('is_verified')
            if is_verified is not None:
                queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        else:
            # Non-staff users only see verified vehicles (except their own)
            if not (hasattr(user, 'driver_profile')):
                queryset = queryset.filter(is_verified=True)
        
        return queryset

    @action(detail=False, methods=['get'])
    def my_vehicles(self, request):
        """
        Get all vehicles belonging to the current user (driver).
        """
        if not hasattr(request.user, 'driver_profile'):
            return Response(
                {'detail': 'You do not have a driver profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        vehicles = Vehicle.objects.filter(driver=request.user.driver_profile)
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser]
    )
    def verify(self, request, pk=None):
        """
        Admin endpoint to verify a vehicle.
        """
        vehicle = self.get_object()
        vehicle.is_verified = True
        vehicle.save(update_fields=['is_verified', 'updated_at'])
        
        return Response({
            'message': 'Vehicle verified successfully.',
            'vehicle': VehicleSerializer(vehicle).data
        })

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser]
    )
    def unverify(self, request, pk=None):
        """
        Admin endpoint to unverify a vehicle.
        """
        vehicle = self.get_object()
        vehicle.is_verified = False
        vehicle.save(update_fields=['is_verified', 'updated_at'])
        
        return Response({
            'message': 'Vehicle unverified successfully.',
            'vehicle': VehicleSerializer(vehicle).data
        })

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Toggle the active status of a vehicle.
        """
        vehicle = self.get_object()
        
        # Check ownership
        if vehicle.driver.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You do not own this vehicle.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        vehicle.is_active = not vehicle.is_active
        vehicle.save(update_fields=['is_active', 'updated_at'])
        
        return Response({
            'message': f'Vehicle {"activated" if vehicle.is_active else "deactivated"} successfully.',
            'is_active': vehicle.is_active
        })

