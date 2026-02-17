# ADR-001: Autenticación con JWT

**Estado:** Aceptado  
**Fecha:** 2026-02-16  
**Decisor(es):** Tech Lead, Security Engineer  
**Contexto:** FASE 3 — Diseño Técnico

---

## Contexto y Problema

BioAI Hub requiere un sistema de autenticación que:
1. Sea stateless para permitir escalabilidad horizontal
2. Funcione bien con arquitectura frontend (Next.js) + backend (Django) separados
3. Permita autenticación en API REST
4. Sea seguro contra ataques comunes (XSS, CSRF)
5. Soporte refresh tokens para mejor UX (opcional MVP)

**Decisión requerida:** ¿Qué mecanismo de autenticación usar?

---

## Opciones Consideradas

### Opción 1: Django Sessions (Cookies)
**Descripción:** Usar sistema de sessions nativo de Django con cookies

**Pros:**
- Nativo de Django, sin librerías adicionales
- CSRF protection built-in
- Revocación inmediata (eliminar sesión en BD)

**Contras:**
- Stateful (sesiones en BD o caché)
- Dificulta escalabilidad horizontal
- No ideal para separación frontend/backend
- Requiere sticky sessions si múltiples instancias

### Opción 2: JWT (JSON Web Tokens)
**Descripción:** Tokens firmados (HS256 o RS256) con claims del usuario

**Pros:**
- Stateless (no requiere DB lookup en cada request)
- Ideal para arquitecturas separadas (frontend/backend)
- Escalabilidad horizontal sin complicaciones
- Standard de industria (RFC 7519)
- Permite múltiples clients (web, mobile futuro)

**Contras:**
- No revocable inmediatamente (hasta que expire)
- Requiere estrategia de refresh tokens
- Tokens largos en headers

### Opción 3: OAuth2 / OpenID Connect
**Descripción:** Delegar autenticación a proveedor externo (Google, GitHub)

**Pros:**
- No manejo de contraseñas
- SSO institucional (Google Workspace UNAM)
- Experiencia de usuario familiar

**Contras:**
- Dependencia de servicio externo
- Complejidad adicional en MVP
- Requiere configuración institucional (aprobaciones)

---

## Decisión

**Elegimos: Opción 2 — JWT con Access Token + Refresh Token (opcional MVP)**

**Justificación:**
1. **Stateless:** Facilita escalabilidad horizontal sin sticky sessions
2. **Arquitectura desacoplada:** Ideal para Next.js (frontend) + Django (backend)
3. **Standard:** Django REST Framework tiene soporte maduro (djangorestframework-simplejwt)
4. **Futuro-proof:** Permitirá agregar mobile app sin cambios
5. **MVP simple:** Access token suficiente, refresh token post-MVP

---

## Implementación Detallada

### 1. Librería: `djangorestframework-simplejwt`

```bash
pip install djangorestframework-simplejwt
```

### 2. Configuración Django

```python
# config/settings/base.py

INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),  # 24h para MVP
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # 7 días (post-MVP)
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,  # Requiere tabla blacklist
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('SECRET_KEY'),  # Django SECRET_KEY
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
```

### 3. Claims Personalizados

```python
# apps/authentication/serializers.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Claims personalizados
        token['email'] = user.email
        token['is_admin'] = user.is_admin
        token['email_verified'] = user.email_verified_at is not None
        
        return token
```

### 4. Endpoints de Autenticación

```python
# apps/authentication/urls.py

from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Post-MVP
    path('logout/', LogoutView.as_view(), name='logout'),  # Blacklist token
]
```

### 5. Frontend: Almacenamiento del Token

**Opción A: httpOnly Cookie (RECOMENDADO para MVP)**

```typescript
// Next.js API Route: /api/auth/login
export async function POST(request: Request) {
  const { email, password } = await request.json();
  
  // Call Django API
  const response = await fetch(`${process.env.DJANGO_API_URL}/api/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  
  if (response.ok) {
    const data = await response.json();
    
    // Store token in httpOnly cookie
    const res = NextResponse.json({ success: true });
    res.cookies.set('access_token', data.access, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24, // 24h
    });
    
    return res;
  }
  
  return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 });
}
```

**Opción B: localStorage (Alternativa, más simple pero menos seguro)**

```typescript
// lib/api/auth.ts
export async function login(email: string, password: string) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return { success: true };
  }
  
  return { success: false, error: await response.json() };
}
```

### 6. Frontend: Interceptor Axios

```typescript
// lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Request interceptor: incluir token
apiClient.interceptors.request.use((config) => {
  // Opción A: Cookie automática (httpOnly)
  // No hacer nada, el browser envía cookie automáticamente
  
  // Opción B: localStorage
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
});

// Response interceptor: manejar 401 (token expirado)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Logout y redirect a login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

## Seguridad

