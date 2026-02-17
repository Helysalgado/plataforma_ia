"""
Serializers for interactions app (votes and notifications).

US-16: Votar Recurso
US-18: Notificaciones In-App
"""

from rest_framework import serializers
from apps.interactions.models import Vote, Notification


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


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    
    US-18: Notificaciones In-App
    """
    
    is_read = serializers.BooleanField(read_only=True)
    resource_title = serializers.CharField(source='resource.latest_version.title', read_only=True, allow_null=True)
    resource_id = serializers.UUIDField(source='resource.id', read_only=True, allow_null=True)
    actor_name = serializers.CharField(source='actor.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'message',
            'resource_id',
            'resource_title',
            'actor_name',
            'is_read',
            'read_at',
            'created_at'
        ]
        read_only_fields = fields


class NotificationListSerializer(serializers.Serializer):
    """
    Serializer for notification list response.
    
    US-18: Notificaciones In-App
    """
    
    count = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    notifications = NotificationSerializer(many=True)
