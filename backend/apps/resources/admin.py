from django.contrib import admin
from apps.resources.models import Resource, ResourceVersion


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Admin interface for Resource model."""
    
    list_display = ('id', 'owner', 'source_type', 'forks_count', 'created_at')
    list_filter = ('source_type', 'created_at')
    search_fields = ('id', 'owner__email', 'owner__name')
    raw_id_fields = ('owner', 'derived_from_resource', 'derived_from_version')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(ResourceVersion)
class ResourceVersionAdmin(admin.ModelAdmin):
    """Admin interface for ResourceVersion model."""
    
    list_display = ('id', 'resource', 'version_number', 'title', 'type', 'status', 'is_latest', 'created_at')
    list_filter = ('type', 'status', 'is_latest', 'created_at')
    search_fields = ('title', 'description', 'resource__id')
    raw_id_fields = ('resource',)
    readonly_fields = ('id', 'content_hash', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
