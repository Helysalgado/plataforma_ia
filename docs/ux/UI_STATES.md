# UI STATES — BioAI Hub

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Dominio:** bioai.ccg.unam.mx  
**Versión:** 1.0  
**Fecha:** 2026-02-16  
**Fase:** FASE 2.5 — UX State Formalization  
**Rol activo:** UX Lead + Tech Lead

---

## 1. OBJETIVO Y CRITICIDAD

Este documento formaliza **todos los estados UI** por pantalla identificando:
- Estados de carga (loading)
- Estados vacíos (empty)
- Estados de error (validation, backend, network)
- Estados de éxito (success)
- Estados de permisos (unauthorized, forbidden)

**Criticidad:** Según ORCHESTRATOR_MASTER.md (línea 106-107):
> "No avanzar a FASE 3 (Arquitectura) hasta que todos los estados estén formalizados y su impacto técnico identificado."

**Impacto técnico:**
1. Estados impactan **modelo de datos** (campos de estado, validación)
2. Estados impactan **endpoints** (códigos HTTP, manejo de errores)
3. Estados impactan **historias** (criterios Given/When/Then deben contemplar estados)
4. Estados impactan **RBAC** (reglas de autorización)

---

## 2. METODOLOGÍA

Para cada pantalla:
1. **Pantalla base** (diseño Figma o descripción funcional)
2. **Estados identificados** (exhaustivos)
3. **Triggers** (qué dispara cada estado)
4. **Mensajes al usuario** (copy específico)
5. **Acciones disponibles** (qué puede hacer el usuario)
6. **Impacto técnico** (entidades, endpoints, validaciones)

---

## 3. PANTALLAS ANALIZADAS

### Pantallas con diseño Figma existente:
1. Home (Landing) — `home.png`
2. Explore — `explore.png`
3. Resource Detail — `resource-detail.png`
4. Publish — `publish.png`
5. Profile — `profile.png`

### Pantallas sin diseño Figma (flujo crítico):
6. Register / Login (autenticación)
7. Verify Email
8. Edit Resource
9. Notifications Panel
10. Admin: Validate Resource Modal

---

## 4. ESTADOS POR PANTALLA

---

### PANTALLA 1: HOME (LANDING)

**Ruta:** `/`  
**Figma:** `home.png`  
**Acceso:** Público (anónimo o autenticado)

#### Estados identificados:

##### Estado 1.1: Loading (Carga Inicial)
**Trigger:** Primera carga de la página, fetching featured resources

**UI:**
- Skeleton loaders en sección "Featured Resources"
- Spinner central o placeholders animados
- Header y footer estáticos (no loading)

**Mensaje:** (Sin texto, solo indicador visual)

**Acciones disponibles:**
- Ninguna (esperar)

**Duración esperada:** <1s

**Impacto técnico:**
- Frontend: Componente con estado `isLoading`
- Backend: Endpoint `GET /resources/featured` debe responder <500ms

---

##### Estado 1.2: Success (Carga Exitosa)
**Trigger:** API responde con featured resources

**UI:**
- Hero section con mensaje: "Discover and Share AI Resources for Bioinformatics"
- Grid de 3-6 featured resources (cards)
- CTA: "Explore Resources", "Publish Resource"

**Acciones disponibles:**
- Click en "Explore Resources" → `/explore`
- Click en "Publish Resource" → `/login` (si anónimo) o `/publish` (si autenticado)
- Click en featured resource card → `/resources/:id`

**Impacto técnico:**
- Endpoint: `GET /resources/featured` (retorna 6 recursos Validated ordenados por votos)
- Frontend: Renderiza ResourceCard components

---

##### Estado 1.3: Empty (Sin Featured Resources)
**Trigger:** No existen recursos Validated en la plataforma (inicio del proyecto)

**UI:**
- Hero section normal
- Sección "Featured Resources" muestra:
  - Ilustración de empty state (icono de cohete/laboratorio)
  - Mensaje: "Be the first to publish a resource!"
  - CTA: "Publish Now" (si autenticado) o "Sign Up to Publish" (si anónimo)

**Acciones disponibles:**
- Click en CTA → `/publish` o `/register`

**Impacto técnico:**
- Lógica: Si `featured_resources.length === 0`, mostrar empty state
- No requiere endpoint adicional

---

##### Estado 1.4: Backend Error
**Trigger:** API `/resources/featured` falla (500, timeout, red)

**UI:**
- Hero section normal
- Sección "Featured Resources" muestra:
  - Icono de error (⚠️)
  - Mensaje: "Unable to load featured resources. Please try again."
  - Botón: "Retry"

**Acciones disponibles:**
- Click en "Retry" → Volver a llamar API

**Impacto técnico:**
- Frontend: Estado `error` + handler de retry
- Logging: Registrar error en consola y backend

---

**Resumen impactos técnicos Home:**
- Endpoint: `GET /resources/featured`
- Entidades: `Resource`, `ResourceVersion`
- Estados frontend: `isLoading`, `isError`, `featuredResources[]`
- Componentes: `ResourceCard`, `EmptyState`, `ErrorBoundary`

---

### PANTALLA 2: REGISTER (REGISTRO)

**Ruta:** `/register`  
**Figma:** No existe (flujo estándar)  
**Acceso:** Público (solo anónimos)

#### Estados identificados:

##### Estado 2.1: Initial (Formulario Vacío)
**Trigger:** Usuario accede a `/register`

**UI:**
- Formulario con campos:
  - Email (input tipo email)
  - Nombre completo (input texto)
  - Contraseña (input tipo password con toggle show/hide)
  - Confirmar contraseña (input tipo password)
  - Checkbox "Acepto términos y condiciones" (con link a T&C)
- Botón "Registrarse" (habilitado si formulario válido)
- Link: "¿Ya tienes cuenta? Inicia sesión"

**Acciones disponibles:**
- Completar formulario
- Click en "Registrarse" (si válido)
- Click en "Inicia sesión" → `/login`

**Impacto técnico:**
- Validaciones frontend: email formato, contraseña ≥8 chars + regex
- Estado: `formData`, `errors`, `isValid`

