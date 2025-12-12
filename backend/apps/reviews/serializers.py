"""
Serializers for the Reviews app.
"""

from rest_framework import serializers

from apps.rides.serializers import RideMinimalSerializer
from apps.users.serializers import UserMinimalSerializer

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model - read operations.
    """
    ride = RideMinimalSerializer(read_only=True)
    reviewer = UserMinimalSerializer(read_only=True)
    target = UserMinimalSerializer(read_only=True)
    review_type_display = serializers.CharField(
        source='get_review_type_display',
        read_only=True
    )

    class Meta:
        model = Review
        fields = [
            'id',
            'ride',
            'reviewer',
            'target',
            'review_type',
            'review_type_display',
            'rating',
            'comment',
            'response',
            'response_at',
            'is_visible',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'ride',
            'reviewer',
            'target',
            'review_type',
            'response',
            'response_at',
            'is_visible',
            'created_at',
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new review.
    """
    ride_id = serializers.UUIDField(write_only=True)
    target_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Review
        fields = [
            'ride_id',
            'target_id',
            'rating',
            'comment',
        ]

    def validate_ride_id(self, value):
        """
        Ensure ride exists and is completed.
        """
        from apps.rides.models import Ride
        
        try:
            ride = Ride.objects.get(id=value)
        except Ride.DoesNotExist:
            raise serializers.ValidationError('Ride not found.')
        
        if ride.status != Ride.RideStatus.FINISHED:
            raise serializers.ValidationError(
                'You can only review completed rides.'
            )
        
        return value

    def validate(self, attrs):
        """
        Validate the review.
        """
        from apps.bookings.models import Booking
        from apps.rides.models import Ride
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = self.context['request'].user
        ride_id = attrs.get('ride_id')
        target_id = attrs.get('target_id')
        
        ride = Ride.objects.get(id=ride_id)
        
        try:
            target = User.objects.get(id=target_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'target_id': 'Target user not found.'
            })
        
        # Determine review type based on user role
        is_driver = hasattr(user, 'driver_profile') and ride.driver == user.driver_profile
        
        if is_driver:
            # Driver reviewing a passenger
            review_type = Review.ReviewType.PASSENGER_REVIEW
            
            # Check if target was a passenger on this ride
            if not Booking.objects.filter(
                ride=ride,
                user=target,
                status=Booking.BookingStatus.COMPLETED
            ).exists():
                raise serializers.ValidationError({
                    'target_id': 'This user was not a passenger on this ride.'
                })
        else:
            # Passenger reviewing the driver
            review_type = Review.ReviewType.DRIVER_REVIEW
            
            # Check if user was a passenger on this ride
            if not Booking.objects.filter(
                ride=ride,
                user=user,
                status=Booking.BookingStatus.COMPLETED
            ).exists():
                raise serializers.ValidationError(
                    'You were not a passenger on this ride.'
                )
            
            # Check if target is the driver
            if not (hasattr(target, 'driver_profile') and 
                    ride.driver == target.driver_profile):
                raise serializers.ValidationError({
                    'target_id': 'Target must be the driver of this ride.'
                })
        
        # Check for existing review
        if Review.objects.filter(
            ride_id=ride_id,
            reviewer=user,
            target=target
        ).exists():
            raise serializers.ValidationError(
                'You have already reviewed this user for this ride.'
            )
        
        attrs['review_type'] = review_type
        attrs['target'] = target
        
        return attrs

    def create(self, validated_data):
        """
        Create review.
        """
        from apps.rides.models import Ride
        
        user = self.context['request'].user
        ride_id = validated_data.pop('ride_id')
        validated_data.pop('target_id')
        
        ride = Ride.objects.get(id=ride_id)
        
        return Review.objects.create(
            ride=ride,
            reviewer=user,
            **validated_data
        )


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a review.
    """

    class Meta:
        model = Review
        fields = [
            'rating',
            'comment',
        ]


class ReviewResponseSerializer(serializers.Serializer):
    """
    Serializer for responding to a review.
    """
    response = serializers.CharField(max_length=500)


class ReviewFlagSerializer(serializers.Serializer):
    """
    Serializer for flagging a review.
    """
    reason = serializers.CharField(max_length=500)


class ReviewModerateSerializer(serializers.Serializer):
    """
    Serializer for moderating a review (admin).
    """
    is_visible = serializers.BooleanField()


class ReviewStatsSerializer(serializers.Serializer):
    """
    Serializer for review statistics.
    """
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()

