# PRD REFINED — BioAI Hub

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Dominio:** bioai.ccg.unam.mx  
**Versión:** 1.1 (refinado post-auditoría)  
**Fecha:** 2026-02-16  
**Base:** PRD_BASE.md + TECH_AUDIT.md + decisiones técnicas

---

## 1. DECISIONES TÉCNICAS TOMADAS

### 1.1 Identidad del Proyecto
- **Nombre técnico:** `bioai-hub`
- **Branding:** BioAI Hub — Institutional AI Repository
- **Dominio:** bioai.ccg.unam.mx (subdominio institucional CCG)
- **Repositorio:** `plataforma_ia` (mantener actual)

### 1.2 Autenticación
- **Modelo:** Cualquier email (no restringido a @ccg.unam.mx)
- **Verificación:** Obligatoria (link de confirmación por email)
- **Tecnología:** Django Auth + JWT
- **Extensibilidad:** Preparado para SSO futuro (Google Workspace UNAM)

**Justificación:** Apertura controlada desde MVP para facilitar adopción, manteniendo calidad mediante validación de email.

### 1.3 Roles y Permisos (RBAC)
- **Roles MVP:** Admin y User (2 roles)
- **Admin:** Todos los permisos (CRUD recursos, validar, gestionar usuarios)
- **User:** Publicar, editar propios, votar, reutilizar, reportar

**Diseño extensible:** Arquitectura preparada para roles futuros (Reviewer, Moderator) aunque no implementados en MVP.

### 1.4 Diagramas como Código (DaC)
- **Simples:** Mermaid (arquitectura, ERD básico, flujos)
- **Complejos:** PlantUML (si se requieren diagramas avanzados en fases posteriores)
- **Ubicación:** `/docs/*/diagrams/*.mmd` o `.puml`

---

## 2. REQUISITOS FUNCIONALES DETALLADOS

### 2.1 Autenticación y Usuarios

#### RF-AUTH-01: Registro de Usuario
- **Descripción:** Usuario puede registrarse con cualquier email
- **Flujo:**
  1. Usuario completa formulario: email, nombre, contraseña
  2. Sistema valida unicidad de email
  3. Sistema envía email de verificación con token
  4. Usuario hace clic en link de verificación
  5. Sistema activa cuenta
- **Validaciones:**
  - Email formato válido
  - Contraseña mínimo 8 caracteres (1 mayúscula, 1 número)
  - Nombre no vacío
- **Estados UI:** loading, validation error, backend error, success
- **Endpoint:** `POST /auth/register`
- **Entidad:** `User`

#### RF-AUTH-02: Verificación de Email
- **Descripción:** Usuario verifica email antes de poder publicar recursos
- **Flujo:**
  1. Usuario recibe email con link (token único, expira en 24h)
  2. Usuario hace clic en link
  3. Sistema valida token y marca email como verificado
  4. Usuario redirigido a dashboard con mensaje de bienvenida
- **Estados UI:** loading, token inválido/expirado, success
- **Endpoint:** `GET /auth/verify-email/:token`
- **Campo:** `user.email_verified_at` (timestamp, nullable)

#### RF-AUTH-03: Login
- **Descripción:** Usuario inicia sesión con email y contraseña
- **Flujo:**
  1. Usuario ingresa credenciales
  2. Sistema valida y genera JWT
  3. Frontend almacena token (httpOnly cookie o localStorage)
  4. Usuario redirigido a intended route o dashboard
- **Validaciones:**
  - Email debe existir y estar verificado
  - Contraseña correcta
  - Cuenta no suspendida
- **Estados UI:** loading, validation error, backend error (401), success
- **Endpoint:** `POST /auth/login`

#### RF-AUTH-04: Logout
- **Descripción:** Usuario cierra sesión
- **Flujo:**
  1. Usuario hace clic en "Cerrar sesión"
  2. Frontend elimina token
  3. Redirige a home pública
- **Endpoint:** `POST /auth/logout` (opcional, si se usa token blacklist)

#### RF-AUTH-05: Recuperación de Contraseña
- **Descripción:** Usuario puede resetear contraseña olvidada
- **Flujo:**
  1. Usuario solicita reset con email
  2. Sistema envía link con token (expira en 1h)
  3. Usuario ingresa nueva contraseña
  4. Sistema valida token y actualiza contraseña