---

##### Estado 2.2: Validation Error (Errores de Formulario)
**Trigger:** Usuario completa formulario con datos inválidos

**Errores posibles:**

| Campo | Validación | Mensaje Error |
|---|---|---|
| Email | Formato inválido | "Ingresa un email válido" |
| Email | Vacío | "Email es obligatorio" |
| Nombre | Vacío | "Nombre es obligatorio" |
| Contraseña | <8 chars | "Contraseña debe tener mínimo 8 caracteres" |
| Contraseña | Sin mayúscula | "Contraseña debe incluir al menos 1 mayúscula" |
| Contraseña | Sin número | "Contraseña debe incluir al menos 1 número" |
| Confirmar | No coincide | "Las contraseñas no coinciden" |
| T&C | No aceptado | "Debes aceptar los términos y condiciones" |

**UI:**
- Mensajes de error inline debajo de cada campo
- Borde rojo en campos con error
- Botón "Registrarse" deshabilitado si hay errores

**Acciones disponibles:**
- Corregir campos con error

**Impacto técnico:**
- Validaciones frontend (Zod, Yup, o validación manual)
- Estado: `errors: Record<string, string>`

---

##### Estado 2.3: Loading (Enviando Registro)
**Trigger:** Usuario hace clic en "Registrarse" (formulario válido)

**UI:**
- Botón "Registrarse" cambia a:
  - Texto: "Registrando..."
  - Spinner dentro del botón
  - Botón deshabilitado
- Campos del formulario deshabilitados

**Acciones disponibles:**
- Ninguna (esperar)

**Duración esperada:** 1-3s

**Impacto técnico:**
- Estado: `isSubmitting: true`
- Endpoint: `POST /auth/register`

---

##### Estado 2.4: Backend Error (Registro Fallido)
**Trigger:** API responde con error

**Errores posibles:**

| Error Backend | Código HTTP | Mensaje Usuario |
|---|---|---|
| Email ya registrado | 409 Conflict | "Este email ya está registrado. ¿Olvidaste tu contraseña?" (con link) |
| Email inválido | 400 Bad Request | "Email inválido" |
| Error de servidor | 500 | "Error del servidor. Intenta nuevamente en unos minutos" |
| Timeout | - | "Conexión lenta. Intenta nuevamente" |

**UI:**
- Toast/Alert en la parte superior con mensaje de error
- Formulario se habilita nuevamente
- Botón "Registrarse" vuelve a estado normal

**Acciones disponibles:**
- Corregir datos (si aplica)
- Reintentar envío
- Link a "¿Olvidaste tu contraseña?" (si email duplicado)

**Impacto técnico:**
- Estado: `error: string | null`
- Manejo de códigos HTTP específicos
- Logging en backend

---

##### Estado 2.5: Success (Registro Exitoso)
**Trigger:** API responde 201 Created, usuario creado

**UI:**
- Redirige automáticamente a pantalla "Verify Email"
- Toast verde: "¡Registro exitoso! Verifica tu email para continuar"

**Acciones disponibles:**
- Usuario es redirigido a `/auth/verify-email-sent` (pantalla informativa)

**Impacto técnico:**
- Endpoint: `POST /auth/register` retorna 201
- Backend: Crea `User` con `email_verified_at = NULL`
- Backend: Envía email de verificación con token (job async)
- Frontend: Redirige con `router.push('/auth/verify-email-sent')`

---

**Resumen impactos técnicos Register:**
- Endpoint: `POST /auth/register`
- Entidades: `User` (`email`, `name`, `password_hash`, `email_verified_at`)
- Validaciones backend: email único, contraseña segura
- Email enviado: Verificación con token (expira 24h)
- Estados frontend: `formData`, `errors`, `isSubmitting`, `error`

---

### PANTALLA 3: VERIFY EMAIL

**Ruta:** `/auth/verify-email/:token` o `/auth/verify-email-sent` (informativa)  
**Figma:** No existe  
**Acceso:** Público

#### Estados identificados:

##### Estado 3.1: Email Sent (Informativa)
**Trigger:** Usuario acaba de registrarse

**UI:**
- Icono de sobre/email (grande, centrado)
- Título: "Verifica tu email"
- Mensaje: "Enviamos un email de verificación a **[email]**. Haz clic en el link para activar tu cuenta."
- Sub-mensaje: "Si no ves el email, revisa tu carpeta de spam."
- Botón: "Reenviar email" (habilitado después de 60s)
- Link: "Cambiar email" (opcional MVP)

**Acciones disponibles:**
- Esperar email
- Click en "Reenviar email" (después de 60s) → `POST /auth/resend-verification`

**Impacto técnico:**
- Endpoint: `POST /auth/resend-verification` (rate limited: 3 veces/hora)
- Timer frontend: 60s countdown antes de habilitar "Reenviar"

---

##### Estado 3.2: Verifying (Usuario hace clic en link del email)
**Trigger:** Usuario accede a `/auth/verify-email/:token` desde email

**UI:**
- Spinner central
- Mensaje: "Verificando tu email..."

**Acciones disponibles:**
- Ninguna (esperar)

**Duración esperada:** <2s

**Impacto técnico:**
- Endpoint: `GET /auth/verify-email/:token`
- Backend valida token (no expirado, no usado, usuario existe)

---

##### Estado 3.3: Success (Verificación Exitosa)
**Trigger:** Token válido, backend actualiza `email_verified_at`

**UI:**
- Icono de check verde (grande)
- Título: "¡Email verificado!"
- Mensaje: "Tu cuenta ha sido activada exitosamente."
- Botón: "Iniciar sesión" → `/login`

**Acciones disponibles:**
- Click en "Iniciar sesión"

**Impacto técnico:**
- Backend actualiza: `user.email_verified_at = now()`
- Redirect a `/login` con query param `?verified=true` (para mostrar mensaje bienvenida)

---

##### Estado 3.4: Error - Token Expired
**Trigger:** Token tiene más de 24h

