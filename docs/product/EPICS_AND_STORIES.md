# EPICS AND STORIES — BioAI Hub

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Dominio:** bioai.ccg.unam.mx  
**Versión:** 1.0  
**Fecha:** 2026-02-16  
**Base:** E2E_PRIORITY_FLOW.md + PRD_REFINED.md

---

## CONVENCIONES Y TRAZABILIDAD

### Identificadores:
- **Épicas:** `EPIC-01`, `EPIC-02`, ...
- **Historias:** `US-01`, `US-02`, ...
- **Tickets:** `T-001`, `T-002`, ... (en GitHub Issues)

### Estructura de Historia:
Cada historia incluye:
1. **ID + Título**
2. **Épica padre**
3. **Descripción (As a... I want... So that...)**
4. **Criterios de Aceptación (Given/When/Then)**
5. **Definition of Done (DoD)**
6. **Prioridad:** Must-Have, Should-Have, Could-Have
7. **Estimación:** S (Small), M (Medium), L (Large), XL (Extra Large)
8. **Dependencias:** IDs de historias prerequisito
9. **Trazabilidad:** Pantallas Figma, Endpoints, Entidades, Tests

---

## ÉPICAS (MVP)

### EPIC-01: Autenticación y Gestión de Usuarios
**Objetivo:** Permitir registro, verificación, login y gestión básica de usuarios

**Historias:**
- US-01: Registro con verificación de email
- US-02: Inicio de sesión y logout
- US-03: Recuperación de contraseña
- US-04: Perfil público de usuario

**Valor:** Base para acceso seguro a features protegidas

---

### EPIC-02: Catálogo y Exploración de Recursos
**Objetivo:** Permitir a usuarios explorar, buscar y filtrar recursos de IA

**Historias:**
- US-05: Explorar catálogo de recursos
- US-06: Buscar y filtrar recursos
- US-07: Ver detalle completo de recurso

**Valor:** Descubrimiento eficiente de recursos de calidad

---

### EPIC-03: Publicación y Versionado de Recursos
**Objetivo:** Permitir a usuarios publicar y versionar recursos

**Historias:**
- US-08: Publicar nuevo recurso (Internal)
- US-09: Publicar recurso con GitHub-linked
- US-10: Editar recurso propio (versionado automático)
- US-11: Eliminar recurso propio

**Valor:** Compartir conocimiento con trazabilidad institucional

---

### EPIC-04: Validación y Calidad
**Objetivo:** Sistema de validación automático y manual para garantizar calidad

**Historias:**
- US-12: Solicitar validación de recurso
- US-13: Validar recurso manualmente (Admin)
- US-14: Promoción automática a Validated
- US-15: Revocar validación (Admin)

**Valor:** Señal de calidad institucional

---

### EPIC-05: Interacciones Comunitarias
**Objetivo:** Votos, reutilización y reconocimiento

**Historias:**
- US-16: Votar recurso
- US-17: Reutilizar recurso (fork)
- US-18: Notificaciones in-app

**Valor:** Colaboración y reconocimiento comunitario

---

## HISTORIAS MUST-HAVE (FASE 1: MVP)

---

### US-01: Registro con Verificación de Email
**Épica:** EPIC-01  
**Prioridad:** Must-Have  
**Estimación:** M  
**Dependencias:** Ninguna

**Historia:**
> Como usuario nuevo,  
> Quiero registrarme con mi email y verificar mi cuenta,  
> Para poder publicar recursos en la plataforma.

**Criterios de Aceptación:**

#### CA-01.1: Registro exitoso
```gherkin
Given que soy un usuario no registrado
When accedo a la página de registro
And completo el formulario con:
  | Campo      | Valor                  |
  | Email      | juan@example.com       |
  | Nombre     | Juan Pérez             |
  | Contraseña | SecurePass123!         |
And hago clic en "Registrarse"
Then el sistema crea mi cuenta
And envía un email de verificación a juan@example.com
And me redirige a una pantalla con mensaje "Verifica tu email"
And mi cuenta tiene email_verified_at = NULL
```

#### CA-01.2: Validación de email único
```gherkin
Given que ya existe un usuario con email "juan@example.com"
When intento registrarme con el mismo email
Then el sistema muestra error: "Este email ya está registrado"
And no crea una cuenta duplicada
```