- **Estados UI:** loading, validation error, token inválido/expirado, success
- **Endpoints:** `POST /auth/password-reset-request`, `POST /auth/password-reset-confirm/:token`

---

### 2.2 Explorar Recursos (Público)

#### RF-EXPLORE-01: Listar Recursos
- **Descripción:** Cualquier usuario (anónimo o autenticado) puede explorar catálogo
- **Flujo:**
  1. Usuario accede a `/explore`
  2. Sistema muestra recursos paginados (20 por página)
  3. Por defecto: ordenados por fecha creación (más recientes primero)
- **Filtros disponibles:**
  - Tipo de recurso (Prompt, Workflow, Notebook, Dataset, Tool)
  - Estado (Sandbox, Validated, Todos)
  - Source type (Internal, GitHub-linked, Todos)
  - Tags (multi-select)
- **Búsqueda:** Texto libre en título y descripción
- **Estados UI:** loading, empty (sin resultados), error, success
- **Endpoint:** `GET /resources?page=1&type=...&status=...&search=...`
- **Entidad:** `Resource`, `ResourceVersion`

#### RF-EXPLORE-02: Vista de Tarjeta (Card)
- **Descripción:** Cada recurso se muestra como tarjeta con información resumida
- **Información visible:**
  - Título
  - Autor (nombre + foto)
  - Badge de estado (Sandbox / Validated)
  - Tags (máximo 3 visibles)
  - Métricas: votos, usos, fecha última versión
  - Thumbnail o icono según tipo
- **Acción:** Click en tarjeta → `/resources/:id`

---

### 2.3 Detalle de Recurso

#### RF-DETAIL-01: Vista de Recurso (Público)
- **Descripción:** Visualización completa de recurso con última versión publicada
- **Información visible:**
  - Título
  - Descripción completa
  - Autor (link a perfil)
  - Badge de estado (Sandbox / Validated)
  - Tags completos
  - Tipo de recurso
  - Source type:
    - Si Internal: contenido almacenado en plataforma
    - Si GitHub-linked: link a repo, tag/commit, license
  - PID: `ccg-ai:R-000123@v1.2.0`
  - Métricas: votos totales, usos, fecha creación, fecha última actualización
  - Historial de versiones (lista básica)
  - Derived from (si es fork): link a recurso original
  - Forks count (cuántos lo reutilizaron)
- **Secciones:**
  - Información principal
  - Contenido / Instrucciones
  - Ejemplo mínimo (si aplica)
  - Discusión (comentarios - post-MVP)
- **Estados UI:** loading, not found (404), error, success
- **Endpoint:** `GET /resources/:id`
- **Entidades:** `Resource`, `ResourceVersion`, `User`

#### RF-DETAIL-02: Acciones según Rol (Usuario Anónimo)
- **Permitido:**
  - Ver toda la información
- **Bloqueado:**
  - Votar (mostrar "Inicia sesión para votar")
  - Reutilizar (mostrar "Inicia sesión para reutilizar")
  - Editar
  - Eliminar
  - Validar

#### RF-DETAIL-03: Acciones según Rol (Usuario Autenticado - No Owner)
- **Permitido:**
  - Votar (1 vez por recurso, toggle)
  - Reutilizar (fork)
  - Reportar (si sistema de reportes en MVP - TBD)
- **Bloqueado:**
  - Editar
  - Eliminar
  - Validar (solo Admin)

#### RF-DETAIL-04: Acciones según Rol (Owner)
- **Permitido:**
  - Todo lo de User autenticado
  - Editar recurso (botón "Editar" → `/resources/:id/edit`)
  - Eliminar recurso (con confirmación)
  - Ver historial de versiones completo
- **Bloqueado:**
  - Validar (solo Admin, no auto-validación)

#### RF-DETAIL-05: Acciones según Rol (Admin)
- **Permitido:**
  - Todo lo anterior
  - Validar cualquier recurso (promover Sandbox → Validated)
  - Editar cualquier recurso
  - Eliminar cualquier recurso
  - Revocar validación (Validated → Sandbox)

---

### 2.4 Publicar Recurso