**UI:**
- Icono de reloj/warning
- Título: "Link expirado"
- Mensaje: "Este link de verificación ha expirado. Solicita uno nuevo."
- Botón: "Reenviar email de verificación" → formulario para ingresar email

**Acciones disponibles:**
- Ingresar email y solicitar nuevo link

**Impacto técnico:**
- Backend: Validación de `token.created_at + 24h < now()`
- Endpoint: `POST /auth/resend-verification` con email

---

##### Estado 3.5: Error - Token Invalid
**Trigger:** Token no existe, ya fue usado, o formato inválido

**UI:**
- Icono de error
- Título: "Link inválido"
- Mensaje: "Este link de verificación no es válido. Verifica que copiaste la URL completa del email."
- Botón: "Volver a inicio" → `/`

**Acciones disponibles:**
- Click en "Volver a inicio"

**Impacto técnico:**
- Backend: Validación de token en DB
- Logging: Registrar intentos de tokens inválidos (posible ataque)

---

**Resumen impactos técnicos Verify Email:**
- Endpoints: `GET /auth/verify-email/:token`, `POST /auth/resend-verification`
- Entidades: `User` (`email_verified_at`), `VerificationToken` (tabla opcional o usar JWT)
- Validaciones: Token no expirado, no usado, usuario existe
- Rate limiting: Reenvío limitado a 3 veces/hora
- Estados frontend: `isVerifying`, `verificationStatus: 'success' | 'expired' | 'invalid'`

---

### PANTALLA 4: LOGIN

**Ruta:** `/login`  
**Figma:** No existe  
**Acceso:** Público (solo anónimos)

#### Estados identificados:

##### Estado 4.1: Initial
**Trigger:** Usuario accede a `/login`

**UI:**
- Formulario con campos:
  - Email
  - Contraseña (con toggle show/hide)
  - Checkbox "Recordarme" (opcional MVP)
- Botón "Iniciar sesión"
- Links:
  - "¿Olvidaste tu contraseña?"
  - "¿No tienes cuenta? Regístrate"

**Acciones disponibles:**
- Completar formulario
- Click en "Iniciar sesión"
- Click en "¿Olvidaste tu contraseña?" → `/auth/forgot-password`
- Click en "Regístrate" → `/register`

---

##### Estado 4.2: Validation Error
**Trigger:** Campos vacíos o formato inválido

**Errores:**
- Email vacío: "Email es obligatorio"
- Email inválido: "Ingresa un email válido"
- Contraseña vacía: "Contraseña es obligatoria"

**UI:**
- Mensajes inline debajo de campos
- Botón deshabilitado si hay errores

---

##### Estado 4.3: Loading
**Trigger:** Usuario hace clic en "Iniciar sesión"

**UI:**
- Botón cambia a "Iniciando sesión..." con spinner
- Campos deshabilitados

**Duración esperada:** 1-2s

---

##### Estado 4.4: Backend Error - Credentials Invalid
**Trigger:** Email o contraseña incorrectos

**UI:**
- Alert rojo en la parte superior del formulario:
  - "Credenciales incorrectas. Verifica tu email y contraseña."
- Campos se mantienen (no se limpian)
- Botón vuelve a estado normal

**Código HTTP:** 401 Unauthorized

**Acciones disponibles:**
- Corregir credenciales
- Click en "¿Olvidaste tu contraseña?"

**Impacto técnico:**
- Backend: NO revelar si el error es email o contraseña (seguridad)
- Rate limiting: 5 intentos fallidos / 15 min por IP

---

##### Estado 4.5: Backend Error - Email Not Verified
**Trigger:** Usuario intenta login pero `email_verified_at IS NULL`

**UI:**
- Alert amarillo/warning:
  - "Tu email no ha sido verificado. Revisa tu bandeja de entrada."
  - Botón: "Reenviar email de verificación"

**Código HTTP:** 403 Forbidden

**Acciones disponibles:**
- Click en "Reenviar email"

**Impacto técnico:**
- Backend valida `email_verified_at IS NOT NULL` antes de generar JWT
- Endpoint: `POST /auth/resend-verification`

---

##### Estado 4.6: Backend Error - Account Suspended
**Trigger:** `user.is_active = false` (usuario suspendido por admin)

**UI:**
- Alert rojo:
  - "Tu cuenta ha sido suspendida. Contacta al administrador."
  - Email de contacto: admin@ccg.unam.mx (configurable)

**Código HTTP:** 403 Forbidden

**Acciones disponibles:**
- Contactar admin (external)

**Impacto técnico:**
- Backend valida `is_active = true` antes de login
- Logging: Registrar intentos de login de cuentas suspendidas

---

##### Estado 4.7: Success
**Trigger:** Credenciales correctas, email verificado, cuenta activa

**UI:**
- Redirect automático a:
  - Intended route (si vino de redirect) ej: `/publish`
  - O dashboard `/` (home autenticado)
- Toast verde: "¡Bienvenido de nuevo, [Nombre]!"

**Acciones disponibles:**
- Usuario ya está en página destino

**Impacto técnico:**
- Backend genera JWT (access token, expira 24h)
- Backend (opcional) genera refresh token (expira 7d)
- Frontend almacena token (httpOnly cookie recomendado, o localStorage)
- Frontend actualiza estado global de auth
- Redirect: `router.push(intendedRoute || '/')`

---

**Resumen impactos técnicos Login:**
- Endpoint: `POST /auth/login`
- Entidades: `User` (`email`, `password_hash`, `email_verified_at`, `is_active`)
- Validaciones: Credenciales correctas, email verificado, cuenta activa
- Rate limiting: 5 intentos fallidos / 15 min por IP
- JWT: Access token (24h), opcional refresh token (7d)
- Estados frontend: `formData`, `isSubmitting`, `error`

---

### PANTALLA 5: EXPLORE (CATÁLOGO)

**Ruta:** `/explore`  
**Figma:** `explore.png`  
**Acceso:** Público (anónimo o autenticado)

#### Estados identificados:

##### Estado 5.1: Loading (Carga Inicial)
**Trigger:** Primera carga o cambio de filtros

