# BioAI Hub — Institutional AI Repository

**Proyecto:** Plataforma institucional para gestión, validación y reutilización de recursos de IA en bioinformática  
**Institución:** Centro de Ciencias Genómicas (CCG), UNAM  
**Dominio:** bioai.ccg.unam.mx  
**Versión:** 1.0.0 (MVP)

---

## 📋 Descripción

BioAI Hub es una plataforma web que permite a investigadores del CCG:
- 📝 Publicar recursos de IA (prompts, workflows, notebooks, modelos)
- ✅ Validar calidad mediante revisión institucional o métricas comunitarias
- 🔄 Reutilizar recursos con trazabilidad (fork con derivación)
- 🔍 Explorar catálogo con búsqueda, filtros y versionado semántico

---

## 🏗️ Arquitectura

**Stack Tecnológico:**
- **Frontend:** Next.js 14 (App Router) + React 18 + TypeScript + Tailwind CSS
- **Backend:** Django 5 + Django REST Framework (DRF)
- **Database:** PostgreSQL 15+
- **Auth:** JWT (djangorestframework-simplejwt)
- **Infrastructure:** Docker + Nginx
- **CI/CD:** GitHub Actions

**Arquitectura:** Monolítica Modular (backend modularizado por dominios)

Más detalles: [`/docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md)

---

## 📁 Estructura del Repositorio

```
plataforma_ia/
├── backend/                      # Django + DRF backend
│   ├── apps/
│   │   ├── authentication/       # Users, roles, JWT
│   │   ├── resources/            # Resources, versions
│   │   ├── interactions/         # Votes, forks
│   │   ├── validation/           # Validation workflow
│   │   └── notifications/        # In-app notifications
│   ├── config/                   # Django settings
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                     # Next.js frontend
│   ├── app/                      # App Router pages
│   ├── components/               # React components
│   ├── lib/                      # Utilities, API client
│   ├── public/                   # Static assets
│   ├── package.json
│   └── Dockerfile
├── docs/                         # Documentación técnica
│   ├── product/                  # PRD, roadmap, historias
│   ├── architecture/             # Arquitectura, ADRs
│   ├── data/                     # Modelo de datos, ERD
│   ├── api/                      # OpenAPI spec
│   ├── quality/                  # Testing strategy, BDD
│   ├── ux/                       # UX flows, UI states
│   └── ai/                       # AI usage log
├── orchestration/                # Protocolo de desarrollo
├── docker-compose.yml            # Orquestación de servicios
├── Makefile                      # Comandos comunes
├── .github/
│   └── workflows/                # CI/CD pipelines
├── AGENTS.md                     # Convenciones del proyecto
└── README.md                     # Este archivo
```

---

## 🚀 Quick Start

### Prerequisitos

- Docker 24+ y Docker Compose 2+
- (Opcional) Python 3.11+ y Node 20+ para desarrollo local sin Docker

### 1. Clonar el repositorio

```bash
git clone https://github.com/ccg-unam/plataforma_ia.git
cd plataforma_ia
```

### 2. Configurar variables de entorno

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

Editar `.env` con tus credenciales (ver sección Variables de Entorno).

### 3. Iniciar con Docker Compose

```bash
# Construir e iniciar todos los servicios
docker-compose up --build

# O usar Makefile
make dev
```

**Servicios disponibles:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Django: http://localhost:8000/admin
- PostgreSQL: localhost:5432

### 4. Ejecutar migraciones y crear superusuario

```bash
# Migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser

# Seed roles iniciales (Admin, User)
docker-compose exec backend python manage.py seed_roles
```

---

## 🛠️ Comandos Disponibles (Makefile)

```bash
# Desarrollo
make dev              # Iniciar todos los servicios
make dev-backend      # Solo backend + DB
make dev-frontend     # Solo frontend

# Tests
make test             # Todos los tests
make test-backend     # Backend (pytest)
make test-frontend    # Frontend (Jest)
make test-e2e         # E2E (Playwright)

# Linting
make lint             # Lint backend + frontend
make format           # Format código (black, prettier)

# Base de datos
make migrate          # Ejecutar migraciones
make makemigrations   # Crear migraciones
make seed             # Seed data de prueba

# Limpieza
make clean            # Limpiar containers y volumes
make reset-db         # Reset completo de BD
```

---

## 📚 Documentación

### Producto
- [PRD Refined](docs/product/PRD_REFINED.md) — Requisitos funcionales detallados
- [Roadmap](docs/product/ROADMAP.md) — Fases MVP → Expansión → Inteligencia
- [Épicas y Historias](docs/product/EPICS_AND_STORIES.md) — 10 historias Must-Have
- [Flujo E2E Prioritario](docs/product/E2E_PRIORITY_FLOW.md) — Journey del usuario

### Arquitectura
- [Arquitectura General](docs/architecture/ARCHITECTURE.md) — Diseño de alto nivel
- [ADR-001: Autenticación JWT](docs/architecture/ADR-001-authentication.md)
- [ADR-002: Versionado de Recursos](docs/architecture/ADR-002-versioning.md)
- [ADR-003: RBAC](docs/architecture/ADR-003-rbac.md)

### Datos
- [Modelo de Datos](docs/data/DATA_MODEL.md) — Schema PostgreSQL completo
- [ERD (Mermaid)](docs/data/diagrams/er.mmd) — Diagrama de entidades

### API
- [OpenAPI Spec](docs/api/openapi.yaml) — Especificación completa de endpoints

### Calidad
- [Estrategia de Testing](docs/quality/TEST_STRATEGY.md) — Pirámide de tests
- [BDD Features](docs/quality/BDD_FEATURES.feature) — Gherkin scenarios
- [Plan E2E](docs/quality/E2E_PLAN.md) — Playwright tests

### UX
- [Flujo de Navegación](docs/ux/NAVIGATION_FLOW.md) — User flows por rol
- [Estados UI](docs/ux/UI_STATES.md) — 50+ estados por pantalla

---

## 🧪 Testing

### Backend (pytest)

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=apps --cov-report=html

# Solo unit tests
pytest apps/resources/tests/test_services.py

# BDD features
pytest --gherkin-terminal-reporter
```

**Target:** ≥70% coverage

### Frontend (Jest)

```bash
cd frontend/

# Todos los tests
npm test

# Con cobertura
npm test -- --coverage

# Watch mode
npm test -- --watch
```

**Target:** ≥60% coverage

### E2E (Playwright)

```bash
cd frontend/

# Ejecutar E2E
npm run test:e2e

# Con UI (debugging)
npm run test:e2e:ui

# Ver reporte
npm run test:e2e:report
```

---

## 🔐 Variables de Entorno

### Backend (`backend/.env`)

```env
# Django
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/bioai_dev

# JWT
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ACCESS_TOKEN_LIFETIME=1440  # 24 horas (minutos)
JWT_REFRESH_TOKEN_LIFETIME=10080  # 7 días (minutos)

# Email (para verificación)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # Dev: imprime en consola
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend  # Prod
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@example.com
# EMAIL_HOST_PASSWORD=your-password

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Rate Limiting
RATELIMIT_ENABLE=True
```

### Frontend (`frontend/.env.local`)

```env
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Public URL
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

⚠️ **Importante:** NUNCA commitear archivos `.env` con secretos reales. Usar `.env.example` como template.

---

## 📦 Dependencias Principales

### Backend

```txt
Django==5.0+
djangorestframework==3.14+
djangorestframework-simplejwt==5.3+
psycopg2-binary==2.9+
django-cors-headers==4.3+
django-ratelimit==4.1+
pytest==7.4+
pytest-django==4.5+
factory-boy==3.3+
```

### Frontend

```json
{
  "next": "^14.0.0",
  "react": "^18.0.0",
  "typescript": "^5.0.0",
  "tailwindcss": "^3.0.0",
  "axios": "^1.6.0",
  "@playwright/test": "^1.40.0"
}
```

---

## 🤝 Contribución

### Workflow

1. **Crear issue** en GitHub con formato `T-xxx — <título>`
2. **Referenciar historia** `US-xx` correspondiente
3. **Branch:** `feature/T-xxx-descripcion` o `fix/T-xxx-descripcion`
4. **Commits:** `T-xxx: <mensaje>` (formato convencional)
5. **Tests:** Todos los tests deben pasar (unit + integration + E2E)
6. **PR:** Incluir checklist de DoD (ver `AGENTS.md`)

### Definition of Done

✅ Criterios de aceptación cumplidos (Given/When/Then)  
✅ Tests escritos (unit + integration si aplica)  
✅ Coverage ≥70% backend, ≥60% frontend  
✅ Linter pasando (black, flake8, ESLint)  
✅ Documentación actualizada (si cambia comportamiento)  
✅ Code review aprobado  
✅ E2E test actualizado (si aplica al flujo principal)

Ver [`AGENTS.md`](AGENTS.md) para más detalles.

---

## 🚢 Deployment

### Staging

```bash
# Construir imágenes de producción
docker-compose -f docker-compose.prod.yml build

# Deploy a staging
make deploy-staging
```

### Production

```bash
# Deploy a bioai.ccg.unam.mx
make deploy-production
```

Más detalles: [`/docs/delivery/RELEASE_PLAN.md`](docs/delivery/RELEASE_PLAN.md) (pendiente en FASE 8)

---

## 📊 Estado del Proyecto

**Fase actual:** FASE 7 — Implementación (Setup)

| Fase | Estado |
|---|---|
| ✅ FASE 1: Auditoría | Completa |
| ✅ FASE 2: Refinamiento de Producto | Completa |
| ✅ FASE 2.5: UX State Formalization | Completa |
| ✅ FASE 3: Arquitectura | Completa |
| ✅ FASE 4: Modelo de Datos | Completa |
| ✅ FASE 5: API | Completa |
| ✅ FASE 6: Calidad y Testing | Completa |
| 🚧 FASE 7: Implementación | En progreso (Setup) |
| ⏳ FASE 8: Infraestructura | Pendiente |

**Progreso documentación:** 12,000+ líneas de docs técnicas generadas

---

## 📝 Licencia

[Pendiente definir con institución CCG]

---

## 👥 Equipo

**Institución:** Centro de Ciencias Genómicas (CCG), UNAM  
**Contacto:** [Pendiente]

---

## 🔗 Enlaces Útiles

- **Documentación completa:** [`/docs`](docs/)
- **Protocolo de desarrollo:** [`/orchestration/ORCHESTRATOR_MASTER.md`](orchestration/ORCHESTRATOR_MASTER.md)
- **Convenciones:** [`AGENTS.md`](AGENTS.md)
- **Issues/Tickets:** [GitHub Issues](https://github.com/ccg-unam/plataforma_ia/issues)

---

**Última actualización:** 2026-02-16  
**Versión README:** 1.0
