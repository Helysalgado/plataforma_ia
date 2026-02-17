"""
User and Role models for authentication and authorization.

Based on:
- /docs/data/DATA_MODEL.md
- /docs/architecture/ADR-003-rbac.md
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom manager for User model."""
    
    def create_user(self, email, name, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError(_('Email is required'))
        if not name:
            raise ValueError(_('Name is required'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified_at', timezone.now())
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model.
    
    Uses email as the unique identifier instead of username.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, max_length=255, db_index=True)
    name = models.CharField(_('full name'), max_length=255)
    
    # Email verification
    email_verified_at = models.DateTimeField(_('email verified at'), null=True, blank=True)
    verification_token = models.CharField(_('verification token'), max_length=100, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_login_at = models.DateTimeField(_('last login at'), null=True, blank=True)
    
    # Roles (many-to-many)
    roles = models.ManyToManyField('Role', through='UserRole', related_name='users', blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def is_email_verified(self):
        """Check if email is verified."""
        return self.email_verified_at is not None
    
    @property
    def is_admin(self):
        """Check if user has Admin role."""
        return self.roles.filter(name='Admin').exists() or self.is_superuser
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.roles.filter(name=role_name).exists()


class Role(models.Model):
    """
    Role model for RBAC.
    
    MVP roles: Admin, User
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('role name'), max_length=50, unique=True, db_index=True)
    description = models.TextField(_('description'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Many-to-many through table for User and Role.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_at = models.DateTimeField(_('assigned at'), auto_now_add=True)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')
        verbose_name = _('user role')
        verbose_name_plural = _('user roles')
    
    def __str__(self):
        return f'{self.user.email} - {self.role.name}'