#### CA-01.3: Validación de contraseña
```gherkin
Given que completo el formulario de registro
When ingreso contraseña "12345" (menos de 8 caracteres)
Then el sistema muestra error: "Contraseña debe tener mínimo 8 caracteres, 1 mayúscula y 1 número"
And no permite enviar el formulario
```

#### CA-01.4: Verificación de email
```gherkin
Given que me registré con email "juan@example.com"
And recibí email de verificación con token único
When hago clic en el link de verificación
Then el sistema valida el token
And actualiza email_verified_at = now()
And me redirige a /login con mensaje "Email verificado, inicia sesión"
```

#### CA-01.5: Token expirado
```gherkin
Given que recibí email de verificación hace 25 horas
When hago clic en el link de verificación
Then el sistema muestra error: "Link expirado. Solicita un nuevo email de verificación"
And no verifica mi cuenta
```

**Definition of Done:**
- ✅ Formulario de registro funcional con validaciones frontend
- ✅ API endpoint `POST /auth/register` implementado
- ✅ Validaciones backend (email único, contraseña segura)
- ✅ Email de verificación enviado con token único (expira en 24h)
- ✅ API endpoint `GET /auth/verify-email/:token` implementado
- ✅ Tests unitarios (validaciones)
- ✅ Tests de integración (registro + verificación)
- ✅ Test E2E (flujo completo registro → verificación → login)

**Trazabilidad:**
- Pantalla: `/register`, `/auth/verify-email/:token`
- Endpoints: `POST /auth/register`, `GET /auth/verify-email/:token`
- Entidades: `User` (`email`, `email_verified_at`, `password_hash`)
- Tests: `UT-AUTH-01`, `IT-AUTH-01`, `E2E-01`

---

### US-02: Inicio de Sesión y Logout
**Épica:** EPIC-01  
**Prioridad:** Must-Have  
**Estimación:** S  
**Dependencias:** US-01

**Historia:**
> Como usuario registrado y verificado,  
> Quiero iniciar sesión con mi email y contraseña,  
> Para acceder a features protegidas de la plataforma.

**Criterios de Aceptación:**

#### CA-02.1: Login exitoso
```gherkin
Given que soy un usuario registrado con email verificado
When accedo a /login
And ingreso email "juan@example.com" y contraseña correcta
And hago clic en "Iniciar sesión"
Then el sistema genera un JWT (access token)
And me redirige a "/" (home autenticado)
And veo mi nombre en el sidebar
```

#### CA-02.2: Credenciales incorrectas
```gherkin
Given que ingreso email "juan@example.com"
And ingreso contraseña incorrecta
When hago clic en "Iniciar sesión"
Then el sistema muestra error: "Credenciales incorrectas"
And no me permite acceder
```

#### CA-02.3: Email no verificado
```gherkin
Given que me registré pero no verifiqué mi email
When intento iniciar sesión
Then el sistema muestra error: "Verifica tu email antes de iniciar sesión"
And muestra botón "Reenviar email de verificación"
```

#### CA-02.4: Logout
```gherkin
Given que estoy autenticado
When hago clic en "Cerrar sesión"
Then el sistema elimina mi token
And me redirige a "/" (home público)
And ya no puedo acceder a rutas protegidas
```

**Definition of Done:**
- ✅ Formulario de login funcional
- ✅ API endpoint `POST /auth/login` implementado
- ✅ JWT generado con expiración (24h)
- ✅ Middleware de autenticación en backend
- ✅ Frontend almacena token (httpOnly cookie o localStorage)
- ✅ API endpoint `POST /auth/logout` implementado (opcional si token blacklist)
- ✅ Tests unitarios + integración
- ✅ Test E2E (login → acceso a ruta protegida → logout)

**Trazabilidad:**
- Pantalla: `/login`
- Endpoints: `POST /auth/login`, `POST /auth/logout`
- Entidades: `User`
- Tests: `UT-AUTH-02`, `IT-AUTH-02`, `E2E-02`

---

### US-05: Explorar Catálogo de Recursos
**Épica:** EPIC-02  
**Prioridad:** Must-Have  
**Estimación:** M  
**Dependencias:** Ninguna (acceso público)

**Historia:**
> Como usuario (anónimo o autenticado),  
> Quiero explorar el catálogo de recursos con paginación,  
> Para descubrir recursos de IA relevantes.

**Criterios de Aceptación:**

