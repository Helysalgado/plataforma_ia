"""URL configuration for resources app."""

from django.urls import path
from apps.resources.views import (
    ResourceListView,
    ResourceDetailView,
    ResourceCreateView,
)

urlpatterns = [
    path('', ResourceListView.as_view(), name='resource-list'),
    path('create/', ResourceCreateView.as_view(), name='resource-create'),
    path('<uuid:resource_id>/', ResourceDetailView.as_view(), name='resource-detail'),
]
