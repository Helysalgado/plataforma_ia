# AGENTS.md — Plataforma CCG IA (Next.js + Django + Postgres)

Este archivo define **cómo deben trabajar los agentes** (humanos o IA) en este repositorio.
Es la **fuente de verdad** para convenciones, flujo de trabajo, calidad y entrega.

## 0) Principios
- **MVP primero**: evitar sobreingeniería; modularidad sí, microservicios no en MVP.
- **Spec-Driven + TDD**: especificación y tests antes/ junto al código.
- **Decisiones registradas**: cada decisión relevante -> ADR.
- **Seguridad por defecto**: mínimos privilegios, secrets fuera del repo, auditoría.
- **Trazabilidad total**: PRD → épicas → historias → tickets → commits → tests.

## 1) Roles (agentes) y responsabilidades
### 1. Product Manager (PM)
- Mantiene `/docs/product/PRD_REFINED.md`, `/docs/product/ROADMAP.md`
- Define épicas, historias, criterios de aceptación y prioridades.

### 2. UX/Analyst
- Aporta journeys, edge cases, copy y criterios Given/When/Then.
- Mantiene `/docs/product/EPICS_AND_STORIES.md`

### 3. Tech Lead / Architect
- Mantiene arquitectura y decisiones:
  - `/docs/architecture/ARCHITECTURE.md`
  - `/docs/architecture/ADR-*.md`
  - Diagramas DaC: `/docs/architecture/diagrams/*`
- Controla riesgos, NFRs, modularización, patrones.

### 4. Backend Engineer (Python/Django/DRF)
- Implementa modelos, servicios, endpoints, validaciones.
- Mantiene:
  - `/docs/api/openapi.yaml` (o `/docs/api/OPENAPI.md`)
  - tests unit/integration (pytest)

### 5. Frontend Engineer (Next.js)
- Implementa flujo E2E navegable.
- Mantiene componentes, páginas, state management, accesibilidad.
- tests unit (jest) e integración (si aplica).

### 6. QA / Testing Engineer
- Define estrategia de pruebas y calidad:
  - `/docs/quality/TEST_STRATEGY.md`
  - `/docs/quality/BDD_FEATURES.feature`
  - `/docs/quality/E2E_PLAN.md`
- Asegura al menos 1 test E2E del flujo principal.

### 7. DevOps / Platform Engineer
- Docker, CI/CD, entornos, secretos, backups, observabilidad.
- Mantiene:
  - `/docs/delivery/CI_CD.md`
  - `/docs/delivery/RELEASE_PLAN.md`

## 2) Flujo de trabajo (obligatorio)
1) **Auditoría → Refinamiento → Diseño → Tests → Implementación** (en ese orden)
2) Todo cambio debe tener:
   - historia/ticket asociado
   - tests correspondientes
   - actualización de docs si cambia comportamiento

## 3) Definition of Done (DoD)
Una historia se considera “Done” cuando:
- Cumple criterios de aceptación (Given/When/Then)
- Incluye tests:
  - unit + (si aplica) integration
- No rompe lint/format
- Se actualizó documentación (si aplica)
- Se revisó seguridad básica (authz, validación input, secretos)

## 4) Convenciones de código (MVP)
### Backend (Django/DRF)
- Service layer para lógica de negocio; views delgadas.
- Validación estricta; errores consistentes.
- Migraciones explícitas.
- Logs auditables para acciones relevantes.

### Frontend (Next.js)
- Componentes reutilizables; accesibilidad básica.
- Manejo de estado claro (evitar complejidad prematura).
- UI coherente con navegación del flujo E2E.

## 5) Testing (mínimos)
- Unit tests (TDD para lógica central)
- Integration tests (API + DB)
- BDD: features en Gherkin para historias Must-Have
- E2E: al menos 1 test del flujo principal end-to-end

