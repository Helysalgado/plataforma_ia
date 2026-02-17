"""
Tests for Vote model.

US-16: Votar Recurso
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.interactions.models import Vote
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
    """Create a test resource with version."""
    resource = Resource.objects.create(owner=user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=resource,
        version_number='1.0.0',
        title='Test Resource',
        description='A test resource',
        type='Prompt',
        content='Test content',
        is_latest=True
    )
    return resource


@pytest.mark.django_db
class TestVoteModel:
    """Tests for Vote model."""
    
    def test_create_vote(self, user, resource):
        """Test creating a vote."""
        vote = Vote.objects.create(user=user, resource=resource)
        
        assert vote.id is not None
        assert vote.user == user
        assert vote.resource == resource
        assert vote.created_at is not None
    
    def test_unique_vote_per_user_per_resource(self, user, resource):
        """Test that a user can only vote once per resource."""
        # Create first vote
        Vote.objects.create(user=user, resource=resource)
        
        # Try to create duplicate vote
        with pytest.raises(IntegrityError):
            Vote.objects.create(user=user, resource=resource)
    
    def test_multiple_users_can_vote_same_resource(self, user, another_user, resource):
        """Test that multiple users can vote for the same resource."""
        vote1 = Vote.objects.create(user=user, resource=resource)
        vote2 = Vote.objects.create(user=another_user, resource=resource)
        
        assert vote1.resource == vote2.resource
        assert vote1.user != vote2.user
        assert Vote.objects.filter(resource=resource).count() == 2
    
    def test_user_can_vote_multiple_resources(self, user):
        """Test that a user can vote for multiple resources."""
        resource1 = Resource.objects.create(owner=user, source_type='Internal')
        ResourceVersion.objects.create(
            resource=resource1,
            version_number='1.0.0',
            title='Resource 1',
            description='Test',
            type='Prompt',
            content='Test',
            is_latest=True
        )
        
        resource2 = Resource.objects.create(owner=user, source_type='Internal')
        ResourceVersion.objects.create(
            resource=resource2,
            version_number='1.0.0',
            title='Resource 2',
            description='Test',
            type='Workflow',
            content='Test',
            is_latest=True
        )
        
        vote1 = Vote.objects.create(user=user, resource=resource1)
        vote2 = Vote.objects.create(user=user, resource=resource2)
        
        assert Vote.objects.filter(user=user).count() == 2
    
    def test_vote_cascade_delete_on_user_delete(self, user, resource):
        """Test that votes are deleted when user is deleted."""
        Vote.objects.create(user=user, resource=resource)
        assert Vote.objects.filter(user=user).count() == 1
        
        # Delete user
        user.delete()
        
        # Vote should be deleted
        assert Vote.objects.filter(resource=resource).count() == 0
    
    def test_vote_cascade_delete_on_resource_delete(self, user, resource):
        """Test that votes are deleted when resource is deleted."""
        Vote.objects.create(user=user, resource=resource)
        assert Vote.objects.filter(resource=resource).count() == 1
        
        # Delete resource
        resource.delete()
        
        # Vote should be deleted
        assert Vote.objects.filter(user=user).count() == 0
    
    def test_resource_votes_count(self, user, another_user, resource):
        """Test counting votes for a resource."""
        Vote.objects.create(user=user, resource=resource)
        Vote.objects.create(user=another_user, resource=resource)
        
        votes_count = resource.votes.count()
        assert votes_count == 2
