# BDD FEATURES — BioAI Hub

# Este archivo contiene features en formato Gherkin (BDD)
# para las historias Must-Have del MVP.
#
# Herramienta: pytest-bdd (backend)
# Referencia: EPICS_AND_STORIES.md

# =============================================================================
# FEATURE 1: USER REGISTRATION (US-01)
# =============================================================================

Feature: User Registration
  Como usuario nuevo
  Quiero registrarme con mi email y verificar mi cuenta
  Para poder publicar recursos en la plataforma

  Background:
    Given la base de datos está limpia
    And no existe usuario con email "juan@example.com"

  Scenario: Successful registration
    Given que no estoy registrado
    When envío POST a /api/auth/register/ con:
      | campo      | valor              |
      | email      | juan@example.com   |
      | name       | Juan Pérez         |
      | password   | SecurePass123!     |
    Then recibo código de estado 201
    And la respuesta contiene "user_id"
    And el usuario es creado con email_verified_at NULL
    And se envía email de verificación a "juan@example.com"

  Scenario: Duplicate email
    Given que existe usuario con email "juan@example.com"
    When envío POST a /api/auth/register/ con email "juan@example.com"
    Then recibo código de estado 409
    And el mensaje de error contiene "already registered"

  Scenario: Weak password rejected
    When envío POST a /api/auth/register/ con password "12345"
    Then recibo código de estado 400
    And el mensaje de error contiene "password"

  Scenario: Invalid email format
    When envío POST a /api/auth/register/ con email "invalid-email"
    Then recibo código de estado 400
    And el mensaje de error contiene "email"

  Scenario: Email verification success
    Given que me registré con email "juan@example.com"
    And recibí email con token de verificación
    When envío GET a /api/auth/verify-email/{token}
    Then recibo código de estado 200
    And el usuario tiene email_verified_at NOT NULL
    And el mensaje indica "Email verificado"

  Scenario: Email verification with expired token
    Given que me registré hace 25 horas
    And el token de verificación ha expirado (>24h)
    When intento verificar con el token expirado
    Then recibo código de estado 400
    And el mensaje contiene "expired"

# =============================================================================
# FEATURE 2: USER LOGIN (US-02)
# =============================================================================

Feature: User Login
  Como usuario registrado y verificado
  Quiero iniciar sesión con mi email y contraseña
  Para acceder a features protegidas

  Background:
    Given existe usuario con:
      | email            | name       | email_verified |
      | juan@example.com | Juan Pérez | true           |

  Scenario: Successful login
    When envío POST a /api/auth/login/ con:
      | email            | password       |
      | juan@example.com | SecurePass123! |
    Then recibo código de estado 200
    And la respuesta contiene "access" token
    And la respuesta contiene información del usuario
    And el token JWT es válido

  Scenario: Invalid credentials
    When envío POST a /api/auth/login/ con password incorrecta
    Then recibo código de estado 401
    And el mensaje contiene "Invalid credentials"

  Scenario: Email not verified
    Given que mi email NO está verificado (email_verified_at IS NULL)
    When intento iniciar sesión
    Then recibo código de estado 403
    And el código de error es "EMAIL_NOT_VERIFIED"

  Scenario: Account suspended
    Given que mi cuenta está suspendida (is_active = false)
    When intento iniciar sesión
    Then recibo código de estado 403
    And el mensaje contiene "suspended"

  Scenario: Rate limiting after 5 failed attempts
    When envío 5 intentos de login con contraseña incorrecta
    And envío un 6to intento
    Then recibo código de estado 429
    And el mensaje contiene "rate limit"

# =============================================================================
# FEATURE 3: EXPLORE RESOURCES (US-05)
# =============================================================================

Feature: Explore Resources
  Como usuario (anónimo o autenticado)
  Quiero explorar el catálogo de recursos con paginación
  Para descubrir recursos de IA relevantes

  Background:
    Given existen 50 recursos publicados en la plataforma

  Scenario: List resources with pagination
    When envío GET a /api/resources/
    Then recibo código de estado 200
    And la respuesta contiene 20 recursos (página 1)
    And la respuesta contiene "count" = 50
    And la respuesta contiene "next" URL
    And cada recurso muestra: título, autor, badge, tags, votos

  Scenario: Navigate to page 2
    When envío GET a /api/resources/?page=2
    Then recibo código de estado 200
    And la respuesta contiene recursos 21-40
    And la respuesta contiene "previous" URL

  Scenario: Empty state (no resources)
    Given que NO existen recursos publicados
    When envío GET a /api/resources/
    Then recibo código de estado 200
    And la respuesta contiene "count" = 0
    And la respuesta contiene "results" = []

  Scenario: Default ordering (most recent first)
    Given que existen recursos con diferentes fechas
    When envío GET a /api/resources/
    Then los recursos están ordenados por created_at DESC

