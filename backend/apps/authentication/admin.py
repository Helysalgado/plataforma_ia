"""
Django admin configuration for authentication app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import User, Role, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model."""
    
    ordering = ['-created_at']
    list_display = ('email', 'name', 'is_active', 'is_email_verified', 'is_admin', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'email_verified_at', 'roles')
    search_fields = ('email', 'name')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (_('Email verification'), {'fields': ('email_verified_at', 'verification_token')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login_at', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login_at')
    # Note: roles use through model (UserRole), so filter_horizontal is not applicable


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin for Role model."""
    
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin for UserRole through model."""
    
    list_display = ('user', 'role', 'assigned_at')
    list_filter = ('role',)
    search_fields = ('user__email', 'role__name')
    readonly_fields = ('assigned_at',)
