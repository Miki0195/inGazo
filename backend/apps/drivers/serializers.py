"""
Serializers for the Drivers app.
"""

from rest_framework import serializers

from apps.users.serializers import UserMinimalSerializer

from .models import Driver, DriverDocument


class DriverSerializer(serializers.ModelSerializer):
    """
    Serializer for Driver model - read operations.
    """
    user = UserMinimalSerializer(read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Driver
        fields = [
            'id',
            'user',
            'full_name',
            'license_number',
            'license_expiry',
            'rating',
            'total_trips',
            'total_reviews',
            'is_verified',
            'is_active',
            'bio',
            'accepts_smoking',
            'accepts_pets',
            'accepts_luggage',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'rating',
            'total_trips',
            'total_reviews',
            'is_verified',
            'created_at',
        ]


class DriverCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new driver profile.
    """

    class Meta:
        model = Driver
        fields = [
            'license_number',
            'license_expiry',
            'license_photo_url',
            'bio',
            'accepts_smoking',
            'accepts_pets',
            'accepts_luggage',
        ]

    def create(self, validated_data):
        """
        Create driver profile for the current user.
        """
        user = self.context['request'].user
        
        # Check if user already has a driver profile
        if hasattr(user, 'driver_profile'):
            raise serializers.ValidationError(
                'User already has a driver profile.'
            )
        
        # New applications start as unverified and inactive until reviewed
        return Driver.objects.create(
            user=user,
            is_verified=False,
            is_active=False,
            **validated_data,
        )


class DriverUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating driver profile.
    """

    class Meta:
        model = Driver
        fields = [
            'license_number',
            'license_expiry',
            'license_photo_url',
            'bio',
            'accepts_smoking',
            'accepts_pets',
            'accepts_luggage',
            'is_active',
        ]


class DriverMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal driver serializer for nested representations.
    """
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    profile_photo_url = serializers.CharField(
        source='user.profile_photo_url',
        read_only=True
    )

    class Meta:
        model = Driver
        fields = [
            'id',
            'full_name',
            'profile_photo_url',
            'rating',
            'total_trips',
            'is_verified',
        ]
        read_only_fields = fields


class DriverDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Driver Documents.
    """

    class Meta:
        model = DriverDocument
        fields = [
            'id',
            'document_type',
            'document_url',
            'status',
            'expiry_date',
            'rejection_reason',
            'reviewed_at',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'rejection_reason',
            'reviewed_at',
            'created_at',
        ]


class DriverDocumentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading driver documents.
    """

    class Meta:
        model = DriverDocument
        fields = [
            'document_type',
            'document_url',
            'expiry_date',
        ]

    def create(self, validated_data):
        driver = self.context['driver']
        return DriverDocument.objects.create(driver=driver, **validated_data)


class DriverDocumentReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to review driver documents.
    """

    class Meta:
        model = DriverDocument
        fields = [
            'status',
            'rejection_reason',
        ]

    def validate(self, attrs):
        if attrs.get('status') == DriverDocument.DocumentStatus.REJECTED:
            if not attrs.get('rejection_reason'):
                raise serializers.ValidationError({
                    'rejection_reason': 'Rejection reason is required when rejecting a document.'
                })
        return attrs