# =============================================================================
# FEATURE 4: SEARCH AND FILTER (US-06)
# =============================================================================

Feature: Search and Filter Resources
  Como usuario
  Quiero buscar y filtrar recursos por tipo, estado y tags
  Para encontrar exactamente lo que necesito

  Background:
    Given existen recursos variados:
      | título                | tipo      | status    | tags                |
      | Protein Folding       | Prompt    | Validated | protein, folding    |
      | RNA-seq Workflow      | Workflow  | Sandbox   | RNA-seq, bio        |
      | AlphaFold Notebook    | Notebook  | Validated | protein, AlphaFold  |

  Scenario: Text search in title
    When envío GET a /api/resources/?search=protein
    Then recibo 2 recursos (Protein Folding, AlphaFold Notebook)

  Scenario: Filter by type
    When envío GET a /api/resources/?type=Workflow
    Then recibo 1 recurso (RNA-seq Workflow)

  Scenario: Filter by status Validated
    When envío GET a /api/resources/?status=Validated
    Then recibo 2 recursos (Protein Folding, AlphaFold Notebook)

  Scenario: Combined filters
    When envío GET a /api/resources/?type=Prompt&status=Validated&search=protein
    Then recibo 1 recurso (Protein Folding)

  Scenario: No results with restrictive filters
    When envío GET a /api/resources/?type=Dataset&status=Validated
    Then recibo código 200
    And count = 0
    And results = []

# =============================================================================
# FEATURE 5: RESOURCE DETAIL (US-07)
# =============================================================================

Feature: Resource Detail
  Como usuario
  Quiero ver el detalle completo de un recurso
  Para evaluar su calidad y decidir si lo uso

  Background:
    Given existe recurso "R-123" con:
      | campo       | valor                     |
      | título      | Protein Folding Prompt    |
      | status      | Validated                 |
      | votes       | 25                        |
      | forks_count | 5                         |

  Scenario: View resource detail (public access)
    When envío GET a /api/resources/R-123/
    Then recibo código 200
    And veo título "Protein Folding Prompt"
    And veo badge "Validated"
    And veo PID "ccg-ai:R-123@v1.0.0"
    And veo autor con link a perfil
    And veo métricas: 25 votos, 5 forks

  Scenario: Resource not found
    When envío GET a /api/resources/R-999999/
    Then recibo código 404

  Scenario: Buttons for anonymous user
    Given que NO estoy autenticado
    When consulto detalle del recurso
    Then los botones Upvote y Reuse están en respuesta
    But mi rol no permite acción (frontend lo deshabilita)

  Scenario: Buttons for authenticated user (not owner)
    Given que estoy autenticado como "user2@example.com"
    And NO soy owner del recurso R-123
    When consulto detalle
    Then puedo votar y reutilizar
    But NO puedo editar ni eliminar

  Scenario: Buttons for owner
    Given que estoy autenticado como owner del recurso
    When consulto detalle
    Then puedo votar, reutilizar, editar y eliminar
    But NO puedo validar (solo Admin)

  Scenario: Buttons for admin
    Given que estoy autenticado como Admin
    When consulto detalle de cualquier recurso
    Then puedo votar, reutilizar, editar, eliminar Y validar

# =============================================================================
# FEATURE 6: PUBLISH RESOURCE (US-08)
# =============================================================================

Feature: Publish Resource
  Como usuario autenticado y verificado
  Quiero publicar un nuevo recurso con contenido interno
  Para compartirlo con la comunidad

  Background:
    Given estoy autenticado como "juan@example.com"
    And mi email está verificado

  Scenario: Publish Internal resource successfully
    When envío POST a /api/resources/ con:
      | campo       | valor                          |
      | title       | RNA-seq Analysis Workflow      |
      | description | Paso a paso para análisis...   |
      | type        | Workflow                       |
      | source_type | Internal                       |
      | tags        | ["RNA-seq", "bio"]             |
      | content     | Instrucciones detalladas...    |
      | status      | Sandbox                        |
    Then recibo código 201
    And se crea Resource con owner = yo
    And se crea ResourceVersion v1.0.0 con status = Sandbox
    And se genera PID "ccg-ai:R-{id}@v1.0.0"
    And se calcula content_hash SHA256

  Scenario: Publish with Request Validation
    When envío POST con status = "Pending Validation"
    Then se crea recurso con status = Pending Validation
    And se crea notificación para Admins: "Nueva solicitud de validación"

  Scenario: Publish without email verified
    Given que mi email NO está verificado
    When intento publicar recurso
    Then recibo código 403
    And el error es "EMAIL_NOT_VERIFIED"

  Scenario: Publish GitHub-linked resource
    When envío POST con:
      | source_type | GitHub-Linked                      |
      | repo_url    | https://github.com/user/repo       |
      | repo_tag    | v1.2.0                             |
      | license     | MIT                                |
    Then se crea recurso con source_type = GitHub-Linked
    And NO se requiere campo "content"
    And repo_url y license son obligatorios

  Scenario: Validation error - missing required fields
    When envío POST sin campo "title"
    Then recibo código 400
    And el error indica "title" es obligatorio

