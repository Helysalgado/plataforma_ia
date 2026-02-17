"""
URL configuration for authentication app.
"""

from django.urls import path
from apps.authentication import views

app_name = 'authentication'

urlpatterns = [
    # Registration and verification
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    
    # Login
    path('login/', views.LoginView.as_view(), name='login'),
]
