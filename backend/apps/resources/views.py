"""
API views for resources app.

US-05: Explorar Recursos
US-06: Buscar y Filtrar
US-07: Ver Detalle
US-08: Publicar Recurso
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Count

from apps.resources.models import Resource, ResourceVersion
from apps.resources.services import ResourceService
from apps.resources.serializers import (
    ResourceListSerializer,
    ResourceDetailSerializer,
    CreateResourceSerializer,
)


class ResourceListView(APIView):
    """
    List resources with pagination, search and filters.
    
    GET /api/resources/
    
    Query params:
        - page (int): Page number (default: 1)
        - page_size (int): Items per page (default: 20, max: 100)
        - search (str): Text search
        - type (str): Filter by type (Prompt, Workflow, etc.)
        - status (str): Filter by status (Sandbox, Validated, etc.)
        - tags (str): Comma-separated tags
        - ordering (str): -created_at, created_at, -votes
    
    US-05: Explorar Recursos
    US-06: Buscar y Filtrar
    """
    
    permission_classes = [AllowAny]  # Anonymous users can browse
    
    def get(self, request):
        # Parse query params
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        search = request.query_params.get('search', '').strip()
        ordering = request.query_params.get('ordering', '-created_at')
        
        # Filters
        filters = {}
        if request.query_params.get('type'):
            filters['type'] = request.query_params.get('type')
        if request.query_params.get('status'):
            filters['status'] = request.query_params.get('status')
        if request.query_params.get('tags'):
            filters['tags'] = request.query_params.get('tags').split(',')
        
        # Call service
        result = ResourceService.list_resources(
            filters=filters,
            search=search if search else None,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )
        
        # Serialize results
        # Annotate votes_count for each resource
        resource_ids = [r.id for r in result['results']]
        votes_counts = dict(
            Resource.objects.filter(id__in=resource_ids)
            .annotate(votes_count_annotated=Count('votes'))
            .values_list('id', 'votes_count_annotated')
        )
        
        # Attach votes_count to each resource
        for resource in result['results']:
            resource.votes_count_annotated = votes_counts.get(resource.id, 0)
        
        serializer = ResourceListSerializer(result['results'], many=True)
        
        return Response({
            'results': serializer.data,
            'count': result['count'],
            'page': result['page'],
            'page_size': result['page_size'],
            'has_next': result['has_next'],
            'has_previous': result['has_previous'],
        })


class ResourceDetailView(APIView):
    """
    Get resource detail by ID.
    
    GET /api/resources/{id}/
    
    US-07: Ver Detalle
    """
    
    permission_classes = [AllowAny]  # Anonymous users can view
    
    def get(self, request, resource_id):
        try:
            resource = Resource.objects.prefetch_related(
                'versions',
                'owner',
                'owner__roles'
            ).annotate(
                votes_count_annotated=Count('votes')
            ).get(id=resource_id, deleted_at__isnull=True)
        except Resource.DoesNotExist:
            return Response(
                {'error': 'Resource not found', 'error_code': 'RESOURCE_NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ResourceDetailSerializer(resource)
        return Response(serializer.data)


class ResourceCreateView(APIView):
    """
    Create a new resource.
    
    POST /api/resources/
    
    US-08: Publicar Recurso
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreateResourceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Validation error',
                    'error_code': 'VALIDATION_ERROR',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resource = ResourceService.create_resource(
                owner=request.user,
                data=serializer.validated_data
            )
            
            # Serialize response
            resource = Resource.objects.prefetch_related(
                'versions',
                'owner',
                'owner__roles'
            ).annotate(
                votes_count_annotated=Count('votes')
            ).get(id=resource.id)
            
            detail_serializer = ResourceDetailSerializer(resource)
            
            return Response(
                detail_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except ValueError as e:
            return Response(
                {'error': str(e), 'error_code': 'BUSINESS_ERROR'},
                status=status.HTTP_400_BAD_REQUEST
            )