#### CA-05.1: Listar recursos con paginación
```gherkin
Given que existen 50 recursos publicados
When accedo a /explore
Then veo una lista de 20 recursos (página 1)
And cada recurso muestra: título, autor, badge (Sandbox/Validated), tags, votos, usos
And veo controles de paginación: "Anterior" (deshabilitado), "Siguiente", "Página 1 de 3"
```

#### CA-05.2: Navegación de páginas
```gherkin
Given que estoy en /explore página 1
When hago clic en "Siguiente"
Then me redirige a /explore?page=2
And veo recursos 21-40
And botón "Anterior" está habilitado
```

#### CA-05.3: Estado vacío (sin recursos)
```gherkin
Given que no existen recursos publicados
When accedo a /explore
Then veo mensaje: "No hay recursos disponibles aún"
And veo ilustración de empty state
And si estoy autenticado, veo CTA: "Sé el primero en publicar un recurso"
```

#### CA-05.4: Ordenamiento predeterminado
```gherkin
Given que existen recursos con diferentes fechas de creación
When accedo a /explore
Then los recursos están ordenados por fecha de creación (más recientes primero)
```

**Definition of Done:**
- ✅ Página /explore funcional (responsive)
- ✅ API endpoint `GET /resources?page=X` implementado
- ✅ Paginación backend (20 items por página)
- ✅ Componente ResourceCard con información resumida
- ✅ Empty state diseñado e implementado
- ✅ Tests unitarios (componente)
- ✅ Tests de integración (API paginación)
- ✅ Test E2E (navegar catálogo)

**Trazabilidad:**
- Pantalla: `/explore` (Figma: `explore.png`)
- Endpoints: `GET /resources`
- Entidades: `Resource`, `ResourceVersion`, `User`
- Tests: `UT-EXPLORE-01`, `IT-EXPLORE-01`, `E2E-03`

---

### US-06: Buscar y Filtrar Recursos
**Épica:** EPIC-02  
**Prioridad:** Must-Have  
**Estimación:** M  
**Dependencias:** US-05

**Historia:**
> Como usuario,  
> Quiero buscar y filtrar recursos por tipo, estado y tags,  
> Para encontrar exactamente lo que necesito.

**Criterios de Aceptación:**

#### CA-06.1: Búsqueda textual
```gherkin
Given que existen recursos con títulos variados
When ingreso "protein folding" en el campo de búsqueda
And presiono Enter
Then veo solo recursos cuyo título o descripción contiene "protein folding"
And la URL se actualiza a /explore?search=protein+folding
```

#### CA-06.2: Filtro por tipo
```gherkin
Given que existen recursos de tipo Prompt, Workflow y Notebook
When selecciono filtro "Tipo: Prompt"
Then veo solo recursos de tipo Prompt
And la URL se actualiza a /explore?type=Prompt
```

#### CA-06.3: Filtro por estado (Validated)
```gherkin
Given que existen recursos en Sandbox y Validated
When selecciono filtro "Estado: Validated"
Then veo solo recursos con badge Validated
And la URL se actualiza a /explore?status=Validated
```

#### CA-06.4: Filtros combinados
```gherkin
Given que existen recursos variados
When selecciono "Tipo: Workflow" AND "Estado: Validated" AND busco "RNA-seq"
Then veo solo recursos que cumplen los 3 criterios
And la URL contiene todos los parámetros: /explore?type=Workflow&status=Validated&search=RNA-seq
```

#### CA-06.5: Sin resultados
```gherkin
Given que aplico filtros muy restrictivos
When no existen recursos que coincidan
Then veo mensaje: "No se encontraron recursos con estos filtros"
And veo botón "Limpiar filtros"
```

**Definition of Done:**
- ✅ Barra de búsqueda funcional con debounce (300ms)
- ✅ Filtros dropdown (Tipo, Estado, Tags)
- ✅ API soporta query params: `?search=X&type=Y&status=Z&tags=A,B`
- ✅ Filtros persisten en URL (navegación back funciona)
- ✅ Botón "Limpiar filtros"
- ✅ Tests unitarios (lógica de filtros)
- ✅ Tests de integración (API con filtros)
- ✅ Test E2E (buscar + filtrar)

**Trazabilidad:**
- Pantalla: `/explore` (Figma: `explore.png`)
- Endpoints: `GET /resources?search=X&type=Y&status=Z`
- Entidades: `Resource`, `ResourceVersion`
- Tests: `UT-EXPLORE-02`, `IT-EXPLORE-02`, `E2E-04`

---

