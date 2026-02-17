"""
Tests for version history service.

US-22: Historial de Versiones
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.resources.models import Resource, ResourceVersion
from apps.resources.services import ResourceService

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user('user@example.com', 'Test User', 'pass123')


@pytest.fixture
def resource_with_versions(user):
    """Create a resource with multiple versions."""
    resource = Resource.objects.create(owner=user, source_type='Internal')
    
    # Create 3 versions
    v1 = ResourceVersion.objects.create(
        resource=resource,
        version_number='1.0.0',
        title='Initial Version',
        description='First version',
        type='Prompt',
        tags=['v1'],
        content='Content v1',
        status='Validated',
        is_latest=False
    )
    v1.created_at = timezone.now() - timezone.timedelta(days=10)
    v1.save()
    
    v2 = ResourceVersion.objects.create(
        resource=resource,
        version_number='1.1.0',
        title='Updated Version',
        description='Second version',
        type='Prompt',
        tags=['v1', 'v2'],
        content='Content v2',
        status='Validated',
        is_latest=False
    )
    v2.created_at = timezone.now() - timezone.timedelta(days=5)
    v2.save()
    
    v3 = ResourceVersion.objects.create(
        resource=resource,
        version_number='2.0.0',
        title='Major Update',
        description='Third version with breaking changes',
        type='Prompt',
        tags=['v2'],
        content='Content v3',
        status='Sandbox',
        is_latest=True
    )
    
    return resource


@pytest.mark.django_db
class TestVersionHistoryService:
    """Tests for ResourceService.get_version_history"""
    
    def test_get_version_history_returns_all_versions(self, resource_with_versions):
        """Test that version history returns all versions."""
        versions = ResourceService.get_version_history(resource_with_versions.id)
        
        assert versions.count() == 3
    
    def test_versions_ordered_by_created_at_desc(self, resource_with_versions):
        """Test that versions are ordered newest first."""
        versions = ResourceService.get_version_history(resource_with_versions.id)
        
        version_numbers = [v.version_number for v in versions]
        assert version_numbers == ['2.0.0', '1.1.0', '1.0.0']
    
    def test_version_history_includes_metadata(self, resource_with_versions):
        """Test that version history includes all necessary metadata."""
        versions = ResourceService.get_version_history(resource_with_versions.id)
        
        latest = versions.first()
        assert latest.version_number == '2.0.0'
        assert latest.title == 'Major Update'
        assert latest.status == 'Sandbox'
        assert latest.is_latest is True
        assert latest.type == 'Prompt'
        assert latest.tags == ['v2']
    
    def test_version_history_nonexistent_resource(self):
        """Test getting history for nonexistent resource raises error."""
        import uuid
        fake_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match='Resource not found'):
            ResourceService.get_version_history(fake_id)
    
    def test_version_history_soft_deleted_resource(self, resource_with_versions):
        """Test getting history for soft-deleted resource raises error."""
        resource_with_versions.deleted_at = timezone.now()
        resource_with_versions.save()
        
        with pytest.raises(ValueError, match='Resource not found'):
            ResourceService.get_version_history(resource_with_versions.id)
    
    def test_version_history_single_version(self, user):
        """Test version history with only one version."""
        resource = Resource.objects.create(owner=user, source_type='Internal')
        ResourceVersion.objects.create(
            resource=resource,
            version_number='1.0.0',
            title='Only Version',
            description='Test',
            type='Prompt',
            content='Content',
            is_latest=True
        )
        
        versions = ResourceService.get_version_history(resource.id)
        
        assert versions.count() == 1
        assert versions.first().version_number == '1.0.0'
    
    def test_version_history_with_validated_timestamps(self, user):
        """Test that validated_at timestamps are preserved."""
        resource = Resource.objects.create(owner=user, source_type='Internal')
        
        validated_time = timezone.now() - timezone.timedelta(days=3)
        ResourceVersion.objects.create(
            resource=resource,
            version_number='1.0.0',
            title='Validated Version',
            description='Test',
            type='Prompt',
            content='Content',
            status='Validated',
            validated_at=validated_time,
            is_latest=True
        )
        
        versions = ResourceService.get_version_history(resource.id)
        
        assert versions.first().validated_at == validated_time
