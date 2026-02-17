"""
API integration tests for version history.

US-22: Historial de Versiones
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from apps.resources.models import Resource, ResourceVersion

User = get_user_model()


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user('user@example.com', 'Test User', 'pass123')


@pytest.fixture
def resource_with_versions(user):
    """Create a resource with multiple versions."""
    resource = Resource.objects.create(owner=user, source_type='Internal')
    
    # Create 3 versions with different timestamps
    v1 = ResourceVersion.objects.create(
        resource=resource,
        version_number='1.0.0',
        title='Version 1',
        description='First',
        type='Prompt',
        tags=['initial'],
        content='Content 1',
        status='Validated',
        is_latest=False
    )
    v1.created_at = timezone.now() - timezone.timedelta(days=10)
    v1.save()
    
    v2 = ResourceVersion.objects.create(
        resource=resource,
        version_number='1.5.0',
        title='Version 1.5',
        description='Second',
        type='Prompt',
        tags=['update'],
        content='Content 2',
        status='Validated',
        is_latest=False
    )
    v2.created_at = timezone.now() - timezone.timedelta(days=5)
    v2.save()
    
    ResourceVersion.objects.create(
        resource=resource,
        version_number='2.0.0',
        title='Version 2',
        description='Latest',
        type='Prompt',
        tags=['major'],
        content='Content 3',
        status='Sandbox',
        is_latest=True
    )
    
    return resource


@pytest.mark.django_db
class TestVersionHistoryAPI:
    """Tests for GET /api/resources/{id}/versions/"""
    
    def test_get_version_history(self, api_client, resource_with_versions):
        """Test getting version history."""
        response = api_client.get(f'/api/resources/{resource_with_versions.id}/versions/')
        
        assert response.status_code == 200
        assert str(response.data['resource_id']) == str(resource_with_versions.id)
        assert response.data['count'] == 3
        assert len(response.data['versions']) == 3
    
    def test_versions_ordered_newest_first(self, api_client, resource_with_versions):
        """Test that versions are ordered by creation date (newest first)."""
        response = api_client.get(f'/api/resources/{resource_with_versions.id}/versions/')
        
        versions = response.data['versions']
        version_numbers = [v['version_number'] for v in versions]
        
        assert version_numbers == ['2.0.0', '1.5.0', '1.0.0']
    
    def test_version_includes_metadata(self, api_client, resource_with_versions):
        """Test that each version includes necessary metadata."""
        response = api_client.get(f'/api/resources/{resource_with_versions.id}/versions/')
        
        latest = response.data['versions'][0]
        
        assert latest['version_number'] == '2.0.0'
        assert latest['title'] == 'Version 2'
        assert latest['status'] == 'Sandbox'
        assert latest['is_latest'] is True
        assert latest['type'] == 'Prompt'
        assert latest['tags'] == ['major']
        assert 'pid' in latest
        assert 'created_at' in latest
    
    def test_version_history_is_public(self, api_client, resource_with_versions):
        """Test that version history is accessible without authentication."""
        # No authentication
        response = api_client.get(f'/api/resources/{resource_with_versions.id}/versions/')
        
        assert response.status_code == 200
        assert response.data['count'] == 3
    
    def test_version_history_nonexistent_resource(self, api_client):
        """Test getting history for nonexistent resource returns 404."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = api_client.get(f'/api/resources/{fake_id}/versions/')
        
        assert response.status_code == 404
        assert response.data['error_code'] == 'RESOURCE_NOT_FOUND'
    
    def test_version_history_soft_deleted_resource(self, api_client, resource_with_versions):
        """Test getting history for soft-deleted resource returns 404."""
        resource_with_versions.deleted_at = timezone.now()
        resource_with_versions.save()
        
        response = api_client.get(f'/api/resources/{resource_with_versions.id}/versions/')
        
        assert response.status_code == 404
        assert response.data['error_code'] == 'RESOURCE_NOT_FOUND'
    
    def test_version_history_single_version(self, api_client, user):
        """Test version history with only one version."""
        resource = Resource.objects.create(owner=user, source_type='Internal')
        ResourceVersion.objects.create(
            resource=resource,
            version_number='1.0.0',
            title='Only Version',
            description='Test',
            type='Prompt',
            tags=['solo'],
            content='Content',
            is_latest=True
        )
        
        response = api_client.get(f'/api/resources/{resource.id}/versions/')
        
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['versions'][0]['version_number'] == '1.0.0'
