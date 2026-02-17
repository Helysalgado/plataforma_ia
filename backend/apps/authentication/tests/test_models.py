"""
Tests for User model.

US-01: Registro de Usuario
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.authentication.models import Role, UserRole

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""
    
    def test_create_user_success(self):
        """Test creating a user is successful."""
        email = 'test@example.com'
        name = 'Test User'
        password = 'testpass123'
        
        user = User.objects.create_user(
            email=email,
            name=name,
            password=password
        )
        
        assert user.email == email
        assert user.name == name
        assert user.check_password(password)
        assert user.is_active is True
        assert user.is_staff is False
        assert user.email_verified_at is None
        assert user.verification_token is None
    
    def test_create_user_email_normalized(self):
        """Test email is normalized for new users."""
        email = 'test@EXAMPLE.COM'
        user = User.objects.create_user(email, 'Test User', 'test123')
        
        assert user.email == 'test@example.com'
    
    def test_create_user_without_email_raises_error(self):
        """Test creating user without email raises ValueError."""
        with pytest.raises(ValueError, match='Email is required'):
            User.objects.create_user('', 'Test User', 'test123')
    
    def test_create_user_without_name_raises_error(self):
        """Test creating user without name raises ValueError."""
        with pytest.raises(ValueError, match='Name is required'):
            User.objects.create_user('test@example.com', '', 'test123')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='admin123'
        )
        
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.is_active is True
        assert user.email_verified_at is not None  # Auto-verified
    
    def test_is_email_verified_property(self):
        """Test is_email_verified property."""
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        assert user.is_email_verified is False
        
        user.email_verified_at = timezone.now()
        user.save()
        assert user.is_email_verified is True
    
    def test_is_admin_property_with_admin_role(self):
        """Test is_admin property returns True for Admin role."""
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        admin_role, _ = Role.objects.get_or_create(name='Admin', description='Administrator')
        UserRole.objects.create(user=user, role=admin_role)
        
        assert user.is_admin is True
    
    def test_is_admin_property_without_admin_role(self):
        """Test is_admin property returns False for regular user."""
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        user_role, _ = Role.objects.get_or_create(name='User', description='Regular user')
        UserRole.objects.create(user=user, role=user_role)
        
        assert user.is_admin is False
    
    def test_has_role_method(self):
        """Test has_role method."""
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        user_role, _ = Role.objects.get_or_create(name='User')
        UserRole.objects.create(user=user, role=user_role)
        
        assert user.has_role('User') is True
        assert user.has_role('Admin') is False


@pytest.mark.django_db
class TestRoleModel:
    """Tests for Role model."""
    
    def test_create_role(self):
        """Test creating a role."""
        role = Role.objects.create(name='Admin', description='Administrator')
        
        assert role.name == 'Admin'
        assert role.description == 'Administrator'
        assert str(role) == 'Admin'
    
    def test_role_name_unique(self):
        """Test role name must be unique."""
        Role.objects.create(name='Admin')
        
        with pytest.raises(Exception):  # IntegrityError
            Role.objects.create(name='Admin')
