"""
Integration tests for authentication API.

US-01: Registro de Usuario
US-02: Login
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core import mail
from apps.authentication.models import Role

User = get_user_model()


@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient()


@pytest.fixture
def user_role():
    """Create User role."""
    role, _ = Role.objects.get_or_create(name='User', description='Regular user')
    return role


@pytest.mark.django_db
@pytest.mark.integration
class TestRegisterAPI:
    """Integration tests for POST /api/auth/register/"""
    
    def test_register_success(self, api_client, user_role):
        """
        Given datos válidos de registro
        When POST /api/auth/register/
        Then retorna 201 Created
        And usuario es creado con email_verified_at NULL
        And se envía email de verificación
        """
        # Arrange
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'SecurePass123!',
        }
        
        # Act
        response = api_client.post('/api/auth/register/', data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user_id' in response.data
        assert 'Registration successful' in response.data['message']
        
        # Check user was created
        user = User.objects.get(email=data['email'])
        assert user.name == data['name']
        assert user.email_verified_at is None
        assert user.verification_token is not None
        
        # Check email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [data['email']]
    
    def test_register_duplicate_email(self, api_client, user_role):
        """
        Given que existe usuario con email test@example.com
        When intento registrar con el mismo email
        Then retorna 409 Conflict
        """
        # Arrange
        User.objects.create_user('test@example.com', 'Existing', 'pass123')
        data = {
            'email': 'test@example.com',
            'name': 'New User',
            'password': 'SecurePass123!',
        }
        
        # Act
        response = api_client.post('/api/auth/register/', data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'already registered' in response.data['error'].lower()
    
    def test_register_weak_password(self, api_client, user_role):
        """
        Given contraseña débil
        When intento registrar
        Then retorna 400 Bad Request
        """
        # Arrange
        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': '12345',  # Too weak
        }
        
        # Act
        response = api_client.post('/api/auth/register/', data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_invalid_email(self, api_client, user_role):
        """
        Given email inválido
        When intento registrar
        Then retorna 400 Bad Request
        """
        # Arrange
        data = {
            'email': 'invalid-email',
            'name': 'Test User',
            'password': 'SecurePass123!',
        }
        
        # Act
        response = api_client.post('/api/auth/register/', data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.integration
class TestVerifyEmailAPI:
    """Integration tests for GET /api/auth/verify-email/{token}/"""
    
    def test_verify_email_success(self, api_client):
        """
        Given token válido
        When GET /api/auth/verify-email/{token}/
        Then retorna 200 OK
        And email_verified_at se actualiza
        """
        # Arrange
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        token = 'valid_token_123'
        user.verification_token = token
        user.save()
        
        # Act
        response = api_client.get(f'/api/auth/verify-email/{token}/')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'Email verified successfully' in response.data['message']
        assert 'user' in response.data
        
        # Check user was verified
        user.refresh_from_db()
        assert user.email_verified_at is not None
        assert user.verification_token is None
    
    def test_verify_email_invalid_token(self, api_client):
        """
        Given token inválido
        When intento verificar
        Then retorna 400 Bad Request
        """
        # Act
        response = api_client.get('/api/auth/verify-email/invalid_token/')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid or expired' in response.data['error']


@pytest.mark.django_db
@pytest.mark.integration
class TestLoginAPI:
    """Integration tests for POST /api/auth/login/"""
    
    def test_login_success(self, api_client):
        """
        Given usuario registrado y verificado
        When POST /api/auth/login/ con credenciales válidas
        Then retorna 200 OK
        And retorna access token y refresh token
        And retorna user data
        """
        # Arrange
        email = 'test@example.com'
        password = 'SecurePass123!'
        user = User.objects.create_user(email, 'Test User', password)
        user.email_verified_at = timezone.now()
        user.save()
        
        data = {
            'email': email,
            'password': password,
        }
        
        # Act
        response = api_client.post('/api/auth/login/', data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == email
        assert len(response.data['access']) > 50  # JWT token
    
    def test_login_invalid_credentials(self, api_client):
        """
        Given credenciales incorrectas
        When intento login
        Then retorna 401 Unauthorized
        """
        # Arrange
        data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpass',
        }
        
        # Act
        response = api_client.post('/api/auth/login/', data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'Invalid credentials' in response.data['error']
    
    def test_login_email_not_verified(self, api_client):
        """
        Given usuario con email NO verificado
        When intento login
        Then retorna 403 Forbidden
        And error_code es EMAIL_NOT_VERIFIED
        """
        # Arrange
        email = 'test@example.com'
        password = 'SecurePass123!'
        user = User.objects.create_user(email, 'Test User', password)
        # email_verified_at is None
        
        data = {
            'email': email,
            'password': password,
        }
        
        # Act
        response = api_client.post('/api/auth/login/', data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['error_code'] == 'EMAIL_NOT_VERIFIED'
    
    def test_login_suspended_account(self, api_client):
        """
        Given usuario suspendido (is_active=False)
        When intento login
        Then retorna 403 Forbidden
        """
        # Arrange
        email = 'test@example.com'
        password = 'SecurePass123!'
        user = User.objects.create_user(email, 'Test User', password)
        user.email_verified_at = timezone.now()
        user.is_active = False
        user.save()
        
        data = {
            'email': email,
            'password': password,
        }
        
        # Act
        response = api_client.post('/api/auth/login/', data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'suspended' in response.data['error'].lower()
