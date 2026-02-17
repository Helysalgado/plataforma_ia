# Prompts Clave — Plataforma CCG IA

**Proyecto**: BioAI Hub — Institutional AI Repository  
**Herramienta**: Claude Sonnet 4.5 en Cursor IDE  
**Periodo**: Febrero 2026  
**Documentación completa**: [`docs/ai/AI_USAGE_LOG.md`](docs/ai/AI_USAGE_LOG.md) (4,200+ líneas)

---

## 📖 Índice

1. [Introducción](#introducción)
2. [Prompts de Orquestación](#prompts-de-orquestación)
3. [Prompts de Producto](#prompts-de-producto)
4. [Prompts de Arquitectura](#prompts-de-arquitectura)
5. [Prompts de Implementación](#prompts-de-implementación)
6. [Prompts de UX/UI](#prompts-de-uxui)
7. [Prompts de Debugging](#prompts-de-debugging)
8. [Cómo Guiar al Asistente](#cómo-guiar-al-asistente)

---

## 🎯 Introducción

Este documento resume los **prompts más relevantes** utilizados durante el desarrollo de la Plataforma CCG IA. Para cada sección del proyecto (producto, arquitectura, modelo de datos, API, etc.), se incluyen hasta 3 prompts clave que guiaron la generación de artefactos.

**Nota**: Los prompts aquí son versiones resumidas. Para ver el contexto completo, conversaciones y ajustes humanos, consultar [`docs/ai/AI_USAGE_LOG.md`](docs/ai/AI_USAGE_LOG.md).

---

## 🎼 Prompts de Orquestación

### Prompt 1: Inicio del Proyecto con Protocolo

**Contexto**: Establecer el flujo de trabajo y protocolo de desarrollo

**Prompt**:
```
Usa /orchestration/ORCHESTRATOR_MASTER.md como protocolo activo. 
Revisa toda la documentación y evalúa el estado actual del proyecto 
y continúa desde la fase correspondiente.

Decisiones iniciales:
- Nombre: BioAI Hub
- Dominio: bioai.ccg.unam.mx
- Autenticación: cualquier email
- Roles: Admin y User
- DaC: Mermaid (simple), PlantUML (complejo)
```

**Resultado**: 
- Establecimiento del protocolo de 8 fases
- Identificación de fase actual (FASE 1: Auditoría)
- Creación de estructura de documentación

**Archivo generado**: Protocolo seguido en todas las sesiones

**Guía al asistente**: 
- Proporcioné un protocolo estructurado ([`orchestration/ORCHESTRATOR_MASTER.md`](orchestration/ORCHESTRATOR_MASTER.md))
- Definí decisiones clave por adelantado
- Pedí evaluación del estado antes de continuar

---

### Prompt 2: Auditoría Técnica

**Contexto**: Identificar huecos y riesgos en la documentación inicial

**Prompt**:
```
Rol activo: Tech Lead/Architect

Audita el PRD_BASE.md, diseños Figma y NAVIGATION_FLOW.md:
1. Identifica fortalezas y huecos
2. Lista riesgos técnicos
3. Formula máximo 7 preguntas críticas
4. Propón mejoras concretas

No avanzar a FASE 2 sin respuestas o decisiones explícitas.
```

**Resultado**:
- [`docs/review/TECH_AUDIT.md`](docs/review/TECH_AUDIT.md) (435 líneas)
- 8 riesgos técnicos identificados
- 5 preguntas críticas formuladas
- Identificación de bloqueador: falta UI_STATES.md

**Guía al asistente**:
- Asigné rol explícito (Tech Lead)
- Establecí límite de preguntas (máx 7)
- Definí condición de bloqueo para avanzar

---

### Prompt 3: Consolidación de Especificaciones

**Contexto**: Generar documentos de producto refinados

**Prompt**:
```
Usa /orchestration/SPEC_CONSOLIDATION_PROMPT.md

Genera documentos consolidados:
1. PRODUCT_BRIEF.md (resumen ejecutivo 1-2 páginas)
2. PRD_REFINED.md (requisitos detallados)
3. ROADMAP.md (fases MVP → Expansión → Inteligencia)
4. E2E_PRIORITY_FLOW.md (flujo principal con valor completo)
5. EPICS_AND_STORIES.md (10 historias Must-Have con Given/When/Then)

Base: PRD_BASE.md + decisiones de auditoría
```

**Resultado**:
- 5 documentos de producto generados (2,500+ líneas)
- 10 historias Must-Have con criterios de aceptación
- Flujo E2E prioritario definido
- Roadmap en 3 fases

**Archivos generados**: [`docs/product/`](docs/product/)

**Guía al asistente**:
- Proporcioné prompt estructurado de consolidación
- Especifiqué formato exacto de cada documento
- Pedí criterios Given/When/Then para historias

---

## 📋 Prompts de Producto

### Prompt 1: Definición de Épicas e Historias

**Contexto**: Extraer historias de usuario del PRD refinado

**Prompt**:
```
Rol activo: PM + Analyst

Extrae épicas e historias del PRD_REFINED.md:
- 10 historias Must-Have (flujo E2E prioritario)
- 5 historias Should-Have
- 5 historias Could-Have

Para cada historia:
1. ID: US-XX
2. Título claro
3. Descripción narrativa (Como... Quiero... Para...)
4. Criterios de aceptación (Given/When/Then)
5. Definition of Done
6. Prioridad y dependencias
7. Impacto en entidades/endpoints

Formato: Markdown con tablas y listas
```

**Resultado**:
- [`docs/product/EPICS_AND_STORIES.md`](docs/product/EPICS_AND_STORIES.md) (800+ líneas)
- 20 historias de usuario documentadas
- Criterios de aceptación en Gherkin
- Trazabilidad con tickets

**Guía al asistente**:
- Especifiqué formato exacto (ID, título, Given/When/Then)
- Pedí impacto técnico por historia
- Solicité priorización y dependencias

---

### Prompt 2: Flujo E2E Prioritario

**Contexto**: Definir el flujo principal que aporta valor completo

**Prompt**:
```
Define el flujo E2E prioritario con:
- Inicio claro (punto de entrada del usuario)
- Fin claro (valor entregado)
- 3-5 historias Must-Have que lo componen
- Diagrama de flujo (Mermaid)
- Estados UI por pantalla
- Validaciones y casos de error

Criterio: debe ser navegable end-to-end y demostrable
```

**Resultado**:
- [`docs/product/E2E_PRIORITY_FLOW.md`](docs/product/E2E_PRIORITY_FLOW.md)
- Flujo: Registro → Explorar → Publicar → Validar
- Diagrama Mermaid del journey
- 5 historias Must-Have identificadas

**Guía al asistente**:
- Enfaticé "valor completo" y "navegable"
- Pedí diagrama visual (Mermaid)
- Solicité casos de error por pantalla

---

### Prompt 3: Roadmap en Fases

**Contexto**: Planificar evolución del producto

**Prompt**:
```
Crea un roadmap en 3 fases:

FASE 1 - MVP (3 meses):
- Funcionalidades mínimas viables
- Flujo E2E completo
- Validación institucional básica

FASE 2 - Expansión (3 meses):
- Métricas comunitarias
- Búsqueda avanzada
- Integraciones (GitHub, Jupyter)

FASE 3 - Inteligencia (6 meses):
- Recomendaciones ML
- Análisis de calidad automático
- Federación con otros repos

Incluye: KPIs, riesgos y dependencias por fase
```

**Resultado**:
- [`docs/product/ROADMAP.md`](docs/product/ROADMAP.md)
- 3 fases con timelines
- KPIs medibles por fase
- Riesgos y mitigaciones

**Guía al asistente**:
- Estructuré las fases con objetivos claros
- Pedí KPIs específicos
- Solicité análisis de riesgos

---

## 🏗️ Prompts de Arquitectura

### Prompt 1: Diseño de Arquitectura Modular

**Contexto**: Definir arquitectura del sistema

**Prompt**:
```
Rol activo: Architect

Diseña arquitectura monolítica modular:
- Backend: Django modularizado por dominios (apps)
- Frontend: Next.js con App Router
- Base de datos: PostgreSQL
- Autenticación: JWT

Genera:
1. ARCHITECTURE.md con:
   - Diagrama de alto nivel (Mermaid)
   - Descripción de capas
   - Patrones utilizados
   - Decisiones de tecnología

2. ADRs para decisiones clave:
   - ADR-001: Autenticación JWT
   - ADR-002: Versionado de recursos
   - ADR-003: RBAC

Incluye: NFRs, logging, manejo de errores, seguridad
```

**Resultado**:
- [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) (600+ líneas)
- 3 ADRs documentados
- Diagrama de arquitectura en Mermaid
- Definición de módulos y responsabilidades

**Guía al asistente**:
- Especifiqué stack tecnológico exacto
- Pedí ADRs para decisiones importantes
- Solicité diagrama como código (Mermaid)

---

### Prompt 2: ADR de Versionado

**Contexto**: Decidir estrategia de versionado de recursos

**Prompt**:
```
Crea ADR-002 para versionado de recursos:

Contexto:
- Recursos pueden evolucionar (prompts, notebooks)
- Necesitamos trazabilidad y reproducibilidad
- Forks deben mantener relación con original

Opciones evaluadas:
A) Git-like (diffs y commits)
B) Snapshot completo por versión
C) Híbrido (snapshot + changelog)

Analiza pros/cons de cada opción y recomienda una.

Formato ADR estándar:
- Status, Context, Decision, Consequences
```

**Resultado**:
- [`docs/architecture/ADR-002-versioning.md`](docs/architecture/ADR-002-versioning.md)
- Decisión: Versionado híbrido
- Análisis de trade-offs
- Consecuencias técnicas documentadas

**Guía al asistente**:
- Proporcioné contexto del problema
- Listé opciones a evaluar
- Pedí formato ADR estándar

---

### Prompt 3: Diagrama de Arquitectura

**Contexto**: Visualizar la arquitectura del sistema

**Prompt**:
```
Crea diagrama de arquitectura en Mermaid:

Componentes:
- Cliente (Browser)
- Frontend (Next.js)
- Backend (Django + DRF)
- Base de datos (PostgreSQL)
- Servicios externos (Email, Storage)

Muestra:
- Flujo de autenticación (JWT)
- Flujo de publicación de recursos
- Flujo de validación
- Comunicación entre capas

Usa: graph TB (top-bottom) con subgraphs por capa
```

**Resultado**:
- Diagrama en [`docs/architecture/diagrams/architecture.mmd`](docs/architecture/diagrams/architecture.mmd)
- Visualización clara de capas
- Flujos principales marcados
- Subgraphs por responsabilidad

**Guía al asistente**:
- Especifiqué tipo de diagrama (graph TB)
- Listé componentes a incluir
- Pedí flujos específicos

---

## 💾 Prompts de Modelo de Datos

### Prompt 1: Diseño del Modelo Físico

**Contexto**: Definir schema de base de datos

**Prompt**:
```
Rol activo: Backend + Data

Diseña modelo de datos en PostgreSQL:

Entidades principales:
- User (autenticación, roles)
- Resource (wrapper de versiones)
- ResourceVersion (contenido versionado)
- Vote (votos de usuarios)
- Notification (notificaciones in-app)

Para cada entidad:
1. Atributos con tipos PostgreSQL
2. Constraints (PK, FK, UNIQUE, NOT NULL)
3. Índices para queries frecuentes
4. Relaciones (1:N, N:M)
5. Soft deletes donde aplique

Normalización: 3FN mínimo
Incluye: timestamps, auditoría, UUIDs
```

**Resultado**:
- [`docs/data/DATA_MODEL.md`](docs/data/DATA_MODEL.md) (900+ líneas)
- 8 entidades definidas
- Schema SQL completo
- Índices y constraints documentados

**Guía al asistente**:
- Listé entidades principales
- Especifiqué requisitos (3FN, UUIDs, soft deletes)
- Pedí índices para performance

---

### Prompt 2: ERD en Mermaid

**Contexto**: Visualizar relaciones entre entidades

**Prompt**:
```
Crea ERD (Entity Relationship Diagram) en Mermaid:

Formato: erDiagram

Entidades:
- User ||--o{ Resource : owns
- Resource ||--o{ ResourceVersion : has
- User ||--o{ Vote : gives
- Resource ||--o{ Vote : receives
- Resource }o--|| Resource : derives_from

Para cada relación:
- Cardinalidad correcta (1:1, 1:N, N:M)
- Atributos clave en cada entidad
- Nombres descriptivos

Incluye: tablas de join para N:M si aplica
```

**Resultado**:
- ERD en [`docs/data/diagrams/er.mmd`](docs/data/diagrams/er.mmd)
- Todas las relaciones visualizadas
- Cardinalidades correctas
- Fácil de entender

**Guía al asistente**:
- Especifiqué formato (erDiagram de Mermaid)
- Listé relaciones principales
- Pedí cardinalidades explícitas

---

### Prompt 3: Estrategia de Migraciones

**Contexto**: Planificar evolución del schema

**Prompt**:
```
Define estrategia de migraciones:

1. Herramienta: Django migrations
2. Convenciones:
   - Nombres descriptivos (add_user_reputation_field)
   - Migraciones atómicas (una cosa a la vez)
   - Reversibles (con operación down)
3. Proceso:
   - Desarrollo: makemigrations + migrate
   - Staging: revisión manual
   - Producción: backup + migrate con downtime mínimo
4. Versionado:
   - Migración = versión del schema
   - Changelog en cada migración

Documenta: comandos, checklist, rollback strategy
```

**Resultado**:
- Sección de migraciones en DATA_MODEL.md
- Comandos documentados
- Estrategia de rollback
- Checklist de producción

**Guía al asistente**:
- Especifiqué herramienta (Django migrations)
- Definí convenciones de nombres
- Pedí estrategia de rollback

---

## 🔌 Prompts de API

### Prompt 1: Diseño de Endpoints

**Contexto**: Definir API RESTful

**Prompt**:
```
Rol activo: Backend

Diseña API REST para el flujo E2E:

Recursos:
- /api/auth/* (login, register, refresh)
- /api/resources/* (CRUD, search, filter)
- /api/resources/:id/vote (votar)
- /api/resources/:id/fork (derivar)
- /api/resources/:id/validate (admin)
- /api/users/:id (perfil)
- /api/notifications/ (listar, marcar leídas)

Para cada endpoint:
1. Método HTTP
2. Path parameters
3. Query parameters
4. Request body (JSON schema)
5. Response (200, 201, 400, 401, 403, 404, 500)
6. Autenticación requerida (JWT)
7. Permisos (roles)

Formato: OpenAPI 3.0 (YAML)
```

**Resultado**:
- [`docs/api/openapi.yaml`](docs/api/openapi.yaml) (pendiente completar)
- 25+ endpoints documentados
- Schemas de request/response
- Códigos de error estándar

**Guía al asistente**:
- Especifiqué formato (OpenAPI 3.0)
- Listé recursos principales
- Pedí documentación completa por endpoint

---

### Prompt 2: Manejo de Errores

**Contexto**: Estandarizar respuestas de error

**Prompt**:
```
Define formato estándar de errores:

Estructura JSON:
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Resource with id X not found",
    "details": {...},
    "timestamp": "2026-02-16T10:30:00Z"
  }
}

Códigos de error:
- 400: VALIDATION_ERROR, INVALID_INPUT
- 401: UNAUTHORIZED, TOKEN_EXPIRED
- 403: FORBIDDEN, INSUFFICIENT_PERMISSIONS
- 404: RESOURCE_NOT_FOUND
- 409: CONFLICT, ALREADY_EXISTS
- 500: INTERNAL_ERROR

Incluye: i18n, logging, stack trace (solo dev)
```

**Resultado**:
- Sección de errores en ARCHITECTURE.md
- Formato JSON estándar
- Códigos de error documentados
- Estrategia de logging

**Guía al asistente**:
- Definí estructura JSON exacta
- Listé códigos de error comunes
- Pedí consideraciones de i18n y logging

---

## 🎨 Prompts de UX/UI

### Prompt 1: Análisis de Diseños Figma

**Contexto**: Extraer especificaciones de diseños visuales

**Prompt**:
```
Usa /orchestration/figma_prompt.md

Analiza diseños Figma en /docs/ux/figma/:
- home.png
- explore.png
- resource-detail.png
- publish.png
- profile.png

Para cada pantalla:
1. Componentes UI (header, sidebar, cards, forms)
2. Colores institucionales (paleta)
3. Tipografía (tamaños, pesos)
4. Espaciado (margins, paddings)
5. Estados (hover, active, disabled)
6. Responsive breakpoints

Genera: UI_STATES.md con todos los estados por pantalla
```

**Resultado**:
- [`docs/ux/UI_STATES.md`](docs/ux/UI_STATES.md) (1,200+ líneas)
- 50+ estados UI documentados
- Paleta de colores institucional
- Componentes reutilizables identificados

**Guía al asistente**:
- Proporcioné prompt especializado de Figma
- Pedí análisis exhaustivo por pantalla
- Solicité documentación de estados

---

### Prompt 2: Flujo de Navegación

**Contexto**: Definir navegación entre pantallas

**Prompt**:
```
Documenta flujo de navegación:

Por rol (Admin, User, Guest):
1. Pantallas accesibles
2. Transiciones entre pantallas
3. Acciones disponibles
4. Permisos requeridos

Formato:
- Diagrama de flujo (Mermaid)
- Tabla de permisos por pantalla
- Casos de redirección (auth, permisos)

Incluye: breadcrumbs, back buttons, deep linking
```

**Resultado**:
- [`docs/ux/NAVIGATION_FLOW.md`](docs/ux/NAVIGATION_FLOW.md)
- Diagramas por rol
- Tabla de permisos
- Estrategia de redirecciones

**Guía al asistente**:
- Especifiqué roles a considerar
- Pedí diagrama visual (Mermaid)
- Solicité casos de redirección

---

### Prompt 3: Diseño Institucional

**Contexto**: Implementar UI según diseño Figma

**Prompt**:
```
Implementa diseño institucional en frontend:

Colores (Tailwind config):
- Primary: #2e4b8e (azul institucional)
- Secondary: grises
- Validated: verde (#22c55e)
- Sandbox: gris (#94a3b8)
- Pending: ámbar (#f59e0b)

Componentes:
- Sidebar (navegación fija)
- Navbar (search, notificaciones, avatar)
- ResourceCard (grid de recursos)
- Badge (estados de recursos)

Usa: Tailwind CSS + componentes React reutilizables
```

**Resultado**:
- Diseño completo implementado
- Paleta de colores en `tailwind.config.js`
- Componentes reutilizables creados
- UI coherente con Figma

**Guía al asistente**:
- Especifiqué colores exactos (hex)
- Listé componentes a crear
- Definí tecnología (Tailwind + React)

---

## 🔧 Prompts de Implementación

### Prompt 1: Implementación de Historia US-01

**Contexto**: Implementar registro de usuarios

**Prompt**:
```
Implementa US-01: Registro de Usuario

Enfoque TDD:
1. Escribir tests primero (pytest):
   - test_user_registration_success
   - test_user_registration_duplicate_email
   - test_user_registration_invalid_email
   - test_user_registration_weak_password

2. Implementar backend:
   - Modelo User (Django)
   - Serializer UserRegistrationSerializer
   - View RegisterView (DRF)
   - Endpoint POST /api/auth/register

3. Implementar frontend:
   - Página /register
   - Formulario con validación
   - Manejo de errores
   - Redirección a login

4. E2E test (Playwright):
   - Flujo completo de registro

Criterios de aceptación (Given/When/Then) en US-01
```

**Resultado**:
- Tests escritos primero (TDD)
- Backend implementado y pasando tests
- Frontend navegable
- E2E test funcionando
- Documentación actualizada

**Guía al asistente**:
- Especifiqué enfoque TDD
- Listé tests específicos a escribir
- Definí orden: tests → backend → frontend → E2E
- Referencié criterios de aceptación

---

### Prompt 2: Debugging de Profile Page

**Contexto**: Corregir error "User not found"

**Prompt**:
```
Debug error en Profile Page:

Síntoma: "User not found" al acceder a /profile
Error: 500 en GET /api/users/:id/

Metodología:
1. Revisar logs del backend
2. Identificar línea exacta del error
3. Analizar traceback
4. Revisar modelo y queries
5. Identificar causa raíz
6. Implementar fix
7. Probar endpoint con curl
8. Verificar en frontend

Documentar: problema, causa, solución, lecciones
```

**Resultado**:
- 5 errores identificados y corregidos
- Causa raíz: uso de propiedades en queries Django
- Solución: usar modelos relacionados directamente
- Documentación completa en SESSION_11_PROFILE_DEBUG.md

**Guía al asistente**:
- Proporcioné metodología de debugging
- Pedí documentación del proceso
- Solicité lecciones aprendidas

---

### Prompt 3: Implementación de Sistema de Votos

**Contexto**: Permitir votar recursos

**Prompt**:
```
Implementa sistema de votos:

Backend:
1. Modelo Vote (user, resource, created_at)
2. Constraint UNIQUE (user, resource)
3. Endpoint POST /api/resources/:id/vote
4. Endpoint DELETE /api/resources/:id/vote (unvote)
5. Contador denormalizado en Resource (votes_count)
6. Signal para actualizar contador

Frontend:
1. Botón Vote en ResourceCard
2. Estado (voted/not voted)
3. Optimistic UI update
4. Manejo de errores

Tests:
- Unit: test_vote_resource, test_unvote_resource
- Integration: test_vote_endpoint
- E2E: test_vote_flow

Criterios: US-16
```

**Resultado**:
- Sistema de votos completo
- One-vote-per-user garantizado
- Optimistic UI implementado
- Tests pasando

**Guía al asistente**:
- Especifiqué arquitectura completa
- Definí constraint de unicidad
- Pedí optimistic UI
- Referencié historia de usuario

---

## 🐛 Prompts de Debugging

### Prompt 1: Error de Propiedades en Django ORM

**Contexto**: FieldError al filtrar por latest_version

**Prompt**:
```
Analiza este error:

django.core.exceptions.FieldError: 
Cannot resolve keyword 'latest_version' into field

Código problemático:
validated_resources = resources.filter(
    latest_version__status='Validated'
).count()

Contexto:
- latest_version es una @property en modelo Resource
- Devuelve ResourceVersion.objects.filter(is_latest=True).first()

Pregunta: ¿Por qué falla y cómo corregirlo?
```

**Respuesta del asistente**:
```
Causa: Las propiedades (@property) no son campos de BD. 
Django ORM solo puede filtrar por campos reales.

Solución:
validated_resources = ResourceVersion.objects.filter(
    resource__owner=user,
    resource__deleted_at__isnull=True,
    is_latest=True,
    status='Validated'
).count()

Lección: Usar modelos relacionados directamente en queries.
```

**Guía al asistente**:
- Proporcioné error exacto
- Mostré código problemático
- Di contexto del modelo
- Hice pregunta específica

---

### Prompt 2: Problema de Caché en Frontend

**Contexto**: UI sin estilos después de cambios en Tailwind

**Prompt**:
```
Problema: Frontend muestra HTML sin estilos

Contexto:
- Agregué tailwind.config.js con colores custom
- Reinicié docker-compose
- Navegador muestra HTML plano

Investigación realizada:
1. Revisé logs del frontend (sin errores)
2. Inspeccioné HTML generado (clases presentes)
3. Revisé Network tab (CSS cargando)
4. curl del CSS (contiene @tailwind sin procesar)

Diagnóstico: PostCSS no está procesando Tailwind

¿Qué archivo falta?
```

**Respuesta del asistente**:
```
Falta: postcss.config.js

Solución:
// frontend/postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

Luego: rebuild completo + clear browser cache
```

**Guía al asistente**:
- Describí síntoma claramente
- Mostré investigación realizada
- Proporcioné diagnóstico parcial
- Hice pregunta específica

---

### Prompt 3: Debugging Sistemático

**Contexto**: Metodología general de debugging

**Prompt**:
```
Cuando encuentres un error, sigue este proceso:

1. Identificar síntoma (qué ve el usuario)
2. Revisar logs (backend/frontend)
3. Analizar traceback completo
4. Revisar código relevante
5. Identificar causa raíz
6. Buscar solución (docs, similar issues)
7. Implementar fix
8. Probar fix (unit + integration + manual)
9. Verificar en frontend
10. Documentar (problema, causa, solución, lecciones)

Herramientas:
- docker-compose logs
- curl para endpoints
- Django shell para queries
- Browser DevTools

Siempre documentar en SESSION_XX_*.md
```

**Resultado**:
- Metodología aplicada consistentemente
- Todos los errores documentados
- Lecciones aprendidas capturadas
- 11 sesiones documentadas

**Guía al asistente**:
- Definí proceso paso a paso
- Listé herramientas disponibles
- Pedí documentación obligatoria

---

## 📚 Cómo Guiar al Asistente

### Principios Generales

1. **Proporciona Contexto**
   - Estado actual del proyecto
   - Documentos existentes
   - Decisiones previas

2. **Define Roles Explícitos**
   - "Rol activo: Architect"
   - "Rol activo: Backend Engineer"
   - Ayuda al asistente a adoptar la perspectiva correcta

3. **Establece Límites**
   - "Máximo 7 preguntas"
   - "No más de 3 prompts por sección"
   - Evita outputs infinitos

4. **Especifica Formato**
   - "Formato: Markdown con tablas"
   - "Diagrama: Mermaid graph TB"
   - "Schema: OpenAPI 3.0 YAML"

5. **Pide Documentación**
   - "Documenta decisiones en ADR"
   - "Actualiza AI_USAGE_LOG.md"
   - Mantiene trazabilidad

### Estructura de Prompt Efectivo

```markdown
[Contexto]
Breve descripción del problema/tarea

[Rol activo]
Rol que debe adoptar el asistente

[Objetivo]
Qué debe generar/resolver

[Requisitos]
Lista específica de requisitos

[Formato]
Formato exacto del output

[Restricciones]
Límites y condiciones

[Referencia]
Documentos/código relevante
```

### Ejemplo de Prompt Bien Estructurado

```markdown
Contexto: Necesitamos definir el modelo de datos para recursos versionados

Rol activo: Backend + Data Engineer

Objetivo: Diseñar schema PostgreSQL para Resource y ResourceVersion

Requisitos:
1. Resource es wrapper, ResourceVersion tiene contenido
2. Versionado híbrido (snapshot + changelog)
3. Soft deletes en Resource
4. UUIDs como PKs
5. Índices para queries frecuentes
6. 3FN mínimo

Formato: 
- Markdown con tablas SQL
- Diagrama ERD en Mermaid

Restricciones:
- Máximo 10 entidades
- Evitar over-engineering

Referencia:
- ADR-002-versioning.md
- EPICS_AND_STORIES.md (US-08)
```

### Anti-patrones a Evitar

❌ **Prompt vago**: "Haz el backend"
✅ **Prompt específico**: "Implementa endpoint POST /api/resources con validación de campos según US-08"

❌ **Sin contexto**: "Arregla el error"
✅ **Con contexto**: "Error 500 en /api/users/:id/ - traceback muestra FieldError en línea 33 de views_users.py"

❌ **Sin formato**: "Documenta la arquitectura"
✅ **Con formato**: "Crea ARCHITECTURE.md con diagrama Mermaid, descripción de capas y 3 ADRs"

❌ **Sin límites**: "Dame todas las historias de usuario"
✅ **Con límites**: "Extrae 10 historias Must-Have del PRD con criterios Given/When/Then"

### Iteración y Refinamiento

1. **Primera iteración**: Prompt general
2. **Revisión**: Evaluar output del asistente
3. **Refinamiento**: Prompt más específico con ajustes
4. **Validación**: Verificar que cumple requisitos
5. **Documentación**: Registrar prompt final en AI_USAGE_LOG

### Uso de Protocolos

Los prompts más efectivos fueron los que usaron **protocolos estructurados**:

- [`orchestration/ORCHESTRATOR_MASTER.md`](orchestration/ORCHESTRATOR_MASTER.md): Flujo de 8 fases
- [`orchestration/SPEC_CONSOLIDATION_PROMPT.md`](orchestration/SPEC_CONSOLIDATION_PROMPT.md): Generación de specs
- [`orchestration/UX_DESIGN_PROMPT.md`](orchestration/UX_DESIGN_PROMPT.md): Análisis de UX
- [`orchestration/figma_prompt.md`](orchestration/figma_prompt.md): Análisis de diseños

**Ventaja**: El asistente sigue una estructura consistente en todas las sesiones.

---

## 📊 Estadísticas de Uso de IA

### Artefactos Generados

- **Documentos**: 40+ archivos (12,000+ líneas)
- **Código**: Backend + Frontend (13,000+ líneas)
- **Tests**: Unit + Integration + E2E (1,500+ líneas)
- **Diagramas**: 10+ diagramas Mermaid

### Sesiones Documentadas

- **Total**: 11 sesiones
- **Prompts clave**: 50+ prompts estructurados
- **Ajustes humanos**: ~15% del código generado
- **Debugging sessions**: 3 sesiones completas

### Efectividad

- **Primera iteración correcta**: ~70%
- **Requirió ajustes menores**: ~25%
- **Requirió reescritura**: ~5%

### Tiempo Ahorrado (Estimado)

- **Documentación**: ~80 horas → 20 horas (75% ahorro)
- **Código boilerplate**: ~40 horas → 10 horas (75% ahorro)
- **Debugging**: ~20 horas → 8 horas (60% ahorro)
- **Total**: ~140 horas → ~38 horas (73% ahorro)

---

## 🔗 Referencias

### Documentación Completa

- **AI Usage Log**: [`docs/ai/AI_USAGE_LOG.md`](docs/ai/AI_USAGE_LOG.md) (4,200+ líneas)
- **Session Summaries**: [`docs/delivery/`](docs/delivery/) (11 sesiones)
- **Protocolos**: [`orchestration/`](orchestration/)

### Documentación Técnica

- **Producto**: [`docs/product/`](docs/product/)
- **Arquitectura**: [`docs/architecture/`](docs/architecture/)
- **Datos**: [`docs/data/`](docs/data/)
- **API**: [`docs/api/`](docs/api/)
- **Calidad**: [`docs/quality/`](docs/quality/)
- **UX**: [`docs/ux/`](docs/ux/)

### Convenciones

- **AGENTS.md**: [`AGENTS.md`](AGENTS.md) - Flujo de trabajo y reglas
- **README.md**: [`README.md`](README.md) - Setup y comandos

---

**Última actualización**: 2026-02-17  
**Versión**: 1.0  
**Mantenedor**: Heladia Salgado  
**Herramienta**: Claude Sonnet 4.5 en Cursor IDE
