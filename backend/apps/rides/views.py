"""
Views for the Rides app.
"""

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.drivers.permissions import IsDriver

from .models import Ride, RideRecurring, RideStop
from .permissions import IsRideOwner, IsRideOwnerOrReadOnly
from .serializers import (
    RideCreateSerializer,
    RideRecurringCreateSerializer,
    RideRecurringSerializer,
    RideSearchSerializer,
    RideSerializer,
    RideStopSerializer,
    RideUpdateSerializer,
)


class RideViewSet(ModelViewSet):
    """
    ViewSet for Ride CRUD operations and search.
    """
    queryset = Ride.objects.select_related(
        'driver', 'driver__user', 'vehicle'
    ).prefetch_related('stops').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RideCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RideUpdateSerializer
        elif self.action == 'search':
            return RideSearchSerializer
        return RideSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated(), IsDriver()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsRideOwnerOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Filter queryset based on query parameters.
        """
        queryset = Ride.objects.select_related(
            'driver', 'driver__user', 'vehicle'
        ).prefetch_related('stops')
        
        # Base filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        else:
            # By default, only show scheduled rides
            queryset = queryset.filter(status=Ride.RideStatus.SCHEDULED)
        
        # Filter by date
        date_filter = self.request.query_params.get('date')
        if date_filter:
            queryset = queryset.filter(departure_time__date=date_filter)
        
        # Filter future rides only
        if self.request.query_params.get('future_only', 'true').lower() == 'true':
            queryset = queryset.filter(departure_time__gte=timezone.now())
        
        # Filter by cities
        start_city = self.request.query_params.get('start_city')
        if start_city:
            queryset = queryset.filter(start_city__icontains=start_city)
        
        end_city = self.request.query_params.get('end_city')
        if end_city:
            queryset = queryset.filter(end_city__icontains=end_city)
        
        # Filter by available seats
        min_seats = self.request.query_params.get('min_seats')
        if min_seats:
            queryset = queryset.filter(seats_available__gte=int(min_seats))
        
        # Filter by max price
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price_per_seat__lte=float(max_price))
        
        # Filter by driver
        driver_id = self.request.query_params.get('driver_id')
        if driver_id:
            queryset = queryset.filter(driver_id=driver_id)
        
        return queryset.order_by('departure_time')

    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Search for rides based on geographic proximity and other filters.
        Uses PostGIS spatial queries for efficient location-based search.
        """
        serializer = RideSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Create point objects for search
        start_point = Point(data['start_lng'], data['start_lat'], srid=4326)
        end_point = Point(data['end_lng'], data['end_lat'], srid=4326)
        radius_km = data.get('radius_km', 10.0)
        
        # Base queryset - only scheduled, future rides with available seats
        queryset = Ride.objects.select_related(
            'driver', 'driver__user', 'vehicle'
        ).prefetch_related('stops').filter(
            status=Ride.RideStatus.SCHEDULED,
            departure_time__gte=timezone.now(),
            seats_available__gte=data.get('min_seats', 1)
        )
        
        # Filter by geographic proximity using PostGIS
        # Find rides where start location is within radius of search start
        # and end location is within radius of search end
        queryset = queryset.filter(
            start_location__distance_lte=(start_point, D(km=radius_km)),
            end_location__distance_lte=(end_point, D(km=radius_km))
        )
        
        # Filter by date if provided
        if data.get('date'):
            queryset = queryset.filter(departure_time__date=data['date'])
        
        # Filter by max price if provided
        if data.get('max_price'):
            queryset = queryset.filter(price_per_seat__lte=data['max_price'])
        
        # Annotate with distances and order by start distance
        queryset = queryset.annotate(
            start_distance=Distance('start_location', start_point),
            end_distance=Distance('end_location', end_point)
        ).order_by('start_distance', 'departure_time')
        
        # Serialize and return
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RideSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RideSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_rides(self, request):
        """
        Get all rides for the current driver.
        """
        if not hasattr(request.user, 'driver_profile'):
            return Response(
                {'detail': 'You do not have a driver profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        rides = Ride.objects.filter(
            driver=request.user.driver_profile
        ).select_related('vehicle').prefetch_related('stops')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            rides = rides.filter(status=status_filter)
        
        serializer = RideSerializer(rides, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a scheduled ride.
        """
        ride = self.get_object()
        
        # Check ownership
        if ride.driver.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You do not own this ride.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if ride.status != Ride.RideStatus.SCHEDULED:
            return Response(
                {'detail': 'Only scheduled rides can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ride.status = Ride.RideStatus.CANCELLED
        ride.save(update_fields=['status', 'updated_at'])
        
        # TODO: Notify passengers about cancellation
        
        return Response({
            'message': 'Ride cancelled successfully.',
            'ride': RideSerializer(ride).data
        })

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Start a scheduled ride.
        """
        ride = self.get_object()
        
        # Check ownership
        if ride.driver.user != request.user:
            return Response(
                {'detail': 'You do not own this ride.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if ride.status != Ride.RideStatus.SCHEDULED:
            return Response(
                {'detail': 'Only scheduled rides can be started.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ride.status = Ride.RideStatus.ONGOING
        ride.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'message': 'Ride started successfully.',
            'ride': RideSerializer(ride).data
        })

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        """
        Finish an ongoing ride.
        """
        ride = self.get_object()
        
        # Check ownership
        if ride.driver.user != request.user:
            return Response(
                {'detail': 'You do not own this ride.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if ride.status != Ride.RideStatus.ONGOING:
            return Response(
                {'detail': 'Only ongoing rides can be finished.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ride.status = Ride.RideStatus.FINISHED
        ride.save(update_fields=['status', 'updated_at'])
        
        # Increment driver's trip count
        ride.driver.increment_trips()
        
        return Response({
            'message': 'Ride finished successfully.',
            'ride': RideSerializer(ride).data
        })

    @action(detail=True, methods=['post', 'get'])
    def stops(self, request, pk=None):
        """
        Manage ride stops.
        GET: List all stops
        POST: Add a new stop
        """
        ride = self.get_object()
        
        if request.method == 'GET':
            serializer = RideStopSerializer(ride.stops.all(), many=True)
            return Response(serializer.data)
        
        # POST - Add stop
        if ride.driver.user != request.user:
            return Response(
                {'detail': 'You do not own this ride.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RideStopSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ride=ride)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RideRecurringViewSet(ModelViewSet):
    """
    ViewSet for Recurring Ride CRUD operations.
    """
    queryset = RideRecurring.objects.select_related(
        'driver', 'driver__user', 'vehicle'
    ).all()
    permission_classes = [permissions.IsAuthenticated, IsDriver]

    def get_serializer_class(self):
        if self.action == 'create':
            return RideRecurringCreateSerializer
        return RideRecurringSerializer

    def get_queryset(self):
        """
        Filter to show only current user's recurring rides.
        """
        user = self.request.user
        
        if user.is_staff:
            return RideRecurring.objects.select_related(
                'driver', 'driver__user', 'vehicle'
            ).all()
        
        if hasattr(user, 'driver_profile'):
            return RideRecurring.objects.filter(
                driver=user.driver_profile
            ).select_related('driver', 'driver__user', 'vehicle')
        
        return RideRecurring.objects.none()

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Toggle the active status of a recurring ride.
        """
        recurring = self.get_object()
        
        if recurring.driver.user != request.user:
            return Response(
                {'detail': 'You do not own this recurring ride.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        recurring.is_active = not recurring.is_active
        recurring.save(update_fields=['is_active', 'updated_at'])
        
        return Response({
            'message': f'Recurring ride {"activated" if recurring.is_active else "deactivated"}.',
            'is_active': recurring.is_active
        })