#### RF-PUBLISH-01: Formulario de Publicación
- **Descripción:** Usuario autenticado y verificado puede publicar nuevo recurso
- **Precondición:** `user.email_verified_at IS NOT NULL`
- **Ruta:** `/publish`
- **Campos obligatorios:**
  - Título (max 200 chars)
  - Descripción (markdown, max 5000 chars)
  - Tipo de recurso (select: Prompt, Workflow, Notebook, Dataset, Tool, Other)
  - Source type (select: Internal, GitHub-linked)
  - Estado inicial (select: Sandbox, Request Validation)
- **Campos condicionales (si source_type = GitHub-linked):**
  - Repository URL (obligatorio, validar formato GitHub)
  - Tag (recomendado para Validated)
  - Commit SHA (recomendado para Validated)
  - License (obligatorio, select: MIT, Apache 2.0, GPL-3.0, CC-BY, CC-BY-SA, Custom)
- **Campos opcionales:**
  - Tags (multi-input, max 10 tags, cada tag max 30 chars)
  - Example (texto o código, max 2000 chars)
- **Validaciones:**
  - Título único por usuario (soft validation, warning)
  - URL de GitHub válida si aplica
  - License obligatoria si GitHub-linked
- **Estados UI:** validation error, backend error, success
- **Endpoint:** `POST /resources`
- **Entidades:** `Resource`, `ResourceVersion`

#### RF-PUBLISH-02: Creación de Recurso y Versión Inicial
- **Flujo backend:**
  1. Crear `Resource`:
     - `owner_id = current_user.id`
     - `source_type = form.source_type`
     - `created_at = now()`
  2. Crear `ResourceVersion` (v1.0.0):
     - `resource_id = resource.id`
     - `version_number = 1.0.0`
     - `status = form.status` (Sandbox o Pending Validation)
     - `title, description, tags, type, content` = form data
     - Si Internal: `content_hash = SHA256(content)`
     - Si GitHub-linked: `repo_url, tag, commit_sha, license`
     - `is_latest = true`
     - `created_at = now()`
  3. Si status = "Request Validation":
     - Crear notificación para Admins
- **Resultado:**
  - Redirigir a `/resources/:id`
  - Mostrar toast: "Recurso publicado exitosamente"
  - Si Request Validation: "Solicitud de validación enviada"

---

### 2.5 Editar Recurso

#### RF-EDIT-01: Editar Recurso (Owner o Admin)
- **Precondición:** `current_user.id == resource.owner_id OR current_user.is_admin`
- **Ruta:** `/resources/:id/edit`
- **Comportamiento por estado de última versión:**

**Caso A: Última versión NO validada (status = Sandbox o Pending Validation)**
- Actualizar versión existente in-place (no crear nueva versión)
- Permitir cambiar todos los campos
- Actualizar `updated_at`

**Caso B: Última versión SÍ validada (status = Validated)**
- Crear nueva versión (vNext)
- Incrementar version_number (ej: 1.0.0 → 1.1.0)
- Nueva versión con status = Sandbox
- Versión anterior permanece como Validated e `is_latest = false`
- Nueva versión con `is_latest = true`

- **Validaciones:** Iguales a publicación
- **Estados UI:** validation error, backend error, success
- **Endpoint:** `PATCH /resources/:id`
- **Banner post-edición (caso B):**
  - "Nueva versión creada (v1.1.0). La versión anterior permanece validada."

#### RF-EDIT-02: Eliminar Recurso
- **Precondición:** Owner o Admin
- **Flujo:**
  1. Usuario hace clic en "Eliminar"
  2. Modal de confirmación: "¿Eliminar recurso? Esta acción no se puede deshacer."
  3. Usuario confirma
  4. Sistema realiza soft delete (`deleted_at = now()`)
  5. Recurso desaparece de Explore
  6. Redirigir a `/explore` con toast: "Recurso eliminado"
- **Endpoint:** `DELETE /resources/:id`
- **Nota:** Soft delete para auditoría. Forks derivados NO se eliminan (mantienen trazabilidad).

---

### 2.6 Votar Recurso

#### RF-VOTE-01: Votar Recurso
- **Precondición:** Usuario autenticado
- **Regla:** 1 voto por usuario por recurso
- **Comportamiento:** Toggle (votar/desvotar)
- **Flujo:**
  1. Usuario hace clic en botón "Upvote" (icono corazón/star)
  2. Sistema valida que no haya votado previamente
  3. Si no votado: crear voto, incrementar contador
  4. Si ya votado: eliminar voto, decrementar contador
  5. Actualizar UI inmediatamente (optimistic update)
