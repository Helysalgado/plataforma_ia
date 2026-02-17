# IMPLEMENTATION SETUP — BioAI Hub

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Versión:** 1.0  
**Fecha:** 2026-02-16  
**Fase:** FASE 7 — Implementación (Setup)  
**Rol activo:** Backend Engineer + Frontend Engineer + DevOps

---

## 1. OBJETIVO

Documentar el setup inicial del repositorio, estructura de directorios, y configuración del ambiente de desarrollo.

---

## 2. ESTRUCTURA DEL REPOSITORIO (GENERADA)

```
plataforma_ia/
├── backend/                      # Django + DRF Backend
│   ├── apps/
│   │   ├── authentication/       # Users, roles, JWT (pendiente implementar)
│   │   ├── resources/            # Resources, versions (pendiente implementar)
│   │   ├── interactions/         # Votes, forks (pendiente implementar)
│   │   ├── validation/           # Validation workflow (pendiente implementar)
│   │   └── notifications/        # In-app notifications (pendiente implementar)
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py           # ✅ Settings base
│   │   │   ├── development.py   # ✅ Dev settings
│   │   │   ├── production.py    # ✅ Prod settings
│   │   │   └── test.py           # ✅ Test settings
│   │   ├── urls.py               # ✅ URL routing
│   │   ├── wsgi.py               # ✅ WSGI config
│   │   ├── asgi.py               # ✅ ASGI config
│   │   └── exceptions.py         # ✅ Custom exception handler
│   ├── tests/                    # Global tests
│   ├── manage.py                 # ✅ Django management
│   ├── requirements.txt          # ✅ Python dependencies
│   ├── .env.example              # ✅ Environment template
│   ├── pytest.ini                # ✅ Pytest config
│   ├── .flake8                   # ✅ Flake8 config
│   ├── pyproject.toml            # ✅ Black/isort config
│   ├── Dockerfile                # ✅ Docker image
│   └── .gitignore                # ✅ Git ignore
├── frontend/                     # Next.js Frontend
│   ├── app/
│   │   ├── layout.tsx            # ✅ Root layout
│   │   ├── page.tsx              # ✅ Home page (placeholder)
│   │   └── globals.css           # ✅ Global styles
│   ├── components/               # React components (pendiente)
│   ├── lib/                      # Utilities, API client (pendiente)
│   ├── public/                   # Static assets
│   ├── styles/
│   │   └── globals.css           # ✅ Tailwind base
│   ├── e2e/                      # E2E tests (pendiente)
│   ├── package.json              # ✅ NPM dependencies
│   ├── .env.example              # ✅ Environment template
│   ├── next.config.js            # ✅ Next.js config
│   ├── tsconfig.json             # ✅ TypeScript config
│   ├── tailwind.config.js        # ✅ Tailwind config
│   ├── jest.config.js            # ✅ Jest config
│   ├── jest.setup.ts             # ✅ Jest setup
│   ├── playwright.config.ts     # ✅ Playwright config
│   ├── .eslintrc.json            # ✅ ESLint config
│   ├── .prettierrc               # ✅ Prettier config
│   ├── Dockerfile                # ✅ Docker image
│   └── .gitignore                # ✅ Git ignore
├── docs/                         # ✅ Documentación técnica completa
│   ├── product/                  # PRD, roadmap, historias
│   ├── architecture/             # Arquitectura, ADRs
│   ├── data/                     # Modelo de datos, ERD
│   ├── api/                      # OpenAPI spec
│   ├── quality/                  # Testing strategy, BDD
│   ├── ux/                       # UX flows, UI states
│   └── ai/                       # AI usage log
├── orchestration/                # ✅ Protocolo de desarrollo
├── docker-compose.yml            # ✅ Orquestación de servicios
├── Makefile                      # ✅ Comandos comunes
├── .github/
│   └── workflows/                # CI/CD pipelines (pendiente FASE 8)
├── AGENTS.md                     # ✅ Convenciones del proyecto
└── README.md                     # ✅ Documentación principal
```

---

## 3. TECNOLOGÍAS CONFIGURADAS

### 3.1 Backend (Django)

**Framework:**
- Django 5.0.1
- Django REST Framework 3.14.0
- djangorestframework-simplejwt 5.3.1 (JWT auth)

**Database:**
- PostgreSQL 15 (via Docker)
- psycopg2-binary 2.9.9

**Testing:**
- pytest 7.4.3
- pytest-django 4.7.0
- pytest-cov 4.1.0
- pytest-bdd 6.1.1
- factory-boy 3.3.0

**Code Quality:**
- black 23.12.1 (formatter)
- flake8 6.1.0 (linter)
- isort 5.13.2 (import sorter)

**Production:**
- gunicorn 21.2.0 (WSGI server)
- whitenoise 6.6.0 (static files)

---

### 3.2 Frontend (Next.js)

**Framework:**
- Next.js 14.1.0
- React 18.2.0
- TypeScript 5.3.3

**Styling:**
- Tailwind CSS 3.4.1
- PostCSS 8.4.33
- Autoprefixer 10.4.17