**UI:**
- Skeleton loaders para cards (6-8 placeholders)
- Filtros y barra de búsqueda habilitados (no loading)
- Paginación oculta

**Duración esperada:** <1s

---

##### Estado 5.2: Success (Recursos Cargados)
**Trigger:** API responde con recursos

**UI:**
- Grid de ResourceCards (20 por página)
- Cada card muestra:
  - Título
  - Autor (nombre + avatar)
  - Badge (Sandbox/Validated)
  - Tags (máx 3 visibles)
  - Métricas: votos, usos
  - Thumbnail/icono según tipo
- Controles de paginación: "Anterior", "Página X de Y", "Siguiente"
- Filtros activos visibles (tags removibles)

**Acciones disponibles:**
- Click en card → `/resources/:id`
- Cambiar filtros
- Buscar
- Navegar páginas

---

##### Estado 5.3: Empty - No Resources (Global)
**Trigger:** No existen recursos en la plataforma

**UI:**
- Ilustración de laboratorio vacío
- Título: "No hay recursos disponibles aún"
- Mensaje: "Sé el primero en publicar un recurso de IA"
- CTA: "Publicar Recurso" → `/publish` (si autenticado) o `/register` (si anónimo)

**Acciones disponibles:**
- Click en CTA

**Impacto técnico:**
- Lógica: `resources.length === 0 && !hasFilters`

---

##### Estado 5.4: Empty - No Results (Filtros Activos)
**Trigger:** Filtros/búsqueda no devuelven resultados

**UI:**
- Ilustración de búsqueda vacía (lupa con X)
- Título: "No se encontraron recursos"
- Mensaje: "No hay recursos que coincidan con tus filtros actuales"
- Filtros activos mostrados: "Tipo: Workflow", "Estado: Validated", "Búsqueda: 'protein xyz'"
- Botón: "Limpiar filtros"

**Acciones disponibles:**
- Click en "Limpiar filtros" → Resetear todos los filtros
- Modificar filtros manualmente

**Impacto técnico:**
- Lógica: `resources.length === 0 && hasFilters`
- Estado: `activeFilters: { search, type, status, tags }`

---

##### Estado 5.5: Backend Error
**Trigger:** API falla (500, timeout, red)

**UI:**
- Icono de error (⚠️)
- Título: "No se pudieron cargar los recursos"
- Mensaje: "Ocurrió un error al conectar con el servidor. Intenta nuevamente."
- Botón: "Reintentar"

**Acciones disponibles:**
- Click en "Reintentar" → Volver a llamar API

**Impacto técnico:**
- Estado: `error: Error | null`
- Logging: Registrar error en backend

---

##### Estado 5.6: Loading Pagination
**Trigger:** Usuario navega a otra página

**UI:**
- Scroll automático al top
- Skeleton loaders reemplazan cards
- Filtros y paginación deshabilitados temporalmente

**Duración esperada:** <1s

---

**Resumen impactos técnicos Explore:**
- Endpoint: `GET /resources?page=X&search=Y&type=Z&status=W&tags=A,B`
- Entidades: `Resource`, `ResourceVersion`, `User`
- Query params: paginación (20 items), filtros combinados
- Estados frontend: `isLoading`, `resources[]`, `pagination`, `activeFilters`, `error`
- Componentes: `ResourceCard`, `EmptyState`, `Pagination`, `FilterBar`

---

### PANTALLA 6: RESOURCE DETAIL

**Ruta:** `/resources/:id`  
**Figma:** `resource-detail.png`  
**Acceso:** Público (comportamiento varía según rol)

#### Estados identificados:

##### Estado 6.1: Loading
**Trigger:** Carga inicial de recurso

**UI:**
- Skeleton loader para:
  - Header (título, autor, badge)
  - Descripción
  - Métricas
  - Botones
- Sidebar estático (si autenticado)

**Duración esperada:** <1s

---

##### Estado 6.2: Success - Anónimo
**Trigger:** API responde, usuario no autenticado

**UI:**
- Información completa visible (título, descripción, métricas, tags, PID, autor)
- Botones:
  - "Upvote" (deshabilitado con tooltip: "Inicia sesión para votar")
  - "Reuse" (deshabilitado con tooltip: "Inicia sesión para reutilizar")
- NO visible: Edit, Delete, Validate

**Acciones disponibles:**
- Ver información
- Click en autor → `/profile/:id`
- Click en botones deshabilitados → Modal "Inicia sesión" con redirect

---

##### Estado 6.3: Success - Autenticado (No Owner)
**Trigger:** Usuario autenticado, no es owner

**UI:**
- Todo visible
- Botones:
  - "Upvote" (habilitado, estado dinámico: voted/not voted)
  - "Reuse" (habilitado)
- NO visible: Edit, Delete, Validate (a menos que Admin)

**Acciones disponibles:**
- Votar (toggle)
- Reutilizar → Redirect a `/resources/:newId/edit`

---

##### Estado 6.4: Success - Owner
**Trigger:** Usuario es owner del recurso

**UI:**
- Todo visible
- Botones:
  - "Upvote", "Reuse" (habilitados)
  - "Edit" (habilitado) → `/resources/:id/edit`
  - "Delete" (habilitado) → Modal confirmación
- NO visible: Validate

**Acciones disponibles:**
- Votar, reutilizar
- Editar → Modal si última versión Validated: "Editar creará nueva versión"
- Eliminar → Modal: "¿Eliminar recurso? No se puede deshacer"

---

##### Estado 6.5: Success - Admin
**Trigger:** Usuario es Admin

**UI:**
- Todo visible
- Botones:
  - "Upvote", "Reuse", "Edit", "Delete" (habilitados)
  - **"Validate"** (habilitado si status != Validated)
  - **"Revoke Validation"** (habilitado si status == Validated)

**Acciones disponibles:**
- Todas las anteriores
- Validar → Modal: "¿Validar este recurso?"
- Revocar → Modal: "¿Revocar validación? Incluye razón" (textarea obligatorio)

---