- **Endpoint:** `POST /resources/:id/vote` (idempotente, toggle)
- **Entidad:** `Vote` (`user_id`, `resource_id`, `created_at`)
- **Notificación (opcional MVP):** Notificar a owner si voto es el 10º (alcanza criterio de promoción)

---

### 2.7 Reutilizar Recurso (Fork)

#### RF-FORK-01: Reutilizar Recurso
- **Precondición:** Usuario autenticado
- **Ruta trigger:** Botón "Reuse This Resource" en `/resources/:id`
- **Flujo:**
  1. Usuario hace clic en "Reuse"
  2. Sistema crea nuevo `Resource`:
     - `owner_id = current_user.id`
     - `derived_from_resource_id = original_resource.id`
     - `derived_from_version_id = original_resource.latest_version.id`
     - `source_type = Internal` (fork siempre es interno)
  3. Sistema crea `ResourceVersion` inicial (v1.0.0):
     - Copia contenido de versión original
     - `status = Sandbox`
     - `is_latest = true`
  4. Incrementar contador `original_resource.forks_count`
  5. Redirigir a `/resources/:newId/edit`
  6. Mostrar banner: "Recurso reutilizado. Edítalo y publícalo."
- **Trazabilidad:**
  - Recurso nuevo muestra: "Derived from: [Original Resource Title]"
  - Recurso original muestra: "Forked X times"
- **Endpoint:** `POST /resources/:id/fork`
- **Entidades:** `Resource` (con campos `derived_from_*`)

---

### 2.8 Validación de Recursos

#### RF-VALIDATE-01: Promoción Automática (Sandbox → Validated)
- **Criterios (todos deben cumplirse):**
  - `votes_count >= 10`
  - `uses_count >= 50` (views + forks + upvotes combinados - TBD definición exacta)
  - `created_at >= now() - 14 days` (al menos 2 semanas de antigüedad)
  - `reports_critical_count == 0` (si sistema de reportes en MVP)
- **Proceso:**
  - Job periódico (cron diario) evalúa recursos en Sandbox
  - Si cumple criterios: `status = Validated`, `validated_at = now()`
  - Crear notificación para owner: "Tu recurso ha sido validado"
- **Nota:** Promoción automática es por **versión**, no por recurso completo.

#### RF-VALIDATE-02: Validación Manual (Admin)
- **Precondición:** `current_user.is_admin`
- **Flujo:**
  1. Admin accede a `/resources/:id`
  2. Admin hace clic en "Validate" (botón visible solo para Admin)
  3. Modal de confirmación: "¿Validar esta versión?"
  4. Sistema actualiza `latest_version.status = Validated`, `validated_at = now()`
  5. Crear notificación para owner
  6. Actualizar UI con badge Validated
- **Endpoint:** `POST /resources/:id/validate`
- **Nota:** Admin puede validar en cualquier momento, sin esperar criterios automáticos.

#### RF-VALIDATE-03: Revocar Validación (Admin)
- **Precondición:** `current_user.is_admin`
- **Flujo:**
  1. Admin hace clic en "Revoke Validation"
  2. Modal de confirmación con razón (texto obligatorio)
  3. Sistema actualiza `latest_version.status = Sandbox`, `validated_at = null`
  4. Crear notificación para owner con razón
- **Endpoint:** `POST /resources/:id/revoke-validation`
- **Uso:** Para recursos que después de validados presentan problemas.

---

### 2.9 Perfil de Usuario

#### RF-PROFILE-01: Perfil Público
- **Ruta:** `/profile/:id` (perfil de otro usuario) o `/profile` (propio)
- **Información visible:**
  - Nombre
  - Email (oculto si no es propio perfil)
  - Avatar (opcional, Gravatar o default)
  - Fecha de registro
  - Métricas de reputación:
    - Total recursos publicados
    - Total recursos validados (como owner)
    - Total validaciones realizadas (si Admin)
    - Total votos recibidos
    - Total forks recibidos
    - Impacto total (métrica combinada)
- **Secciones:**
  - Recursos publicados (lista con tarjetas)
  - Recursos validados (filtro)
  - Actividad reciente (opcional MVP)
- **Estados UI:** loading, not found (404), error, success
- **Endpoint:** `GET /users/:id`
- **Entidad:** `User` + agregaciones de `Resource`, `Vote`

