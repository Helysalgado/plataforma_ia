"""
Resource services.

Business logic for resource management, publishing, listing, etc.

US-05: Explorar Recursos
US-06: Buscar y Filtrar
US-08: Publicar Recurso
"""

from django.db import transaction
from django.db.models import Q, Count, Prefetch
from django.contrib.auth import get_user_model
from apps.resources.models import Resource, ResourceVersion

User = get_user_model()


class ResourceService:
    """Service layer for resource operations."""
    
    @staticmethod
    def list_resources(filters=None, search=None, ordering='-created_at', page=1, page_size=20):
        """
        List resources with pagination, search and filters.
        
        Args:
            filters (dict): Filters (type, status, tags)
            search (str): Text search (title, description)
            ordering (str): Order by field (default: -created_at)
            page (int): Page number (1-indexed)
            page_size (int): Items per page
        
        Returns:
            dict: {
                'results': List of resources,
                'count': Total count,
                'page': Current page,
                'page_size': Items per page,
                'has_next': Boolean,
                'has_previous': Boolean
            }
        """
        filters = filters or {}
        
        # Base queryset (exclude soft-deleted)
        queryset = Resource.objects.filter(deleted_at__isnull=True)
        
        # Prefetch latest version for each resource
        latest_versions = Prefetch(
            'versions',
            queryset=ResourceVersion.objects.filter(is_latest=True),
            to_attr='latest_version_list'
        )
        queryset = queryset.prefetch_related(latest_versions, 'owner', 'owner__roles')
        
    # Annotate with votes count (skip if Vote model doesn't exist yet)
        # queryset = queryset.annotate(votes_count_annotated=Count('votes'))
        
        # Apply filters on latest version
        if 'type' in filters:
            queryset = queryset.filter(versions__is_latest=True, versions__type=filters['type'])
        
        if 'status' in filters:
            queryset = queryset.filter(versions__is_latest=True, versions__status=filters['status'])
        
        if 'tags' in filters:
            # JSONB contains check (PostgreSQL)
            tags = filters['tags'] if isinstance(filters['tags'], list) else [filters['tags']]
            queryset = queryset.filter(versions__is_latest=True, versions__tags__contains=tags)
        
        # Text search (title or description in latest version)
        if search:
            queryset = queryset.filter(
                Q(versions__is_latest=True) &
                (Q(versions__title__icontains=search) | Q(versions__description__icontains=search))
            )
        
        # Ensure distinct (due to joins on versions)
        queryset = queryset.distinct()
        
        # Ordering
        if ordering == '-created_at':
            queryset = queryset.order_by('-created_at')
        elif ordering == 'created_at':
            queryset = queryset.order_by('created_at')
        elif ordering == '-votes':
            queryset = queryset.order_by('-votes_count_annotated')
        
        # Count total
        total_count = queryset.count()
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])
        
        return {
            'results': results,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': end < total_count,
            'has_previous': page > 1,
        }
    
    @staticmethod
    @transaction.atomic
    def create_resource(owner, data):
        """
        Create a new resource with initial version v1.0.0.
        
        Args:
            owner (User): Resource owner
            data (dict): Resource data (title, description, type, etc.)
        
        Returns:
            Resource: Created resource with v1.0.0
        
        US-08: Publicar Recurso
        """
        # Create Resource wrapper
        resource = Resource.objects.create(
            owner=owner,
            source_type=data.get('source_type', 'Internal')
        )
        
        # Create initial version (v1.0.0)
        version = ResourceVersion.objects.create(
            resource=resource,
            version_number='1.0.0',
            title=data['title'],
            description=data['description'],
            type=data['type'],
            tags=data.get('tags', []),
            content=data.get('content'),
            repo_url=data.get('repo_url'),
            repo_tag=data.get('repo_tag'),
            license=data.get('license'),
            example=data.get('example'),
            status=data.get('status', 'Sandbox'),
            is_latest=True
        )
        
        return resource
