from django.contrib import admin
from apps.interactions.models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Admin interface for Vote model."""
    
    list_display = ('id', 'user', 'resource', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__name', 'resource__id')
    raw_id_fields = ('user', 'resource')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'
