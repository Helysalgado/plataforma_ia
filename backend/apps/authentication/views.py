"""
Views for authentication app.

US-01: Registro de Usuario
US-02: Login
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.translation import gettext_lazy as _
from apps.authentication.services import AuthService
from apps.authentication.serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyEmailSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    """
    API endpoint for user registration.
    
    US-01: Registro de Usuario
    
    POST /api/auth/register/
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Register a new user."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = AuthService.register(
                email=serializer.validated_data['email'],
                name=serializer.validated_data['name'],
                password=serializer.validated_data['password'],
            )
            
            return Response(
                {
                    'message': _('Registration successful. Please check your email to verify your account.'),
                    'user_id': str(user.id),
                },
                status=status.HTTP_201_CREATED
            )
        
        except ValueError as e:
            return Response(
                {
                    'error': str(e),
                    'error_code': 'REGISTRATION_FAILED',
                },
                status=status.HTTP_409_CONFLICT
            )


class VerifyEmailView(APIView):
    """
    API endpoint for email verification.
    
    US-01: Registro de Usuario (verificación)
    
    GET /api/auth/verify-email/{token}/
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, token):
        """Verify user email with token."""
        try:
            user = AuthService.verify_email(token)
            
            return Response(
                {
                    'message': _('Email verified successfully. You can now log in.'),
                    'user': UserSerializer(user).data,
                },
                status=status.HTTP_200_OK
            )
        
        except ValueError as e:
            return Response(
                {
                    'error': str(e),
                    'error_code': 'VERIFICATION_FAILED',
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(APIView):
    """
    API endpoint for user login.
    
    US-02: Login
    
    POST /api/auth/login/
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Authenticate user and return JWT tokens."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = AuthService.login(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
            )
            
            return Response(
                {
                    'message': _('Login successful'),
                    'user': UserSerializer(result['user']).data,
                    'access': result['access'],
                    'refresh': result['refresh'],
                },
                status=status.HTTP_200_OK
            )
        
        except ValueError as e:
            error_message = str(e)
            error_code = 'AUTHENTICATION_FAILED'
            status_code = status.HTTP_401_UNAUTHORIZED
            
            # Check for specific error codes
            if 'Email not verified' in error_message:
                error_code = 'EMAIL_NOT_VERIFIED'
                status_code = status.HTTP_403_FORBIDDEN
            elif 'Account is suspended' in error_message:
                error_code = 'ACCOUNT_SUSPENDED'
                status_code = status.HTTP_403_FORBIDDEN
            
            return Response(
                {
                    'error': error_message.split(',')[0] if ',' in error_message else error_message,
                    'error_code': error_code,
                },
                status=status_code
            )
