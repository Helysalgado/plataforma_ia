"""
Serializers for resources app.

US-05: Explorar Recursos
US-07: Ver Detalle
US-08: Publicar Recurso
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.resources.models import Resource, ResourceVersion
from apps.authentication.serializers import UserSerializer

User = get_user_model()


class ResourceVersionSerializer(serializers.ModelSerializer):
    """Serializer for ResourceVersion model."""
    
    pid = serializers.CharField(read_only=True)
    
    class Meta:
        model = ResourceVersion
        fields = (
            'id',
            'version_number',
            'title',
            'description',
            'type',
            'tags',
            'content',
            'content_hash',
            'repo_url',
            'repo_tag',
            'repo_commit_sha',
            'license',
            'example',
            'changelog',
            'status',
            'validated_at',
            'is_latest',
            'pid',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'content_hash', 'pid', 'created_at', 'updated_at')


class ResourceListSerializer(serializers.ModelSerializer):
    """
    Serializer for Resource list (with latest version embedded).
    
    US-05: Explorar Recursos
    """
    
    owner = UserSerializer(read_only=True)
    latest_version = ResourceVersionSerializer(read_only=True)
    votes_count = serializers.IntegerField(read_only=True, source='votes_count_annotated')
    
    class Meta:
        model = Resource
        fields = (
            'id',
            'owner',
            'source_type',
            'latest_version',
            'votes_count',
            'forks_count',
            'is_fork',
            'created_at',
        )
        read_only_fields = fields


class ResourceDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Resource detail (with all data).
    
    US-07: Ver Detalle
    """
    
    owner = UserSerializer(read_only=True)
    latest_version = ResourceVersionSerializer(read_only=True)
    votes_count = serializers.IntegerField(read_only=True, source='votes_count_annotated')
    derived_from_resource_id = serializers.UUIDField(read_only=True)
    derived_from_version_id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = Resource
        fields = (
            'id',
            'owner',
            'source_type',
            'latest_version',
            'votes_count',
            'forks_count',
            'is_fork',
            'derived_from_resource_id',
            'derived_from_version_id',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class CreateResourceSerializer(serializers.Serializer):
    """
    Serializer for creating a new resource.
    
    US-08: Publicar Recurso
    """
    
    # Metadata
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    type = serializers.ChoiceField(choices=['Prompt', 'Workflow', 'Notebook', 'Dataset', 'Tool', 'Other'])
    tags = serializers.ListField(child=serializers.CharField(), default=list)
    
    # Source
    source_type = serializers.ChoiceField(choices=['Internal', 'GitHub-Linked'], default='Internal')
    
    # Internal content
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # GitHub-Linked content
    repo_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    repo_tag = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    license = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # Optional
    example = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(
        choices=['Sandbox', 'Pending Validation'],
        default='Sandbox'
    )
    
    def validate(self, data):
        """Cross-field validation."""
        source_type = data.get('source_type', 'Internal')
        
        # Internal: content is required
        if source_type == 'Internal':
            if not data.get('content'):
                raise serializers.ValidationError({
                    'content': 'Content is required for Internal resources'
                })
        
        # GitHub-Linked: repo_url and license are required
        if source_type == 'GitHub-Linked':
            if not data.get('repo_url'):
                raise serializers.ValidationError({
                    'repo_url': 'Repository URL is required for GitHub-Linked resources'
                })
            if not data.get('license'):
                raise serializers.ValidationError({
                    'license': 'License is required for GitHub-Linked resources'
                })
        
        return data


class ValidateResourceSerializer(serializers.Serializer):
    """
    Serializer for validate resource response.
    
    US-13: Validar Recurso (Admin)
    """
    
    message = serializers.CharField()
    resource_id = serializers.UUIDField()
    status = serializers.CharField()
    validated_at = serializers.DateTimeField()


class ForkResourceSerializer(serializers.Serializer):
    """
    Serializer for fork resource response.
    
    US-17: Reutilizar Recurso (Fork)
    """
    
    message = serializers.CharField()
    forked_resource_id = serializers.UUIDField()
    original_resource_id = serializers.UUIDField()
    derived_from_version = serializers.CharField()


class VersionHistorySerializer(serializers.Serializer):
    """
    Serializer for version history list.
    
    US-22: Historial de Versiones
    """
    
    id = serializers.UUIDField()
    version_number = serializers.CharField()
    title = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    validated_at = serializers.DateTimeField(allow_null=True)
    is_latest = serializers.BooleanField()
    
    # Summary fields (not full content)
    type = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField())
    
    # PID
    pid = serializers.CharField()