### US-07: Ver Detalle Completo de Recurso
**Épica:** EPIC-02  
**Prioridad:** Must-Have  
**Estimación:** L  
**Dependencias:** US-05

**Historia:**
> Como usuario,  
> Quiero ver el detalle completo de un recurso,  
> Para evaluar su calidad y decidir si lo uso o reutilizo.

**Criterios de Aceptación:**

#### CA-07.1: Información completa visible
```gherkin
Given que existe un recurso con ID "R-000042"
When accedo a /resources/R-000042
Then veo:
  | Campo                | Ejemplo                                      |
  | Título               | Protein Folding Prompt                       |
  | Autor                | Dr. Ana García (link a perfil)               |
  | Badge estado         | Validated (verde)                            |
  | PID                  | ccg-ai:R-000042@v1.0.0                       |
  | Descripción          | (markdown renderizado)                       |
  | Tipo                 | Prompt                                       |
  | Tags                 | protein, folding, AlphaFold                  |
  | Votos                | 25                                           |
  | Usos                 | 120                                          |
  | Forks                | 5                                            |
  | Fecha creación       | 2026-01-15                                   |
  | Última actualización | 2026-02-10                                   |
```

#### CA-07.2: Contenido según source_type (Internal)
```gherkin
Given que el recurso es source_type = Internal
When veo el detalle
Then veo sección "Contenido" con texto completo
And veo sección "Ejemplo" si existe
```

#### CA-07.3: Contenido según source_type (GitHub-linked)
```gherkin
Given que el recurso es source_type = GitHub-linked
When veo el detalle
Then veo link a repositorio GitHub
And veo tag/commit referenciado
And veo licencia (MIT, Apache, etc.)
And veo botón "View on GitHub" (external link)
```

#### CA-07.4: Botones según rol (Anónimo)
```gherkin
Given que soy usuario anónimo
When veo el detalle de un recurso
Then veo botones deshabilitados:
  - Upvote (con tooltip "Inicia sesión para votar")
  - Reuse (con tooltip "Inicia sesión para reutilizar")
And NO veo botones: Edit, Delete, Validate
```

#### CA-07.5: Botones según rol (Autenticado, no owner)
```gherkin
Given que estoy autenticado pero no soy owner del recurso
When veo el detalle
Then veo botones habilitados:
  - Upvote
  - Reuse
And NO veo botones: Edit, Delete, Validate
```

#### CA-07.6: Botones según rol (Owner)
```gherkin
Given que soy el owner del recurso
When veo el detalle
Then veo botones:
  - Upvote, Reuse (habilitados)
  - Edit, Delete (habilitados)
And NO veo botón: Validate
```

#### CA-07.7: Botones según rol (Admin)
```gherkin
Given que soy Admin
When veo el detalle de cualquier recurso
Then veo todos los botones:
  - Upvote, Reuse, Edit, Delete, Validate (habilitados)
```

#### CA-07.8: Recurso no encontrado
```gherkin
Given que no existe recurso con ID "R-999999"
When accedo a /resources/R-999999
Then veo página 404: "Recurso no encontrado"
And veo botón "Volver a Explorar"
```

**Definition of Done:**
- ✅ Página /resources/:id funcional (responsive)
- ✅ API endpoint `GET /resources/:id` implementado
- ✅ Renderizado de markdown para descripción
- ✅ Badges Sandbox/Validated con estilos diferenciados
- ✅ Botones condicionales según rol
- ✅ Link a perfil de autor
- ✅ Sección "Derived from" si es fork
- ✅ Tests unitarios (componente, lógica de permisos)
- ✅ Tests de integración (API)
- ✅ Test E2E (navegar de Explore → Detail)

**Trazabilidad:**
- Pantalla: `/resources/:id` (Figma: `resource-detail.png`)
- Endpoints: `GET /resources/:id`
- Entidades: `Resource`, `ResourceVersion`, `User`
- Tests: `UT-DETAIL-01`, `IT-DETAIL-01`, `E2E-05`

---

### US-08: Publicar Nuevo Recurso (Internal)
**Épica:** EPIC-03  
**Prioridad:** Must-Have  
**Estimación:** L  
**Dependencias:** US-01, US-02

**Historia:**
> Como usuario autenticado y verificado,  
> Quiero publicar un nuevo recurso con contenido interno,  
> Para compartirlo con la comunidad CCG.

**Criterios de Aceptación:**

