"""
Tests for Vote services.

US-16: Votar Recurso
"""

import pytest
from django.contrib.auth import get_user_model
from apps.interactions.models import Vote
from apps.interactions.services import VoteService
from apps.resources.models import Resource, ResourceVersion

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user('voter@example.com', 'Voter User', 'pass123')


@pytest.fixture
def another_user():
    """Create another test user."""
    return User.objects.create_user('voter2@example.com', 'Voter 2', 'pass123')


@pytest.fixture
def resource(user):
    """Create a test resource."""
    resource = Resource.objects.create(owner=user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=resource,
        version_number='1.0.0',
        title='Test Resource',
        description='Test',
        type='Prompt',
        content='Test content',
        is_latest=True
    )
    return resource


@pytest.mark.django_db
class TestVoteService:
    """Tests for VoteService."""
    
    def test_toggle_vote_first_time(self, user, resource):
        """Test voting for the first time."""
        result = VoteService.toggle_vote(user, resource.id)
        
        assert result['action'] == 'voted'
        assert result['votes_count'] == 1
        assert Vote.objects.filter(user=user, resource=resource).exists()
    
    def test_toggle_vote_second_time_unvotes(self, user, resource):
        """Test voting twice removes the vote."""
        # First vote
        VoteService.toggle_vote(user, resource.id)
        
        # Second vote (unvote)
        result = VoteService.toggle_vote(user, resource.id)
        
        assert result['action'] == 'unvoted'
        assert result['votes_count'] == 0
        assert not Vote.objects.filter(user=user, resource=resource).exists()
    
    def test_toggle_vote_multiple_users(self, user, another_user, resource):
        """Test multiple users voting for same resource."""
        result1 = VoteService.toggle_vote(user, resource.id)
        result2 = VoteService.toggle_vote(another_user, resource.id)
        
        assert result1['action'] == 'voted'
        assert result2['action'] == 'voted'
        assert result2['votes_count'] == 2
    
    def test_toggle_vote_nonexistent_resource(self, user):
        """Test voting for nonexistent resource raises error."""
        import uuid
        fake_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match='Resource not found'):
            VoteService.toggle_vote(user, fake_id)
    
    def test_toggle_vote_soft_deleted_resource(self, user, resource):
        """Test voting for soft-deleted resource raises error."""
        from django.utils import timezone
        
        # Soft delete resource
        resource.deleted_at = timezone.now()
        resource.save()
        
        with pytest.raises(ValueError, match='Resource not found'):
            VoteService.toggle_vote(user, resource.id)
    
    def test_get_user_voted_resources(self, user):
        """Test getting list of resources user has voted for."""
        # Create 3 resources
        resources = []
        for i in range(3):
            r = Resource.objects.create(owner=user, source_type='Internal')
            ResourceVersion.objects.create(
                resource=r,
                version_number='1.0.0',
                title=f'Resource {i}',
                description='Test',
                type='Prompt',
                content='Test',
                is_latest=True
            )
            resources.append(r)
        
        # Vote for 2 of them
        Vote.objects.create(user=user, resource=resources[0])
        Vote.objects.create(user=user, resource=resources[2])
        
        voted_ids = VoteService.get_user_voted_resources(user)
        
        assert len(voted_ids) == 2
        assert resources[0].id in voted_ids
        assert resources[2].id in voted_ids
        assert resources[1].id not in voted_ids
    
    def test_has_user_voted(self, user, resource):
        """Test checking if user has voted for resource."""
        # Initially not voted
        assert VoteService.has_user_voted(user, resource.id) is False
        
        # After voting
        Vote.objects.create(user=user, resource=resource)
        assert VoteService.has_user_voted(user, resource.id) is True
