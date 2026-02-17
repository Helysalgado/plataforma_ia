"""
Resource and ResourceVersion models.

Based on:
- /docs/data/DATA_MODEL.md (sections 3.4 and 3.5)
- /docs/architecture/ADR-002-versioning.md

US-05: Explorar Recursos
US-06: Buscar y Filtrar
US-07: Ver Detalle
US-08: Publicar Recurso
"""

import uuid
import hashlib
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

User = get_user_model()


class Resource(models.Model):
    """
    Resource model (wrapper for versions).
    
    A Resource is a container for multiple versions.
    The actual content lives in ResourceVersion.
    """
    
    SOURCE_TYPE_CHOICES = [
        ('Internal', 'Internal'),
        ('GitHub-Linked', 'GitHub-Linked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name=_('owner')
    )
    source_type = models.CharField(
        _('source type'),
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default='Internal'
    )
    
    # Fork/derivation tracking
    derived_from_resource = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forks',
        verbose_name=_('derived from resource')
    )
    derived_from_version = models.ForeignKey(
        'ResourceVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_resources',
        verbose_name=_('derived from version')
    )
    
    # Denormalized metrics (for performance)
    forks_count = models.IntegerField(_('forks count'), default=0)
    
    # Soft delete
    deleted_at = models.DateTimeField(_('deleted at'), null=True, blank=True, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'resources'
        verbose_name = _('resource')
        verbose_name_plural = _('resources')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        latest = self.latest_version
        return f"{latest.title if latest else 'Untitled'} (by {self.owner.name})"
    
    @property
    def latest_version(self):
        """Get the latest version of this resource."""
        return self.versions.filter(is_latest=True).first()
    
    @property
    def votes_count(self):
        """Count of votes (computed). Placeholder until Vote model exists."""
        # TODO: Re-enable when Vote model exists (US-16)
        # return self.votes.count()
        return 0
    
    @property
    def is_fork(self):
        """Check if this resource is a fork."""
        return self.derived_from_resource_id is not None


class ResourceVersion(models.Model):
    """
    ResourceVersion model (versionable content).
    
    Contains the actual content of a resource at a specific version.
    Implements hybrid snapshot versioning (ADR-002).
    """
    
    TYPE_CHOICES = [
        ('Prompt', 'Prompt'),
        ('Workflow', 'Workflow'),
        ('Notebook', 'Notebook'),
        ('Dataset', 'Dataset'),
        ('Tool', 'Tool'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('Sandbox', 'Sandbox'),
        ('Pending Validation', 'Pending Validation'),
        ('Validated', 'Validated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name=_('resource')
    )
    
    # Version info
    version_number = models.CharField(
        _('version number'),
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d+\.\d+\.\d+$',
                message='Version must be in format MAJOR.MINOR.PATCH (e.g., 1.0.0)'
            )
        ]
    )
    
    # Metadata
    title = models.CharField(_('title'), max_length=200, db_index=True)
    description = models.TextField(_('description'))
    type = models.CharField(_('type'), max_length=50, choices=TYPE_CHOICES)
    tags = models.JSONField(_('tags'), default=list, blank=True)
    
    # Content (Internal)
    content = models.TextField(_('content'), null=True, blank=True)
    content_hash = models.CharField(_('content hash'), max_length=64, null=True, blank=True)
    
    # GitHub-Linked metadata
    repo_url = models.URLField(_('repository URL'), max_length=500, null=True, blank=True)
    repo_tag = models.CharField(_('repository tag'), max_length=100, null=True, blank=True)
    repo_commit_sha = models.CharField(_('commit SHA'), max_length=40, null=True, blank=True)
    license = models.CharField(_('license'), max_length=50, null=True, blank=True)
    
    # Usage example and changelog
    example = models.TextField(_('example'), null=True, blank=True)
    changelog = models.TextField(_('changelog'), null=True, blank=True)
    
    # Validation status
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='Sandbox',
        db_index=True
    )
    validated_at = models.DateTimeField(_('validated at'), null=True, blank=True, db_index=True)
    
    # Version tracking
    is_latest = models.BooleanField(_('is latest'), default=True, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'resource_versions'
        verbose_name = _('resource version')
        verbose_name_plural = _('resource versions')
        ordering = ['-created_at']
        unique_together = ('resource', 'version_number')
        indexes = [
            models.Index(fields=['resource', '-created_at']),
            models.Index(fields=['resource', 'is_latest']),
            models.Index(fields=['status']),
            models.Index(fields=['-validated_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} v{self.version_number} ({self.status})"
    
    @property
    def pid(self):
        """Generate Persistent Identifier (PID)."""
        return f"ccg-ai:R-{self.resource_id}@v{self.version_number}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate content_hash for Internal resources."""
        if self.resource.source_type == 'Internal' and self.content:
            self.content_hash = hashlib.sha256(self.content.encode('utf-8')).hexdigest()
        
        super().save(*args, **kwargs)