#### RF-PROFILE-02: Editar Perfil Propio
- **Ruta:** `/profile/edit`
- **Campos editables:**
  - Nombre
  - Avatar URL (o upload - post-MVP)
  - Bio (max 500 chars)
  - Preferencias de notificación (post-MVP)
- **Endpoint:** `PATCH /users/:id`

---

### 2.10 Notificaciones

#### RF-NOTIF-01: Notificaciones In-App
- **Ruta:** `/notifications`
- **Precondición:** Usuario autenticado
- **Tipos de notificación (MVP):**
  - Recurso validado (automático o manual)
  - Recurso reutilizado (fork)
  - Validación revocada (con razón)
  - Solicitud de validación recibida (para Admins)
- **Información por notificación:**
  - Tipo (icono diferenciado)
  - Mensaje
  - Link al recurso/usuario relacionado
  - Timestamp
  - Estado: unread / read
- **Acciones:**
  - Marcar como leída (individual o todas)
  - Click en notificación → navegar a recurso
- **Badge:** Contador de no leídas en navbar (campana con número)
- **Estados UI:** loading, empty, error, success
- **Endpoint:** `GET /notifications`, `PATCH /notifications/:id/read`, `POST /notifications/mark-all-read`
- **Entidad:** `Notification` (`user_id`, `type`, `resource_id`, `message`, `read_at`, `created_at`)

#### RF-NOTIF-02: Notificaciones Email (Post-MVP)
- **Tipos:** Igual que in-app
- **Frecuencia:** Instantáneo o daily digest (configurable por usuario)
- **Requisito:** Servicio SMTP configurado

---

### 2.11 Historial de Versiones

#### RF-VERSION-01: Listar Versiones de Recurso
- **Ruta:** `/resources/:id/versions` (opcional MVP, puede ser sección dentro de `/resources/:id`)
- **Información por versión:**
  - Version number (v1.0.0, v1.1.0)
  - Status (Sandbox, Validated)
  - Fecha de creación
  - Changelog (si se agregó)
  - Link a versión específica: `/resources/:id/versions/:versionId`
- **Estados UI:** loading, empty (solo 1 versión), error, success
- **Endpoint:** `GET /resources/:id/versions`

#### RF-VERSION-02: Ver Versión Específica
- **Ruta:** `/resources/:id/versions/:versionId`
- **Comportamiento:** Igual que RF-DETAIL-01, pero mostrando datos de versión específica (no latest)
- **Nota:** Edición y eliminación solo disponibles en latest version
- **Endpoint:** `GET /resources/:id/versions/:versionId`

---

### 2.12 Reportes (TBD - Evaluar Inclusión en MVP)

#### RF-REPORT-01: Reportar Recurso
- **Precondición:** Usuario autenticado
- **Flujo:**
  1. Usuario hace clic en "Report" (icono bandera)
  2. Modal con razón (select: Contenido inapropiado, Error técnico, Spam, Plagio, Otro)
  3. Descripción adicional (textarea, max 500 chars)
  4. Usuario envía reporte
  5. Sistema crea `Report`, notifica a Admins
- **Endpoint:** `POST /resources/:id/report`
- **Entidad:** `Report` (`user_id`, `resource_id`, `reason`, `description`, `status`, `created_at`)

#### RF-REPORT-02: Gestión de Reportes (Admin)
- **Ruta:** `/admin/reports`
- **Acciones:**
  - Ver lista de reportes pendientes
  - Marcar como resuelto / rechazado
  - Tomar acción sobre recurso (editar, eliminar, revocar validación)
- **Endpoint:** `GET /admin/reports`, `PATCH /reports/:id`

**Decisión pendiente:** ¿Incluir sistema de reportes en MVP o post-MVP?  
**Impacto:** Criterio de promoción automática menciona "0 reportes críticos".  
**Recomendación auditoría:** Incluir sistema básico de reportes para habilitar criterio de promoción.

---

## 3. REQUISITOS NO FUNCIONALES (NFRs)

### 3.1 Performance
- **NFR-PERF-01:** Tiempo de carga de página Explore < 2s (con 100 recursos)
- **NFR-PERF-02:** Tiempo de respuesta API (p95) < 500ms
- **NFR-PERF-03:** Búsqueda y filtrado < 1s

**Estrategia:** Índices en PostgreSQL (title, tags, created_at), paginación estándar (20 items), sin optimizaciones prematuras.

