"""
Admin for interactions app.

US-16: Votar Recurso
US-18: Notificaciones In-App
"""

from django.contrib import admin
from apps.interactions.models import Vote, Notification


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Admin interface for Vote model."""
    
    list_display = ('id', 'user', 'resource', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__name', 'resource__id')
    raw_id_fields = ('user', 'resource')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    
    list_display = ('id', 'user', 'type', 'is_read_display', 'created_at')
    list_filter = ('type', 'read_at', 'created_at')
    search_fields = ('user__email', 'user__name', 'message')
    raw_id_fields = ('user', 'resource', 'actor')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'
    
    def is_read_display(self, obj):
        return obj.is_read
    is_read_display.boolean = True
    is_read_display.short_description = 'Read'