**HTTP Client:**
- axios 1.6.5

**Testing:**
- Jest 29.7.0
- React Testing Library 14.1.2
- @testing-library/user-event 14.5.2
- MSW 2.0.13 (API mocking)
- Playwright 1.41.0 (E2E)

**Code Quality:**
- ESLint 8.56.0
- Prettier 3.2.4

---

### 3.3 Infrastructure

**Containerization:**
- Docker 24+
- Docker Compose 2+

**Database:**
- PostgreSQL 15-alpine

**Reverse Proxy (Producción):**
- Nginx (pendiente configurar en FASE 8)

---

## 4. CONFIGURACIÓN INICIAL

### 4.1 Variables de Entorno

**Backend (`backend/.env`):**
```bash
cp backend/.env.example backend/.env
```

Editar `backend/.env`:
```env
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
DATABASE_URL=postgresql://postgres:postgres@db:5432/bioai_dev
JWT_SECRET_KEY=tu-jwt-secret-aqui
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend (`frontend/.env.local`):**
```bash
cp frontend/.env.example frontend/.env.local
```

Editar `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

---

### 4.2 Iniciar Servicios con Docker

```bash
# Construir e iniciar todos los servicios
docker-compose up --build

# O usar Makefile
make dev
```

**Servicios disponibles:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin
- PostgreSQL: localhost:5432

---

### 4.3 Ejecutar Migraciones (Primera Vez)

```bash
# Esperar a que los servicios estén up
sleep 10

# Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser
```

---

## 5. PRÓXIMOS PASOS (FASE 7 — IMPLEMENTACIÓN)

### 5.1 Backend: Implementar Apps

**Orden recomendado:**
1. **`apps.authentication`** (US-01, US-02)
   - Model: User, Role, UserRole
   - Services: AuthService (register, login, verify_email)
   - Views: RegisterView, LoginView, VerifyEmailView
   - Serializers: UserSerializer, RegisterSerializer, LoginSerializer
   - Tests: unit (service) + integration (API)

2. **`apps.resources`** (US-05, US-06, US-07, US-08)
   - Model: Resource, ResourceVersion
   - Services: ResourceService, VersioningService
   - Views: ResourceViewSet
   - Serializers: ResourceSerializer, ResourceVersionSerializer
   - Tests: unit + integration

3. **`apps.interactions`** (US-16, US-17)
   - Model: Vote
   - Services: VoteService, ForkService
   - Views: VoteView, ForkView
   - Tests: unit + integration

4. **`apps.validation`** (US-13, US-14, US-15)
   - Services: ValidationService, AutoPromotionService
   - Views: ValidateView, RevokeValidationView
   - Management Command: `promote_resources` (cron job)
   - Tests: unit + integration

5. **`apps.notifications`** (US-18)
   - Model: Notification
   - Services: NotificationService
   - Views: NotificationViewSet
   - Tests: unit + integration

---

### 5.2 Frontend: Implementar Páginas

**Orden recomendado:**
1. **Auth Pages** (US-01, US-02)
   - `/register` (RegisterPage)
   - `/login` (LoginPage)
   - `/verify-email/[token]` (VerifyEmailPage)

2. **Core Pages** (US-05, US-06, US-07)
   - `/` (HomePage con featured resources)
   - `/explore` (ExplorePage con búsqueda y filtros)
   - `/resources/[id]` (ResourceDetailPage)

3. **Publish Page** (US-08)
   - `/publish` (PublishPage con formulario)

4. **Profile Pages**
   - `/profile` (UserProfilePage)
   - `/profile/resources` (MyResourcesPage)

5. **Notifications** (US-18)
   - Notification Bell (component)
   - Notification Panel (component)

---

### 5.3 Componentes Compartidos

**UI Components:**
- `Button`
- `Input`, `Textarea`, `Select`
- `Badge` (Sandbox, Validated, Pending Validation)
- `Card` (ResourceCard)
- `Modal`
- `Toast` (success/error messages)
- `Skeleton` (loading states)

**Layout Components:**
- `Navbar` (con auth state)
- `Sidebar` (navegación)
- `Footer`

**Feature Components:**
- `VoteButton`
- `ReuseButton`
- `ShareButton`
- `ValidationBadge`
- `ResourceStats` (votes, forks, views)

---

### 5.4 API Client (Frontend)

**Estructura:**
```
frontend/lib/
├── api/
│   ├── client.ts            # Axios instance con interceptors
│   ├── auth.ts              # Auth endpoints
│   ├── resources.ts         # Resources endpoints
│   ├── notifications.ts     # Notifications endpoints
│   └── types.ts             # TypeScript types
├── hooks/
│   ├── useAuth.ts           # Auth hook (context)
│   ├── useResource.ts       # Resource hook
│   └── useNotifications.ts  # Notifications hook
└── utils/
    ├── format.ts            # Date, number formatting
    └── validation.ts        # Form validation helpers
```

---

## 6. ESTRATEGIA DE IMPLEMENTACIÓN (TDD)