#### CA-08.1: Publicación exitosa
```gherkin
Given que soy usuario autenticado con email verificado
When accedo a /publish
And completo el formulario:
  | Campo       | Valor                                  |
  | Título      | RNA-seq Analysis Workflow              |
  | Descripción | Paso a paso para análisis de RNA-seq   |
  | Tipo        | Workflow                               |
  | Source type | Internal                               |
  | Tags        | RNA-seq, bioinformática, transcriptómica |
  | Contenido   | (texto con instrucciones detalladas)   |
  | Ejemplo     | (código de ejemplo)                    |
  | Estado      | Sandbox                                |
And hago clic en "Publish"
Then el sistema crea Resource y ResourceVersion v1.0.0
And me redirige a /resources/:newId
And veo toast: "Recurso publicado exitosamente"
And el recurso tiene badge "Sandbox"
```

#### CA-08.2: Validaciones de formulario
```gherkin
Given que estoy en /publish
When intento enviar formulario sin completar título
Then veo error: "Título es obligatorio"
And el formulario no se envía
```

#### CA-08.3: Solicitar validación al publicar
```gherkin
Given que completo el formulario
When selecciono "Estado: Request Validation"
And hago clic en "Publish"
Then el sistema crea recurso con status = Pending Validation
And crea notificación para Admins: "Nueva solicitud de validación"
And veo toast: "Recurso publicado. Solicitud de validación enviada"
```

#### CA-08.4: Usuario no verificado no puede publicar
```gherkin
Given que mi email NO está verificado
When intento acceder a /publish
Then me redirige a /profile
And veo mensaje: "Verifica tu email antes de publicar recursos"
```

**Definition of Done:**
- ✅ Página /publish funcional con formulario completo
- ✅ Validaciones frontend (campos obligatorios, max length)
- ✅ API endpoint `POST /resources` implementado
- ✅ Validaciones backend (email_verified, campos obligatorios)
- ✅ Creación de Resource + ResourceVersion v1.0.0
- ✅ Generación de PID: `ccg-ai:R-XXXXXX@v1.0.0`
- ✅ Cálculo de content_hash (SHA256)
- ✅ Notificación a Admins si Request Validation
- ✅ Tests unitarios + integración
- ✅ Test E2E (publicar recurso → ver detalle)

**Trazabilidad:**
- Pantalla: `/publish` (Figma: `publish.png`)
- Endpoints: `POST /resources`
- Entidades: `Resource`, `ResourceVersion`
- Tests: `UT-PUBLISH-01`, `IT-PUBLISH-01`, `E2E-06`

---

### US-16: Votar Recurso
**Épica:** EPIC-05  
**Prioridad:** Must-Have  
**Estimación:** S  
**Dependencias:** US-07

**Historia:**
> Como usuario autenticado,  
> Quiero votar un recurso para reconocer su valor,  
> Con la opción de deshacer mi voto (toggle).

**Criterios de Aceptación:**

#### CA-16.1: Votar recurso (primera vez)
```gherkin
Given que estoy autenticado
And que no he votado el recurso "R-000042"
And el recurso tiene 25 votos
When hago clic en botón "Upvote"
Then el sistema registra mi voto
And el contador incrementa visualmente: 25 → 26
And el botón cambia a estado "voted" (icono relleno)
And veo toast: "Voto registrado"
```

#### CA-16.2: Deshacer voto (toggle)
```gherkin
Given que ya voté el recurso "R-000042"
And el botón muestra estado "voted"
When hago clic en botón "Upvote" nuevamente
Then el sistema elimina mi voto
And el contador decrementa: 26 → 25
And el botón cambia a estado "not voted" (icono outline)
And veo toast: "Voto retirado"
```

#### CA-16.3: Usuario anónimo no puede votar
```gherkin
Given que soy usuario anónimo
When intento hacer clic en "Upvote"
Then veo tooltip: "Inicia sesión para votar"
And el botón está deshabilitado
```

#### CA-16.4: Persistencia de votos
```gherkin
Given que voté el recurso "R-000042"
When recargo la página
Then el botón sigue mostrando estado "voted"
And el contador mantiene mi voto
```

**Definition of Done:**
- ✅ Botón Upvote con estados (not voted, voted, disabled)
- ✅ API endpoint `POST /resources/:id/vote` (idempotente, toggle)
- ✅ Validación: 1 voto por usuario por recurso
- ✅ Optimistic update en frontend (UX inmediata)
- ✅ Rollback si API falla
- ✅ Tests unitarios (lógica toggle)
- ✅ Tests de integración (API vote)
- ✅ Test E2E (votar → desvotar)

