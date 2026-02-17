"""
API views for interactions app.

US-16: Votar Recurso
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.interactions.services import VoteService
from apps.interactions.serializers import VoteToggleSerializer


class VoteToggleView(APIView):
    """
    Toggle vote for a resource.
    
    POST /api/resources/{resource_id}/vote/
    
    If user has already voted: removes vote (unvote)
    If user hasn't voted: adds vote
    
    US-16: Votar Recurso
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, resource_id):
        try:
            result = VoteService.toggle_vote(
                user=request.user,
                resource_id=resource_id
            )
            
            serializer = VoteToggleSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'error': str(e), 'error_code': 'RESOURCE_NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
