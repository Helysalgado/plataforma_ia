"""
Tests for resource validation service.

US-13: Validar Recurso (Admin)
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.resources.models import Resource, ResourceVersion
from apps.resources.services import ResourceService
from apps.authentication.models import Role

User = get_user_model()


@pytest.fixture
def admin_role():
    """Create Admin role."""
    role, _ = Role.objects.get_or_create(
        name='Admin',
        defaults={'description': 'Administrator'}
    )
    return role


@pytest.fixture
def user_role():
    """Create User role."""
    role, _ = Role.objects.get_or_create(
        name='User',
        defaults={'description': 'Standard user'}
    )
    return role


@pytest.fixture
def admin_user(admin_role):
    """Create an admin user."""
    user = User.objects.create_user('admin@example.com', 'Admin User', 'pass123')
    user.roles.add(admin_role)
    user.email_verified_at = timezone.now()
    user.save()
    return user


@pytest.fixture
def regular_user(user_role):
    """Create a regular user."""
    user = User.objects.create_user('user@example.com', 'Regular User', 'pass123')
    user.roles.add(user_role)
    user.email_verified_at = timezone.now()
    user.save()
    return user


@pytest.fixture
def sandbox_resource(regular_user):
    """Create a resource in Sandbox status."""
    resource = Resource.objects.create(owner=regular_user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=resource,
        version_number='1.0.0',
        title='Sandbox Resource',
        description='A resource in sandbox',
        type='Prompt',
        content='Test content',
        status='Sandbox',
        is_latest=True
    )
    return resource


@pytest.fixture
def pending_resource(regular_user):
    """Create a resource in Pending Validation status."""
    resource = Resource.objects.create(owner=regular_user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=resource,
        version_number='1.0.0',
        title='Pending Resource',
        description='A resource pending validation',
        type='Workflow',
        content='Test content',
        status='Pending Validation',
        is_latest=True
    )
    return resource


@pytest.mark.django_db
class TestResourceValidationService:
    """Tests for ResourceService.validate_resource"""
    
    def test_admin_can_validate_sandbox_resource(self, admin_user, sandbox_resource):
        """Test admin can validate resource in Sandbox status."""
        result = ResourceService.validate_resource(admin_user, sandbox_resource.id)
        
        assert result.id == sandbox_resource.id
        latest = result.latest_version
        assert latest.status == 'Validated'
        assert latest.validated_at is not None
    
    def test_admin_can_validate_pending_resource(self, admin_user, pending_resource):
        """Test admin can validate resource in Pending Validation status."""
        result = ResourceService.validate_resource(admin_user, pending_resource.id)
        
        latest = result.latest_version
        assert latest.status == 'Validated'
        assert latest.validated_at is not None
    
    def test_non_admin_cannot_validate(self, regular_user, sandbox_resource):
        """Test regular user cannot validate resources."""
        with pytest.raises(ValueError, match='Only administrators can validate'):
            ResourceService.validate_resource(regular_user, sandbox_resource.id)
    
    def test_validate_nonexistent_resource(self, admin_user):
        """Test validating nonexistent resource raises error."""
        import uuid
        fake_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match='Resource not found'):
            ResourceService.validate_resource(admin_user, fake_id)
    
    def test_validate_already_validated_resource(self, admin_user, sandbox_resource):
        """Test validating already validated resource raises error."""
        # First validation
        ResourceService.validate_resource(admin_user, sandbox_resource.id)
        
        # Try to validate again
        with pytest.raises(ValueError, match='already validated'):
            ResourceService.validate_resource(admin_user, sandbox_resource.id)
    
    def test_validate_soft_deleted_resource(self, admin_user, sandbox_resource):
        """Test validating soft-deleted resource raises error."""
        # Soft delete
        sandbox_resource.deleted_at = timezone.now()
        sandbox_resource.save()
        
        with pytest.raises(ValueError, match='Resource not found'):
            ResourceService.validate_resource(admin_user, sandbox_resource.id)
