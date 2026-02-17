"""
API integration tests for interactions app.

US-16: Votar Recurso
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.authentication.models import Role
from apps.interactions.models import Vote
from apps.resources.models import Resource, ResourceVersion

User = get_user_model()


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user with User role."""
    from apps.authentication.models import Role
    Role.objects.get_or_create(
        name='User',
        defaults={'description': 'Standard user'}
    )
    
    user = User.objects.create_user('test@example.com', 'Test User', 'pass123')
    user_role = Role.objects.get(name='User')
    user.roles.add(user_role)
    user.email_verified_at = '2024-01-01T00:00:00Z'
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
def resource(user):
    """Create a test resource."""
    resource = Resource.objects.create(owner=user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=resource,
        version_number='1.0.0',
        title='Test Resource',
        description='A test resource',
        type='Prompt',
        content='Test content',
        status='Validated',
        is_latest=True
    )
    return resource


@pytest.mark.django_db
class TestVoteToggleAPI:
    """Tests for POST /api/resources/{id}/vote/"""
    
    def test_vote_for_resource(self, authenticated_client, resource):
        """Test voting for a resource."""
        response = authenticated_client.post(f'/api/resources/{resource.id}/vote/')
        
        assert response.status_code == 200
        assert response.data['action'] == 'voted'
        assert response.data['votes_count'] == 1
        
        # Verify vote was created
        assert Vote.objects.filter(resource=resource).count() == 1
    
    def test_unvote_resource(self, authenticated_client, user, resource):
        """Test unvoting (voting twice)."""
        # First vote
        response1 = authenticated_client.post(f'/api/resources/{resource.id}/vote/')
        assert response1.status_code == 200
        assert response1.data['action'] == 'voted'
        
        # Second vote (unvote)
        response2 = authenticated_client.post(f'/api/resources/{resource.id}/vote/')
        assert response2.status_code == 200
        assert response2.data['action'] == 'unvoted'
        assert response2.data['votes_count'] == 0
        
        # Verify vote was deleted
        assert Vote.objects.filter(resource=resource).count() == 0
    
    def test_vote_unauthenticated(self, api_client, resource):
        """Test unauthenticated user cannot vote."""
        response = api_client.post(f'/api/resources/{resource.id}/vote/')
        
        assert response.status_code == 401
    
    def test_vote_nonexistent_resource(self, authenticated_client):
        """Test voting for nonexistent resource returns 404."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = authenticated_client.post(f'/api/resources/{fake_id}/vote/')
        
        assert response.status_code == 404
        assert response.data['error_code'] == 'RESOURCE_NOT_FOUND'
    
    def test_vote_count_increments(self, authenticated_client, user, resource):
        """Test that votes_count increments correctly."""
        # Create another user
        user2 = User.objects.create_user('test2@example.com', 'Test 2', 'pass123')
        user2_role = Role.objects.get(name='User')
        user2.roles.add(user2_role)
        user2.email_verified_at = '2024-01-01T00:00:00Z'
        user2.save()
        
        # User 1 votes
        response1 = authenticated_client.post(f'/api/resources/{resource.id}/vote/')
        assert response1.data['votes_count'] == 1
        
        # User 2 votes (need to authenticate as user2)
        from apps.authentication.services import AuthService
        tokens2 = AuthService.login(user2.email, 'pass123')
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens2["access"]}')
        
        response2 = authenticated_client.post(f'/api/resources/{resource.id}/vote/')
        assert response2.data['votes_count'] == 2
