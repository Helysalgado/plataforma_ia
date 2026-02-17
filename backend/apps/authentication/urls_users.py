"""User profile endpoints"""

from django.urls import path
from apps.authentication import views_users

app_name = 'users'

urlpatterns = [
    # User profile
    path('<uuid:user_id>/', views_users.UserDetailView.as_view(), name='user-detail'),
    path('<uuid:user_id>/resources/', views_users.UserResourcesView.as_view(), name='user-resources'),
]

