"""
Interaction services (votes and notifications).

Business logic for voting system and notification management.

US-16: Votar Recurso
US-18: Notificaciones In-App
"""

from django.db import transaction, IntegrityError
from django.utils import timezone
from apps.interactions.models import Vote, Notification
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


class NotificationService:
    """Service layer for notification operations."""
    
    @staticmethod
    @transaction.atomic
    def create_notification(user, notification_type, message, resource=None, actor=None):
        """
        Create a notification for a user.
        
        Args:
            user (User): The recipient of the notification
            notification_type (str): Type of notification (resource_validated, resource_forked, etc.)
            message (str): Human-readable message
            resource (Resource, optional): Related resource
            actor (User, optional): User who triggered the notification
        
        Returns:
            Notification: The created notification
        
        US-18: Notificaciones In-App
        """
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            message=message,
            resource=resource,
            actor=actor
        )
        return notification
    
    @staticmethod
    def get_user_notifications(user, unread_only=False):
        """
        Get notifications for a user.
        
        Args:
            user (User): The user
            unread_only (bool): If True, return only unread notifications
        
        Returns:
            QuerySet: Notifications queryset
        
        US-18: Notificaciones In-App
        """
        notifications = Notification.objects.filter(user=user).select_related('resource', 'actor')
        
        if unread_only:
            notifications = notifications.filter(read_at__isnull=True)
        
        return notifications
    
    @staticmethod
    @transaction.atomic
    def mark_as_read(notification_id, user):
        """
        Mark a notification as read.
        
        Args:
            notification_id (UUID): The notification ID
            user (User): The user (must be the owner)
        
        Returns:
            Notification: The updated notification
        
        Raises:
            ValueError: If notification doesn't exist or user is not the owner
        
        US-18: Notificaciones In-App
        """
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
        except Notification.DoesNotExist:
            raise ValueError('Notification not found or access denied')
        
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=['read_at'])
        
        return notification
    
    @staticmethod
    @transaction.atomic
    def mark_all_as_read(user):
        """
        Mark all notifications as read for a user.
        
        Args:
            user (User): The user
        
        Returns:
            int: Number of notifications marked as read
        
        US-18: Notificaciones In-App
        """
        count = Notification.objects.filter(
            user=user,
            read_at__isnull=True
        ).update(read_at=timezone.now())
        
        return count
    
    @staticmethod
    def get_unread_count(user):
        """
        Get count of unread notifications for a user.
        
        Args:
            user (User): The user
        
        Returns:
            int: Count of unread notifications
        
        US-18: Notificaciones In-App
        """
        return Notification.objects.filter(user=user, read_at__isnull=True).count()
