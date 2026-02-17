"""
Tests for AuthService.

US-01: Registro de Usuario
US-02: Login
"""

import pytest
from django.core import mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.authentication.services import AuthService
from apps.authentication.models import Role

User = get_user_model()


@pytest.mark.django_db
class TestAuthServiceRegister:
    """Tests for AuthService.register()"""
    
    def test_register_success(self):
        """
        Given que no existe usuario con email test@example.com
        When llamo a AuthService.register()
        Then el usuario es creado exitosamente
        And se asigna rol "User"
        And se genera verification_token
        And se envía email de verificación
        """
        # Arrange
        email = 'test@example.com'
        name = 'Test User'
        password = 'SecurePass123!'
        
        # Ensure "User" role exists
        Role.objects.get_or_create(name='User')
        
        # Act
        user = AuthService.register(email, name, password)
        
        # Assert
        assert user.email == email
        assert user.name == name
        assert user.check_password(password)
        assert user.is_active is True
        assert user.email_verified_at is None
        assert user.verification_token is not None
        assert len(user.verification_token) > 20  # Token length
        
        # Check role assignment
        assert user.has_role('User') is True
        
        # Check email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [email]
        assert 'Verifica tu email' in mail.outbox[0].subject
        assert user.verification_token in mail.outbox[0].body
    
    def test_register_duplicate_email_raises_error(self):
        """
        Given que existe usuario con email test@example.com
        When intento registrar con el mismo email
        Then se lanza ValueError
        """
        # Arrange
        email = 'test@example.com'
        User.objects.create_user(email, 'Existing User', 'pass123')
        
        # Act & Assert
        with pytest.raises(ValueError, match='Email already registered'):
            AuthService.register(email, 'New User', 'newpass123')
    
    def test_register_email_normalized(self):
        """Test que email se normaliza al registrar"""
        Role.objects.get_or_create(name='User')
        
        user = AuthService.register('Test@EXAMPLE.COM', 'Test', 'pass123')
        
        assert user.email == 'test@example.com'


@pytest.mark.django_db
class TestAuthServiceVerifyEmail:
    """Tests for AuthService.verify_email()"""
    
    def test_verify_email_success(self):
        """
        Given que usuario tiene verification_token válido
        When llamo a AuthService.verify_email(token)
        Then email_verified_at se actualiza
        And verification_token se limpia
        """
        # Arrange
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        token = 'valid_token_123'
        user.verification_token = token
        user.save()
        
        # Act
        verified_user = AuthService.verify_email(token)
        
        # Assert
        assert verified_user.id == user.id
        assert verified_user.email_verified_at is not None
        assert verified_user.verification_token is None
    
    def test_verify_email_invalid_token_raises_error(self):
        """
        Given que token no existe
        When intento verificar
        Then se lanza ValueError
        """
        with pytest.raises(ValueError, match='Invalid or expired verification token'):
            AuthService.verify_email('invalid_token')
    
    def test_verify_email_expired_token_raises_error(self):
        """
        Given que token tiene más de 24 horas
        When intento verificar
        Then se lanza ValueError
        """
        # Arrange
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        token = 'expired_token'
        user.verification_token = token
        user.created_at = timezone.now() - timedelta(hours=25)  # 25 hours ago
        user.save()
        
        # Act & Assert
        with pytest.raises(ValueError, match='Verification token has expired'):
            AuthService.verify_email(token)
    
    def test_verify_email_already_verified_raises_error(self):
        """
        Given que usuario ya tiene email verificado
        When intento verificar nuevamente
        Then se lanza ValueError
        """
        # Arrange
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        user.email_verified_at = timezone.now()
        user.verification_token = 'token'
        user.save()
        
        # Act & Assert
        with pytest.raises(ValueError, match='Invalid or expired verification token'):
            AuthService.verify_email('token')


@pytest.mark.django_db
class TestAuthServiceLogin:
    """Tests for AuthService.login()"""
    
    def test_login_success(self):
        """
        Given que usuario está registrado y email verificado
        When llamo a AuthService.login()
        Then retorna user, access token y refresh token
        And last_login_at se actualiza
        """
        # Arrange
        email = 'test@example.com'
        password = 'SecurePass123!'
        user = User.objects.create_user(email, 'Test User', password)
        user.email_verified_at = timezone.now()
        user.save()
        
        # Act
        result = AuthService.login(email, password)
        
        # Assert
        assert 'user' in result
        assert 'access' in result
        assert 'refresh' in result
        assert result['user'].id == user.id
        assert isinstance(result['access'], str)
        assert isinstance(result['refresh'], str)
        assert len(result['access']) > 50  # JWT token length
        
        # Check last_login_at updated
        user.refresh_from_db()
        assert user.last_login_at is not None
    
    def test_login_invalid_email_raises_error(self):
        """
        Given que email no existe
        When intento login
        Then se lanza ValueError
        """
        with pytest.raises(ValueError, match='Invalid credentials'):
            AuthService.login('nonexistent@example.com', 'pass123')
    
    def test_login_invalid_password_raises_error(self):
        """
        Given que password es incorrecta
        When intento login
        Then se lanza ValueError
        """
        # Arrange
        user = User.objects.create_user('test@example.com', 'Test', 'correctpass')
        user.email_verified_at = timezone.now()
        user.save()
        
        # Act & Assert
        with pytest.raises(ValueError, match='Invalid credentials'):
            AuthService.login('test@example.com', 'wrongpass')
    
    def test_login_email_not_verified_raises_error(self):
        """
        Given que email NO está verificado
        When intento login
        Then se lanza ValueError con código EMAIL_NOT_VERIFIED
        """
        # Arrange
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        # email_verified_at is None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            AuthService.login('test@example.com', 'pass123')
        
        assert 'Email not verified' in str(exc_info.value)
    
    def test_login_suspended_account_raises_error(self):
        """
        Given que usuario está suspendido (is_active=False)
        When intento login
        Then se lanza ValueError
        """
        # Arrange
        user = User.objects.create_user('test@example.com', 'Test', 'pass123')
        user.email_verified_at = timezone.now()
        user.is_active = False
        user.save()
        
        # Act & Assert
        with pytest.raises(ValueError, match='Account is suspended'):
            AuthService.login('test@example.com', 'pass123')