##### Estado 6.6: Error - Not Found (404)
**Trigger:** Recurso no existe o fue eliminado (soft delete)

**UI:**
- Ilustración de error 404
- Título: "Recurso no encontrado"
- Mensaje: "El recurso que buscas no existe o fue eliminado"
- Botón: "Volver a Explorar" → `/explore`

**Código HTTP:** 404 Not Found

---

##### Estado 6.7: Error - Backend Error (500)
**Trigger:** API falla al cargar recurso

**UI:**
- Icono de error
- Título: "Error al cargar recurso"
- Mensaje: "Ocurrió un error. Intenta recargar la página."
- Botón: "Reintentar"

**Código HTTP:** 500 Internal Server Error

---

##### Estado 6.8: Modal - Confirm Delete
**Trigger:** Owner/Admin hace clic en "Delete"

**UI:**
- Modal centrado
- Título: "¿Eliminar recurso?"
- Mensaje: "Esta acción no se puede deshacer. El recurso será eliminado permanentemente."
- Botones:
  - "Cancelar" (outline)
  - "Eliminar" (rojo, destructivo)

**Estados del modal:**
- **Loading:** Botón "Eliminar" cambia a "Eliminando..." con spinner
- **Success:** Modal se cierra, redirect a `/explore`, toast: "Recurso eliminado"
- **Error:** Toast rojo: "Error al eliminar recurso. Intenta nuevamente"

**Impacto técnico:**
- Endpoint: `DELETE /resources/:id`
- Backend: Soft delete (`deleted_at = now()`)

---

##### Estado 6.9: Modal - Confirm Validate
**Trigger:** Admin hace clic en "Validate"

**UI:**
- Modal centrado
- Título: "¿Validar este recurso?"
- Mensaje: "El recurso será marcado como Validated y el owner recibirá una notificación."
- Botones:
  - "Cancelar"
  - "Validar" (verde)

**Estados del modal:**
- **Loading:** Botón "Validar" cambia a "Validando..."
- **Success:** Modal se cierra, badge cambia a Validated, toast: "Recurso validado exitosamente"
- **Error:** Toast: "Error al validar recurso"

**Impacto técnico:**
- Endpoint: `POST /resources/:id/validate`
- Backend: Actualiza `status = Validated`, `validated_at = now()`
- Backend: Crea `Notification` para owner

---

##### Estado 6.10: Modal - Revoke Validation
**Trigger:** Admin hace clic en "Revoke Validation"

**UI:**
- Modal centrado
- Título: "Revocar validación"
- Mensaje: "El recurso volverá a estado Sandbox. El owner recibirá una notificación."
- Campo: Textarea "Razón" (obligatorio, max 500 chars)
- Botones:
  - "Cancelar"
  - "Revocar" (rojo)

**Validación:** Razón no puede estar vacía

**Estados del modal:**
- **Loading:** Botón "Revocar" cambia a "Revocando..."
- **Success:** Modal se cierra, badge cambia a Sandbox, toast: "Validación revocada"
- **Error:** Toast: "Error al revocar validación"

**Impacto técnico:**
- Endpoint: `POST /resources/:id/revoke-validation`
- Body: `{ reason: string }`
- Backend: Actualiza `status = Sandbox`, `validated_at = null`
- Backend: Crea `Notification` con razón

---

**Resumen impactos técnicos Resource Detail:**
- Endpoints: `GET /resources/:id`, `DELETE /resources/:id`, `POST /resources/:id/validate`, `POST /resources/:id/revoke-validation`, `POST /resources/:id/vote`, `POST /resources/:id/fork`
- Entidades: `Resource`, `ResourceVersion`, `User`, `Vote`, `Notification`
- Lógica RBAC: Permisos condicionales según rol
- Modales: Delete, Validate, Revoke Validation (con estados loading/success/error)
- Estados frontend: `isLoading`, `resource`, `currentUser`, `hasVoted`, `error`

---

### PANTALLA 7: PUBLISH (PUBLICAR RECURSO)

**Ruta:** `/publish`  
**Figma:** `publish.png`  
**Acceso:** Solo autenticados con `email_verified_at IS NOT NULL`

#### Estados identificados:

##### Estado 7.1: Unauthorized - Not Authenticated
**Trigger:** Usuario anónimo intenta acceder a `/publish`

**UI:**
- Redirect automático a `/login?redirect=/publish`

**Impacto técnico:**
- Middleware frontend: Protected route

---

##### Estado 7.2: Forbidden - Email Not Verified
**Trigger:** Usuario autenticado pero `email_verified_at IS NULL`

**UI:**
- Redirect a `/profile` o modal inline:
  - Título: "Verifica tu email"
  - Mensaje: "Debes verificar tu email antes de publicar recursos"
  - Botón: "Reenviar email de verificación"

**Código HTTP:** 403 Forbidden (si intenta enviar form)

**Impacto técnico:**
- Validación frontend: Checar `user.email_verified_at`
- Backend: Validar en endpoint `POST /resources`

---

##### Estado 7.3: Initial (Formulario Vacío)
**Trigger:** Usuario accede a `/publish` (verificado)

**UI:**
- Formulario con campos (según Figma `publish.png`):
  - **Título** (input, max 200 chars)
  - **Descripción** (textarea markdown, max 5000 chars, con preview)
  - **Tipo** (select: Prompt, Workflow, Notebook, Dataset, Tool, Other)
  - **Source Type** (radio: Internal, GitHub-linked)
  - **Tags** (multi-input, max 10 tags)
  - **Contenido** (textarea, visible si Internal)
  - **Ejemplo** (textarea opcional, max 2000 chars)
  - **Repo URL** (input, visible si GitHub-linked, obligatorio)
  - **Tag/Commit** (input, visible si GitHub-linked, recomendado)
  - **License** (select, visible si GitHub-linked, obligatorio)
  - **Estado inicial** (radio: Sandbox, Request Validation)
- Botón "Publish" (habilitado si formulario válido)

**Acciones disponibles:**
- Completar formulario
- Toggle markdown preview (descripción)
- Cambiar source type → Muestra campos condicionales
- Click en "Publish"

