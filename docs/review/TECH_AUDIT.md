# TECH AUDIT — BioAI Hub (Auditoría Técnica Retroactiva)

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Dominio:** bioai.ccg.unam.mx  
**Fecha auditoría:** 2026-02-16  
**Rol activo:** Tech Lead / Architect  
**Fase:** FASE 1 (Auditoría Técnica)

---

## 1. RESUMEN EJECUTIVO

Esta auditoría evalúa la documentación y artefactos existentes del proyecto BioAI Hub para identificar fortalezas, huecos y riesgos técnicos antes de continuar con el diseño de arquitectura.

**Estado general:** El proyecto cuenta con una base sólida (PRD técnico, flujo de navegación detallado, diseños Figma profesionales), pero requiere consolidación de documentación de producto y formalización crítica de estados UI antes de avanzar a arquitectura.

---

## 2. DOCUMENTOS AUDITADOS

### Fuentes revisadas:
- [`/docs/product/PRD_BASE.md`](../product/PRD_BASE.md)
- [`/docs/ux/NAVIGATION_FLOW.md`](../ux/NAVIGATION_FLOW.md)
- [`/AGENTS.md`](../../AGENTS.md)
- [`/orchestration/ORCHESTRATOR_MASTER.md`](../../orchestration/ORCHESTRATOR_MASTER.md)
- Diseños Figma: `/docs/ux/figma/` (5 pantallas: home, explore, publish, resource-detail, profile)

---

## 3. FORTALEZAS IDENTIFICADAS

### 3.1 PRD Técnico Sólido
✅ **PRD_BASE.md** presenta:
- Problema y oportunidad claramente definidos
- Stakeholders identificados
- Alcance MVP vs Out of Scope bien delimitado
- Stack tecnológico justificado (Next.js + Django + PostgreSQL)
- Modelo conceptual de versionado híbrido (interno vs GitHub-linked)
- Identificador persistente tipo DOI ligero (`ccg-ai:R-000123@v1.2.0`)
- Modelo Sandbox/Validated con criterios de promoción automática
- Roadmap evolutivo en 3 fases
- KPIs cuantificables

### 3.2 Flujo de Navegación Detallado
✅ **NAVIGATION_FLOW.md** presenta:
- 13 secciones de flujo documentadas
- Routing público vs autenticado claramente separado
- Variaciones de comportamiento por rol (Anonymous, User, Owner, Admin)
- Flujos especiales: Reuse (fork), Edit con versionado, Validación, Notificaciones
- Mapeo con pantallas Figma
- Trazabilidad de acciones por estado de usuario

### 3.3 Diseños Visuales Profesionales
✅ **Figma assets** (5 pantallas):
- Home (landing institucional)
- Explore (búsqueda y filtrado)
- Publish (wizard de publicación)
- Resource Detail (vista completa con métricas)
- Profile (reputación y contribuciones)

### 3.4 Gobernanza Técnica Clara
✅ **AGENTS.md** define:
- Roles de agentes (PM, UX, Tech Lead, Backend, Frontend, QA, DevOps)
- Flujo obligatorio: Auditoría → Refinamiento → Diseño → Tests → Implementación
- Definition of Done (DoD)
- Convenciones de código
- Testing mínimos (unit/integration/BDD/E2E)
- Diagramas como código (DaC)
- Trazabilidad total (EPIC/US/T/ADR/ENT/API/UT/IT/BDD/E2E)

---

## 4. HUECOS IDENTIFICADOS

### 4.1 Documentación de Producto (FASE 2)
❌ **Faltantes críticos:**
- `PRODUCT_BRIEF.md` (resumen ejecutivo de 1-2 páginas)
- `PRD_REFINED.md` (expansión del PRD_BASE con decisiones técnicas tomadas)
- `ROADMAP.md` (fases con hitos y criterios de éxito)
- `E2E_PRIORITY_FLOW.md` (flujo E2E prioritario con valor completo) - archivo existe pero está vacío
- `EPICS_AND_STORIES.md` (épicas e historias Must-Have/Should-Have con Given/When/Then)
- `TICKETS.md` o sistema de tickets en GitHub Issues