## 6) Diagramas como código (DaC)
- Usar Mermaid o PlantUML.
- Guardar en:
  - `/docs/architecture/diagrams/architecture.mmd`
  - `/docs/data/diagrams/er.mmd`
  - `/docs/infra/diagrams/infra.mmd`
- Mantenerlos sincronizados con el código.

## 7) Seguridad y secretos
- Secrets solo por variables de entorno.
- Nunca commitear `.env`.
- Revisar permisos y RBAC antes de exponer endpoints.

## 8) Registro de uso de IA (obligatorio)
Mantener `/docs/ai/AI_USAGE_LOG.md` con:
- Prompts clave
- Herramientas usadas (Cursor, LLMs, etc.)
- Ejemplos antes/después
- Ajustes humanos y decisiones

## 9) Comandos (a completar cuando se inicialice el repo)
- Backend:
  - `make backend-dev`
  - `make backend-test`
- Frontend:
  - `make frontend-dev`
  - `make frontend-test`
- E2E:
  - `make e2e`
- CI:
  - `make ci`

## 10) Backlog, Tickets y Trazabilidad (GitHub-first)

### 10.1 Identificadores oficiales
- Épicas: `EPIC-01`, `EPIC-02`, ...
- Historias: `US-01`, `US-02`, ...
- Tickets (GitHub Issues): `T-001`, `T-002`, ...
- ADRs: `ADR-001`, `ADR-002`, ...
- Entidades: `ENT-RESOURCE`, `ENT-USER`, ...
- Endpoints: `API-XXX-01`
- Tests:
  - Unit: `UT-XXX-01`
  - Integration: `IT-XXX-01`
  - BDD: `BDD-XXX-01`
  - E2E: `E2E-01`

### 10.2 Fuente de verdad
- Backlog funcional (épicas e historias): `/docs/product/EPICS_AND_STORIES.md`
- Tickets operativos y estado (Planned/In Progress/Done): **GitHub Issues/Projects**
- Documentación técnica (arquitectura, datos, API, calidad): `/docs/*`

> Regla: **No registrar estados de tickets en Markdown.**
> El estado vive únicamente en GitHub.

### 10.3 Reglas de trazabilidad obligatorias
- Cada historia `US-xx` debe listar los tickets `T-xxx` que la implementan.
- Cada ticket `T-xxx` (Issue) debe referenciar:
  - Historia `US-xx`
  - Área (Backend/Frontend/Data/QA/Infra/E2E/Docs)
  - Módulo o ruta del repo
  - Impacto (qué habilita)
  - IDs relacionados (ENT/API/UT/IT/BDD/E2E) cuando aplique

### 10.4 Convención de GitHub Issues (Tickets)
- Todo ticket es un **Issue** con título:
  - `T-001 — <título>`
- El cuerpo del Issue debe incluir (mínimo):
  - `User Story: US-xx`
  - `Área: Backend|Frontend|Data|QA|Infra|E2E|Docs`
  - `Módulo/Ruta: ...`
  - `Impacto: ...`
  - `Checklist de tareas`
  - `Trazabilidad (opcional): ENT-..., API-..., UT-..., IT-..., BDD-..., E2E-...`

### 10.5 Commits y PRs (obligatorio)
- Todo commit y PR debe referenciar al menos un ticket:
  - `T-001: <mensaje>`
- PR template debe incluir:
  - Ticket(s): `T-xxx`
  - Historia: `US-xx`
  - Tests ejecutados (unit/integration/e2e)
  - Docs actualizadas si aplica

### 10.6 Política de implementación
- Prohibido implementar funcionalidad sin:
  - Historia `US-xx` definida con criterios Given/When/Then
  - Ticket `T-xxx` creado en GitHub y vinculado a la historia

### 10.7 Opcional: índice de tickets en docs
Si se requiere para auditoría académica, crear:
- `/docs/product/TICKETS_INDEX.md`
que contenga únicamente:
- Lista de `T-xxx` con link a GitHub Issues
- (sin estados)

