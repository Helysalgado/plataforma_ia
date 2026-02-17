# ARCHITECTURE — BioAI Hub

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Versión:** 1.0  
**Fecha:** 2026-02-16  
**Fase:** FASE 3 — Diseño Técnico  
**Rol activo:** Tech Lead / Architect

---

## 1. VISIÓN ARQUITECTÓNICA

### 1.1 Principio Rector
**Arquitectura monolítica modular evolutiva** que permite:
- Desarrollo rápido del MVP
- Modularidad interna por dominios
- Escalabilidad incremental sin reescritura
- Migración futura a microservicios si es necesario (post-MVP)

### 1.2 Principios de Diseño
1. **Separation of Concerns:** Capas claramente definidas (Frontend, API, Service, Data)
2. **Domain-Driven Design (lite):** Módulos organizados por dominio de negocio
3. **SOLID:** Especialmente Single Responsibility y Dependency Inversion
4. **Security by Default:** Autenticación, autorización, validación en todas las capas
5. **Testability:** Inyección de dependencias, mocking fácil
6. **Observability:** Logging estructurado, métricas, auditoría

---

## 2. ARQUITECTURA DE ALTO NIVEL

### 2.1 Diagrama de Arquitectura

Ver diagrama detallado en [`diagrams/architecture.mmd`](diagrams/architecture.mmd)

**Componentes principales:**

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Next.js 14+ (Frontend)                    │ │
│  │  - Pages Router / App Router                           │ │
│  │  - React Server Components (RSC)                       │ │
│  │  - Client Components (interactividad)                  │ │
│  │  - State Management: React Context + Custom Hooks     │ │
│  │  - UI Library: Tailwind CSS + shadcn/ui               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS / JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Nginx (Reverse Proxy)                     │ │
│  │  - SSL Termination                                     │ │
│  │  - Rate Limiting (global)                              │ │
│  │  - Load Balancing (futuro)                             │ │
│  │  - Static Files (Next.js build)                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
    ┌────────────────────┐    ┌────────────────────┐
    │   Next.js Server   │    │  Django Backend    │
    │   (Port 3000)      │    │  (Port 8000)       │
    └────────────────────┘    └────────────────────┘
                 │                         │
                 │                         ▼
                 │          ┌─────────────────────────────────┐
                 │          │     APPLICATION LAYER           │
                 │          │  ┌────────────────────────────┐ │
                 │          │  │   Django REST Framework    │ │
                 │          │  │   - JWT Authentication     │ │
                 │          │  │   - Permission Classes     │ │
                 │          │  │   - Serializers            │ │
                 │          │  │   - ViewSets / APIViews    │ │
                 │          │  └────────────────────────────┘ │
                 │          └─────────────────────────────────┘
                 │                         │
                 │                         ▼
                 │          ┌─────────────────────────────────┐
                 │          │       SERVICE LAYER             │
                 │          │  ┌────────────────────────────┐ │
                 │          │  │  Domain Services           │ │
                 │          │  │  - AuthService             │ │
                 │          │  │  - ResourceService         │ │
                 │          │  │  - VersioningService       │ │
                 │          │  │  - ValidationService       │ │
                 │          │  │  - NotificationService     │ │
                 │          │  └────────────────────────────┘ │
                 │          └─────────────────────────────────┘
                 │                         │
                 │                         ▼
                 │          ┌─────────────────────────────────┐
                 │          │       DATA ACCESS LAYER         │
                 │          │  ┌────────────────────────────┐ │
                 │          │  │  Django ORM Models         │ │
                 │          │  │  - User                    │ │
                 │          │  │  - Resource                │ │
                 │          │  │  - ResourceVersion         │ │
                 │          │  │  - Vote, Notification      │ │
                 │          │  └────────────────────────────┘ │
                 │          └─────────────────────────────────┘
                 │                         │
                 └─────────────────────────┼─────────────────┐
                                           ▼                 │
                              ┌────────────────────┐         │
                              │   PostgreSQL 15+   │         │
                              │   - Primary DB     │         │
                              │   - Connection Pool│         │
                              │   - Daily Backups  │         │
                              └────────────────────┘         │
                                                              │
                              ┌────────────────────┐         │
                              │   External Deps    │◄────────┘
                              │   - SMTP (Email)   │
                              │   - GitHub API     │
                              │   - Gravatar API   │
                              └────────────────────┘
