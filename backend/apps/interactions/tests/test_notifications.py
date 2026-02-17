"""
Tests for notification services.

US-18: Notificaciones In-App
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.interactions.models import Notification
from apps.interactions.services import NotificationService
from apps.resources.models import Resource, ResourceVersion

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user('user@example.com', 'Test User', 'pass123')


@pytest.fixture
def actor():
    """Create actor user."""
    return User.objects.create_user('actor@example.com', 'Actor User', 'pass123')


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
        content='Content',
        is_latest=True
    )
    return resource


@pytest.mark.django_db
class TestNotificationService:
    """Tests for NotificationService"""
    
    def test_create_notification(self, user, resource, actor):
        """Test creating a notification."""
        notification = NotificationService.create_notification(
            user=user,
            notification_type='resource_validated',
            message='Your resource was validated',
            resource=resource,
            actor=actor
        )
        
        assert notification.user == user
        assert notification.type == 'resource_validated'
        assert notification.message == 'Your resource was validated'
        assert notification.resource == resource
        assert notification.actor == actor
        assert notification.is_read is False
    
    def test_get_user_notifications(self, user, resource):
        """Test getting user notifications."""
        # Create 2 notifications
        NotificationService.create_notification(
            user=user,
            notification_type='resource_validated',
            message='Test 1',
            resource=resource
        )
        NotificationService.create_notification(
            user=user,
            notification_type='resource_forked',
            message='Test 2',
            resource=resource
        )
        
        notifications = NotificationService.get_user_notifications(user)
        assert notifications.count() == 2
    
    def test_mark_as_read(self, user, resource):
        """Test marking notification as read."""
        notification = NotificationService.create_notification(
            user=user,
            notification_type='resource_validated',
            message='Test',
            resource=resource
        )
        
        assert notification.is_read is False
        
        updated = NotificationService.mark_as_read(notification.id, user)
        
        assert updated.is_read is True
        assert updated.read_at is not None
    
    def test_mark_all_as_read(self, user, resource):
        """Test marking all notifications as read."""
        # Create 3 unread notifications
        for i in range(3):
            NotificationService.create_notification(
                user=user,
                notification_type='resource_validated',
                message=f'Test {i}',
                resource=resource
            )
        
        count = NotificationService.mark_all_as_read(user)
        
        assert count == 3
        
        unread = NotificationService.get_unread_count(user)
        assert unread == 0
    
    def test_get_unread_count(self, user, resource):
        """Test getting unread count."""
        # Create 2 unread, 1 read
        NotificationService.create_notification(
            user=user,
            notification_type='resource_validated',
            message='Unread 1',
            resource=resource
        )
        NotificationService.create_notification(
            user=user,
            notification_type='resource_forked',
            message='Unread 2',
            resource=resource
        )
        
        notification = NotificationService.create_notification(
            user=user,
            notification_type='resource_validated',
            message='Read',
            resource=resource
        )
        NotificationService.mark_as_read(notification.id, user)
        
        unread_count = NotificationService.get_unread_count(user)
        assert unread_count == 2
