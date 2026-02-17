"""
API integration tests for resource validation.

US-13: Validar Recurso (Admin)
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from apps.authentication.models import Role
from apps.resources.models import Resource, ResourceVersion

User = get_user_model()


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def admin_user():
    """Create an admin user."""
    admin_role, _ = Role.objects.get_or_create(
        name='Admin',
        defaults={'description': 'Administrator'}
    )
    
    user = User.objects.create_user('admin@example.com', 'Admin User', 'pass123')
    user.roles.add(admin_role)
    user.email_verified_at = timezone.now()
    user.save()
    return user


@pytest.fixture
def regular_user():
    """Create a regular user."""
    user_role, _ = Role.objects.get_or_create(
        name='User',
        defaults={'description': 'Standard user'}
    )
    
    user = User.objects.create_user('user@example.com', 'Regular User', 'pass123')
    user.roles.add(user_role)
    user.email_verified_at = timezone.now()
    user.save()
    return user


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create authenticated admin API client."""
    from apps.authentication.services import AuthService
    tokens = AuthService.login(admin_user.email, 'pass123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    return api_client


@pytest.fixture
def user_client(api_client, regular_user):
    """Create authenticated regular user API client."""
    from apps.authentication.services import AuthService
    tokens = AuthService.login(regular_user.email, 'pass123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    return api_client


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
class TestResourceValidateAPI:
    """Tests for POST /api/resources/{id}/validate/"""
    
    def test_admin_can_validate_sandbox_resource(self, admin_client, sandbox_resource):
        """Test admin can validate resource in Sandbox status."""
        response = admin_client.post(f'/api/resources/{sandbox_resource.id}/validate/')
        
        assert response.status_code == 200
        assert response.data['message'] == 'Resource validated successfully'
        assert response.data['status'] == 'Validated'
        assert response.data['validated_at'] is not None
        
        # Verify in database
        sandbox_resource.refresh_from_db()
        assert sandbox_resource.latest_version.status == 'Validated'
    
    def test_admin_can_validate_pending_resource(self, admin_client, pending_resource):
        """Test admin can validate resource in Pending Validation status."""
        response = admin_client.post(f'/api/resources/{pending_resource.id}/validate/')
        
        assert response.status_code == 200
        assert response.data['status'] == 'Validated'
    
    def test_regular_user_cannot_validate(self, user_client, sandbox_resource):
        """Test regular user cannot validate resources."""
        response = user_client.post(f'/api/resources/{sandbox_resource.id}/validate/')
        
        assert response.status_code == 403
        assert response.data['error_code'] == 'PERMISSION_DENIED'
        assert 'Only administrators' in response.data['error']
    
    def test_unauthenticated_cannot_validate(self, api_client, sandbox_resource):
        """Test unauthenticated user cannot validate."""
        response = api_client.post(f'/api/resources/{sandbox_resource.id}/validate/')
        
        assert response.status_code == 401
    
    def test_validate_nonexistent_resource(self, admin_client):
        """Test validating nonexistent resource returns 404."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = admin_client.post(f'/api/resources/{fake_id}/validate/')
        
        assert response.status_code == 404
        assert response.data['error_code'] == 'RESOURCE_NOT_FOUND'
    
    def test_validate_already_validated_resource(self, admin_client, sandbox_resource):
        """Test validating already validated resource returns 400."""
        # First validation
        admin_client.post(f'/api/resources/{sandbox_resource.id}/validate/')
        
        # Try to validate again
        response = admin_client.post(f'/api/resources/{sandbox_resource.id}/validate/')
        
        assert response.status_code == 400
        assert response.data['error_code'] == 'ALREADY_VALIDATED'
    
    def test_owner_cannot_self_validate(self, sandbox_resource):
        """Test resource owner (if not admin) cannot self-validate."""
        # Owner is regular_user, make them authenticated
        from rest_framework.test import APIClient
        from apps.authentication.services import AuthService
        
        client = APIClient()
        tokens = AuthService.login(sandbox_resource.owner.email, 'pass123')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = client.post(f'/api/resources/{sandbox_resource.id}/validate/')
        
        assert response.status_code == 403
        assert response.data['error_code'] == 'PERMISSION_DENIED'