**Impacto:** Sin épicas e historias formalizadas, no se puede iniciar implementación (política de AGENTS.md línea 171-174).

### 4.2 Formalización de Estados UI (FASE 2.5) ⚠️ BLOQUEADOR CRÍTICO
❌ **UI_STATES.md NO EXISTE**

Según ORCHESTRATOR_MASTER.md (línea 106-107):
> "No avanzar a FASE 3 (Arquitectura) hasta que todos los estados estén formalizados y su impacto técnico identificado."

**Estados UI no formalizados:**
- Loading (carga inicial, acciones async)
- Empty (sin datos, primera vez)
- Validation Error (formularios, inputs)
- Backend Error (500, timeouts, red)
- Success (confirmaciones, toasts)
- Permisos insuficientes (401, 403)

**Impacto:**
1. Los estados UI impactan el **modelo de datos** (campos de estado: `resource.status`, `resource_version.validation_status`, `user.is_active`)
2. Los estados UI impactan los **endpoints** (códigos HTTP, manejo de errores, validaciones)
3. Los estados UI impactan las **historias** (criterios Given/When/Then deben contemplar estados)
4. Los estados UI impactan el **RBAC** (reglas de autorización por estado)

### 4.3 Arquitectura y Decisiones Técnicas (FASE 3)
❌ **ARCHITECTURE.md existe pero está vacío**
❌ **No hay ADRs (Architecture Decision Records)**
❌ **No hay diagramas DaC** (`/docs/architecture/diagrams/`)

Decisiones técnicas pendientes:
- Patrón de arquitectura detallado (capas, módulos, dominios)
- Service layer vs views en Django
- State management en Next.js (Context, Zustand, Redux?)
- Estrategia de caché
- Manejo de sesiones y tokens
- Estrategia de RBAC (middleware, decorators, policies)
- Logging y auditoría
- Manejo global de errores

### 4.4 Modelo de Datos (FASE 4)
❌ **DATA_MODEL.md existe pero está vacío**
❌ **No hay ERD (Entity-Relationship Diagram)**

PRD_BASE menciona entidades conceptuales, pero falta:
- Modelo físico detallado (atributos, tipos, constraints)
- Relaciones con cardinalidad
- Índices y performance
- Estrategia de migraciones
- Normalización (3FN)
- Versionado interno de recursos (schema de ResourceVersion)

### 4.5 API (FASE 5)
❌ **openapi.yaml existe en `/docs/api/` pero no revisado**
❌ **Duplicado en `/docs/quality/openapi.yaml`** (posible error)

Pendiente validar:
- Endpoints completos para flujo E2E
- Schemas de request/response
- Códigos de error
- Autenticación/Autorización
- Paginación y filtros
- Versionado de API

### 4.6 Calidad (FASE 6)
❌ **TEST_STRATEGY.md no existe**
❌ **BDD_FEATURES.feature no existe**
❌ **E2E_PLAN.md no existe**

Sin estrategia de testing formal, no se puede garantizar calidad del MVP.

### 4.7 Infraestructura y Entrega (FASE 8)
❌ **INFRASTRUCTURE.md no existe**
❌ **CI_CD.md no existe**
❌ **RELEASE_PLAN.md no existe**
❌ **No hay Dockerfile, docker-compose.yml, Makefile**

### 4.8 Registro de Uso de IA
❌ **AI_USAGE_LOG.md existe pero está vacío**

Violación de AGENTS.md (línea 100-105): obligatorio mantener log de uso de IA.

---

## 5. RIESGOS TÉCNICOS IDENTIFICADOS

### 5.1 Riesgos de Arquitectura (ALTO)
🔴 **Riesgo:** Sin arquitectura formalizada, riesgo de implementación inconsistente y acoplamiento no deseado.