### 3.2 Seguridad
- **NFR-SEC-01:** Autenticación JWT con expiración (24h access token, 7d refresh token)
- **NFR-SEC-02:** Contraseñas hasheadas con bcrypt (Django default)
- **NFR-SEC-03:** CSRF protection en todos los endpoints de mutación
- **NFR-SEC-04:** HTTPS obligatorio en producción
- **NFR-SEC-05:** Rate limiting:
  - Login: 5 intentos / 15 min por IP
  - Registro: 3 cuentas / hora por IP
  - API general: 100 req / min por usuario autenticado
- **NFR-SEC-06:** Validación estricta de inputs (sanitización XSS, SQL injection prevention)
- **NFR-SEC-07:** Secrets en variables de entorno (`.env` nunca commiteado)

### 3.3 Disponibilidad
- **NFR-AVAIL-01:** Uptime ≥ 99% (excluye mantenimientos planificados)
- **NFR-AVAIL-02:** Backup diario de base de datos (retención 30 días)
- **NFR-AVAIL-03:** Backup semanal de archivos estáticos (si se almacenan uploads)

**Estrategia:** VPS con monitoreo básico (uptime check), backups automáticos de PostgreSQL.

### 3.4 Escalabilidad
- **NFR-SCALE-01:** Soportar 50 usuarios concurrentes sin degradación (MVP)
- **NFR-SCALE-02:** Soportar 1000 recursos sin degradación de búsqueda
- **NFR-SCALE-03:** Arquitectura preparada para escalar horizontalmente (stateless backend)

**Estrategia:** Monolito modular, PostgreSQL con conexiones pooling, Next.js con SSR/SSG.

### 3.5 Usabilidad
- **NFR-UX-01:** Interfaz responsive (desktop, tablet, mobile)
- **NFR-UX-02:** Accesibilidad básica (WCAG 2.1 Nivel A mínimo)
- **NFR-UX-03:** Tiempos de feedback visual < 200ms (loading spinners, optimistic updates)
- **NFR-UX-04:** Mensajes de error claros y accionables

### 3.6 Mantenibilidad
- **NFR-MAINT-01:** Código con cobertura de tests ≥ 70% (unit + integration)
- **NFR-MAINT-02:** Documentación técnica actualizada en `/docs`
- **NFR-MAINT-03:** Logs estructurados (JSON) con niveles (DEBUG, INFO, WARNING, ERROR)
- **NFR-MAINT-04:** Versionado semántico de API (aunque MVP es v1 sin versionado explícito)

### 3.7 Observabilidad
- **NFR-OBS-01:** Logs de auditoría para acciones críticas:
  - Creación/edición/eliminación de recursos
  - Validación/revocación de validación
  - Login/registro
- **NFR-OBS-02:** Métricas básicas (Prometheus/Grafana en post-MVP):
  - Request rate, error rate, latency
  - Usuarios activos diarios/semanales
  - Recursos publicados por día
- **NFR-OBS-03:** Alertas básicas (email a admin si uptime < 95% en 24h)

---

## 4. MODELO DE DATOS CONCEPTUAL (Refinado)

### Entidades principales:

#### User
- `id` (PK, UUID)
- `email` (unique, indexed)
- `email_verified_at` (timestamp, nullable)
- `password_hash`
- `name`
- `avatar_url` (nullable)
- `bio` (nullable)
- `is_admin` (boolean, default false)
- `is_active` (boolean, default true)
- `created_at`, `updated_at`

#### Resource
- `id` (PK, UUID)
- `owner_id` (FK → User)
- `source_type` (enum: Internal, GitHub-Linked)
- `derived_from_resource_id` (FK → Resource, nullable) — para forks
- `derived_from_version_id` (FK → ResourceVersion, nullable)
- `forks_count` (integer, default 0)
- `deleted_at` (timestamp, nullable) — soft delete
- `created_at`, `updated_at`

#### ResourceVersion
- `id` (PK, UUID)
- `resource_id` (FK → Resource)
- `version_number` (string, ej: "1.0.0")
- `status` (enum: Sandbox, Pending Validation, Validated)
- `title` (string, max 200)
- `description` (text, markdown)
- `type` (enum: Prompt, Workflow, Notebook, Dataset, Tool, Other)
- `tags` (array/JSONB)
- `content` (text, nullable) — si Internal
- `content_hash` (string, nullable) — SHA256 si Internal
- `repo_url` (string, nullable) — si GitHub-Linked
- `repo_tag` (string, nullable)
- `repo_commit_sha` (string, nullable)
- `license` (string, nullable) — obligatorio si GitHub-Linked
- `example` (text, nullable)
- `changelog` (text, nullable)
- `is_latest` (boolean, default true)
- `validated_at` (timestamp, nullable)
- `created_at`, `updated_at`