```

---

## 3. MÓDULOS POR DOMINIO (BACKEND)

### 3.1 Estructura de Módulos Django

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authentication/         # Dominio: Auth
│   │   ├── models.py           # User (extendido)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py         # AuthService
│   │   ├── permissions.py
│   │   └── tests/
│   ├── resources/              # Dominio: Resources
│   │   ├── models.py           # Resource, ResourceVersion
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py         # ResourceService, VersioningService
│   │   ├── permissions.py
│   │   ├── filters.py
│   │   └── tests/
│   ├── interactions/           # Dominio: Votes, Forks
│   │   ├── models.py           # Vote
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py         # VoteService, ForkService
│   │   └── tests/
│   ├── validation/             # Dominio: Validation
│   │   ├── models.py           # (usa ResourceVersion)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py         # ValidationService
│   │   ├── tasks.py            # Celery: promoción automática
│   │   └── tests/
│   ├── notifications/          # Dominio: Notifications
│   │   ├── models.py           # Notification
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py         # NotificationService
│   │   └── tests/
│   └── core/                   # Shared utilities
│       ├── exceptions.py
│       ├── pagination.py
│       ├── permissions.py      # Base permission classes
│       ├── middleware.py
│       └── utils.py
└── manage.py
```

### 3.2 Responsabilidades por Módulo

#### Módulo: `authentication`
- **Modelos:** `User` (Django AbstractUser extendido)
- **Servicios:**
  - `AuthService.register(email, name, password)` → User + envía email
  - `AuthService.verify_email(token)` → Valida y activa cuenta
  - `AuthService.login(email, password)` → Genera JWT
  - `AuthService.reset_password_request(email)` → Envía email con token
  - `AuthService.reset_password_confirm(token, new_password)` → Resetea contraseña
- **Endpoints:**
  - `POST /api/auth/register`
  - `GET /api/auth/verify-email/:token`
  - `POST /api/auth/login`
  - `POST /api/auth/logout` (opcional, si blacklist)
  - `POST /api/auth/password-reset-request`
  - `POST /api/auth/password-reset-confirm/:token`
  - `POST /api/auth/resend-verification`

#### Módulo: `resources`
- **Modelos:** `Resource`, `ResourceVersion`
- **Servicios:**
  - `ResourceService.create(owner, data)` → Resource + ResourceVersion v1.0.0
  - `ResourceService.update(resource, user, data)` → Update in-place o create new version
  - `ResourceService.delete(resource, user)` → Soft delete
  - `ResourceService.list(filters, pagination)` → Queryset filtrado
  - `ResourceService.get_by_id(id)` → Resource with latest version
  - `VersioningService.create_version(resource, data, increment_type)` → Nueva versión
  - `VersioningService.should_create_new_version(resource)` → Bool (si latest es Validated)
  - `VersioningService.calculate_version_number(current)` → v1.1.0
- **Endpoints:**
  - `GET /api/resources` (público)
  - `GET /api/resources/:id` (público)
  - `POST /api/resources` (autenticado, email verificado)
  - `PATCH /api/resources/:id` (owner o admin)
  - `DELETE /api/resources/:id` (owner o admin)
  - `GET /api/resources/:id/versions` (público)
  - `GET /api/resources/:id/versions/:versionId` (público)
  - `GET /api/resources/featured` (público)

#### Módulo: `interactions`
- **Modelos:** `Vote`
- **Servicios:**
  - `VoteService.toggle_vote(user, resource)` → Create o delete vote
  - `VoteService.has_voted(user, resource)` → Bool
  - `ForkService.fork_resource(user, resource)` → Nuevo Resource derivado