**Mitigación:**
- Completar FASE 3 antes de implementación
- Definir ADRs para decisiones críticas (auth, state management, RBAC)
- Generar diagrama de arquitectura DaC (Mermaid)

### 5.2 Riesgos de Modelo de Datos (ALTO)
🔴 **Riesgo:** Versionado híbrido (interno + GitHub-linked) puede generar complejidad en modelo de datos si no se diseña correctamente.

**Mitigación:**
- Definir schema de ResourceVersion con campos obligatorios/opcionales según `source_type`
- Validar integridad referencial entre Resource ↔ ResourceVersion
- Diseñar estrategia de migraciones evolutivas

### 5.3 Riesgos de UX/UI (MEDIO)
🟡 **Riesgo:** Diseños Figma pueden no contemplar todos los estados edge case (errores, loading, empty, permisos).

**Mitigación:**
- Completar FASE 2.5 (UI_STATES.md) auditando Figma exhaustivamente
- Validar con stakeholders estados de error y feedback visual
- Definir componentes de loading/error/empty reutilizables

### 5.4 Riesgos de Autenticación (MEDIO)
🟡 **Riesgo:** Decisión de "cualquier email" (no solo institucional) abre pregunta de verificación de email y spam.

**Decisión pendiente:**
- ¿Se requiere verificación de email?
- ¿Hay rate limiting en registro?
- ¿Moderación de recursos en primera versión?

### 5.5 Riesgos de RBAC Simple (BAJO-MEDIO)
🟡 **Riesgo:** Modelo Admin/User puede ser demasiado simple para algunos flujos (ej: validación de recursos).

**Observación:** PRD_BASE menciona "revisión humana opcional" para promoción Sandbox → Validated. Con solo 2 roles:
- ¿Solo Admin puede validar?
- ¿Se contempla rol "Reviewer" futuro?

**Mitigación:** Diseñar RBAC extensible (tabla de permisos granulares) aunque MVP use solo 2 roles.

### 5.6 Riesgos de Versionado (MEDIO)
🟡 **Riesgo:** Flujo de edición con versionado automático puede confundir usuarios.

**Observación:** Según NAVIGATION_FLOW.md:
- Si última versión NO validada → actualización crea draft
- Si última versión SÍ validada → crea nueva versión (vNext)

**Pregunta abierta:**
- ¿Usuario puede tener múltiples drafts?
- ¿Cómo se visualiza historial de versiones?
- ¿Se puede "revertir" a versión anterior?

### 5.7 Riesgos de Performance (BAJO)
🟢 **Riesgo:** MVP con PostgreSQL + monolito debe soportar ~20 usuarios activos inicialmente (KPI).

**Mitigación:** Diseñar con índices básicos, sin optimizaciones prematuras. Monitorear en producción.

### 5.8 Riesgos de Dependencias Externas (BAJO)
🟢 **Riesgo:** GitHub-linked resources dependen de disponibilidad de GitHub.

**Observación:** PRD_BASE recomienda tag/commit fijo para Validated. Suficiente para MVP.

---

## 6. AMBIGÜEDADES Y PREGUNTAS CRÍTICAS

### Pregunta 1: Verificación de Email
**Contexto:** Autenticación con "cualquier email" (no solo institucional).

**Pregunta:**
- ¿Se requiere verificación de email (link de confirmación)?
- ¿O registro es instantáneo?

**Impacto:**
- Modelo de datos: campo `user.email_verified_at`
- Endpoints: `/auth/verify-email/:token`
- Estados UI: pantalla "Verifica tu email"

**Recomendación:** Verificación obligatoria para evitar spam y asegurar contacto real.

---

### Pregunta 2: Moderación de Recursos
**Contexto:** PRD_BASE menciona "0 reportes críticos" como criterio de promoción automática.