### 6.1 Ciclo TDD por Historia

Para cada historia (US-xx):

1. **Leer criterios de aceptación** (EPICS_AND_STORIES.md)
2. **Escribir tests** (unit + integration) basados en criterios Given/When/Then
3. **Implementar código** hasta que los tests pasen
4. **Refactorizar** si es necesario
5. **Verificar coverage** (≥70% backend, ≥60% frontend)
6. **Actualizar E2E test** si aplica al flujo principal

---

### 6.2 Orden de Implementación (Historias)

**Sprint 1 (Autenticación y Exploración):**
- US-01: Registro de usuario
- US-02: Login
- US-05: Explorar recursos (lista con paginación)
- US-06: Buscar y filtrar recursos

**Sprint 2 (Publicación y Detalle):**
- US-07: Ver detalle de recurso
- US-08: Publicar recurso

**Sprint 3 (Interacciones):**
- US-16: Votar recurso
- US-17: Reutilizar (Fork) recurso

**Sprint 4 (Validación y Notificaciones):**
- US-13: Validar recurso (Admin)
- US-18: Notificaciones in-app

**Sprint 5 (Features Avanzadas - Should-Have):**
- US-14: Promoción automática
- US-15: Revocar validación
- US-20: Editar recurso con versionado

---

## 7. COMANDOS ÚTILES (Makefile)

```bash
# Desarrollo
make dev              # Iniciar todos los servicios
make stop             # Detener servicios
make down             # Detener y remover containers

# Base de datos
make migrate          # Ejecutar migraciones
make makemigrations   # Crear migraciones
make seed             # Seed data de prueba
make reset-db         # Reset completo de BD

# Testing
make test             # Todos los tests
make test-backend     # Backend (pytest)
make test-frontend    # Frontend (Jest)
make test-e2e         # E2E (Playwright)

# Linting
make lint             # Lint backend + frontend
make format           # Format código (black, prettier)

# Logs
make logs             # Logs de todos los servicios
make logs-backend     # Solo backend
make logs-frontend    # Solo frontend
```

---

## 8. CHECKLIST DE SETUP

### ✅ Estructura de Repositorio
- [x] Backend: estructura de apps creada
- [x] Backend: configuración Django (settings, urls, wsgi, asgi)
- [x] Backend: requirements.txt con todas las dependencias
- [x] Backend: Dockerfile y .gitignore
- [x] Frontend: estructura de Next.js App Router creada
- [x] Frontend: package.json con todas las dependencias
- [x] Frontend: Configuración TypeScript, Tailwind, Jest, Playwright
- [x] Frontend: Dockerfile y .gitignore
- [x] docker-compose.yml con 3 servicios (db, backend, frontend)
- [x] Makefile con comandos comunes
- [x] README.md principal actualizado

### ⏳ Pendiente (Siguiente)
- [ ] Backend: Implementar models (User, Resource, etc.)
- [ ] Backend: Implementar services (AuthService, ResourceService, etc.)
- [ ] Backend: Implementar views/viewsets (DRF)
- [ ] Backend: Implementar serializers
- [ ] Backend: Implementar tests (unit + integration)
- [ ] Frontend: Implementar componentes UI base
- [ ] Frontend: Implementar API client con Axios
- [ ] Frontend: Implementar páginas (register, login, explore, etc.)
- [ ] Frontend: Implementar tests (unit + E2E)
- [ ] FASE 8: CI/CD con GitHub Actions
- [ ] FASE 8: Nginx configuración para producción
- [ ] FASE 8: Deploy a bioai.ccg.unam.mx

---

## 9. MÉTRICAS DE SETUP

| Métrica | Valor |
|---|---|
| **Archivos generados** | 30+ archivos |
| **Líneas de configuración** | ~1500 líneas |
| **Tiempo de generación** | ~30 minutos (con IA) |
| **Tiempo estimado manual** | ~4-6 horas |
| **Aceleración** | **8-12x** |

---

## 10. SIGUIENTES PASOS INMEDIATOS

1. **Instalar dependencias** (si desarrollo local sin Docker):
   ```bash
   make install
   ```

2. **Iniciar servicios**:
   ```bash
   make dev
   ```

3. **Verificar servicios**:
   - Frontend: http://localhost:3000 (debe mostrar "BioAI Hub — Coming Soon")
   - Backend: http://localhost:8000/admin (Django admin - requiere migrations)

4. **Ejecutar migraciones iniciales**:
   ```bash
   make migrate
   ```

5. **Comenzar implementación de US-01 (Registro)** siguiendo TDD:
   - Escribir tests en `backend/apps/authentication/tests/test_auth_service.py`
   - Implementar modelo `User` en `backend/apps/authentication/models.py`
   - Implementar service `AuthService` en `backend/apps/authentication/services.py`
   - Implementar view `RegisterView` en `backend/apps/authentication/views.py`

---

**Documento completado:** 2026-02-16  
**Siguiente paso:** Implementación de historias (US-01 → US-18)  
**Fase siguiente:** FASE 8 — Infraestructura y Deployment