**Impacto técnico:**
- Estado: `formData`, `errors`, `sourceType`
- Validaciones dinámicas según source type

---

##### Estado 7.4: Validation Error
**Trigger:** Usuario intenta enviar formulario inválido

**Errores posibles:**

| Campo | Validación | Mensaje |
|---|---|---|
| Título | Vacío | "Título es obligatorio" |
| Título | >200 chars | "Título no puede exceder 200 caracteres" |
| Descripción | Vacío | "Descripción es obligatoria" |
| Descripción | >5000 chars | "Descripción no puede exceder 5000 caracteres" |
| Tipo | No seleccionado | "Selecciona un tipo de recurso" |
| Source Type | No seleccionado | "Selecciona tipo de fuente" |
| Contenido | Vacío (si Internal) | "Contenido es obligatorio para recursos internos" |
| Repo URL | Vacío (si GitHub) | "URL de repositorio es obligatoria" |
| Repo URL | Formato inválido | "URL debe ser un repositorio GitHub válido" |
| License | No seleccionada (si GitHub) | "Licencia es obligatoria para recursos GitHub" |

**UI:**
- Mensajes inline debajo de campos con error
- Scroll automático al primer error
- Botón "Publish" deshabilitado

---

##### Estado 7.5: Loading (Enviando)
**Trigger:** Usuario hace clic en "Publish" (formulario válido)

**UI:**
- Botón cambia a "Publishing..." con spinner
- Todos los campos deshabilitados
- Progress bar opcional (si sube archivos en futuro)

**Duración esperada:** 2-4s

---

##### Estado 7.6: Backend Error
**Trigger:** API falla

**Errores posibles:**

| Error | Código | Mensaje Usuario |
|---|---|---|
| Título duplicado (mismo owner) | 409 | "Ya tienes un recurso con este título. Usa uno diferente." (warning, permite continuar) |
| URL GitHub inválida | 400 | "La URL de GitHub no es válida o no es accesible" |
| Email no verificado | 403 | "Tu email no está verificado. Verifica antes de publicar." |
| Rate limit excedido | 429 | "Has publicado muchos recursos recientemente. Intenta en 1 hora." |
| Error servidor | 500 | "Error del servidor. Intenta nuevamente." |

**UI:**
- Toast/Alert rojo con mensaje
- Formulario se habilita
- Datos NO se pierden

---

##### Estado 7.7: Success
**Trigger:** Recurso creado exitosamente

**UI:**
- Redirect a `/resources/:newId`
- Toast verde: "¡Recurso publicado exitosamente!"
- Si Request Validation: Toast adicional: "Solicitud de validación enviada"

**Impacto técnico:**
- Endpoint: `POST /resources` retorna 201 con `{ id }`
- Backend: Crea `Resource` + `ResourceVersion` v1.0.0
- Backend: Genera PID: `ccg-ai:R-XXXXXX@v1.0.0`
- Backend (si Internal): Calcula `content_hash = SHA256(content)`
- Backend (si Request Validation): Crea notificación para Admins

---

**Resumen impactos técnicos Publish:**
- Endpoint: `POST /resources`
- Entidades: `Resource`, `ResourceVersion`, `Notification` (si Request Validation)
- Validaciones: Email verificado, campos obligatorios según source type
- Rate limiting: 10 publicaciones / hora por usuario
- Estados frontend: `formData`, `errors`, `isSubmitting`, `sourceType`

---

### PANTALLA 8: EDIT RESOURCE

**Ruta:** `/resources/:id/edit`  
**Figma:** No existe (similar a Publish)  
**Acceso:** Solo Owner o Admin

#### Estados identificados:

##### Estado 8.1: Unauthorized
**Trigger:** Usuario no es owner ni admin

**UI:**
- Redirect a `/resources/:id` con toast rojo: "No tienes permisos para editar este recurso"

**Código HTTP:** 403 Forbidden

---

##### Estado 8.2: Loading (Cargando Recurso)
**Trigger:** Carga inicial para pre-llenar formulario

**UI:**
- Skeleton loader en formulario
- Campos deshabilitados

**Duración esperada:** <1s

---

##### Estado 8.3: Initial (Formulario Pre-llenado)
**Trigger:** API responde con datos del recurso

**UI:**
- Formulario igual a Publish, pero:
  - Campos pre-llenados con datos actuales
  - Banner informativo si última versión es Validated:
    - "⚠️ Este recurso está Validated. Al guardar cambios se creará una nueva versión (vNext) y el recurso volverá a Sandbox."
    - Botón: "Entendido"

**Acciones disponibles:**
- Editar campos
- Click en "Save Changes"
- Click en "Cancel" → Volver a `/resources/:id`

**Impacto técnico:**
- Endpoint: `GET /resources/:id` para obtener datos
- Lógica: Si `latest_version.status == 'Validated'`, mostrar banner

---

##### Estado 8.4: Validation Error
**Trigger:** Igual a Publish (ver 7.4)

---

##### Estado 8.5: Loading (Guardando)
**Trigger:** Usuario hace clic en "Save Changes"

**UI:**
- Botón cambia a "Saving..." con spinner
- Campos deshabilitados

---

##### Estado 8.6: Modal - Confirm Version Creation
**Trigger:** Usuario intenta guardar y última versión es Validated

**UI:**
- Modal centrado
- Título: "Crear nueva versión"
- Mensaje: "Tu recurso actual está Validated. Al guardar, se creará la versión v1.1.0 en estado Sandbox. La versión anterior (v1.0.0) permanecerá Validated."
- Campo: "Changelog" (textarea, max 500 chars, recomendado)
- Botones:
  - "Cancelar"
  - "Crear Nueva Versión" (azul)

**Acciones disponibles:**
- Ingresar changelog opcional
- Confirmar o cancelar

**Impacto técnico:**
- Si confirma: Crear nueva `ResourceVersion` con `version_number` incrementado

---

##### Estado 8.7: Success - Update In-Place
**Trigger:** Última versión NO Validated, edición exitosa