**Pregunta:**
- ¿Existe sistema de reportes en MVP?
- ¿Quién puede reportar? (todos los usuarios autenticados?)
- ¿Qué acciones puede tomar Admin sobre recurso reportado?

**Impacto:**
- Entidad: `Report` (no mencionada en flujo actual)
- Endpoints: `POST /resources/:id/report`
- Historia Must-Have adicional

**Recomendación:** Incluir sistema básico de reportes en MVP para habilitar promoción automática.

---

### Pregunta 3: Historial de Versiones
**Contexto:** ResourceVersion permite versionado, pero UX no está clara.

**Pregunta:**
- ¿Cómo visualiza usuario el historial de versiones?
- ¿Puede comparar versiones (diff)?
- ¿Puede revertir a versión anterior?
- ¿Puede tener múltiples drafts simultáneos?

**Impacto:**
- Pantalla adicional: `/resources/:id/versions`
- Endpoint: `GET /resources/:id/versions`
- Lógica de negocio: reglas de draft vs published

**Recomendación:** Definir UX mínima: lista de versiones con links directos. Comparación y revert para post-MVP.

---

### Pregunta 4: Notificaciones
**Contexto:** NAVIGATION_FLOW.md menciona `/notifications` con tipos MVP.

**Pregunta:**
- ¿Notificaciones in-app solamente o también email?
- ¿Frecuencia de email (instantáneo, daily digest)?
- ¿Usuario puede configurar preferencias de notificación?

**Impacto:**
- Entidad: `Notification`, `NotificationPreference`
- Infraestructura: servicio de email (SMTP)
- Estados UI: configuración en profile

**Recomendación:** Notificaciones in-app para MVP. Email para post-MVP.

---

### Pregunta 5: Métricas de "Uso"
**Contexto:** PRD_BASE menciona "≥ 50 usos" como criterio de promoción.

**Pregunta:**
- ¿Qué cuenta como "uso"? (view, download, reuse/fork, upvote?)
- ¿Se trackean visualizaciones anónimas?
- ¿Hay analytics dashboard para owners?

**Impacto:**
- Entidad: `ResourceMetric` o `ResourceView`
- Endpoint: tracking de eventos
- Privacy: GDPR/consentimiento si trackea IPs

**Recomendación:** "Uso" = combinación de views + reuses + upvotes. Tracking simple sin identificación personal para MVP.

---

## 7. ANÁLISIS DE COHERENCIA

### 7.1 PRD ↔ NAVIGATION_FLOW
✅ **Coherente:** Flujos de navegación mapean bien con requisitos funcionales del PRD.

⚠️ **Gap menor:** PRD menciona "Wizard 5 pasos" para publicación, pero diseño Figma de `publish.png` muestra formulario más simple. Validar con UX.

### 7.2 NAVIGATION_FLOW ↔ Figma
✅ **Coherente:** Las 5 pantallas Figma cubren rutas principales del NAVIGATION_FLOW.

⚠️ **Gaps:**
- No hay pantalla de `/notifications` (mencionada en NAVIGATION_FLOW)
- No hay pantalla de `/resources/:id/versions` (historial de versiones)
- No hay pantalla de login/registro (asumido externo o modal)

**Recomendación:** Definir si estas pantallas son Must-Have para MVP o post-MVP.

### 7.3 Stack Tecnológico vs Requisitos
✅ **Adecuado:**
- Next.js (SEO, React, SSR) → ✅ para plataforma pública
- Django + DRF → ✅ para ecosistema Python científico
- PostgreSQL → ✅ para modelo relacional con versionado

⚠️ **Consideración:** Versionado de recursos puede generar tablas grandes. Diseñar con índices apropiados.

---

## 8. DECISIONES TÉCNICAS TOMADAS (POST-AUDITORÍA)

Basado en respuestas del stakeholder:

1. **Nombre del proyecto:** `bioai-hub`
2. **Branding:** BioAI Hub — Institutional AI Repository
3. **Dominio:** `bioai.ccg.unam.mx`
4. **Autenticación:** Cualquier email (no solo institucional)
5. **Roles:** Simple (Admin y User)
6. **DaC:** Mermaid para diagramas simples, PlantUML para complejos

