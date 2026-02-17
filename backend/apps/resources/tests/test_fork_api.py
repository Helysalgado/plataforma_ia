"""
API integration tests for resource fork.

US-17: Reutilizar Recurso (Fork)
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
def user():
    """Create a test user."""
    user_role, _ = Role.objects.get_or_create(
        name='User',
        defaults={'description': 'Standard user'}
    )
    
    user = User.objects.create_user('user@example.com', 'Test User', 'pass123')
    user.roles.add(user_role)
    user.email_verified_at = timezone.now()
    user.save()
    return user


@pytest.fixture
def another_user():
    """Create another test user."""
    user_role, _ = Role.objects.get_or_create(
        name='User',
        defaults={'description': 'Standard user'}
    )
    
    user = User.objects.create_user('user2@example.com', 'User 2', 'pass123')
    user.roles.add(user_role)
    user.email_verified_at = timezone.now()
    user.save()
    return user


@pytest.fixture
def authenticated_client(api_client, user):
    """Create authenticated API client."""
    from apps.authentication.services import AuthService
    tokens = AuthService.login(user.email, 'pass123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    return api_client


@pytest.fixture
def resource(another_user):
    """Create a test resource."""
    resource = Resource.objects.create(owner=another_user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=resource,
        version_number='1.0.0',
        title='Original Resource',
        description='Original description',
        type='Prompt',
        tags=['test'],
        content='Original content',
        status='Validated',
        is_latest=True
    )
    return resource


@pytest.mark.django_db
class TestResourceForkAPI:
    """Tests for POST /api/resources/{id}/fork/"""
    
    def test_fork_resource(self, authenticated_client, user, resource):
        """Test forking a resource."""
        response = authenticated_client.post(f'/api/resources/{resource.id}/fork/')
        
        assert response.status_code == 201
        assert response.data['message'] == 'Resource forked successfully'
        assert response.data['forked_resource_id'] is not None
        assert response.data['original_resource_id'] == str(resource.id)
        assert response.data['derived_from_version'] == '1.0.0'
        
        # Verify in database
        from uuid import UUID
        forked_id = UUID(response.data['forked_resource_id'])
        forked = Resource.objects.get(id=forked_id)
        assert forked.owner == user
        assert forked.derived_from_resource == resource
        assert forked.is_fork is True
    
    def test_fork_increments_count(self, authenticated_client, resource):
        """Test fork increments forks_count on original."""
        original_count = resource.forks_count
        
        response = authenticated_client.post(f'/api/resources/{resource.id}/fork/')
        
        assert response.status_code == 201
        
        resource.refresh_from_db()
        assert resource.forks_count == original_count + 1
    
    def test_fork_unauthenticated(self, api_client, resource):
        """Test unauthenticated user cannot fork."""
        response = api_client.post(f'/api/resources/{resource.id}/fork/')
        
        assert response.status_code == 401
    
    def test_fork_nonexistent_resource(self, authenticated_client):
        """Test forking nonexistent resource returns 404."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = authenticated_client.post(f'/api/resources/{fake_id}/fork/')
        
        assert response.status_code == 404
        assert response.data['error_code'] == 'RESOURCE_NOT_FOUND'
    
    def test_fork_own_resource(self, authenticated_client, user):
        """Test user can fork their own resource."""
        # Create resource owned by user
        my_resource = Resource.objects.create(owner=user, source_type='Internal')
        ResourceVersion.objects.create(
            resource=my_resource,
            version_number='1.0.0',
            title='My Resource',
            description='Test',
            type='Prompt',
            content='Content',
            is_latest=True
        )
        
        response = authenticated_client.post(f'/api/resources/{my_resource.id}/fork/')
        
        assert response.status_code == 201
        # Even though you own it, you can fork (for experimentation)