**Trazabilidad:**
- Pantalla: `/resources/:id` (dentro de resource-detail)
- Endpoints: `POST /resources/:id/vote`
- Entidades: `Vote` (`user_id`, `resource_id`)
- Tests: `UT-VOTE-01`, `IT-VOTE-01`, `E2E-07`

---

### US-17: Reutilizar Recurso (Fork)
**Épica:** EPIC-05  
**Prioridad:** Must-Have  
**Estimación:** M  
**Dependencias:** US-07, US-10

**Historia:**
> Como usuario autenticado,  
> Quiero reutilizar (fork) un recurso existente,  
> Para adaptarlo a mi caso de uso sin partir de cero.

**Criterios de Aceptación:**

#### CA-17.1: Fork exitoso
```gherkin
Given que estoy autenticado
And que existe recurso "R-000042" con título "Protein Folding Prompt"
When hago clic en botón "Reuse This Resource"
Then el sistema crea un nuevo Resource:
  - owner = yo
  - derived_from_resource_id = R-000042
  - source_type = Internal
And crea ResourceVersion v1.0.0 copiando contenido del original
And incrementa forks_count del recurso original: 5 → 6
And me redirige a /resources/:newId/edit
And veo banner: "Recurso reutilizado exitosamente. Edítalo y publícalo"
```

#### CA-17.2: Trazabilidad bidireccional
```gherkin
Given que forkeé recurso "R-000042"
When veo el detalle de mi fork
Then veo sección "Derived from: Protein Folding Prompt (R-000042)" con link
And cuando accedo al recurso original (R-000042)
Then veo "Forked 6 times"
```

#### CA-17.3: Fork de fork
```gherkin
Given que mi recurso "R-000100" es un fork de "R-000042"
When otro usuario forkea mi recurso
Then el nuevo fork deriva de R-000100 (no del original R-000042)
And la trazabilidad muestra cadena: R-000042 → R-000100 → R-000150
```

#### CA-17.4: Usuario anónimo no puede forkear
```gherkin
Given que soy usuario anónimo
When intento hacer clic en "Reuse"
Then veo tooltip: "Inicia sesión para reutilizar"
And el botón está deshabilitado
```

**Definition of Done:**
- ✅ Botón "Reuse" funcional
- ✅ API endpoint `POST /resources/:id/fork` implementado
- ✅ Creación de nuevo Resource con campos derived_from_*
- ✅ Copia de ResourceVersion latest del original
- ✅ Incremento de forks_count en original
- ✅ Redireccionamiento automático a /edit del fork
- ✅ Sección "Derived from" en detalle de fork
- ✅ Tests unitarios + integración
- ✅ Test E2E (forkear → editar → publicar)

**Trazabilidad:**
- Pantalla: `/resources/:id` (botón Reuse) → `/resources/:newId/edit`
- Endpoints: `POST /resources/:id/fork`
- Entidades: `Resource` (`derived_from_resource_id`, `derived_from_version_id`)
- Tests: `UT-FORK-01`, `IT-FORK-01`, `E2E-08`

---

### US-13: Validar Recurso Manualmente (Admin)
**Épica:** EPIC-04  
**Prioridad:** Must-Have  
**Estimación:** M  
**Dependencias:** US-07

**Historia:**
> Como Admin,  
> Quiero validar manualmente un recurso,  
> Para garantizar calidad institucional sin esperar criterios automáticos.

**Criterios de Aceptación:**

#### CA-13.1: Validar recurso en Sandbox
```gherkin
Given que soy Admin
And que existe recurso "R-000042" con status = Sandbox
When accedo a /resources/R-000042
And hago clic en botón "Validate" (visible solo para Admin)
Then veo modal de confirmación: "¿Validar este recurso?"
And cuando hago clic en "Confirm"
Then el sistema actualiza latest_version.status = Validated
And registra validated_at = now()
And crea notificación para owner: "Tu recurso ha sido validado"
And el badge cambia a "Validated" (verde)
And veo toast: "Recurso validado exitosamente"
```

#### CA-13.2: Validar recurso con Pending Validation
```gherkin
Given que existe recurso con status = Pending Validation
And el owner solicitó validación al publicar
When Admin lo valida manualmente
Then el flujo es igual a CA-13.1
And la notificación a owner menciona: "Tu solicitud de validación ha sido aprobada"
```