**UI:**
- Redirect a `/resources/:id`
- Toast verde: "Recurso actualizado exitosamente"

**Impacto técnico:**
- Backend: Actualiza `ResourceVersion` existente (in-place)
- Actualiza `updated_at`

---

##### Estado 8.8: Success - New Version Created
**Trigger:** Última versión SÍ Validated, edición exitosa

**UI:**
- Redirect a `/resources/:id`
- Toast verde: "Nueva versión creada (v1.1.0). La versión anterior permanece Validated."

**Impacto técnico:**
- Backend: Crea nueva `ResourceVersion`
- Anterior: `is_latest = false`
- Nueva: `is_latest = true`, `status = Sandbox`

---

##### Estado 8.9: Backend Error
**Trigger:** API falla (permisos, servidor, etc.)

**UI:**
- Toast rojo con mensaje de error
- Formulario se mantiene (datos NO se pierden)

---

**Resumen impactos técnicos Edit:**
- Endpoints: `GET /resources/:id`, `PATCH /resources/:id`
- Entidades: `ResourceVersion` (update in-place o create new)
- Lógica de versionado: Checar `latest_version.status`
- Modal condicional si Validated
- Estados frontend: `isLoading`, `formData`, `isSubmitting`, `showVersionModal`

---

### PANTALLA 9: PROFILE (PERFIL)

**Ruta:** `/profile/:id` (público) o `/profile` (propio)  
**Figma:** `profile.png`  
**Acceso:** Público para ver, autenticado para editar propio

#### Estados identificados:

##### Estado 9.1: Loading
**Trigger:** Carga inicial de perfil

**UI:**
- Skeleton loader para:
  - Header (avatar, nombre, métricas)
  - Grid de recursos publicados

---

##### Estado 9.2: Success - Perfil Público
**Trigger:** API responde con datos de usuario

**UI (según Figma):**
- Header:
  - Avatar (Gravatar o default)
  - Nombre
  - Email (solo si es perfil propio)
  - Fecha de registro
  - Botón "Edit Profile" (solo si es propio)
- Métricas:
  - Total recursos publicados
  - Total recursos validated (como owner)
  - Total votos recibidos
  - Total forks recibidos
  - Impacto total (métrica combinada)
- Tabs:
  - "Published Resources" (grid de cards)
  - "Validated Resources" (filtro)

**Acciones disponibles:**
- Ver recursos publicados
- Click en recurso → `/resources/:id`
- Si es propio: Click en "Edit Profile" → `/profile/edit`

---

##### Estado 9.3: Empty - No Resources Published
**Trigger:** Usuario no ha publicado recursos

**UI:**
- Métricas muestran 0
- Tab "Published Resources" muestra:
  - Ilustración empty state
  - Mensaje: "No has publicado recursos aún" (si propio) o "[Nombre] no ha publicado recursos" (si ajeno)
  - CTA (solo si propio): "Publicar mi primer recurso" → `/publish`

---

##### Estado 9.4: Error - User Not Found (404)
**Trigger:** Usuario no existe

**UI:**
- Título: "Usuario no encontrado"
- Mensaje: "El perfil que buscas no existe"
- Botón: "Volver a inicio" → `/`

---

##### Estado 9.5: Backend Error (500)
**Trigger:** API falla

**UI:**
- Icono de error
- Mensaje: "Error al cargar perfil. Intenta nuevamente."
- Botón: "Reintentar"

---

**Resumen impactos técnicos Profile:**
- Endpoints: `GET /users/:id`, `GET /users/:id/resources`
- Entidades: `User`, `Resource`, agregaciones de métricas
- Estados frontend: `isLoading`, `user`, `resources[]`, `error`

---

### PANTALLA 10: NOTIFICATIONS (PANEL)

**Ruta:** Panel desplegable desde navbar (no ruta dedicada en MVP)  
**Figma:** No existe  
**Acceso:** Solo autenticados

#### Estados identificados:

##### Estado 10.1: Loading
**Trigger:** Usuario hace clic en campana

**UI:**
- Panel se abre
- Spinner central
- Mensaje: "Cargando notificaciones..."

**Duración esperada:** <1s

---

##### Estado 10.2: Success - Con Notificaciones
**Trigger:** API responde con notificaciones

**UI:**
- Header del panel:
  - Título: "Notificaciones"
  - Link: "Mark all as read"
- Lista de notificaciones (últimas 20):
  - Cada notificación:
    - Icono según tipo (✓ validado, 🔄 fork, ⚠️ revocado)
    - Mensaje
    - Timestamp relativo ("hace 2 horas")
    - Fondo destacado si unread
    - Click en notificación → Navegar a recurso relacionado

**Acciones disponibles:**
- Click en notificación → Redirige y marca como leída
- Click en "Mark all as read" → Marca todas como leídas

---

##### Estado 10.3: Empty - Sin Notificaciones
**Trigger:** No hay notificaciones

**UI:**
- Ilustración de campana vacía
- Mensaje: "No tienes notificaciones"

---

##### Estado 10.4: Backend Error
**Trigger:** API falla

**UI:**
- Icono de error
- Mensaje: "No se pudieron cargar las notificaciones"
- Botón: "Reintentar"

---

**Resumen impactos técnicos Notifications:**
- Endpoints: `GET /notifications`, `PATCH /notifications/:id/read`, `POST /notifications/mark-all-read`
- Entidades: `Notification`
- Polling: Cada 30s para actualizar badge (o WebSockets post-MVP)
- Estados frontend: `isOpen`, `isLoading`, `notifications[]`, `unreadCount`

---

## 5. IMPACTO TÉCNICO CONSOLIDADO

### 5.1 Modelo de Datos - Campos Derivados de Estados UI

#### Entidad: User
- `email_verified_at` (timestamp, nullable) → Estado: "Email Not Verified"
- `is_active` (boolean, default true) → Estado: "Account Suspended"

#### Entidad: ResourceVersion
- `status` (enum: Sandbox, Pending Validation, Validated) → Badge dinámico
- `validated_at` (timestamp, nullable) → Metadata de validación

