"""
Serializers for the Rides app.
"""

from django.contrib.gis.geos import Point
from rest_framework import serializers

from apps.drivers.serializers import DriverMinimalSerializer
from apps.vehicles.serializers import VehicleMinimalSerializer

from .models import Ride, RideRecurring, RideStop


class PointFieldSerializer(serializers.Field):
    """
    Custom serializer for GeoDjango PointField.
    Accepts and returns coordinates as {lat, lng} or {latitude, longitude}.
    """

    def to_representation(self, value):
        if value is None:
            return None
        return {
            'latitude': value.y,
            'longitude': value.x,
        }

    def to_internal_value(self, data):
        if data is None:
            return None
        
        # Accept both lat/lng and latitude/longitude keys
        lat = data.get('latitude') or data.get('lat')
        lng = data.get('longitude') or data.get('lng')
        
        if lat is None or lng is None:
            raise serializers.ValidationError(
                'Both latitude and longitude are required.'
            )
        
        try:
            lat = float(lat)
            lng = float(lng)
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                'Latitude and longitude must be valid numbers.'
            )
        
        # Validate coordinate ranges
        if not (-90 <= lat <= 90):
            raise serializers.ValidationError(
                'Latitude must be between -90 and 90.'
            )
        if not (-180 <= lng <= 180):
            raise serializers.ValidationError(
                'Longitude must be between -180 and 180.'
            )
        
        # Point takes (x, y) which is (longitude, latitude)
        return Point(lng, lat, srid=4326)


class RideStopSerializer(serializers.ModelSerializer):
    """
    Serializer for RideStop model.
    """
    location = PointFieldSerializer()

    class Meta:
        model = RideStop
        fields = [
            'id',
            'name',
            'location',
            'address',
            'order',
            'estimated_arrival',
            'price_from_start',
        ]
        read_only_fields = ['id']


class RideSerializer(serializers.ModelSerializer):
    """
    Serializer for Ride model - read operations.
    """
    driver = DriverMinimalSerializer(read_only=True)
    vehicle = VehicleMinimalSerializer(read_only=True)
    start_location = PointFieldSerializer()
    end_location = PointFieldSerializer()
    stops = RideStopSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Ride
        fields = [
            'id',
            'driver',
            'vehicle',
            'departure_time',
            'seats_total',
            'seats_available',
            'start_location',
            'end_location',
            'start_city',
            'start_address',
            'end_city',
            'end_address',
            'price_per_seat',
            'estimated_duration_minutes',
            'estimated_distance_km',
            'status',
            'status_display',
            'notes',
            'allows_detours',
            'instant_booking',
            'stops',
            'is_full',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'seats_available',
            'status',
            'created_at',
        ]


class RideCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new ride.
    """
    start_location = PointFieldSerializer()
    end_location = PointFieldSerializer()
    vehicle_id = serializers.UUIDField(write_only=True)
    stops = RideStopSerializer(many=True, required=False)

    class Meta:
        model = Ride
        fields = [
            'vehicle_id',
            'departure_time',
            'seats_total',
            'start_location',
            'end_location',
            'start_city',
            'start_address',
            'end_city',
            'end_address',
            'price_per_seat',
            'estimated_duration_minutes',
            'estimated_distance_km',
            'notes',
            'allows_detours',
            'instant_booking',
            'stops',
        ]

    def validate_vehicle_id(self, value):
        """
        Ensure the vehicle belongs to the driver.
        """
        user = self.context['request'].user
        driver_profile = getattr(user, 'driver_profile', None)

        if not driver_profile:
            raise serializers.ValidationError('You must be a registered driver to create a ride.')

        if not driver_profile.is_verified:
            raise serializers.ValidationError('Your driver profile must be verified to create rides.')
        
        from apps.vehicles.models import Vehicle
        try:
            vehicle = Vehicle.objects.get(id=value)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError('Vehicle not found.')
        
        if vehicle.driver != driver_profile:
            raise serializers.ValidationError(
                'This vehicle does not belong to you.'
            )
        
        if not vehicle.is_active:
            raise serializers.ValidationError(
                'This vehicle is not active.'
            )
        
        return value

    def validate_seats_total(self, value):
        """
        Ensure seats don't exceed vehicle capacity.
        """
        vehicle_id = self.initial_data.get('vehicle_id')
        if vehicle_id:
            from apps.vehicles.models import Vehicle
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
                if value > vehicle.seats:
                    raise serializers.ValidationError(
                        f'Seats cannot exceed vehicle capacity of {vehicle.seats}.'
                    )
            except Vehicle.DoesNotExist:
                pass
        return value

    def create(self, validated_data):
        """
        Create ride with stops.
        """
        user = self.context['request'].user
        stops_data = validated_data.pop('stops', [])
        vehicle_id = validated_data.pop('vehicle_id')
        
        from apps.vehicles.models import Vehicle
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        ride = Ride.objects.create(
            driver=user.driver_profile,
            vehicle=vehicle,
            seats_available=validated_data['seats_total'],
            **validated_data
        )
        
        # Create stops
        for stop_data in stops_data:
            RideStop.objects.create(ride=ride, **stop_data)
        
        return ride


class RideUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a ride.
    """
    start_location = PointFieldSerializer(required=False)
    end_location = PointFieldSerializer(required=False)

    class Meta:
        model = Ride
        fields = [
            'departure_time',
            'seats_total',
            'start_location',
            'end_location',
            'start_city',
            'start_address',
            'end_city',
            'end_address',
            'price_per_seat',
            'estimated_duration_minutes',
            'estimated_distance_km',
            'notes',
            'allows_detours',
            'instant_booking',
        ]

    def validate_seats_total(self, value):
        """
        Ensure new seat total is not less than booked seats.
        """
        if self.instance:
            booked_seats = self.instance.seats_total - self.instance.seats_available
            if value < booked_seats:
                raise serializers.ValidationError(
                    f'Cannot reduce seats below {booked_seats} (already booked).'
                )
        return value


class RideMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal ride serializer for nested representations.
    """
    start_location = PointFieldSerializer()
    end_location = PointFieldSerializer()

    class Meta:
        model = Ride
        fields = [
            'id',
            'departure_time',
            'start_city',
            'end_city',
            'start_location',
            'end_location',
            'price_per_seat',
            'seats_available',
            'status',
        ]
        read_only_fields = fields


class RideRecurringSerializer(serializers.ModelSerializer):
    """
    Serializer for RideRecurring model.
    """
    driver = DriverMinimalSerializer(read_only=True)
    vehicle = VehicleMinimalSerializer(read_only=True)
    start_location = PointFieldSerializer()
    end_location = PointFieldSerializer()
    days_display = serializers.CharField(source='get_days_display', read_only=True)

    class Meta:
        model = RideRecurring
        fields = [
            'id',
            'driver',
            'vehicle',
            'days_of_week',
            'days_display',
            'time_of_day',
            'start_location',
            'end_location',
            'start_city',
            'start_address',
            'end_city',
            'end_address',
            'seats_total',
            'price_per_seat',
            'valid_from',
            'valid_until',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class RideRecurringCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a recurring ride.
    """
    start_location = PointFieldSerializer()
    end_location = PointFieldSerializer()
    vehicle_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = RideRecurring
        fields = [
            'vehicle_id',
            'days_of_week',
            'time_of_day',
            'start_location',
            'end_location',
            'start_city',
            'start_address',
            'end_city',
            'end_address',
            'seats_total',
            'price_per_seat',
            'valid_from',
            'valid_until',
        ]

    def validate_vehicle_id(self, value):
        """
        Ensure the vehicle belongs to the driver.
        """
        user = self.context['request'].user
        
        if not hasattr(user, 'driver_profile'):
            raise serializers.ValidationError(
                'You must be a registered driver to create a recurring ride.'
            )
        
        from apps.vehicles.models import Vehicle
        try:
            vehicle = Vehicle.objects.get(id=value)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError('Vehicle not found.')
        
        if vehicle.driver != user.driver_profile:
            raise serializers.ValidationError(
                'This vehicle does not belong to you.'
            )
        
        return value

    def validate_days_of_week(self, value):
        """
        Ensure days are valid (0-6).
        """
        if not value:
            raise serializers.ValidationError('At least one day must be selected.')
        
        for day in value:
            if day < 0 or day > 6:
                raise serializers.ValidationError(
                    'Days must be between 0 (Monday) and 6 (Sunday).'
                )
        
        return list(set(value))  # Remove duplicates

    def create(self, validated_data):
        """
        Create recurring ride.
        """
        user = self.context['request'].user
        vehicle_id = validated_data.pop('vehicle_id')
        
        from apps.vehicles.models import Vehicle
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        return RideRecurring.objects.create(
            driver=user.driver_profile,
            vehicle=vehicle,
            **validated_data
        )


class RideSearchSerializer(serializers.Serializer):
    """
    Serializer for ride search parameters.
    """
    start_lat = serializers.FloatField(required=True)
    start_lng = serializers.FloatField(required=True)
    end_lat = serializers.FloatField(required=True)
    end_lng = serializers.FloatField(required=True)
    date = serializers.DateField(required=False)
    min_seats = serializers.IntegerField(required=False, min_value=1, default=1)
    max_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2
    )
    radius_km = serializers.FloatField(required=False, default=10.0)