- **Endpoints:**
  - `POST /api/resources/:id/vote` (autenticado, idempotente toggle)
  - `POST /api/resources/:id/fork` (autenticado)

#### Módulo: `validation`
- **Servicios:**
  - `ValidationService.validate_manually(resource, admin)` → Cambia status, crea notificación
  - `ValidationService.revoke_validation(resource, admin, reason)` → Sandbox, notificación
  - `ValidationService.check_auto_promotion_criteria(resource)` → Bool
  - `ValidationService.promote_to_validated(resource)` → Cambio automático
- **Endpoints:**
  - `POST /api/resources/:id/validate` (solo admin)
  - `POST /api/resources/:id/revoke-validation` (solo admin)
- **Tasks (Celery):**
  - `promote_eligible_resources.task()` → Job diario, evalúa criterios

#### Módulo: `notifications`
- **Modelos:** `Notification`
- **Servicios:**
  - `NotificationService.create(user, type, resource, message)` → Notification
  - `NotificationService.mark_as_read(notification)` → read_at = now()
  - `NotificationService.mark_all_as_read(user)` → Bulk update
  - `NotificationService.get_unread_count(user)` → Int
- **Endpoints:**
  - `GET /api/notifications` (autenticado)
  - `PATCH /api/notifications/:id/read` (autenticado)
  - `POST /api/notifications/mark-all-read` (autenticado)

---

## 4. FRONTEND (NEXT.JS)

### 4.1 Estructura de Directorios

```
frontend/
├── app/                        # App Router (Next.js 14+)
│   ├── (public)/               # Public routes
│   │   ├── page.tsx            # Home
│   │   ├── explore/
│   │   │   └── page.tsx
│   │   ├── resources/
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   └── profile/
│   │       └── [id]/
│   │           └── page.tsx
│   ├── (auth)/                 # Auth routes (layout diferente)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── verify-email/
│   │       └── [token]/
│   │           └── page.tsx
│   ├── (protected)/            # Protected routes (middleware)
│   │   ├── publish/
│   │   │   └── page.tsx
│   │   ├── resources/
│   │   │   └── [id]/
│   │   │       └── edit/
│   │   │           └── page.tsx
│   │   └── profile/
│   │       └── page.tsx        # Own profile
│   ├── layout.tsx              # Root layout
│   └── error.tsx               # Error boundary
├── components/
│   ├── ui/                     # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── modal.tsx
│   │   └── ...
│   ├── common/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Footer.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── EmptyState.tsx
│   │   └── ErrorBoundary.tsx
│   ├── resource/
│   │   ├── ResourceCard.tsx
│   │   ├── ResourceDetail.tsx
│   │   ├── ResourceForm.tsx
│   │   ├── VoteButton.tsx
│   │   └── Badge.tsx
│   └── notifications/
│       └── NotificationPanel.tsx
├── lib/
│   ├── api/                    # API clients
│   │   ├── auth.ts
│   │   ├── resources.ts
│   │   ├── notifications.ts
│   │   └── client.ts           # Axios config
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useResource.ts
│   │   └── useNotifications.ts
│   ├── utils/
│   │   ├── validation.ts
│   │   ├── formatting.ts
│   │   └── constants.ts
│   └── types/
│       ├── user.ts
│       ├── resource.ts
│       └── api.ts
├── context/
│   └── AuthContext.tsx         # Global auth state
├── middleware.ts               # Route protection
└── next.config.js
```

### 4.2 Patrones Frontend

#### State Management
- **Global State:** React Context (AuthContext) para autenticación
- **Server State:** React Query (TanStack Query) para datos de API
- **Form State:** React Hook Form con Zod validation
- **UI State:** Local state (`useState`) para componentes

#### Data Fetching
- **Server Components:** Fetch directo en RSC cuando es posible (SEO, performance)
- **Client Components:** React Query para caching y revalidación
- **Patterns:**
  - Loading states con Suspense
  - Error boundaries jerárquicos
  - Optimistic updates (votos)

