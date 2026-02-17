# PRODUCT BRIEF — BioAI Hub

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Dominio:** bioai.ccg.unam.mx  
**Versión:** 1.0  
**Fecha:** 2026-02-16  
**Owner:** Centro de Ciencias Genómicas (CCG) — UNAM

---

## 1. RESUMEN EJECUTIVO

**BioAI Hub** es una plataforma digital institucional que profesionaliza la publicación, versionado, evaluación y reutilización de recursos de Inteligencia Artificial aplicados a bioinformática y genética.

El sistema habilita un modelo de gobernanza automatizada basado en evidencia (votos, usos, validación comunitaria) y genera reputación académica cuantificable para investigadores y estudiantes.

---

## 2. PROBLEMA

La comunidad científica del CCG enfrenta:

- **Dispersión:** Recursos de IA (prompts, workflows, notebooks) dispersos en repositorios personales, chats y correos
- **Informalidad:** Sin estándares de calidad, versionado ni trazabilidad institucional
- **Invisibilidad:** Trabajo no reconocido profesionalmente; sin métricas de impacto
- **Dependencia:** Confianza exclusiva en GitHub sin respaldo institucional
- **Duplicación:** Re-invención constante de soluciones similares por falta de catálogo centralizado

**Consecuencia:** Pérdida de eficiencia, conocimiento no reutilizable, impacto no medible.

---

## 3. SOLUCIÓN

**BioAI Hub** es una plataforma web colaborativa que:

1. **Centraliza** recursos de IA en un catálogo institucional navegable
2. **Versioniza** recursos con identificadores persistentes tipo DOI ligero (`ccg-ai:R-000123@v1.0.0`)
3. **Evalúa** calidad mediante modelo Sandbox → Validated (automático o humano)
4. **Reconoce** contribuciones con métricas de reputación pública
5. **Facilita** reutilización (fork) y trazabilidad de derivaciones
6. **Integra** GitHub opcionalmente sin reemplazarlo

---

## 4. VALOR PROPUESTO

### Para Investigadores:
- ✅ Publicación profesional de recursos con citación institucional
- ✅ Reputación cuantificable (votos, usos, validaciones)
- ✅ Visibilidad dentro de la comunidad CCG
- ✅ Reutilización rápida de recursos validados

### Para la Institución (CCG):
- ✅ Catálogo centralizado de conocimiento en IA aplicada
- ✅ Trazabilidad académica y auditoría
- ✅ Posicionamiento como referente en IA científica
- ✅ Base para futuras publicaciones académicas sobre recursos

### Para Estudiantes:
- ✅ Acceso a recursos validados por expertos
- ✅ Aprendizaje de mejores prácticas
- ✅ Oportunidad de contribuir y generar portafolio profesional

---

## 5. STAKEHOLDERS

| Stakeholder | Rol | Interés |
|---|---|---|
| **Investigadores CCG** | Autores, revisores, usuarios | Publicar y reutilizar recursos |
| **Unidad de Bioinformática** | Generadores iniciales de contenido | Aportar recursos de calidad |
| **Unidad TI** | Soporte técnico | Infraestructura y mantenimiento |
| **Dirección CCG** | Sponsor institucional | Evaluación estratégica |
| **Estudiantes** | Usuarios secundarios | Aprender y contribuir |
| **Comunidad científica externa** | Usuarios futuros (post-MVP) | Acceso público en fase 2 |

---

## 6. ALCANCE MVP

### In Scope:
- ✅ Registro abierto (cualquier email con verificación)
- ✅ Roles: Admin y User
- ✅ Catálogo público de recursos (Explore)
- ✅ Publicación de recursos (formulario)
- ✅ Versionado híbrido (interno o GitHub-linked)
- ✅ Identificador persistente tipo DOI ligero
- ✅ Modelo Sandbox / Validated (automático + manual)
- ✅ Sistema de votos (1 por usuario por recurso)
- ✅ Reutilización (fork) con trazabilidad
- ✅ Métricas básicas (votos, usos, validaciones)
- ✅ Perfil público con reputación
- ✅ Notificaciones in-app

### Out of Scope (MVP):
- ❌ DOI real registrado (solo formato tipo DOI)
- ❌ Ejecución de notebooks en plataforma
- ❌ API pública externa
- ❌ Recomendador inteligente
- ❌ Mirror automático a GitHub
- ❌ Microservicios
- ❌ Notificaciones por email
- ❌ Búsqueda semántica
- ❌ Comparación de versiones (diff)

---

## 7. DIFERENCIADORES

| Feature | GitHub | BioAI Hub |
|---|---|---|
| **Versionado** | Git nativo | Híbrido (interno + GitHub-linked) |
| **Validación** | Stars/issues | Sandbox → Validated automático |
| **Citación** | URL volátil | PID tipo DOI (`ccg-ai:R-...@v1.0`) |
| **Reputación** | Stars globales | Métricas institucionales trazables |
| **Gobernanza** | Descentralizada | Modelo institucional académico |
| **Audiencia** | Universal | Especializada (bio + IA) |

**BioAI Hub no reemplaza GitHub:** lo complementa con gobernanza institucional y citación formal.

---

