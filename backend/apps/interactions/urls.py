"""URL configuration for interactions app."""

from django.urls import path
from apps.interactions.views import VoteToggleView

urlpatterns = [
    path('<uuid:resource_id>/vote/', VoteToggleView.as_view(), name='vote-toggle'),
]