#### Authentication Flow
1. Login → JWT guardado en httpOnly cookie (Next.js API route)
2. Middleware valida cookie en cada request protegido
3. AuthContext provee `user` y `logout()`
4. Refresh token (opcional) manejado en interceptor Axios

---

## 5. CAPAS DE LA APLICACIÓN

### 5.1 Backend Layers

#### Layer 1: API / Presentation (Views)
**Responsabilidad:** Recibir requests HTTP, validar entrada básica, llamar servicio, retornar response

**Principios:**
- Views **delgadas** (thin controllers)
- NO contienen lógica de negocio
- Usan Serializers para validación de entrada
- Usan Permission Classes para autorización
- Manejan excepciones con decorators

**Ejemplo:**
```python
# apps/resources/views.py
class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    
    def create(self, request):
        serializer = ResourceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validación: email verificado
        if not request.user.email_verified_at:
            raise PermissionDenied("Email not verified")
        
        # Lógica en Service Layer
        resource = ResourceService.create(
            owner=request.user,
            data=serializer.validated_data
        )
        
        return Response(
            ResourceSerializer(resource).data,
            status=status.HTTP_201_CREATED
        )
```

#### Layer 2: Service / Business Logic
**Responsabilidad:** Lógica de negocio, orquestación, transacciones

**Principios:**
- Contiene toda la lógica de dominio
- Orquesta múltiples modelos si es necesario
- Maneja transacciones (`@transaction.atomic`)
- Lanza excepciones de dominio
- Es testeable sin HTTP

**Ejemplo:**
```python
# apps/resources/services.py
class ResourceService:
    @staticmethod
    @transaction.atomic
    def create(owner, data):
        # Validación de negocio
        if Resource.objects.filter(owner=owner, title=data['title']).exists():
            # Warning, no error (permite duplicados con warning)
            pass
        
        # Crear Resource
        resource = Resource.objects.create(
            owner=owner,
            source_type=data['source_type']
        )
        
        # Crear ResourceVersion inicial
        version = VersioningService.create_initial_version(
            resource=resource,
            data=data
        )
        
        # Si Request Validation, notificar admins
        if data.get('status') == 'Pending Validation':
            NotificationService.notify_admins_validation_request(resource)
        
        return resource
```

#### Layer 3: Data Access (Models / ORM)
**Responsabilidad:** Persistencia, queries, constraints de BD

**Principios:**
- Define schema de BD
- Métodos de query custom (managers)
- Constraints y validaciones de modelo
- NO contiene lógica de negocio compleja

**Ejemplo:**
```python
# apps/resources/models.py
class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources')
    source_type = models.CharField(max_length=20, choices=SourceTypeChoices.choices)
    derived_from_resource = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    derived_from_version = models.ForeignKey('ResourceVersion', null=True, blank=True, on_delete=models.SET_NULL)
    forks_count = models.IntegerField(default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resources'
        indexes = [
            models.Index(fields=['owner', 'created_at']),
            models.Index(fields=['deleted_at']),  # Soft delete queries
        ]
    
    def get_latest_version(self):
        return self.versions.filter(is_latest=True).first()
```

---

## 6. SEGURIDAD

### 6.1 Autenticación (JWT)

Ver ADR-001 para decisión completa.

**Estrategia:**
- JWT en access token (expira 24h)
- httpOnly cookie para almacenar token (frontend)
- Refresh token opcional (expira 7d) para renovación silenciosa

**Flujo:**
1. Login → Backend genera JWT (HS256, secret en env)
2. Frontend guarda en httpOnly cookie via Next.js API route
3. Cada request incluye cookie automáticamente
4. Backend valida JWT en middleware

**Claims JWT:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "is_admin": false,
  "email_verified": true,
  "exp": 1708300800,
  "iat": 1708214400
}
```

### 6.2 Autorización (RBAC)

Ver ADR-003 para decisión completa.

**Roles MVP:**
- `Admin`: Permisos totales
- `User`: Permisos estándar

**Permission Classes (Django):**
```python
# core/permissions.py
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_admin

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.owner == request.user

