"""
Serializers for the Users app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.drivers.models import Driver

User = get_user_model()


class DriverInlineSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for embedding driver data on the user object.
    Keeps fields minimal to avoid circular imports with drivers serializers.
    """

    class Meta:
        model = Driver
        fields = [
            'id',
            'license_number',
            'license_expiry',
            'bio',
            'accepts_smoking',
            'accepts_pets',
            'accepts_luggage',
            'rating',
            'total_trips',
            'total_reviews',
            'is_verified',
            'is_active',
            'created_at',
        ]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - read operations.
    """
    driver_profile = DriverInlineSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'email',
            'full_name',
            'profile_photo_url',
            'is_verified',
            'created_at',
            'last_login',
            'driver_profile',
        ]
        read_only_fields = [
            'id',
            'is_verified',
            'created_at',
            'last_login',
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'email',
            'full_name',
            'password',
            'password_confirm',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        """
        Validate that password and password_confirm match.
        Ensure at least one of email or phone_number is provided.
        """
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        if not attrs.get('email') and not attrs.get('phone_number'):
            raise serializers.ValidationError(
                'Either email or phone number is required.'
            )

        return attrs

    def create(self, validated_data):
        """
        Create and return a new user.
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """

    class Meta:
        model = User
        fields = [
            'full_name',
            'profile_photo_url',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer to include additional user data.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['is_verified'] = user.is_verified

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to response
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'phone_number': self.user.phone_number,
            'full_name': self.user.full_name,
            'is_verified': self.user.is_verified,
        }
        driver = getattr(self.user, 'driver_profile', None)
        if driver:
            data['user']['driver_profile'] = DriverInlineSerializer(driver).data

        return data


class UserMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for nested representations.
    """

    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'profile_photo_url',
        ]
        read_only_fields = fields