---

## 9. RECOMENDACIONES ESTRATÉGICAS

### Recomendación 1: Completar FASE 2.5 antes de Arquitectura
🔴 **CRÍTICO:** No avanzar a FASE 3 sin formalizar UI_STATES.md.

**Justificación:** Estados UI impactan modelo de datos, endpoints y RBAC. Diseñar arquitectura sin esto genera retrabajo.

### Recomendación 2: Priorizar Épicas Must-Have
🟡 Definir 3-5 historias Must-Have que cubran flujo E2E completo:
- Registro e inicio de sesión
- Explorar recursos (público)
- Publicar recurso (autenticado)
- Validar recurso (admin)
- Reutilizar recurso (fork)

### Recomendación 3: Diseño de RBAC Extensible
🟡 Aunque MVP usa solo Admin/User, diseñar sistema de permisos granulares para facilitar expansión futura (Reviewer, Moderator).

### Recomendación 4: Versionado Inmutable
🟡 Asegurar inmutabilidad de versiones validadas (critical para citación académica). Validar en modelo de datos con constraints.

### Recomendación 5: Estrategia de Tests desde Inicio
🟡 Definir TEST_STRATEGY antes de implementación. TDD para lógica crítica (versionado, promoción automática).

---

## 10. PRÓXIMOS PASOS

### Inmediatos (Bloqueadores):
1. ✅ **TECH_AUDIT.md** (este documento)
2. ⏭️ **PRODUCT_BRIEF.md** (resumen ejecutivo)
3. ⏭️ **PRD_REFINED.md** (PRD + decisiones técnicas)
4. ⏭️ **ROADMAP.md** (fases con hitos)
5. ⏭️ **E2E_PRIORITY_FLOW.md** (flujo prioritario)
6. ⏭️ **EPICS_AND_STORIES.md** (historias Must-Have/Should-Have)
7. 🔴 **UI_STATES.md** (BLOQUEADOR CRÍTICO para FASE 3)

### Post-Bloqueadores:
8. **ARCHITECTURE.md + ADRs** (FASE 3)
9. **DATA_MODEL.md + ERD** (FASE 4)
10. **openapi.yaml validación** (FASE 5)
11. **TEST_STRATEGY.md, BDD_FEATURES, E2E_PLAN** (FASE 6)

---

## 11. CHECKLIST DE COMPLETITUD DE AUDITORÍA

- [x] PRD_BASE.md revisado
- [x] NAVIGATION_FLOW.md revisado
- [x] AGENTS.md revisado
- [x] Diseños Figma (5 pantallas) referenciados
- [x] Fortalezas identificadas
- [x] Huecos documentados
- [x] Riesgos técnicos evaluados
- [x] Preguntas críticas formuladas (5)
- [x] Coherencia entre documentos analizada
- [x] Recomendaciones estratégicas propuestas
- [x] Próximos pasos definidos

---

## 12. CONCLUSIÓN

El proyecto **BioAI Hub** cuenta con una base sólida y profesional. El PRD es técnicamente robusto, los diseños Figma son de calidad institucional, y la gobernanza (AGENTS.md) está bien definida.

**Bloqueador principal:** Falta formalización de estados UI (FASE 2.5), sin la cual no se puede diseñar arquitectura ni modelo de datos de forma correcta.

**Recomendación:** Completar secuencialmente FASE 2 (documentos de producto) y FASE 2.5 (UI_STATES.md) antes de avanzar a FASE 3.

**Viabilidad técnica:** ALTA. Stack adecuado, alcance MVP bien delimitado, riesgos identificados y mitigables.

---

**Auditoría completada:** 2026-02-16  
**Siguiente fase:** FASE 2 - Refinamiento de Producto  
**Rol siguiente:** PM + Analyst