class IsEmailVerified(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.email_verified_at is not None
```

**Extensibilidad futura:**
- Tabla `Permission` (name, codename)
- Tabla `Role` (name, permissions M2M)
- `User.roles` M2M
- Permite agregar roles (Reviewer, Moderator) sin cambiar código

### 6.3 Validación de Entrada

**Frontend:**
- Zod schemas para validación de formularios
- React Hook Form con resolver Zod

**Backend:**
- Django REST Framework Serializers
- Validaciones custom en `validate_<field>` methods
- Sanitización XSS (bleach para markdown)

**Ejemplo:**
```python
# apps/resources/serializers.py
class ResourceCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=5000)
    type = serializers.ChoiceField(choices=ResourceTypeChoices.choices)
    source_type = serializers.ChoiceField(choices=SourceTypeChoices.choices)
    content = serializers.CharField(required=False, allow_blank=True)
    repo_url = serializers.URLField(required=False, allow_blank=True)
    license = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(child=serializers.CharField(max_length=30), max_length=10)
    
    def validate(self, attrs):
        # Validación condicional
        if attrs['source_type'] == 'Internal' and not attrs.get('content'):
            raise serializers.ValidationError("Content is required for Internal resources")
        
        if attrs['source_type'] == 'GitHub-Linked':
            if not attrs.get('repo_url'):
                raise serializers.ValidationError("Repo URL is required for GitHub-linked resources")
            if not attrs.get('license'):
                raise serializers.ValidationError("License is required for GitHub-linked resources")
        
        return attrs
```

### 6.4 Rate Limiting

**Implementación:**
- Django-ratelimit library
- Decorators en views críticos

**Límites:**
- Login: 5 intentos / 15 min por IP
- Register: 3 cuentas / hora por IP
- Publish: 10 recursos / hora por usuario
- API general: 100 req / min por usuario autenticado, 20 req / min por IP anónima

**Ejemplo:**
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/15m', method='POST')
def login_view(request):
    # ...
```

### 6.5 CSRF Protection

**Django:**
- CSRF middleware habilitado por defecto
- CSRF token en formularios

**Next.js:**
- CSRF token en cookies
- Axios interceptor incluye token en headers

### 6.6 HTTPS

