"""
Vote services.

Business logic for voting system.

US-16: Votar Recurso
"""

from django.db import transaction, IntegrityError
from apps.interactions.models import Vote
from apps.resources.models import Resource


class VoteService:
    """Service layer for vote operations."""
    
    @staticmethod
    @transaction.atomic
    def toggle_vote(user, resource_id):
        """
        Toggle vote for a resource.
        
        If user has already voted: remove vote (unvote)
        If user hasn't voted: add vote
        
        Args:
            user (User): The user voting
            resource_id (UUID): The resource ID
        
        Returns:
            dict: {
                'action': 'voted' or 'unvoted',
                'votes_count': int (current total votes)
            }
        
        Raises:
            ValueError: If resource doesn't exist or is soft-deleted
        """
        try:
            resource = Resource.objects.get(id=resource_id, deleted_at__isnull=True)
        except Resource.DoesNotExist:
            raise ValueError('Resource not found or has been deleted')
        
        # Check if user already voted
        existing_vote = Vote.objects.filter(user=user, resource=resource).first()
        
        if existing_vote:
            # Unvote
            existing_vote.delete()
            action = 'unvoted'
        else:
            # Vote
            try:
                Vote.objects.create(user=user, resource=resource)
                action = 'voted'
            except IntegrityError:
                # Race condition: vote was created between check and create
                raise ValueError('Vote already exists')
        
        # Get updated count
        votes_count = resource.votes.count()
        
        return {
            'action': action,
            'votes_count': votes_count,
        }
    
    @staticmethod
    def get_user_voted_resources(user):
        """
        Get list of resource IDs that user has voted for.
        
        Args:
            user (User): The user
        
        Returns:
            set: Set of resource UUIDs
        """
        return set(
            Vote.objects.filter(user=user)
            .values_list('resource_id', flat=True)
        )
    
    @staticmethod
    def has_user_voted(user, resource_id):
        """
        Check if user has voted for a specific resource.
        
        Args:
            user (User): The user
            resource_id (UUID): The resource ID
        
        Returns:
            bool: True if user has voted, False otherwise
        """
        return Vote.objects.filter(user=user, resource_id=resource_id).exists()
