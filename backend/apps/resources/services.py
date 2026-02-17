"""
Resource services.

Business logic for resource management, publishing, listing, etc.

US-05: Explorar Recursos
US-06: Buscar y Filtrar
US-08: Publicar Recurso
US-13: Validar Recurso (Admin)
"""

from django.db import transaction, IntegrityError
from django.db.models import Q, Count, Prefetch
from django.contrib.auth import get_user_model
from django.utils import timezone
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
        
        # Annotate with votes count
        queryset = queryset.annotate(votes_count_annotated=Count('votes'))
        
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
    
    @staticmethod
    @transaction.atomic
    def validate_resource(admin_user, resource_id):
        """
        Validate a resource (change status to Validated).
        
        Only Admin users can validate resources.
        Updates latest_version.status = 'Validated' and sets validated_at.
        
        Args:
            admin_user (User): The admin performing validation
            resource_id (UUID): The resource ID
        
        Returns:
            Resource: The validated resource
        
        Raises:
            ValueError: If resource doesn't exist, is deleted, or user is not admin
        
        US-13: Validar Recurso (Admin)
        """
        # Check admin permission
        if not admin_user.is_admin:
            raise ValueError('Only administrators can validate resources')
        
        # Get resource
        try:
            resource = Resource.objects.select_for_update().get(
                id=resource_id,
                deleted_at__isnull=True
            )
        except Resource.DoesNotExist:
            raise ValueError('Resource not found or has been deleted')
        
        # Get latest version
        latest_version = resource.latest_version
        if not latest_version:
            raise ValueError('Resource has no versions')
        
        # Check if already validated
        if latest_version.status == 'Validated':
            raise ValueError('Resource is already validated')
        
        # Update status
        latest_version.status = 'Validated'
        latest_version.validated_at = timezone.now()
        latest_version.save(update_fields=['status', 'validated_at', 'updated_at'])
        
        # TODO: Create notification for owner (US-18)
        # from apps.notifications.services import NotificationService
        # NotificationService.create_notification(
        #     user=resource.owner,
        #     type='resource_validated',
        #     resource=resource
        # )
        
        return resource
    
    @staticmethod
    @transaction.atomic
    def fork_resource(user, resource_id):
        """
        Fork (reutilizar) a resource.
        
        Creates a new resource derived from the original:
        - Copies latest version content
        - Sets derived_from_resource_id and derived_from_version_id
        - Increments forks_count on original
        - New resource owned by user
        - New version starts at v1.0.0
        
        Args:
            user (User): The user forking the resource
            resource_id (UUID): The resource ID to fork
        
        Returns:
            Resource: The forked (new) resource
        
        Raises:
            ValueError: If resource doesn't exist, is deleted, or has no versions
        
        US-17: Reutilizar Recurso (Fork)
        """
        # Get original resource with lock (will increment forks_count)
        try:
            original_resource = Resource.objects.select_for_update().get(
                id=resource_id,
                deleted_at__isnull=True
            )
        except Resource.DoesNotExist:
            raise ValueError('Resource not found or has been deleted')
        
        # Get latest version
        latest_version = original_resource.latest_version
        if not latest_version:
            raise ValueError('Resource has no versions to fork')
        
        # Create forked resource
        forked_resource = Resource.objects.create(
            owner=user,
            source_type='Internal',  # Forks are always Internal
            derived_from_resource=original_resource,
            derived_from_version=latest_version,
        )
        
        # Copy latest version as v1.0.0
        ResourceVersion.objects.create(
            resource=forked_resource,
            version_number='1.0.0',
            title=f"{latest_version.title} (Fork)",
            description=latest_version.description,
            type=latest_version.type,
            tags=latest_version.tags.copy() if latest_version.tags else [],
            content=latest_version.content,
            # GitHub fields not copied (fork becomes Internal)
            example=latest_version.example,
            status='Sandbox',  # Forks start in Sandbox
            is_latest=True,
        )
        
        # Increment forks_count on original
        original_resource.forks_count += 1
        original_resource.save(update_fields=['forks_count', 'updated_at'])
        
        return forked_resource
    
    @staticmethod
    def get_version_history(resource_id):
        """
        Get version history for a resource.
        
        Returns all versions ordered by creation date (newest first).
        Includes metadata for each version (author, date, status, changes).
        
        Args:
            resource_id (UUID): The resource ID
        
        Returns:
            QuerySet: ResourceVersion queryset
        
        Raises:
            ValueError: If resource doesn't exist or is deleted
        
        US-22: Historial de Versiones
        """
        try:
            resource = Resource.objects.get(
                id=resource_id,
                deleted_at__isnull=True
            )
        except Resource.DoesNotExist:
            raise ValueError('Resource not found or has been deleted')
        
        # Return all versions ordered by created_at (newest first)
        return resource.versions.select_related('resource__owner').order_by('-created_at')