# =============================================================================
# FEATURE 7: VOTE RESOURCE (US-16)
# =============================================================================

Feature: Vote Resource
  Como usuario autenticado
  Quiero votar un recurso para reconocer su valor
  Con opción de deshacer mi voto (toggle)

  Background:
    Given existe recurso "R-123" con 25 votos
    And estoy autenticado como "juan@example.com"

  Scenario: Vote resource (first time)
    Given que NO he votado el recurso R-123
    When envío POST a /api/resources/R-123/vote/
    Then recibo código 200
    And la respuesta indica voted = true
    And votes_count = 26
    And se crea registro en tabla votes

  Scenario: Unvote resource (toggle)
    Given que YA voté el recurso R-123
    When envío POST a /api/resources/R-123/vote/
    Then recibo código 200
    And la respuesta indica voted = false
    And votes_count = 25
    And se elimina registro de tabla votes

  Scenario: Anonymous user cannot vote
    Given que NO estoy autenticado
    When intento votar recurso
    Then recibo código 401

  Scenario: Vote persists after page reload
    Given que voté el recurso R-123
    When consulto GET /api/resources/R-123/
    Then la respuesta indica que ya voté (has_voted = true)

# =============================================================================
# FEATURE 8: FORK RESOURCE (US-17)
# =============================================================================

Feature: Fork Resource (Reuse)
  Como usuario autenticado
  Quiero reutilizar (fork) un recurso existente
  Para adaptarlo a mi caso sin partir de cero

  Background:
    Given existe recurso "R-042" con:
      | owner       | other@example.com      |
      | título      | Protein Folding Prompt |
      | version     | 1.0.0                  |
      | status      | Validated              |
      | content     | Original content...    |
    And estoy autenticado como "juan@example.com"

  Scenario: Fork resource successfully
    When envío POST a /api/resources/R-042/fork/
    Then recibo código 201
    And se crea nuevo Resource con:
      | owner                      | juan@example.com (yo) |
      | derived_from_resource_id   | R-042                 |
      | derived_from_version_id    | (version id de v1.0.0)|
      | source_type                | Internal              |
    And se crea ResourceVersion v1.0.0 copiando contenido del original
    And status del fork = Sandbox
    And forks_count del recurso original incrementa: 5 → 6
    And la respuesta indica el ID del nuevo recurso

  Scenario: Fork traceability bidirectional
    Given que forkeé recurso R-042 (creando R-100)
    When consulto GET /api/resources/R-100/
    Then veo "derived_from_resource" apuntando a R-042
    And cuando consulto GET /api/resources/R-042/
    Then veo forks_count = 6

  Scenario: Anonymous user cannot fork
    Given que NO estoy autenticado
    When intento forkear recurso
    Then recibo código 401

# =============================================================================
# FEATURE 9: VALIDATE RESOURCE (US-13)
# =============================================================================

Feature: Validate Resource (Admin)
  Como Admin
  Quiero validar manualmente un recurso
  Para garantizar calidad institucional

  Background:
    Given existe recurso "R-123" con status = Sandbox
    And estoy autenticado como Admin

  Scenario: Validate resource manually
    When envío POST a /api/resources/R-123/validate/
    Then recibo código 200
    And latest_version.status cambia a "Validated"
    And latest_version.validated_at = now()
    And se crea notificación para owner: "Tu recurso ha sido validado"

  Scenario: Validate resource with Pending Validation
    Given que recurso tiene status = Pending Validation
    When Admin valida manualmente
    Then el flujo es igual
    And la notificación menciona "solicitud aprobada"

  Scenario: Non-admin cannot validate
    Given que estoy autenticado como User (NO Admin)
    When intento validar recurso
    Then recibo código 403

  Scenario: Owner cannot self-validate
    Given que soy owner del recurso R-123
    And NO soy Admin
    When intento validar mi propio recurso
    Then recibo código 403

# =============================================================================
# FEATURE 10: NOTIFICATIONS (US-18)
# =============================================================================

