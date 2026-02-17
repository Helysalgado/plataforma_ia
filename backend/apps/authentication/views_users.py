"""User profile views"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum

from apps.authentication.models import User
from apps.authentication.serializers import UserSerializer
from apps.resources.models import Resource
from apps.resources.serializers import ResourceListSerializer


class UserDetailView(APIView):
    """
    Get user profile information
    
    - Public endpoint (no auth required)
    - Returns user basic info + metrics
    - Used for profile pages
    """
    permission_classes = [AllowAny]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id, is_active=True)
        
        # Get user metrics
        resources = Resource.objects.filter(owner=user, deleted_at__isnull=True)
        
        total_resources = resources.count()
        validated_resources = resources.filter(
            latest_version__status='Validated'
        ).count()
        
        # Total votes received across all user's resources
        total_votes = resources.aggregate(
            total=Sum('vote_count')
        )['total'] or 0
        
        # Total reuses (forks) received
        total_reuses = resources.aggregate(
            total=Sum('reuse_count')
        )['total'] or 0
        
        # Calculate impact (simple formula for MVP)
        # Impact = validated_resources * 10 + total_votes + total_reuses * 5
        total_impact = (validated_resources * 10) + total_votes + (total_reuses * 5)
        
        # Serialize user data
        serializer = UserSerializer(user)
        user_data = serializer.data
        
        # Add metrics
        user_data['metrics'] = {
            'total_resources': total_resources,
            'validated_resources': validated_resources,
            'total_votes': total_votes,
            'total_reuses': total_reuses,
            'total_impact': total_impact,
        }
        
        return Response(user_data, status=status.HTTP_200_OK)


class UserResourcesView(APIView):
    """
    Get user's published resources
    
    - Public endpoint
    - Returns paginated list of resources
    - Can filter by status
    """
    permission_classes = [AllowAny]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id, is_active=True)
        
        # Get query params
        resource_status = request.query_params.get('status', None)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 12))
        
        # Base queryset
        resources = Resource.objects.filter(
            owner=user,
            deleted_at__isnull=True
        ).select_related('latest_version').order_by('-created_at')
        
        # Filter by status if provided
        if resource_status:
            resources = resources.filter(latest_version__status=resource_status)
        
        # Pagination
        total_count = resources.count()
        start = (page - 1) * page_size
        end = start + page_size
        resources = resources[start:end]
        
        # Serialize
        serializer = ResourceListSerializer(resources, many=True)
        
        return Response({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