#### CA-13.3: Usuario no-admin no ve botón Validate
```gherkin
Given que soy usuario autenticado pero NO Admin
When veo el detalle de un recurso
Then NO veo botón "Validate"
```

#### CA-13.4: Owner no puede auto-validar
```gherkin
Given que soy owner del recurso "R-000042"
And NO soy Admin
When veo el detalle de mi recurso
Then NO veo botón "Validate"
```

**Definition of Done:**
- ✅ Botón "Validate" visible solo para Admin
- ✅ Modal de confirmación
- ✅ API endpoint `POST /resources/:id/validate` implementado
- ✅ Middleware de autorización (solo Admin)
- ✅ Actualización de status y validated_at
- ✅ Creación de notificación para owner
- ✅ Tests unitarios (permisos)
- ✅ Tests de integración (API validate)
- ✅ Test E2E (Admin valida → Owner recibe notificación)

**Trazabilidad:**
- Pantalla: `/resources/:id` (botón Validate)
- Endpoints: `POST /resources/:id/validate`
- Entidades: `ResourceVersion` (`status`, `validated_at`), `Notification`
- Tests: `UT-VALIDATE-01`, `IT-VALIDATE-01`, `E2E-09`

---

### US-18: Notificaciones In-App
**Épica:** EPIC-05  
**Prioridad:** Must-Have  
**Estimación:** M  
**Dependencias:** US-13 (validación genera notificación)

**Historia:**
> Como usuario autenticado,  
> Quiero recibir notificaciones in-app de eventos importantes,  
> Para estar informado del estado de mis recursos.

**Criterios de Aceptación:**

#### CA-18.1: Badge de notificaciones no leídas
```gherkin
Given que tengo 3 notificaciones no leídas
When estoy en cualquier página autenticada
Then veo badge rojo con número "3" en icono de campana (navbar)
```

#### CA-18.2: Panel de notificaciones
```gherkin
Given que tengo notificaciones
When hago clic en icono de campana
Then se abre panel desplegable con lista de notificaciones
And cada notificación muestra:
  - Icono según tipo
  - Mensaje
  - Timestamp relativo ("hace 2 horas")
  - Estado: unread (fondo destacado) o read
  - Link al recurso relacionado
```

#### CA-18.3: Tipos de notificación (MVP)
```gherkin
Given que ocurren eventos relevantes
Then recibo notificaciones para:
  | Tipo                   | Mensaje ejemplo                                        |
  | ResourceValidated      | "Tu recurso 'RNA-seq Workflow' ha sido validado"      |
  | ResourceForked         | "Juan Pérez reutilizó tu recurso 'Protein Prompt'"    |
  | ValidationRevoked      | "Tu recurso fue movido a Sandbox. Razón: [texto]"     |
  | ValidationRequested    | (Solo Admin) "Nueva solicitud de validación de Ana García" |
```

#### CA-18.4: Marcar notificación como leída
```gherkin
Given que tengo notificación no leída sobre validación
When hago clic en la notificación
Then me redirige al recurso mencionado
And la notificación se marca como leída (read_at = now())
And el badge decrementa: 3 → 2
```

#### CA-18.5: Marcar todas como leídas
```gherkin
Given que tengo 5 notificaciones no leídas
When hago clic en "Mark all as read"
Then todas se marcan como leídas
And el badge desaparece
```

#### CA-18.6: Estado vacío
```gherkin
Given que no tengo notificaciones
When hago clic en campana
Then veo mensaje: "No tienes notificaciones"
And veo ilustración de empty state
```

**Definition of Done:**
- ✅ Icono de campana en navbar con badge
- ✅ Panel desplegable con lista de notificaciones
- ✅ API endpoint `GET /notifications` implementado
- ✅ API endpoint `PATCH /notifications/:id/read` implementado
- ✅ API endpoint `POST /notifications/mark-all-read` implementado
- ✅ Polling cada 30s para actualizar badge (o WebSockets post-MVP)
- ✅ Notificaciones se crean automáticamente en eventos (validación, fork)
- ✅ Tests unitarios (componente)
- ✅ Tests de integración (API notifications)
- ✅ Test E2E (validar recurso → owner recibe notificación)

**Trazabilidad:**
- Pantalla: Navbar (campana) + Panel desplegable
- Endpoints: `GET /notifications`, `PATCH /notifications/:id/read`, `POST /notifications/mark-all-read`
- Entidades: `Notification`
- Tests: `UT-NOTIF-01`, `IT-NOTIF-01`, `E2E-10`

