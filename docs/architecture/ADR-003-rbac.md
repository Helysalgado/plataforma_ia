# ADR-003: RBAC Extensible

**Estado:** Aceptado  
**Fecha:** 2026-02-16  
**Decisor(es):** Tech Lead, Security Engineer  
**Contexto:** FASE 3 — Diseño Técnico

---

## Contexto y Problema

BioAI Hub requiere un sistema de control de acceso que:
1. **MVP:** Soporte 2 roles simples (Admin, User)
2. **Post-MVP:** Sea extensible para agregar roles (Reviewer, Moderator) sin reescribir código
3. Permita permisos granulares (CRUD por recurso, validar, moderar)
4. Sea eficiente (no ralentizar requests)

**Decisión requerida:** ¿RBAC simple hardcoded o RBAC extensible con tablas de permisos?

---

## Opciones Consideradas

### Opción 1: Roles Hardcoded (Django `is_staff`, `is_superuser`)
**Descripción:** Usar campos booleanos en modelo `User`

```python
class User(AbstractUser):
    is_admin = BooleanField(default=False)  # Equivalente a is_superuser
    email_verified_at = DateTimeField(null=True, blank=True)
```

**Pros:**
- ✅ Muy simple (MVP rápido)
- ✅ Performance (sin joins)

**Contras:**
- ❌ No extensible (agregar Reviewer requiere migración + código)
- ❌ Permisos granulares difíciles
- ❌ Lógica de permisos dispersa en código

---

### Opción 2: Django Guardian (Object-Level Permissions)
**Descripción:** Librería que agrega permisos por objeto individual

**Pros:**
- ✅ Permisos granulares (ej: "user X puede editar resource Y")
- ✅ Librería madura

**Contras:**
- ❌ Overhead para MVP simple
- ❌ Complejidad innecesaria si no se usan permisos por objeto
- ❌ Performance impact (queries adicionales)

---

### Opción 3: RBAC Extensible (Tablas de Roles y Permisos)
**Descripción:** Modelo explícito de Roles y Permisos con M2M

```python
class Role(models.Model):
    name = CharField(max_length=50, unique=True)  # Admin, User, Reviewer, Moderator
    description = TextField(blank=True)
    permissions = ManyToManyField('Permission')

class Permission(models.Model):
    codename = CharField(max_length=100, unique=True)  # "publish_resource", "validate_resource"
    name = CharField(max_length=200)
    description = TextField(blank=True)

class User(AbstractUser):
    roles = ManyToManyField(Role, related_name='users', blank=True)
    email_verified_at = DateTimeField(null=True, blank=True)
    
    @property
    def is_admin(self):
        return self.roles.filter(name='Admin').exists()
    
    def has_permission(self, codename):
        return self.roles.filter(permissions__codename=codename).exists()
```

**Pros:**
- ✅ Extensible (agregar roles sin migración de User)
- ✅ Permisos granulares
- ✅ Administrable via Django Admin
- ✅ Lógica centralizada

**Contras:**
- ⚠️ Más complejo que MVP mínimo
- ⚠️ Overhead de queries (mitigable con caching)

---

## Decisión

**Elegimos: Opción 3 Híbrida — RBAC Extensible con Shortcut para MVP**

**Estrategia:**
1. **Diseño extensible:** Tablas `Role` y `Permission`
2. **MVP simplificado:** Solo 2 roles (Admin, User), permisos predefinidos
3. **Shortcut performance:** Campo `is_admin` computed property (cache)
4. **Post-MVP:** Agregar roles (Reviewer, Moderator) sin cambiar código base

---

## Implementación MVP

### 1. Modelos

```python
# apps/authentication/models.py

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'roles'
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True, db_index=True)
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Computed properties (performance shortcut)
    @property
    def is_admin(self):
        # Cache en request (middleware puede setear esto)
        if not hasattr(self, '_is_admin_cached'):
            self._is_admin_cached = self.roles.filter(name='Admin').exists()
        return self._is_admin_cached
    
    class Meta:
        db_table = 'users'
```