## 8. MODELO DE VERSIONADO HÍBRIDO

### Tipo 1: Internal (versionado nativo)
- Contenido almacenado directamente en plataforma
- PID único: `ccg-ai:R-000123@v1.0.0`
- Inmutabilidad por versión
- Hash SHA-256 de contenido
- Changelog obligatorio

### Tipo 2: GitHub-Linked
- Recurso vive en GitHub, plataforma enlaza
- Campos: `repo_url`, `tag`, `commit_sha`, `license`
- Para recursos Validated se recomienda tag/commit fijo
- Sincronización manual (no automática en MVP)

---

## 9. MODELO SANDBOX / VALIDATED

### Estados:
- **Sandbox:** Recurso recién publicado o en desarrollo
- **Validated:** Recurso promovido por criterios automáticos o revisión manual

### Promoción Automática (criterios):
- ≥ 10 votos
- ≥ 50 usos
- ≥ 2 semanas desde publicación
- 0 reportes críticos

### Revisión Manual:
- Admin puede validar manualmente en cualquier momento
- Admin puede revocar validación si aplica

**Implicación:** Validated es señal de calidad comunitaria, no solo decisión individual.

---

## 10. MÉTRICAS DE ÉXITO (KPIs — Año 1)

| Indicador | Meta |
|---|---|
| **Recursos publicados** | ≥ 50 |
| **Usuarios activos** | ≥ 20 |
| **% Recursos Validated** | ≥ 20% |
| **Participación (votos)** | ≥ 30% de usuarios |
| **Reuses (forks)** | ≥ 10 |
| **Integración en cursos** | ≥ 1 curso |

---

## 11. ROADMAP SIMPLIFICADO

### Fase 1: MVP (Core Platform)
- Infraestructura base + flujo E2E funcional
- Publicación, versionado, validación, reutilización
- Métricas básicas

### Fase 2: Expansión
- Notificaciones email
- Historial de versiones mejorado
- Comparación de versiones (diff)
- Sistema de reportes avanzado

### Fase 3: Inteligencia
- Recomendador basado en uso
- Búsqueda semántica
- API pública
- Apertura a comunidad externa

---

## 12. RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Baja adopción inicial | Media | Alto | Incentivos internos, presentaciones en seminarios |
| Recursos de baja calidad | Media | Medio | Modelo Sandbox/Validated + reportes |
| Dependencia de GitHub | Baja | Medio | Versionado interno robusto como alternativa |
| Sobreingeniería técnica | Media | Alto | Enfoque modular, MVP estricto, evitar microservicios |

---

## 13. CRITERIOS GLOBALES DE ACEPTACIÓN (MVP)

El MVP se considera exitoso cuando:

- ✅ Plataforma estable en producción (bioai.ccg.unam.mx)
- ✅ Al menos 10 usuarios registrados reales
- ✅ Al menos 15 recursos publicados
- ✅ Al menos 3 recursos reutilizados (fork)
- ✅ Al menos 2 recursos promovidos a Validated
- ✅ Integración anunciada en al menos 1 curso o seminario CCG

---

## 14. STACK TECNOLÓGICO

| Capa | Tecnología | Justificación |
|---|---|---|
| **Frontend** | Next.js 14+ | SEO, React maduro, SSR |
| **Backend** | Django 5+ + DRF | Ecosistema Python científico |
| **Base de Datos** | PostgreSQL 15+ | Estabilidad, versionado relacional |
| **Infraestructura** | Docker + VPS | Bajo costo, control institucional |
| **Autenticación** | Django Auth + JWT | Simple, extensible a SSO futuro |
| **Hosting** | Subdominio CCG | bioai.ccg.unam.mx |

---

## 15. SUPUESTOS CRÍTICOS

1. **Adopción:** Investigadores y estudiantes están dispuestos a publicar recursos si hay valor claro
2. **Calidad:** Modelo Sandbox/Validated genera incentivo suficiente para calidad
3. **Infraestructura:** CCG puede hospedar VPS con tráfico inicial bajo (~20 usuarios)
4. **Mantenimiento:** Existe capacidad técnica interna (o externa) para soporte continuo
5. **Evolución:** Plataforma puede escalar modularmente sin reescritura completa

---

## 16. PRÓXIMOS PASOS

1. ✅ Completar auditoría técnica (TECH_AUDIT.md)
2. ⏭️ Refinar PRD con decisiones técnicas (PRD_REFINED.md)
3. ⏭️ Definir roadmap detallado (ROADMAP.md)
4. ⏭️ Formalizar flujo E2E prioritario (E2E_PRIORITY_FLOW.md)
5. ⏭️ Extraer épicas e historias Must-Have (EPICS_AND_STORIES.md)
6. 🔴 Formalizar estados UI (UI_STATES.md) — BLOQUEADOR CRÍTICO
7. Diseñar arquitectura, modelo de datos, API, tests
8. Implementar MVP iterativamente (TDD)
9. Desplegar en bioai.ccg.unam.mx
10. Lanzamiento interno CCG

---

**Documento aprobado para desarrollo:** 2026-02-16  
**Siguiente artefacto:** PRD_REFINED.md  
**Rol siguiente:** PM + Tech Lead
