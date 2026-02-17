"""
Serializers for interactions app.

US-16: Votar Recurso
"""

from rest_framework import serializers
from apps.interactions.models import Vote


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for Vote model."""
    
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    resource_id = serializers.UUIDField(source='resource.id', read_only=True)
    
    class Meta:
        model = Vote
        fields = ('id', 'user_id', 'resource_id', 'created_at')
        read_only_fields = fields


class VoteToggleSerializer(serializers.Serializer):
    """Serializer for vote toggle response."""
    
    action = serializers.ChoiceField(choices=['voted', 'unvoted'])
    votes_count = serializers.IntegerField()
