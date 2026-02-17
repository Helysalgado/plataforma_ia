"""
Authentication services.

Business logic for user registration, login, email verification, etc.

US-01: Registro de Usuario
US-02: Login
"""

import secrets
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import Role, UserRole

User = get_user_model()


class AuthService:
    """Service layer for authentication operations."""
    
    @staticmethod
    @transaction.atomic
    def register(email, name, password):
        """
        Register a new user.
        
        Args:
            email (str): User email
            name (str): User full name
            password (str): User password
        
        Returns:
            User: Created user instance
        
        Raises:
            ValueError: If email already exists
        """
        # Normalize email (lowercase entire email for consistency)
        email = email.lower()
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValueError('Email already registered')
        
        # Create user
        user = User.objects.create_user(
            email=email,
            name=name,
            password=password
        )
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        user.verification_token = verification_token
        user.save(update_fields=['verification_token'])
        
        # Assign default "User" role
        user_role, _ = Role.objects.get_or_create(name='User')
        UserRole.objects.create(user=user, role=user_role)
        
        # Send verification email
        AuthService.send_verification_email(user, verification_token)
        
        return user
    
    @staticmethod
    def send_verification_email(user, verification_token):
        """
        Send email verification link to user.
        
        Args:
            user (User): User instance
            verification_token (str): Verification token
        """
        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email/{verification_token}"
        
        subject = 'BioAI Hub — Verifica tu email'
        message = f"""
Hola {user.name},

Gracias por registrarte en BioAI Hub.

Por favor, verifica tu email haciendo clic en el siguiente enlace:
{verification_url}

Este enlace expirará en 24 horas.

Si no solicitaste este registro, puedes ignorar este email.

—
BioAI Hub
Centro de Ciencias Genómicas (CCG), UNAM
        """.strip()
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    
    @staticmethod
    @transaction.atomic
    def verify_email(token):
        """
        Verify user email with token.
        
        Args:
            token (str): Verification token
        
        Returns:
            User: Verified user instance
        
        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            user = User.objects.get(verification_token=token, email_verified_at__isnull=True)
        except User.DoesNotExist:
            raise ValueError('Invalid or expired verification token')
        
        # Check if token is expired (24 hours)
        token_age = timezone.now() - user.created_at
        if token_age.total_seconds() > 24 * 60 * 60:  # 24 hours
            raise ValueError('Verification token has expired')
        
        # Mark email as verified
        user.email_verified_at = timezone.now()
        user.verification_token = None  # Clear token
        user.save(update_fields=['email_verified_at', 'verification_token'])
        
        return user
    
    @staticmethod
    def login(email, password):
        """
        Authenticate user and return JWT tokens.
        
        Args:
            email (str): User email
            password (str): User password
        
        Returns:
            dict: {
                'user': User instance,
                'access': Access token,
                'refresh': Refresh token
            }
        
        Raises:
            ValueError: If credentials are invalid or email not verified
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError('Invalid credentials')
        
        # Check password
        if not user.check_password(password):
            raise ValueError('Invalid credentials')
        
        # Check if email is verified
        if not user.is_email_verified:
            raise ValueError('Email not verified', 'EMAIL_NOT_VERIFIED')
        
        # Check if account is active
        if not user.is_active:
            raise ValueError('Account is suspended')
        
        # Update last login
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login_at'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
