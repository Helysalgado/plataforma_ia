"""
Serializers for authentication app.

US-01: Registro de Usuario
US-02: Login
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from apps.authentication.models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    
    class Meta:
        model = Role
        fields = ('id', 'name', 'description')
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (public representation)."""
    
    roles = RoleSerializer(many=True, read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'is_active',
            'email_verified_at',
            'roles',
            'is_admin',
            'created_at',
        )
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    
    US-01: Registro de Usuario
    """
    
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    
    # Note: Email uniqueness validation moved to service layer
    # to return proper 409 Conflict status code
    
    def validate_name(self, value):
        """Validate name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError('Name cannot be empty')
        return value.strip()


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    US-02: Login
    """
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )


class VerifyEmailSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    
    US-01: Registro de Usuario (verificación)
    """
    
    token = serializers.CharField(required=True)
