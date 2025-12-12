"""
Views for the Bookings app.
"""

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Booking
from .permissions import IsBookingOwner, IsBookingParticipant
from .serializers import (
    BookingCancelSerializer,
    BookingConfirmSerializer,
    BookingCreateSerializer,
    BookingSerializer,
    BookingUpdateSerializer,
    DriverBookingSerializer,
)


class BookingViewSet(ModelViewSet):
    """
    ViewSet for Booking CRUD operations.
    """
    queryset = Booking.objects.select_related(
        'ride', 'ride__driver', 'ride__vehicle', 'user'
    ).all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        elif self.action == 'cancel':
            return BookingCancelSerializer
        elif self.action == 'respond':
            return BookingConfirmSerializer
        return BookingSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['retrieve', 'cancel']:
            return [permissions.IsAuthenticated(), IsBookingParticipant()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsBookingOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Filter bookings based on user role.
        - Passengers see their own bookings
        - Drivers see bookings for their rides
        - Staff see all bookings
        """
        user = self.request.user
        
        if user.is_staff:
            return Booking.objects.select_related(
                'ride', 'ride__driver', 'ride__vehicle', 'user'
            ).all()
        
        # Base queryset for passenger's own bookings
        from django.db.models import Q
        query = Q(user=user)
        
        # Add driver's ride bookings if user is a driver
        if hasattr(user, 'driver_profile'):
            query |= Q(ride__driver=user.driver_profile)
        
        return Booking.objects.filter(query).select_related(
            'ride', 'ride__driver', 'ride__vehicle', 'user'
        )

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """
        Get all bookings for the current user (as passenger).
        """
        bookings = Booking.objects.filter(
            user=request.user
        ).select_related('ride', 'ride__driver', 'ride__vehicle')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def driver_bookings(self, request):
        """
        Get all bookings for the current user's rides (as driver).
        """
        if not hasattr(request.user, 'driver_profile'):
            return Response(
                {'detail': 'You do not have a driver profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        bookings = Booking.objects.filter(
            ride__driver=request.user.driver_profile
        ).select_related('ride', 'user')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        
        # Filter by ride if provided
        ride_id = request.query_params.get('ride_id')
        if ride_id:
            bookings = bookings.filter(ride_id=ride_id)
        
        serializer = DriverBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking.
        """
        booking = self.get_object()
        serializer = BookingCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not booking.is_cancellable:
            return Response(
                {'detail': 'This booking cannot be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = serializer.validated_data.get('reason', '')
        booking.cancel(cancelled_by=request.user, reason=reason)
        
        # TODO: Send notification to driver/passenger
        
        return Response({
            'message': 'Booking cancelled successfully.',
            'booking': BookingSerializer(booking).data
        })

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """
        Driver endpoint to confirm or reject a pending booking.
        """
        booking = self.get_object()
        
        # Check if user is the driver of the ride
        if not hasattr(request.user, 'driver_profile'):
            return Response(
                {'detail': 'You are not a driver.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.ride.driver != request.user.driver_profile:
            return Response(
                {'detail': 'You are not the driver of this ride.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != Booking.BookingStatus.PENDING:
            return Response(
                {'detail': 'Only pending bookings can be confirmed or rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = BookingConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        message = serializer.validated_data.get('message', '')
        
        if action_type == 'confirm':
            if booking.confirm():
                booking.driver_message = message
                booking.save(update_fields=['driver_message'])
                
                # TODO: Send notification to passenger
                
                return Response({
                    'message': 'Booking confirmed successfully.',
                    'booking': BookingSerializer(booking).data
                })
            else:
                return Response(
                    {'detail': 'Could not confirm booking. Not enough seats available.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:  # reject
            booking.reject(reason=message)
            
            # TODO: Send notification to passenger
            
            return Response({
                'message': 'Booking rejected.',
                'booking': BookingSerializer(booking).data
            })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark a booking as completed (after ride finishes).
        """
        booking = self.get_object()
        
        # Check if user is the driver of the ride
        if not hasattr(request.user, 'driver_profile'):
            return Response(
                {'detail': 'You are not a driver.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.ride.driver != request.user.driver_profile:
            return Response(
                {'detail': 'You are not the driver of this ride.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.complete():
            return Response({
                'message': 'Booking marked as completed.',
                'booking': BookingSerializer(booking).data
            })
        else:
            return Response(
                {'detail': 'Could not complete booking. It must be confirmed first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