#### Entidad: Vote
- Tabla completa derivada de estado "Voted/Not Voted"
- Unique constraint (`user_id`, `resource_id`)

#### Entidad: Notification
- `read_at` (timestamp, nullable) → Estado: Read/Unread
- `type` (enum) → Iconos diferenciados

### 5.2 Endpoints - Códigos HTTP por Estado

| Endpoint | Success | Validation Error | Auth Error | Not Found | Server Error |
|---|---|---|---|---|---|
| POST /auth/register | 201 | 400 | - | - | 500 |
| GET /auth/verify-email/:token | 200 | 400 (expired/invalid) | - | 404 | 500 |
| POST /auth/login | 200 | 400 | 401 (wrong creds), 403 (not verified/suspended) | - | 500 |
| GET /resources | 200 | - | - | - | 500 |
| GET /resources/:id | 200 | - | - | 404 | 500 |
| POST /resources | 201 | 400 | 403 (email not verified) | - | 429 (rate limit), 500 |
| PATCH /resources/:id | 200 | 400 | 403 (not owner/admin) | 404 | 500 |
| DELETE /resources/:id | 204 | - | 403 | 404 | 500 |
| POST /resources/:id/vote | 200 | - | 401 | 404 | 500 |
| POST /resources/:id/fork | 201 | - | 401 | 404 | 500 |
| POST /resources/:id/validate | 200 | - | 403 (not admin) | 404 | 500 |
| POST /resources/:id/revoke-validation | 200 | 400 (missing reason) | 403 | 404 | 500 |

### 5.3 Historias Faltantes Identificadas

Después de analizar estados UI exhaustivamente, **NO se identifican historias Must-Have faltantes**.

Todas las historias en EPICS_AND_STORIES.md cubren los estados UI críticos identificados.

**Historias Should-Have confirmadas para Fase 2:**
- US-20: Editar recurso (estados de versionado completos)
- US-21: Eliminar recurso (modal de confirmación)
- US-23: Reportar recurso (para habilitar criterio de promoción automática)

### 5.4 Componentes Reutilizables Derivados

| Componente | Estados Gestionados | Pantallas que lo usan |
|---|---|---|
| **EmptyState** | Ilustración + mensaje + CTA | Home, Explore, Profile, Notifications |
| **ErrorBoundary** | Error message + retry | Todas |
| **LoadingSpinner** | Spinner + mensaje opcional | Todas |
| **SkeletonCard** | Placeholder animado | Explore, Profile |
| **Badge** | Sandbox/Validated/Pending | Explore, Detail, Profile |
| **Modal** | Open/close + loading + error | Delete, Validate, Revoke, Version |
| **Toast** | Success/error/info + autohide | Todas |
| **VoteButton** | Voted/not voted + loading | Detail |

---

## 6. RIESGOS TÉCNICOS DERIVADOS DEL DISEÑO UX

### Riesgo 1: Complejidad de Versionado (MEDIO)
**Descripción:** Lógica de "editar recurso Validated crea nueva versión" puede confundir usuarios.

**Mitigación:**
- Banner informativo claro antes de editar
- Modal de confirmación con explicación
- Changelog recomendado (no obligatorio MVP)

---

### Riesgo 2: Estados de Error No Contemplados en Figma (ALTO)
**Descripción:** Diseños Figma muestran solo estados success, no errores/loading/empty.

**Mitigación:**
- Usar componentes reutilizables (EmptyState, ErrorBoundary)
- Diseñar ilustraciones consistentes (biblioteca de iconos)
- Documentar copy de errores en sistema de diseño

---

### Riesgo 3: Performance de Polling (Notificaciones) (BAJO)
**Descripción:** Polling cada 30s puede ser ineficiente con muchos usuarios.

**Mitigación:**
- Polling solo si usuario está activo (visibilitychange API)
- Post-MVP: Migrar a WebSockets

---

## 7. PREGUNTAS CRÍTICAS PENDIENTES

### Pregunta 1: Ilustraciones para Empty/Error States
**Contexto:** No existen en diseños Figma

**Pregunta:** ¿Usar biblioteca open-source (ej: unDraw, Storyset) o diseñar custom?

**Recomendación:** Usar biblioteca open-source para MVP, custom para Fase 2

---

### Pregunta 2: Copy de Mensajes de Error
**Contexto:** Mensajes definidos en este doc son propuestas

**Pregunta:** ¿Stakeholder CCG revisará copy antes de implementación?

**Recomendación:** Crear `/docs/ux/COPY.md` con todos los mensajes para revisión

---

### Pregunta 3: Rate Limiting Exacto
**Contexto:** Definimos límites en este doc (ej: 10 publicaciones/hora)

**Pregunta:** ¿Son apropiados para comunidad CCG pequeña inicial?

**Recomendación:** Validar con stakeholder, posiblemente relajar para MVP

---

## 8. CONCLUSIÓN Y DESBLOQUEADOR

**Estados UI formalizados:** ✅ **COMPLETO**

**Pantallas analizadas:** 10 (5 con Figma + 5 críticas sin Figma)

**Estados totales identificados:** 50+ estados únicos

**Impacto en historias:** **NO se identifican gaps críticos**. Historias Must-Have en EPICS_AND_STORIES.md cubren todos los estados UI esenciales.

**Impacto en arquitectura:**
- Modelo de datos: Campos de estado claramente definidos
- Endpoints: Códigos HTTP por estado documentados
- RBAC: Permisos por estado y rol mapeados

**Impacto en testing:**
- Cada estado UI requiere test case específico
- Estados de error críticos para tests de integración
- Modales requieren tests E2E (interacción compleja)

---

**BLOQUEADOR RESUELTO:** Según protocolo ORCHESTRATOR_MASTER.md, ahora se puede **avanzar a FASE 3 (Arquitectura)**.

---

**Documento completado:** 2026-02-16  
**Siguiente artefacto:** Actualizar EPICS_AND_STORIES.md (verificación final) → AI_USAGE_LOG.md  
**Siguiente fase:** FASE 3 — Diseño Técnico (Arquitectura)
