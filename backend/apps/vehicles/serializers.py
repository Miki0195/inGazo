"""
Serializers for the Vehicles app.
"""

from rest_framework import serializers

from apps.drivers.serializers import DriverMinimalSerializer

from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for Vehicle model - read operations.
    """
    driver = DriverMinimalSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'driver',
            'make',
            'model',
            'year',
            'license_plate',
            'color',
            'color_display',
            'seats',
            'photo_url',
            'has_air_conditioning',
            'has_wifi',
            'has_usb_charger',
            'trunk_space',
            'is_active',
            'is_verified',
            'full_name',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'is_verified',
            'created_at',
        ]


class VehicleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new vehicle.
    """

    class Meta:
        model = Vehicle
        fields = [
            'make',
            'model',
            'year',
            'license_plate',
            'color',
            'seats',
            'photo_url',
            'has_air_conditioning',
            'has_wifi',
            'has_usb_charger',
            'trunk_space',
        ]

    def validate_license_plate(self, value):
        """
        Ensure license plate is unique and uppercase.
        """
        value = value.upper().replace(' ', '')
        if Vehicle.objects.filter(license_plate=value).exists():
            raise serializers.ValidationError(
                'A vehicle with this license plate already exists.'
            )
        return value

    def create(self, validated_data):
        """
        Create vehicle for the current user's driver profile.
        """
        user = self.context['request'].user
        
        if not hasattr(user, 'driver_profile'):
            raise serializers.ValidationError(
                'You must be a registered driver to add a vehicle.'
            )
        
        return Vehicle.objects.create(
            driver=user.driver_profile,
            **validated_data
        )


class VehicleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a vehicle.
    """

    class Meta:
        model = Vehicle
        fields = [
            'make',
            'model',
            'year',
            'color',
            'seats',
            'photo_url',
            'has_air_conditioning',
            'has_wifi',
            'has_usb_charger',
            'trunk_space',
            'is_active',
        ]


class VehicleMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal vehicle serializer for nested representations.
    """
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'full_name',
            'license_plate',
            'color',
            'seats',
            'photo_url',
        ]
        read_only_fields = fields