### 2. Seed Data (Initial Roles)

```python
# apps/authentication/management/commands/seed_roles.py

from django.core.management.base import BaseCommand
from apps.authentication.models import Role

class Command(BaseCommand):
    help = 'Seed initial roles for MVP'
    
    def handle(self, *args, **kwargs):
        roles_data = [
            {
                'name': 'Admin',
                'description': 'Full access to all resources and admin panel'
            },
            {
                'name': 'User',
                'description': 'Standard user, can publish and interact with resources'
            },
        ]
        
        for data in roles_data:
            Role.objects.get_or_create(name=data['name'], defaults=data)
        
        self.stdout.write(self.style.SUCCESS('Roles seeded successfully'))
```

### 3. Permission Classes (Django REST Framework)

```python
# apps/core/permissions.py

from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Solo usuarios con rol Admin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

class IsOwnerOrAdmin(BasePermission):
    """
    Solo owner del objeto o Admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.owner == request.user

class IsEmailVerified(BasePermission):
    """
    Solo usuarios con email verificado.
    """
    def has_permission(self, request, view):
        return request.user and request.user.email_verified_at is not None
```

### 4. Uso en Views

```python
# apps/resources/views.py

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated(), IsEmailVerified()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        else:  # list, retrieve
            return [AllowAny()]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def validate(self, request, pk=None):
        resource = self.get_object()
        ValidationService.validate_manually(resource, request.user)
        return Response({'status': 'validated'})
```

---

## Extensibilidad Post-MVP

### Agregar Rol "Reviewer"

```python
# 1. Crear rol en BD (via Django Admin o migration)
Role.objects.create(
    name='Reviewer',
    description='Can validate resources but not edit them'
)

# 2. Agregar permiso específico (si es necesario)
Permission.objects.create(
    codename='validate_resource',
    name='Validate Resource',
    description='Can change resource status to Validated'
)

reviewer_role = Role.objects.get(name='Reviewer')
reviewer_role.permissions.add(Permission.objects.get(codename='validate_resource'))

# 3. Actualizar permission class (si es necesario)
class CanValidate(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin or request.user.roles.filter(
            name__in=['Admin', 'Reviewer']
        ).exists()
```

### Permisos Granulares (Futuro)

```python
class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'permissions'

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, related_name='roles')

# Permisos predefinidos:
PERMISSIONS = [
    ('publish_resource', 'Publish Resource'),
    ('edit_own_resource', 'Edit Own Resource'),
    ('edit_any_resource', 'Edit Any Resource'),
    ('delete_own_resource', 'Delete Own Resource'),
    ('delete_any_resource', 'Delete Any Resource'),
    ('validate_resource', 'Validate Resource'),
    ('revoke_validation', 'Revoke Validation'),
    ('moderate_reports', 'Moderate Reports'),
    ('manage_users', 'Manage Users'),
]
```

---

## Performance Optimization

### Middleware: Cache de Roles

```python
# apps/core/middleware.py

class CacheRolesMiddleware:
    """
    Cache roles del usuario en request para evitar queries repetidos.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Prefetch roles en 1 query
            request.user._cached_roles = list(
                request.user.roles.values_list('name', flat=True)
            )
            request.user._is_admin_cached = 'Admin' in request.user._cached_roles
        
        response = self.get_response(request)
        return response
```

---

## Métricas de Éxito

- ✅ Overhead de permisos <10ms por request (con caching)
- ✅ Agregar nuevo rol sin migración de `User` table
- ✅ 0 bugs de autorización en primeros 3 meses

---

## Referencias

- [Django Permissions](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions-and-authorization)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [RBAC Pattern](https://en.wikipedia.org/wiki/Role-based_access_control)

---

**Decisión aprobada:** 2026-02-16  
**Implementación:** FASE 7 (Backend MVP)  
**Siguiente artefacto:** Diagrama de Arquitectura (Mermaid)
