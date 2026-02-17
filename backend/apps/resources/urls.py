"""URL configuration for resources app."""

from django.urls import path
from apps.resources.views import (
    ResourceListView,
    ResourceDetailView,
    ResourceCreateView,
    ResourceValidateView,
    ResourceForkView,
)
from apps.interactions.views import VoteToggleView

urlpatterns = [
    path('', ResourceListView.as_view(), name='resource-list'),
    path('create/', ResourceCreateView.as_view(), name='resource-create'),
    path('<uuid:resource_id>/', ResourceDetailView.as_view(), name='resource-detail'),
    path('<uuid:resource_id>/vote/', VoteToggleView.as_view(), name='vote-toggle'),
    path('<uuid:resource_id>/validate/', ResourceValidateView.as_view(), name='resource-validate'),
    path('<uuid:resource_id>/fork/', ResourceForkView.as_view(), name='resource-fork'),
]
