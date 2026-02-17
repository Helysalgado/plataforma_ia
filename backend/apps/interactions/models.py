"""
Vote model for resource voting system.

Based on:
- /docs/data/DATA_MODEL.md (section 3.6)
- /docs/product/EPICS_AND_STORIES.md (US-16)

US-16: Votar Recurso
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