---

## HISTORIAS SHOULD-HAVE (FASE 2: EXPANSIÓN)

---

### US-20: Editar Recurso Propio con Versionado
**Épica:** EPIC-03  
**Prioridad:** Should-Have  
**Estimación:** L  
**Dependencias:** US-08

**Historia:**
> Como owner de un recurso,  
> Quiero editarlo después de publicado,  
> Con versionado automático si la última versión está Validated.

(Criterios de aceptación omitidos por brevedad, ver PRD_REFINED.md RF-EDIT-01)

---

### US-21: Eliminar Recurso Propio
**Épica:** EPIC-03  
**Prioridad:** Should-Have  
**Estimación:** S  
**Dependencias:** US-08

**Historia:**
> Como owner de un recurso,  
> Quiero eliminarlo si ya no es relevante,  
> Con confirmación para evitar errores.

(Criterios de aceptación omitidos por brevedad, ver PRD_REFINED.md RF-EDIT-02)

---

### US-22: Historial de Versiones
**Épica:** EPIC-03  
**Prioridad:** Should-Have  
**Estimación:** M  
**Dependencias:** US-20

**Historia:**
> Como usuario,  
> Quiero ver el historial de versiones de un recurso,  
> Para entender su evolución.

---

### US-23: Reportar Recurso
**Épica:** EPIC-04  
**Prioridad:** Should-Have  
**Estimación:** M  
**Dependencias:** US-07

**Historia:**
> Como usuario autenticado,  
> Quiero reportar un recurso con contenido inapropiado o erróneo,  
> Para mantener la calidad de la plataforma.

---

### US-24: Gestión de Reportes (Admin)
**Épica:** EPIC-04  
**Prioridad:** Should-Have  
**Estimación:** M  
**Dependencias:** US-23

**Historia:**
> Como Admin,  
> Quiero gestionar reportes de usuarios,  
> Para tomar acciones sobre recursos problemáticos.

---

## RESUMEN DE PRIORIZACIÓN

### Must-Have (MVP - 10 historias):
- US-01: Registro con verificación
- US-02: Login/Logout
- US-05: Explorar catálogo
- US-06: Buscar y filtrar
- US-07: Ver detalle de recurso
- US-08: Publicar recurso (Internal)
- US-13: Validar recurso (Admin)
- US-16: Votar recurso
- US-17: Reutilizar (fork)
- US-18: Notificaciones in-app

**Total estimado:** ~8-10 sprints (asumiendo 1-2 historias por sprint)

### Should-Have (Fase 2 - 5 historias):
- US-20: Editar recurso con versionado
- US-21: Eliminar recurso
- US-22: Historial de versiones
- US-23: Reportar recurso
- US-24: Gestión de reportes (Admin)

### Could-Have (Fase 3):
- US-30: Notificaciones por email
- US-31: Comparación de versiones (diff)
- US-32: Analytics dashboard para owners
- US-33: Búsqueda semántica
- US-34: API pública

---

## MAPEO: ÉPICAS → HISTORIAS → TICKETS

Cada historia Must-Have generará múltiples tickets técnicos en GitHub Issues:

**Ejemplo: US-08 (Publicar Recurso)**
- `T-015` — Diseñar formulario /publish (Frontend)
- `T-016` — Implementar validaciones frontend (Frontend)
- `T-017` — Crear endpoint POST /resources (Backend)
- `T-018` — Implementar validaciones backend (Backend)
- `T-019` — Crear ResourceVersion con PID (Backend)
- `T-020` — Calcular content_hash SHA256 (Backend)
- `T-021` — Tests unitarios formulario (Frontend)
- `T-022` — Tests integración API /resources (Backend)
- `T-023` — Test E2E publicar recurso (QA)

**Trazabilidad:** Cada ticket en GitHub debe referenciar `User Story: US-08`.

---

## CHANGELOG

### v1.0 — 2026-02-16
- Épicas y historias Must-Have definidas
- Criterios de aceptación en formato Given/When/Then
- Definition of Done por historia
- Trazabilidad con pantallas, endpoints, entidades, tests
- Estimaciones y dependencias identificadas
- Should-Have para Fase 2 listadas

---

**Siguiente artefacto:** UI_STATES.md (BLOQUEADOR CRÍTICO)  
**Rol siguiente:** UX Lead + Tech Lead
