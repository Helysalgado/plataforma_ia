"""
API views for notifications.

US-18: Notificaciones In-App
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.interactions.services import NotificationService
from apps.interactions.serializers import (
    NotificationSerializer,
    NotificationListSerializer,
)


class NotificationListView(APIView):
    """
    List user notifications.
    
    GET /api/notifications/
    Query params:
    - unread_only (bool): If true, return only unread notifications
    
    US-18: Notificaciones In-App
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
        
        notifications = NotificationService.get_user_notifications(
            user=request.user,
            unread_only=unread_only
        )
        
        unread_count = NotificationService.get_unread_count(request.user)
        
        response_data = {
            'count': notifications.count(),
            'unread_count': unread_count,
            'notifications': NotificationSerializer(notifications, many=True).data
        }
        
        serializer = NotificationListSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationMarkReadView(APIView):
    """
    Mark a notification as read.
    
    PATCH /api/notifications/{id}/read/
    
    US-18: Notificaciones In-App
    """
    
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, notification_id):
        try:
            notification = NotificationService.mark_as_read(
                notification_id=notification_id,
                user=request.user
            )
            
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'error': str(e), 'error_code': 'NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )


class NotificationMarkAllReadView(APIView):
    """
    Mark all notifications as read for the authenticated user.
    
    POST /api/notifications/mark-all-read/
    
    US-18: Notificaciones In-App
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        count = NotificationService.mark_all_as_read(user=request.user)
        
        return Response(
            {'message': f'{count} notifications marked as read', 'count': count},
            status=status.HTTP_200_OK
        )


class NotificationUnreadCountView(APIView):
    """
    Get unread notification count for the authenticated user.
    
    GET /api/notifications/unread-count/
    
    US-18: Notificaciones In-App
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        count = NotificationService.get_unread_count(user=request.user)
        
        return Response(
            {'unread_count': count},
            status=status.HTTP_200_OK
        )
