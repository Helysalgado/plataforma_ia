"""
Tests for Resource services.

US-05: Explorar Recursos
US-06: Buscar y Filtrar
US-08: Publicar Recurso
"""

import pytest
from django.contrib.auth import get_user_model
from apps.resources.models import Resource, ResourceVersion
from apps.resources.services import ResourceService

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user('owner@example.com', 'Owner User', 'pass123')


@pytest.fixture
def sample_resources(user):
    """Create sample resources for testing."""
    resources = []
    
    # Resource 1: Prompt, Sandbox
    r1 = Resource.objects.create(owner=user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=r1,
        version_number='1.0.0',
        title='Test Prompt',
        description='A test prompt',
        type='Prompt',
        tags=['test', 'prompt'],
        content='This is a prompt',
        status='Sandbox',
        is_latest=True
    )
    resources.append(r1)
    
    # Resource 2: Workflow, Validated
    r2 = Resource.objects.create(owner=user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=r2,
        version_number='1.0.0',
        title='Test Workflow',
        description='A test workflow',
        type='Workflow',
        tags=['test', 'workflow'],
        content='This is a workflow',
        status='Validated',
        is_latest=True
    )
    resources.append(r2)
    
    # Resource 3: Dataset, Pending
    r3 = Resource.objects.create(owner=user, source_type='Internal')
    ResourceVersion.objects.create(
        resource=r3,
        version_number='1.0.0',
        title='Test Dataset',
        description='A test dataset',
        type='Dataset',
        tags=['test', 'dataset'],
        content='This is a dataset',
        status='Pending Validation',
        is_latest=True
    )
    resources.append(r3)
    
    return resources


@pytest.mark.django_db
class TestResourceService:
    """Tests for ResourceService."""
    
    def test_list_resources_basic(self, sample_resources):
        """Test basic listing of resources."""
        result = ResourceService.list_resources()
        
        assert result['count'] == 3
        assert len(result['results']) == 3
        assert result['page'] == 1
        assert result['has_next'] is False
        assert result['has_previous'] is False
    
    def test_list_resources_pagination(self, sample_resources):
        """Test pagination."""
        # Page 1 (2 items)
        result = ResourceService.list_resources(page=1, page_size=2)
        assert result['count'] == 3
        assert len(result['results']) == 2
        assert result['has_next'] is True
        assert result['has_previous'] is False
        
        # Page 2 (1 item)
        result = ResourceService.list_resources(page=2, page_size=2)
        assert result['count'] == 3
        assert len(result['results']) == 1
        assert result['has_next'] is False
        assert result['has_previous'] is True
    
    def test_list_resources_filter_by_type(self, sample_resources):
        """Test filtering by type."""
        result = ResourceService.list_resources(filters={'type': 'Prompt'})
        
        assert result['count'] == 1
        assert result['results'][0].latest_version.type == 'Prompt'
    
    def test_list_resources_filter_by_status(self, sample_resources):
        """Test filtering by status."""
        result = ResourceService.list_resources(filters={'status': 'Validated'})
        
        assert result['count'] == 1
        assert result['results'][0].latest_version.status == 'Validated'
    
    def test_list_resources_filter_by_tags(self, sample_resources):
        """Test filtering by tags."""
        result = ResourceService.list_resources(filters={'tags': ['workflow']})
        
        assert result['count'] == 1
        assert 'workflow' in result['results'][0].latest_version.tags
    
    def test_list_resources_search(self, sample_resources):
        """Test text search."""
        result = ResourceService.list_resources(search='workflow')
        
        assert result['count'] == 1
        assert 'Workflow' in result['results'][0].latest_version.title
    
    def test_list_resources_ordering(self, sample_resources):
        """Test ordering."""
        # Default: -created_at
        result = ResourceService.list_resources(ordering='-created_at')
        assert result['results'][0].latest_version.title == 'Test Dataset'  # Last created
        
        # Oldest first
        result = ResourceService.list_resources(ordering='created_at')
        assert result['results'][0].latest_version.title == 'Test Prompt'  # First created
    
    def test_create_resource_internal(self, user):
        """Test creating an Internal resource."""
        data = {
            'source_type': 'Internal',
            'title': 'New Prompt',
            'description': 'A new prompt resource',
            'type': 'Prompt',
            'tags': ['new', 'test'],
            'content': 'This is the content',
            'status': 'Sandbox',
        }
        
        resource = ResourceService.create_resource(owner=user, data=data)
        
        assert resource.id is not None
        assert resource.owner == user
        assert resource.source_type == 'Internal'
        
        # Check version
        version = resource.latest_version
        assert version.version_number == '1.0.0'
        assert version.title == 'New Prompt'
        assert version.type == 'Prompt'
        assert version.tags == ['new', 'test']
        assert version.content == 'This is the content'
        assert version.is_latest is True
    
    def test_create_resource_github_linked(self, user):
        """Test creating a GitHub-Linked resource."""
        data = {
            'source_type': 'GitHub-Linked',
            'title': 'GitHub Resource',
            'description': 'A GitHub resource',
            'type': 'Tool',
            'tags': ['github'],
            'repo_url': 'https://github.com/example/repo',
            'repo_tag': 'v1.0.0',
            'license': 'MIT',
            'status': 'Pending Validation',
        }
        
        resource = ResourceService.create_resource(owner=user, data=data)
        
        assert resource.source_type == 'GitHub-Linked'
        
        # Check version
        version = resource.latest_version
        assert version.repo_url == 'https://github.com/example/repo'
        assert version.repo_tag == 'v1.0.0'
        assert version.license == 'MIT'
