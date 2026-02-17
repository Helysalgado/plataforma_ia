"""
API tests for notifications.

US-18: Notificaciones In-App
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from apps.authentication.models import Role
from apps.interactions.services import NotificationService
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
        description='Test',
        type='Prompt',
        content='Content',
        is_latest=True
    )
    return resource


@pytest.mark.django_db
class TestNotificationAPI:
    """Tests for notification endpoints"""
    
    def test_list_notifications(self, authenticated_client, user, resource):
        """Test GET /api/notifications/"""
        # Create notifications
        NotificationService.create_notification(
            user=user,
            notification_type='resource_validated',
            message='Test notification',
            resource=resource
        )
        
        response = authenticated_client.get('/api/notifications/')
        
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['unread_count'] == 1
        assert len(response.data['notifications']) == 1
    
    def test_list_notifications_unauthenticated(self, api_client):
        """Test unauthenticated access returns 401."""
        response = api_client.get('/api/notifications/')
        
        assert response.status_code == 401
    
    def test_mark_notification_as_read(self, authenticated_client, user, resource):
        """Test PATCH /api/notifications/{id}/read/"""
        notification = NotificationService.create_notification(
            user=user,
            notification_type='resource_validated',
            message='Test',
            resource=resource
        )
        
        response = authenticated_client.patch(f'/api/notifications/{notification.id}/read/')
        
        assert response.status_code == 200
        assert response.data['is_read'] is True
        assert response.data['read_at'] is not None
    
    def test_mark_all_as_read(self, authenticated_client, user, resource):
        """Test POST /api/notifications/mark-all-read/"""
        # Create 3 notifications
        for i in range(3):
            NotificationService.create_notification(
                user=user,
                notification_type='resource_validated',
                message=f'Test {i}',
                resource=resource
            )
        
        response = authenticated_client.post('/api/notifications/mark-all-read/')
        
        assert response.status_code == 200
        assert response.data['count'] == 3
    
    def test_get_unread_count(self, authenticated_client, user, resource):
        """Test GET /api/notifications/unread-count/"""
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
        
        response = authenticated_client.get('/api/notifications/unread-count/')
        
        assert response.status_code == 200
        assert response.data['unread_count'] == 2