Feature: Notifications In-App
  Como usuario autenticado
  Quiero recibir notificaciones de eventos importantes
  Para estar informado del estado de mis recursos

  Background:
    Given estoy autenticado como "juan@example.com"

  Scenario: Receive notification when resource is validated
    Given que mi recurso "R-123" tiene status = Sandbox
    When Admin valida el recurso
    Then se crea notificación con:
      | type     | ResourceValidated                        |
      | message  | Tu recurso ha sido validado              |
      | resource | R-123                                    |
      | read_at  | NULL                                     |

  Scenario: List notifications
    Given que tengo 3 notificaciones (2 no leídas, 1 leída)
    When envío GET a /api/notifications/
    Then recibo código 200
    And la respuesta contiene 3 notificaciones
    And unread_count = 2

  Scenario: Mark notification as read
    Given que tengo notificación no leída con id "N-001"
    When envío PATCH a /api/notifications/N-001/read/
    Then recibo código 200
    And la notificación tiene read_at = now()
    And unread_count decrementa en 1

  Scenario: Mark all as read
    Given que tengo 5 notificaciones no leídas
    When envío POST a /api/notifications/mark-all-read/
    Then recibo código 200
    And todas las notificaciones tienen read_at = now()
    And unread_count = 0

  Scenario: Empty state (no notifications)
    Given que NO tengo notificaciones
    When consulto GET /api/notifications/
    Then count = 0
    And results = []

# =============================================================================
# FEATURE 11: EDIT RESOURCE WITH VERSIONING (US-20 - Should-Have)
# =============================================================================

Feature: Edit Resource with Versioning
  Como owner de un recurso
  Quiero editarlo después de publicado
  Con versionado automático si está Validated

  Background:
    Given soy owner del recurso "R-123"
    And estoy autenticado

  Scenario: Edit Sandbox resource (update in-place)
    Given que latest_version tiene status = Sandbox
    When envío PATCH a /api/resources/R-123/ con:
      | title | Updated Title |
    Then recibo código 200
    And latest_version se actualiza in-place (NO nueva versión)
    And version_number sigue siendo "1.0.0"
    And updated_at se actualiza

  Scenario: Edit Validated resource (create new version)
    Given que latest_version tiene:
      | version_number | 1.0.0     |
      | status         | Validated |
    When envío PATCH a /api/resources/R-123/ con:
      | title     | Updated Title                |
      | changelog | Added AlphaFold 3 support    |
    Then recibo código 200
    And se crea nueva ResourceVersion:
      | version_number | 1.1.0   |
      | status         | Sandbox |
      | is_latest      | true    |
    And la versión anterior (v1.0.0):
      | status    | Validated (sin cambios) |
      | is_latest | false                   |
    And la respuesta indica version_created = true

  Scenario: Non-owner cannot edit
    Given que NO soy owner del recurso
    And NO soy Admin
    When intento editar recurso
    Then recibo código 403

# =============================================================================
# FEATURE 12: AUTO-PROMOTION (US-14 - Validation)
# =============================================================================

Feature: Auto-Promotion to Validated
  Como sistema
  Quiero promocionar automáticamente recursos que cumplan criterios
  Para validar calidad basada en evidencia comunitaria

  Background:
    Given existe recurso "R-123" con:
      | status      | Sandbox           |
      | votes_count | 10                |
      | uses_count  | 50                |
      | created_at  | hace 15 días      |
      | reports     | 0 críticos        |

  Scenario: Auto-promotion when all criteria met
    When el job de promoción automática se ejecuta (cron diario)
    Then el sistema evalúa criterios para R-123:
      | criterio           | valor | cumple |
      | votes >= 10        | 10    | ✓      |
      | uses >= 50         | 50    | ✓      |
      | age >= 14 días     | 15    | ✓      |
      | reports_critical=0 | 0     | ✓      |
    And R-123 se promociona a Validated
    And validated_at = now()
    And se crea notificación para owner: "Tu recurso ha sido validado automáticamente"

  Scenario: No promotion if votes insufficient
    Given que recurso tiene solo 9 votos (< 10)
    When el job se ejecuta
    Then el recurso NO se promociona
    And status sigue siendo Sandbox

  Scenario: No promotion if too recent
    Given que recurso fue creado hace 10 días (< 14)
    When el job se ejecuta
    Then el recurso NO se promociona

# =============================================================================
# FEATURE 13: REVOKE VALIDATION (US-15 - Validation)
# =============================================================================

Feature: Revoke Validation (Admin)
  Como Admin
  Quiero revocar validación de un recurso
  Para revertir recursos que ya no cumplen estándares

  Background:
    Given existe recurso "R-123" con status = Validated
    And estoy autenticado como Admin

  Scenario: Revoke validation with reason
    When envío POST a /api/resources/R-123/revoke-validation/ con:
      | reason | Contenido desactualizado, referencias rotas |
    Then recibo código 200
    And latest_version.status cambia a Sandbox
    And validated_at = NULL
    And se crea notificación para owner con razón incluida

  Scenario: Revoke without reason fails
    When intento revocar sin incluir "reason"
    Then recibo código 400
    And el error indica "reason is required"

  Scenario: Non-admin cannot revoke
    Given que estoy autenticado como User (NO Admin)
    When intento revocar validación
    Then recibo código 403
