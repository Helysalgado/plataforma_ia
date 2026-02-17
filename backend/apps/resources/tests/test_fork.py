"""
Tests for fork resource service.

US-17: Reutilizar Recurso (Fork)
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
    return User.objects.create_user('user1@example.com', 'User 1', 'pass123')


@pytest.fixture
def another_user():
    """Create another test user."""
    return User.objects.create_user('user2@example.com', 'User 2', 'pass123')


@pytest.fixture
def resource(user):
    """Create a test resource with latest version."""
    resource = Resource.objects.create(owner=user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=resource,
        version_number='1.0.0',
        title='Original Prompt',
        description='Original description',
        type='Prompt',
        tags=['original', 'test'],
        content='Original content',
        status='Validated',
        is_latest=True
    )
    return resource


@pytest.mark.django_db
class TestForkResourceService:
    """Tests for ResourceService.fork_resource"""
    
    def test_fork_resource_creates_new_resource(self, user, another_user, resource):
        """Test forking creates a new resource."""
        forked = ResourceService.fork_resource(another_user, resource.id)
        
        assert forked.id != resource.id
        assert forked.owner == another_user
        assert forked.source_type == 'Internal'
        assert forked.derived_from_resource == resource
        assert forked.is_fork is True
    
    def test_fork_copies_latest_version(self, another_user, resource):
        """Test fork copies content from latest version."""
        forked = ResourceService.fork_resource(another_user, resource.id)
        
        original_version = resource.latest_version
        forked_version = forked.latest_version
        
        assert forked_version.version_number == '1.0.0'  # Starts fresh
        assert '(Fork)' in forked_version.title
        assert forked_version.description == original_version.description
        assert forked_version.type == original_version.type
        assert forked_version.tags == original_version.tags
        assert forked_version.content == original_version.content
        assert forked_version.status == 'Sandbox'  # Forks start in Sandbox
        assert forked_version.is_latest is True
    
    def test_fork_increments_forks_count(self, another_user, resource):
        """Test fork increments forks_count on original."""
        original_count = resource.forks_count
        
        ResourceService.fork_resource(another_user, resource.id)
        
        resource.refresh_from_db()
        assert resource.forks_count == original_count + 1
    
    def test_fork_sets_derived_from_version(self, another_user, resource):
        """Test fork records which version was forked."""
        original_version = resource.latest_version
        
        forked = ResourceService.fork_resource(another_user, resource.id)
        
        assert forked.derived_from_version == original_version
    
    def test_fork_nonexistent_resource(self, user):
        """Test forking nonexistent resource raises error."""
        import uuid
        fake_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match='Resource not found'):
            ResourceService.fork_resource(user, fake_id)
    
    def test_fork_soft_deleted_resource(self, user, resource):
        """Test forking soft-deleted resource raises error."""
        # Soft delete
        resource.deleted_at = timezone.now()
        resource.save()
        
        with pytest.raises(ValueError, match='Resource not found'):
            ResourceService.fork_resource(user, resource.id)
    
    def test_fork_of_fork(self, user, another_user, resource):
        """Test forking a fork creates correct lineage."""
        # First fork
        first_fork = ResourceService.fork_resource(another_user, resource.id)
        
        # Fork the fork
        second_fork = ResourceService.fork_resource(user, first_fork.id)
        
        # Verify lineage
        assert second_fork.derived_from_resource == first_fork
        assert second_fork.derived_from_resource != resource
        assert first_fork.derived_from_resource == resource
    
    def test_multiple_forks_same_resource(self, user, another_user, resource):
        """Test multiple users can fork the same resource."""
        fork1 = ResourceService.fork_resource(user, resource.id)
        fork2 = ResourceService.fork_resource(another_user, resource.id)
        
        assert fork1.id != fork2.id
        assert fork1.derived_from_resource == resource
        assert fork2.derived_from_resource == resource
        
        resource.refresh_from_db()
        assert resource.forks_count == 2
