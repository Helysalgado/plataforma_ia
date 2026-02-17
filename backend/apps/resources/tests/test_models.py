"""
Tests for Resource and ResourceVersion models.

US-05: Explorar Recursos
US-08: Publicar Recurso
"""

import pytest
import hashlib
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.resources.models import Resource, ResourceVersion

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user('owner@example.com', 'Owner User', 'pass123')


@pytest.fixture
def resource(user):
    """Create a test resource."""
    return Resource.objects.create(owner=user, source_type='Internal')


@pytest.mark.django_db
class TestResourceModel:
    """Tests for Resource model."""
    
    def test_create_resource(self, user):
        """Test creating a resource."""
        resource = Resource.objects.create(
            owner=user,
            source_type='Internal'
        )
        
        assert resource.id is not None
        assert resource.owner == user
        assert resource.source_type == 'Internal'
        assert resource.forks_count == 0
        assert resource.deleted_at is None
        assert resource.created_at is not None
    
    def test_resource_latest_version_property(self, resource):
        """Test latest_version property returns correct version."""
        # Create multiple versions
        v1 = ResourceVersion.objects.create(
            resource=resource,
            version_number='1.0.0',
            title='Version 1',
            description='First version',
            type='Prompt',
            content='Content v1',
            is_latest=False
        )
        v2 = ResourceVersion.objects.create(
            resource=resource,
            version_number='1.1.0',
            title='Version 2',
            description='Second version',
            type='Prompt',
            content='Content v2',
            is_latest=True
        )
        
        assert resource.latest_version.id == v2.id
        assert resource.latest_version.version_number == '1.1.0'
    
    def test_resource_votes_count_property(self, resource):
        """Test votes_count property."""
        # TODO: Update when Vote model is implemented (US-16)
        # Initially 0
        assert resource.votes_count == 0
    
    def test_resource_is_fork_property(self, user):
        """Test is_fork property."""
        # Original resource
        original = Resource.objects.create(owner=user, source_type='Internal')
        assert original.is_fork is False
        
        # Forked resource
        fork = Resource.objects.create(
            owner=user,
            source_type='Internal',
            derived_from_resource=original
        )
        assert fork.is_fork is True
    
    def test_resource_soft_delete(self, resource):
        """Test soft delete functionality."""
        assert resource.deleted_at is None
        
        # Soft delete
        resource.deleted_at = timezone.now()
        resource.save()
        
        assert resource.deleted_at is not None


@pytest.mark.django_db
class TestResourceVersionModel:
    """Tests for ResourceVersion model."""
    
    def test_create_version(self, resource):
        """Test creating a resource version."""
        version = ResourceVersion.objects.create(
            resource=resource,
            version_number='1.0.0',
            title='Test Resource',
            description='Test description',
            type='Prompt',
            tags=['test', 'prompt'],
            content='This is the content',
            status='Sandbox',
            is_latest=True
        )
        
        assert version.id is not None
        assert version.resource == resource
        assert version.version_number == '1.0.0'
        assert version.title == 'Test Resource'
        assert version.type == 'Prompt'
        assert version.tags == ['test', 'prompt']
        assert version.status == 'Sandbox'
        assert version.is_latest is True
        assert version.content_hash is not None  # Auto-generated
    
    def test_version_number_validation(self, resource):
        """Test version_number must follow semantic versioning."""
        # Valid versions
        valid_versions = ['1.0.0', '1.2.3', '10.20.30']
        for version in valid_versions:
            v = ResourceVersion(
                resource=resource,
                version_number=version,
                title='Test',
                description='Test',
                type='Prompt',
                tags=[]  # Required field
            )
            v.full_clean()  # Should not raise
        
        # Invalid versions
        invalid_versions = ['1.0', '1', 'v1.0.0', '1.0.0-beta']
        for version in invalid_versions:
            v = ResourceVersion(
                resource=resource,
                version_number=version,
                title='Test',
                description='Test',
                type='Prompt',
                tags=[]  # Required field
            )
            with pytest.raises(ValidationError):
                v.full_clean()
    
    def test_content_hash_auto_generated(self, resource):
        """Test content_hash is auto-generated on save for Internal resources."""
        version = ResourceVersion.objects.create(
            resource=resource,
            version_number='1.0.0',
            title='Test',
            description='Test',
            type='Prompt',
            content='Test content'
        )
        
        assert version.content_hash is not None
        assert len(version.content_hash) == 64  # SHA256 hex length
        
        # Verify hash is correct
        expected_hash = hashlib.sha256('Test content'.encode('utf-8')).hexdigest()
        assert version.content_hash == expected_hash
    
    def test_pid_property(self, resource):
        """Test PID (Persistent Identifier) generation."""
        version = ResourceVersion.objects.create(
            resource=resource,
            version_number='1.2.3',
            title='Test',
            description='Test',
            type='Prompt'
        )
        
        expected_pid = f"ccg-ai:R-{resource.id}@v1.2.3"
        assert version.pid == expected_pid
    
    def test_unique_version_per_resource(self, resource):
        """Test that version_number must be unique per resource."""
        from django.db import IntegrityError
        
        ResourceVersion.objects.create(
            resource=resource,
            version_number='1.0.0',
            title='Test',
            description='Test',
            type='Prompt'
        )
        
        # Try to create duplicate version
        with pytest.raises(IntegrityError):
            ResourceVersion.objects.create(
                resource=resource,
                version_number='1.0.0',  # Duplicate
                title='Test 2',
                description='Test',
                type='Prompt'
            )
    
    def test_version_status_choices(self, resource):
        """Test status field accepts only valid choices."""
        valid_statuses = ['Sandbox', 'Pending Validation', 'Validated']
        
        for status in valid_statuses:
            v = ResourceVersion.objects.create(
                resource=resource,
                version_number=f'1.0.{valid_statuses.index(status)}',
                title='Test',
                description='Test',
                type='Prompt',
                status=status
            )
            assert v.status == status
    
    def test_version_type_choices(self, resource):
        """Test type field accepts only valid choices."""
        valid_types = ['Prompt', 'Workflow', 'Notebook', 'Dataset', 'Tool', 'Other']
        
        for idx, resource_type in enumerate(valid_types):
            v = ResourceVersion.objects.create(
                resource=resource,
                version_number=f'1.{idx}.0',
                title='Test',
                description='Test',
                type=resource_type
            )
            assert v.type == resource_type
