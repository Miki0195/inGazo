"""
Serializers for the Bookings app.
"""

from rest_framework import serializers

from apps.rides.serializers import RideMinimalSerializer
from apps.users.serializers import UserMinimalSerializer

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model - read operations.
    """
    ride = RideMinimalSerializer(read_only=True)
    user = UserMinimalSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )
    is_cancellable = serializers.BooleanField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'ride',
            'user',
            'seats_reserved',
            'status',
            'status_display',
            'price',
            'payment_status',
            'payment_status_display',
            'pickup_note',
            'passenger_message',
            'driver_message',
            'confirmed_at',
            'cancelled_at',
            'completed_at',
            'cancellation_reason',
            'is_cancellable',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'price',
            'status',
            'payment_status',
            'confirmed_at',
            'cancelled_at',
            'completed_at',
            'created_at',
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new booking.
    """
    ride_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Booking
        fields = [
            'ride_id',
            'seats_reserved',
            'pickup_note',
            'passenger_message',
        ]

    def validate_ride_id(self, value):
        """
        Ensure the ride exists and is available.
        """
        from apps.rides.models import Ride
        
        try:
            ride = Ride.objects.get(id=value)
        except Ride.DoesNotExist:
            raise serializers.ValidationError('Ride not found.')
        
        if ride.status != Ride.RideStatus.SCHEDULED:
            raise serializers.ValidationError(
                'This ride is not available for booking.'
            )
        
        # Check user is not booking their own ride
        user = self.context['request'].user
        if hasattr(user, 'driver_profile') and ride.driver == user.driver_profile:
            raise serializers.ValidationError(
                'You cannot book your own ride.'
            )
        
        return value

    def validate_seats_reserved(self, value):
        """
        Ensure enough seats are available.
        """
        ride_id = self.initial_data.get('ride_id')
        if ride_id:
            from apps.rides.models import Ride
            try:
                ride = Ride.objects.get(id=ride_id)
                if value > ride.seats_available:
                    raise serializers.ValidationError(
                        f'Only {ride.seats_available} seat(s) available.'
                    )
            except Ride.DoesNotExist:
                pass
        return value

    def validate(self, attrs):
        """
        Check for existing active booking.
        """
        user = self.context['request'].user
        ride_id = attrs.get('ride_id')
        
        existing = Booking.objects.filter(
            ride_id=ride_id,
            user=user,
            status__in=['pending', 'confirmed']
        ).exists()
        
        if existing:
            raise serializers.ValidationError(
                'You already have an active booking for this ride.'
            )
        
        return attrs

    def create(self, validated_data):
        """
        Create booking.
        """
        from apps.rides.models import Ride
        
        user = self.context['request'].user
        ride_id = validated_data.pop('ride_id')
        ride = Ride.objects.get(id=ride_id)
        
        # Calculate price
        price = ride.price_per_seat * validated_data['seats_reserved']
        
        booking = Booking.objects.create(
            ride=ride,
            user=user,
            price=price,
            **validated_data
        )
        
        # If ride allows instant booking, confirm immediately
        if ride.instant_booking:
            booking.confirm()
        
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating booking details.
    """

    class Meta:
        model = Booking
        fields = [
            'pickup_note',
            'passenger_message',
        ]


class BookingCancelSerializer(serializers.Serializer):
    """
    Serializer for cancelling a booking.
    """
    reason = serializers.CharField(
        required=False,
        max_length=500,
        allow_blank=True
    )


class BookingConfirmSerializer(serializers.Serializer):
    """
    Serializer for driver to confirm/reject a booking.
    """
    action = serializers.ChoiceField(
        choices=['confirm', 'reject']
    )
    message = serializers.CharField(
        required=False,
        max_length=500,
        allow_blank=True
    )


class DriverBookingSerializer(serializers.ModelSerializer):
    """
    Serializer for driver to view booking details.
    Shows passenger information.
    """
    user = UserMinimalSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    passenger_phone = serializers.CharField(source='user.phone_number', read_only=True)
    passenger_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'passenger_phone',
            'passenger_email',
            'seats_reserved',
            'status',
            'status_display',
            'price',
            'pickup_note',
            'passenger_message',
            'driver_message',
            'created_at',
        ]
        read_only_fields = fields