### 1. Protección contra XSS
**Mitigación:**
- Usar httpOnly cookies (token no accesible desde JavaScript)
- Sanitizar inputs (evitar inyección de scripts)
- CSP headers (Content Security Policy)

### 2. Protección contra CSRF
**Mitigación:**
- Si usa httpOnly cookies: Incluir CSRF token en requests de mutación
- Django CSRF middleware habilitado
- SameSite=Lax en cookies

### 3. Token Leakage
**Mitigación:**
- HTTPS obligatorio en producción
- Tokens con tiempo de expiración corto (24h)
- No loggear tokens
- No incluir información sensible en claims

### 4. Revocación de Tokens

**Problema:** JWT no es revocable inmediatamente (stateless)

**Mitigaciones:**
1. **Token blacklist (djangorestframework-simplejwt):**
   - Tabla `TokenBlacklist` en BD
   - En logout, agregar token a blacklist
   - Middleware chequea blacklist en cada request

2. **Expiración corta + Refresh Token:**
   - Access token corto (1h post-MVP)
   - Refresh token largo (7d)
   - Renovación silenciosa en frontend

3. **Cambio de SECRET_KEY (emergencia):**
   - Invalida todos los tokens activos
   - Usuarios deben login nuevamente

---

## Flujo Completo de Autenticación

### Registro
```
User → Frontend (register form)
     → Next.js API route
     → Django POST /api/auth/register
     → Crea User (email_verified_at = NULL)
     → Envía email con token de verificación
     ← 201 Created
     ← Redirect a "Verify Email" screen
```

### Verificación Email
```
User → Click link en email
     → Next.js page /verify-email/:token
     → Django GET /api/auth/verify-email/:token
     → Valida token, actualiza email_verified_at
     ← 200 OK
     ← Redirect a /login
```

### Login
```
User → Frontend (login form)
     → Next.js API route /api/auth/login
     → Django POST /api/auth/login
     → Valida credenciales
     → Verifica email_verified_at IS NOT NULL
     → Genera JWT con claims custom
     ← 200 OK + { access, refresh }
     → Next.js guarda access en httpOnly cookie
     ← Frontend actualiza AuthContext
     ← Redirect a intended route o dashboard
```

### Request Autenticado
```
User → Frontend (action: publish resource)
     → Axios POST /api/resources
     → Browser incluye cookie automáticamente
     → Django JWT middleware valida token
     → Extrae user_id del claim
     → Ejecuta view con request.user poblado
     ← 201 Created
```

### Logout
```
User → Frontend (click logout)
     → Next.js API route /api/auth/logout
     → Django POST /api/auth/logout (agrega token a blacklist)
     → Next.js elimina cookie
     → Frontend limpia AuthContext
     ← Redirect a home público
```

---

## Alternativas Descartadas y Por Qué

### Por qué NO Django Sessions:
- Stateful, dificulta escalabilidad horizontal
- Requiere BD o caché compartido entre instancias
- Sticky sessions complejizan load balancing

### Por qué NO OAuth2 (MVP):
- Complejidad adicional innecesaria para MVP
- Requiere aprobaciones institucionales (Google Workspace UNAM)
- Dependencia de servicio externo
- **Post-MVP:** Agregar como opción adicional (no reemplazo)

### Por qué HS256 y NO RS256:
- **HS256 (HMAC):** Symmetric, misma clave para firmar y verificar
  - Más simple para monolito
  - Backend genera y verifica tokens
- **RS256 (RSA):** Asymmetric, clave privada (firma) y pública (verifica)
  - Útil si múltiples servicios validan tokens
  - Overhead innecesario en MVP monolítico

**Decisión:** HS256 para MVP, considerar RS256 si migra a microservicios

---

## Métricas de Éxito

- ✅ Login exitoso en <2s (p95)
- ✅ Token válido por 24h sin relogin
- ✅ 0 incidentes de seguridad (XSS, CSRF) en primeros 3 meses
- ✅ Rate limiting funciona (5 intentos fallidos / 15 min)

---

## Extensiones Futuras (Post-MVP)

1. **Refresh Token automático:**
   - Access token corto (1h)
   - Refresh token largo (7d)
   - Renovación silenciosa en frontend

2. **OAuth2 / SSO institucional:**
   - Login con Google Workspace UNAM
   - Coexiste con login tradicional

3. **Two-Factor Authentication (2FA):**
   - TOTP (Google Authenticator)
   - Obligatorio para Admins

4. **Session Management:**
   - Ver sesiones activas en /profile/settings
   - Cerrar sesiones remotas

---

## Referencias

- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [djangorestframework-simplejwt Docs](https://django-rest-framework-simplejwt.readthedocs.io/)
- [OWASP: JWT Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

---

**Decisión aprobada:** 2026-02-16  
**Implementación:** FASE 7 (Backend MVP)  
**Próximo ADR:** ADR-002 (Versionado de Recursos)
