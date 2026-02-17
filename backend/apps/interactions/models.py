"""
Interaction models: Vote and Notification.

Based on:
- /docs/data/DATA_MODEL.md (sections 3.6, 3.7)
- /docs/product/EPICS_AND_STORIES.md (US-16, US-18)
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Vote(models.Model):
    """
    Vote model - represents a user's vote on a resource.
    
    Business rules:
    - One vote per user per resource (enforced by unique constraint)
    - To unvote: delete the row (no toggle boolean)
    - Cascade delete if user or resource is deleted
    
    US-16: Votar Recurso
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name=_('user')
    )
    resource = models.ForeignKey(
        'resources.Resource',
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name=_('resource')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'votes'
        verbose_name = _('vote')
        verbose_name_plural = _('votes')
        unique_together = ('user', 'resource')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['resource']),
        ]
    
    def __str__(self):
        return f"{self.user.name} voted for {self.resource.id}"


class Notification(models.Model):
    """
    Notification model for in-app notifications.
    
    Notifies users of important events:
    - Resource validated (owner)
    - Resource forked (owner)
    - Validation requested (admin)
    
    US-18: Notificaciones In-App
    """
    
    TYPE_CHOICES = [
        ('resource_validated', 'Resource Validated'),
        ('resource_forked', 'Resource Forked'),
        ('validation_requested', 'Validation Requested'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipient
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('user')
    )
    
    # Notification details
    type = models.CharField(
        _('type'),
        max_length=50,
        choices=TYPE_CHOICES
    )
    
    message = models.TextField(
        _('message'),
        help_text=_('Human-readable notification message')
    )
    
    # Related resource (optional)
    resource = models.ForeignKey(
        'resources.Resource',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('resource'),
        null=True,
        blank=True
    )
    
    # Actor (who triggered the notification, optional)
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='triggered_notifications',
        verbose_name=_('actor'),
        null=True,
        blank=True,
        help_text=_('User who triggered this notification (e.g., who forked the resource)')
    )
    
    # Read status
    read_at = models.DateTimeField(
        _('read at'),
        null=True,
        blank=True,
        help_text=_('Timestamp when notification was read')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'read_at']),
        ]
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
    
    def __str__(self):
        return f"{self.user.email}: {self.type} ({self.created_at})"
    
    @property
    def is_read(self):
        """Check if notification has been read."""
        return self.read_at is not None