#### Vote
- `id` (PK, UUID)
- `user_id` (FK → User)
- `resource_id` (FK → Resource)
- `created_at`
- **Unique constraint:** (`user_id`, `resource_id`)

#### Notification
- `id` (PK, UUID)
- `user_id` (FK → User)
- `type` (enum: ResourceValidated, ResourceForked, ValidationRevoked, ValidationRequested)
- `resource_id` (FK → Resource, nullable)
- `related_user_id` (FK → User, nullable) — ej: quién forkeó
- `message` (text)
- `read_at` (timestamp, nullable)
- `created_at`

#### Report (opcional MVP)
- `id` (PK, UUID)
- `user_id` (FK → User) — reporter
- `resource_id` (FK → Resource)
- `reason` (enum: Inappropriate, TechnicalError, Spam, Plagiarism, Other)
- `description` (text)
- `status` (enum: Pending, Resolved, Rejected)
- `resolved_by_user_id` (FK → User, nullable)
- `resolved_at` (timestamp, nullable)
- `created_at`

---

## 5. CONSTRAINTS Y REGLAS DE NEGOCIO

### 5.1 Versionado
- Cada edición de recurso con última versión Validated crea nueva versión (vNext)
- Solo la última versión (`is_latest = true`) puede editarse
- Versiones Validated son inmutables (no se pueden editar in-place)
- Version numbering: semántico (major.minor.patch) o simple incremental (1, 2, 3) — TBD en diseño de datos

### 5.2 Validación
- Promoción automática evalúa versión, no recurso completo
- Un recurso puede tener múltiples versiones Validated en su historial
- Admin puede validar manualmente sin esperar criterios automáticos
- Revocar validación NO elimina versión, solo cambia status

### 5.3 Forks
- Fork siempre crea recurso con `source_type = Internal`
- Fork siempre comienza con `status = Sandbox`
- Trazabilidad bidireccional: fork → original y original → forks count
- Eliminar recurso original NO elimina forks (independencia)

### 5.4 Permisos
- Solo usuario con `email_verified_at IS NOT NULL` puede publicar
- Solo owner o admin puede editar/eliminar recurso
- Solo admin puede validar/revocar validación
- Usuario suspendido (`is_active = false`) no puede login ni publicar

### 5.5 Métricas
- `uses_count` = views + forks + upvotes (definición exacta TBD en arquitectura)
- Métricas se actualizan en tiempo real (no batch)
- Votos son reversibles (toggle)

---

## 6. INTEGRACIONES EXTERNAS

### 6.1 GitHub (GitHub-Linked Resources)
- **Integración:** Manual (usuario pega URL, tag, commit)
- **Validación:** Validar formato URL GitHub en backend
- **Sincronización:** No automática en MVP (usuario actualiza manualmente)
- **Post-MVP:** Webhook para detectar cambios en repo

### 6.2 Email (SMTP)
- **Uso:** Verificación de email, recuperación de contraseña
- **Proveedor:** TBD (SendGrid, Mailgun, SMTP institucional)
- **Templates:** HTML básicos
- **Post-MVP:** Notificaciones por email

### 6.3 Gravatar (Avatar)
- **Uso:** Avatar por defecto basado en email
- **Fallback:** Icono con iniciales si no tiene Gravatar

---

## 7. ESTRATEGIA DE DESPLIEGUE

### 7.1 Infraestructura MVP
- **Hosting:** VPS pública (DigitalOcean, Linode, o servidor CCG)
- **Dominio:** bioai.ccg.unam.mx (DNS gestionado por CCG)
- **Contenedores:** Docker + Docker Compose
- **Servicios:**
  - Next.js (frontend) — puerto 3000
  - Django + Gunicorn (backend) — puerto 8000
  - PostgreSQL — puerto 5432 (no expuesto)
  - Nginx (reverse proxy) — puerto 80/443