**Producción:**
- HTTPS obligatorio (Nginx + Let's Encrypt)
- HSTS header (Strict-Transport-Security)
- Secure cookies (`Secure`, `HttpOnly`, `SameSite=Lax`)

---

## 7. BASE DE DATOS

### 7.1 PostgreSQL Configuration

**Versión:** 15+

**Connection Pooling:**
- pgBouncer (opcional MVP, recomendado para producción)
- Django settings: `CONN_MAX_AGE = 600` (10 min)

**Backups:**
- Backup diario automático (pg_dump)
- Retención: 30 días
- Backup semanal completo (retención 6 meses)

### 7.2 Migraciones

**Estrategia:**
- Django migrations (evolutivo)
- Migraciones reversibles siempre que sea posible
- Squash migrations periódicamente (cada release mayor)

**Proceso:**
```bash
# Crear migración
python manage.py makemigrations

# Aplicar
python manage.py migrate

# Rollback (si es necesario)
python manage.py migrate <app> <migration_name>
```

### 7.3 Índices Críticos

Definidos en modelos, pero resumen:
- `User.email` (unique)
- `Resource.owner` + `Resource.created_at` (filtros comunes)
- `Resource.deleted_at` (soft delete queries)
- `ResourceVersion.resource_id` + `ResourceVersion.is_latest` (latest version lookup)
- `ResourceVersion.status` (filtros por Validated)
- `Vote.user_id` + `Vote.resource_id` (unique constraint + lookups)
- `Notification.user_id` + `Notification.read_at` (unread count)

---

## 8. INTEGRACIÓN CON SERVICIOS EXTERNOS

### 8.1 Email (SMTP)

**Proveedor:** TBD (SendGrid, Mailgun, o SMTP institucional)

**Uso:**
- Verificación de email
- Recuperación de contraseña
- (Post-MVP) Notificaciones por email

**Configuración:**
```python
# Django settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('SMTP_HOST')
EMAIL_PORT = env('SMTP_PORT')
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('SMTP_USER')
EMAIL_HOST_PASSWORD = env('SMTP_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@bioai.ccg.unam.mx'
```

**Templates:**
- HTML + texto plano (fallback)
- Variables: `{{user_name}}`, `{{verification_link}}`, etc.

### 8.2 GitHub API (Opcional MVP)

**Uso futuro:**
- Validar URLs de repositorio
- Webhook para sincronización automática
- Fetch README para preview

**MVP:** Solo validación básica de formato URL

### 8.3 Gravatar

**Uso:** Avatar por defecto basado en email

**Fallback:** Icono con iniciales si no tiene Gravatar

---

## 9. OBSERVABILIDAD Y LOGGING

### 9.1 Logging

**Formato:** JSON estructurado (facilita parsing)

**Niveles:**
- `DEBUG`: Development only
- `INFO`: Eventos normales (login, registro, publicación)
- `WARNING`: Eventos anormales pero manejables (rate limit alcanzado)
- `ERROR`: Errores inesperados (excepciones, API failures)
- `CRITICAL`: Fallos que requieren atención inmediata (BD down)

**Logs auditables (obligatorios):**
- Registro de usuario
- Verificación de email
- Login/logout
- Creación/edición/eliminación de recursos
- Validación/revocación de validación
- Acciones admin

**Ejemplo:**
```python
import logging
import json

logger = logging.getLogger(__name__)

def log_audit(action, user, resource=None, details=None):
    log_data = {
        'action': action,
        'user_id': str(user.id),
        'user_email': user.email,
        'resource_id': str(resource.id) if resource else None,
        'timestamp': datetime.now().isoformat(),
        'details': details
    }
    logger.info(json.dumps(log_data))
```

### 9.2 Métricas (Post-MVP)

**Herramientas:** Prometheus + Grafana

**Métricas clave:**
- Request rate (req/s)
- Error rate (%)
- Latency (p50, p95, p99)
- Usuarios activos (DAU, MAU)
- Recursos publicados por día
- Votos por día
- Forks por día

### 9.3 Monitoreo (MVP simple)

**Uptime check:** UptimeRobot o similar (ping a `/health` endpoint)

**Alertas:**
- Email a admin si uptime <95% en 24h
- Email si BD down

---

## 10. DEPLOYMENT

### 10.1 Contenedores (Docker)

**Servicios:**
- `frontend`: Next.js (Node 20)
- `backend`: Django + Gunicorn (Python 3.11)
- `db`: PostgreSQL 15
- `nginx`: Reverse proxy

**docker-compose.yml** (simplificado):
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    networks:
      - app-network

  backend:
    build: ./backend
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - SMTP_HOST=${SMTP_HOST}
    depends_on:
      - db
    networks:
      - app-network

  frontend:
    build: ./frontend
    command: npm run start
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=${API_URL}
    depends_on:
      - backend
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_volume:/static
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
    networks:
      - app-network

volumes:
  postgres_data:
  static_volume:

networks:
  app-network:
    driver: bridge
```

### 10.2 CI/CD

Ver `/docs/delivery/CI_CD.md` (FASE 8) para detalles completos.

**Pipeline básico (GitHub Actions):**
1. Lint (ESLint, Black, Flake8)
2. Tests (Jest, Pytest)
3. Build (Next.js, Django collectstatic)
4. Deploy (SSH a VPS, docker-compose up)

---

## 11. PERFORMANCE

### 11.1 Estrategias de Optimización

**Backend:**
- Query optimization (select_related, prefetch_related)
- Paginación estándar (20 items)
- Índices en BD (ver sección 7.3)
- Connection pooling (pgBouncer)

**Frontend:**
- Server-Side Rendering (SSR) para SEO
- Static Site Generation (SSG) para páginas estáticas (home)
- Code splitting (Next.js automático)
- Image optimization (next/image)
- React Query caching (stale-while-revalidate)

**Caching (Post-MVP):**
- Redis para caché de queries frecuentes (featured resources, user profiles)
- Django cache framework

### 11.2 NFRs Recordatorio

Ver PRD_REFINED.md sección 3:
- Tiempo de carga Explore <2s
- Tiempo respuesta API p95 <500ms
- Búsqueda/filtrado <1s
- Uptime ≥99%

---

## 12. TESTING

### 12.1 Pirámide de Tests

```
       /\
      /  \  E2E (1 test flujo principal)
     /    \
    /      \ Integration (API + DB)
   /        \
  /          \ Unit (lógica de negocio)
 /____________\
```

**Backend:**
- **Unit:** Services, utils, validators (pytest)
- **Integration:** API endpoints + DB (pytest + DRF test client)
- **Coverage target:** ≥70%

**Frontend:**
- **Unit:** Components, hooks, utils (Jest + React Testing Library)
- **Integration:** Forms con validación (opcional MVP)
- **Coverage target:** ≥60% (componentes críticos)

**E2E:**
- Playwright o Cypress
- 1 test del flujo E2E prioritario (Registro → Publicar → Validar → Reutilizar)

### 12.2 Estrategia de Mocking

**Backend:**
- Mock servicios externos (SMTP, GitHub API)
- Factory Boy para fixtures
- pytest fixtures para DB state

**Frontend:**
- Mock API calls (MSW - Mock Service Worker)
- Mock hooks de React Query

---

## 13. ESCALABILIDAD FUTURA

### 13.1 Preparación para Escalar (Post-MVP)

**Horizontal Scaling:**
- Backend stateless (JWT, no sessions en memoria)
- Múltiples instancias Django detrás de load balancer
- PostgreSQL replication (read replicas)

**Vertical Scaling:**
- Aumentar recursos VPS (CPU, RAM)
- Optimizar queries (EXPLAIN ANALYZE)

**Migración a Microservicios (si es necesario):**
1. Extraer módulo `notifications` como servicio independiente
2. Extraer `validation` (job Celery ya es semi-independiente)
3. API Gateway (Kong, AWS API Gateway)

---

## 14. RIESGOS ARQUITECTÓNICOS Y MITIGACIONES

### Riesgo 1: Monolito se vuelve acoplado
**Mitigación:**
- Enforcar separación de capas con code reviews
- Service layer independiente de HTTP
- Módulos con interfaces claras

### Riesgo 2: Performance de búsqueda con muchos recursos
**Mitigación:**
- Índices desde MVP
- Post-MVP: ElasticSearch para búsqueda full-text

### Riesgo 3: Versionado complejo genera bugs
**Mitigación:**
- Tests exhaustivos de casos de versionado
- Documentación clara del algoritmo
- ADR-002 documenta decisiones

---

## 15. ADRs RELACIONADOS

- [ADR-001: Autenticación con JWT](ADR-001-authentication.md)
- [ADR-002: Versionado de Recursos](ADR-002-versioning.md)
- [ADR-003: RBAC Extensible](ADR-003-rbac.md)

---

## 16. PRÓXIMOS PASOS

1. ✅ **ARCHITECTURE.md** (este documento)
2. ⏭️ Generar ADRs (ADR-001, ADR-002, ADR-003)
3. ⏭️ Crear diagrama de arquitectura (Mermaid) en `/diagrams/architecture.mmd`
4. ⏭️ Continuar con FASE 4 (Modelo de Datos + ERD)

---

**Documento completado:** 2026-02-16  
**Siguiente artefacto:** ADR-001-authentication.md  
**Rol siguiente:** Architect
