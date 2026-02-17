"""
API integration tests for resources app.

US-05: Explorar Recursos
US-06: Buscar y Filtrar
US-07: Ver Detalle
US-08: Publicar Recurso
"""

import pytest
import hashlib
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.authentication.models import Role
from apps.resources.models import Resource, ResourceVersion

User = get_user_model()


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user with User role."""
    # Create Role if it doesn't exist
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
def sample_resources(user):
    """Create sample resources."""
    resources = []
    
    # Resource 1: Prompt
    r1 = Resource.objects.create(owner=user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=r1,
        version_number='1.0.0',
        title='Test Prompt',
        description='A test prompt',
        type='Prompt',
        tags=['test'],
        content='Prompt content',
        status='Validated',
        is_latest=True
    )
    resources.append(r1)
    
    # Resource 2: Workflow
    r2 = Resource.objects.create(owner=user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=r2,
        version_number='1.0.0',
        title='Test Workflow',
        description='A test workflow',
        type='Workflow',
        tags=['workflow'],
        content='Workflow content',
        status='Sandbox',
        is_latest=True
    )
    resources.append(r2)
    
    return resources


@pytest.mark.django_db
class TestResourceListAPI:
    """Tests for GET /api/resources/"""
    
    def test_list_resources_anonymous(self, api_client, sample_resources):
        """Test anonymous users can list resources."""
        response = api_client.get('/api/resources/')
        
        assert response.status_code == 200
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2
    
    def test_list_resources_pagination(self, api_client, sample_resources):
        """Test pagination."""
        response = api_client.get('/api/resources/?page=1&page_size=1')
        
        assert response.status_code == 200
        assert response.data['count'] == 2
        assert len(response.data['results']) == 1
        assert response.data['has_next'] is True
    
    def test_list_resources_filter_type(self, api_client, sample_resources):
        """Test filtering by type."""
        response = api_client.get('/api/resources/?type=Prompt')
        
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['latest_version']['type'] == 'Prompt'
    
    def test_list_resources_filter_status(self, api_client, sample_resources):
        """Test filtering by status."""
        response = api_client.get('/api/resources/?status=Validated')
        
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['latest_version']['status'] == 'Validated'
    
    def test_list_resources_search(self, api_client, sample_resources):
        """Test text search."""
        response = api_client.get('/api/resources/?search=Workflow')
        
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert 'Workflow' in response.data['results'][0]['latest_version']['title']


@pytest.mark.django_db
class TestResourceDetailAPI:
    """Tests for GET /api/resources/{id}/"""
    
    def test_get_resource_detail(self, api_client, sample_resources):
        """Test getting resource detail."""
        resource_id = sample_resources[0].id
        response = api_client.get(f'/api/resources/{resource_id}/')
        
        assert response.status_code == 200
        assert response.data['id'] == str(resource_id)
        assert response.data['latest_version']['title'] == 'Test Prompt'
    
    def test_get_nonexistent_resource(self, api_client):
        """Test getting nonexistent resource returns 404."""
        import uuid
        fake_id = uuid.uuid4()
        response = api_client.get(f'/api/resources/{fake_id}/')
        
        assert response.status_code == 404
        assert response.data['error_code'] == 'RESOURCE_NOT_FOUND'


@pytest.mark.django_db
class TestResourceCreateAPI:
    """Tests for POST /api/resources/create/"""
    
    def test_create_resource_internal(self, authenticated_client):
        """Test creating an Internal resource."""
        data = {
            'source_type': 'Internal',
            'title': 'My New Prompt',
            'description': 'A new prompt',
            'type': 'Prompt',
            'tags': ['new', 'test'],
            'content': 'This is the content',
            'status': 'Sandbox',
        }
        
        response = authenticated_client.post('/api/resources/create/', data, format='json')
        
        assert response.status_code == 201
        assert response.data['latest_version']['title'] == 'My New Prompt'
        assert response.data['latest_version']['version_number'] == '1.0.0'
        assert response.data['source_type'] == 'Internal'
    
    def test_create_resource_github_linked(self, authenticated_client):
        """Test creating a GitHub-Linked resource."""
        data = {
            'source_type': 'GitHub-Linked',
            'title': 'GitHub Tool',
            'description': 'A tool from GitHub',
            'type': 'Tool',
            'tags': ['github'],
            'repo_url': 'https://github.com/example/repo',
            'license': 'MIT',
            'status': 'Pending Validation',
        }
        
        response = authenticated_client.post('/api/resources/create/', data, format='json')
        
        assert response.status_code == 201
        assert response.data['source_type'] == 'GitHub-Linked'
        assert response.data['latest_version']['repo_url'] == 'https://github.com/example/repo'
    
    def test_create_resource_unauthenticated(self, api_client):
        """Test unauthenticated user cannot create resource."""
        data = {
            'title': 'Test',
            'description': 'Test',
            'type': 'Prompt',
            'content': 'Content',
        }
        
        response = api_client.post('/api/resources/create/', data, format='json')
        
        assert response.status_code == 401
    
    def test_create_resource_internal_without_content(self, authenticated_client):
        """Test Internal resource requires content."""
        data = {
            'source_type': 'Internal',
            'title': 'Test',
            'description': 'Test',
            'type': 'Prompt',
            # Missing content
        }
        
        response = authenticated_client.post('/api/resources/create/', data, format='json')
        
        assert response.status_code == 400
        assert 'content' in response.data['details']
    
    def test_create_resource_github_without_repo(self, authenticated_client):
        """Test GitHub-Linked resource requires repo_url and license."""
        data = {
            'source_type': 'GitHub-Linked',
            'title': 'Test',
            'description': 'Test',
            'type': 'Tool',
            # Missing repo_url and license
        }
        
        response = authenticated_client.post('/api/resources/create/', data, format='json')
        
        assert response.status_code == 400
        assert 'repo_url' in response.data['details'] or 'license' in response.data['details']