### 7.2 CI/CD Simple
- **Repositorio:** GitHub (privado o público según CCG)
- **CI:** GitHub Actions
- **Pipeline:**
  1. Lint (ESLint, Black, Flake8)
  2. Tests (Jest, Pytest)
  3. Build (Next.js, Django collectstatic)
  4. Deploy (SSH a VPS, docker-compose up)
- **Ambientes:** Staging (opcional) y Production

### 7.3 Secrets Management
- **Variables de entorno** en `.env` (nunca en repo)
- **Secrets en CI:** GitHub Secrets
- **Producción:** Archivo `.env` en VPS con permisos restringidos

---

## 8. ROADMAP DETALLADO

### Fase 1: MVP (Core Platform) — 12-16 semanas
**Objetivo:** Flujo E2E funcional con 3-5 historias Must-Have

**Hitos:**
1. **Semanas 1-2:** Diseño técnico (arquitectura, modelo de datos, API)
2. **Semanas 3-4:** Setup infraestructura (Docker, CI/CD, DB)
3. **Semanas 5-8:** Implementación backend (auth, recursos, versionado, votos)
4. **Semanas 9-12:** Implementación frontend (páginas, componentes, flujo E2E)
5. **Semanas 13-14:** Testing (unit, integration, E2E) + fixes
6. **Semanas 15-16:** Deploy, UAT interno, lanzamiento CCG

**Entregables:**
- Plataforma desplegada en bioai.ccg.unam.mx
- Flujo E2E: Registro → Explorar → Publicar → Validar → Reutilizar
- Tests automatizados (≥70% cobertura)
- Documentación técnica completa

### Fase 2: Expansión — 8-12 semanas
**Objetivo:** Mejoras de UX y features secundarias

**Features:**
- Notificaciones por email
- Historial de versiones mejorado (comparación visual)
- Sistema de reportes completo
- Métricas avanzadas (analytics dashboard para owners)
- Búsqueda avanzada (filtros combinados)
- Exportar/importar recursos (JSON, YAML)

### Fase 3: Inteligencia — 12+ semanas
**Objetivo:** Features avanzadas de IA y apertura pública

**Features:**
- Recomendador basado en uso y tags
- Búsqueda semántica (embeddings)
- API pública (REST + GraphQL)
- Apertura a comunidad externa (registro abierto sin restricción)
- Integración con Jupyter Hub (ejecutar notebooks)
- DOI real (integración con DataCite o similar)

---

## 9. CAMBIOS RESPECTO A PRD_BASE.md

### Decisiones agregadas:
1. ✅ Autenticación con cualquier email (no solo institucional)
2. ✅ Verificación de email obligatoria
3. ✅ Roles simples: Admin y User (diseño extensible)
4. ✅ Nombre técnico: `bioai-hub`, branding: BioAI Hub
5. ✅ Dominio: bioai.ccg.unam.mx
6. ✅ DaC: Mermaid (simple) + PlantUML (complejo)

### Refinamientos:
- ✅ Requisitos funcionales detallados por pantalla (RF-*)
- ✅ Estados UI identificados por requisito
- ✅ Endpoints mapeados
- ✅ Entidades con campos detallados
- ✅ Reglas de negocio explícitas
- ✅ NFRs cuantificados
- ✅ Estrategia de despliegue definida

### Pendientes post-auditoría:
- ⏭️ Decisión final sobre sistema de reportes en MVP (recomendado: SÍ)
- ⏭️ Definición exacta de `uses_count` (views + forks + upvotes)
- ⏭️ Version numbering schema (semántico vs incremental)
- ⏭️ Proveedor de email (SMTP)

---

## 10. REFERENCIAS

- [`PRD_BASE.md`](PRD_BASE.md) — documento original
- [`TECH_AUDIT.md`](../review/TECH_AUDIT.md) — auditoría técnica
- [`PRODUCT_BRIEF.md`](PRODUCT_BRIEF.md) — resumen ejecutivo
- [`NAVIGATION_FLOW.md`](../ux/NAVIGATION_FLOW.md) — flujos de navegación
- [`AGENTS.md`](../../AGENTS.md) — gobernanza técnica
- [`ORCHESTRATOR_MASTER.md`](../../orchestration/ORCHESTRATOR_MASTER.md) — protocolo de desarrollo

---

**Documento refinado:** 2026-02-16  
**Siguiente artefacto:** ROADMAP.md  
**Rol siguiente:** PM
