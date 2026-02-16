# PRD Documento Técnico Completo

## Plataforma Colaborativa de Recursos y Asistentes de IA

### Centro de Ciencias Genómicas -- UNAM



------------------------------------------------------------------------

# 1. Resumen Ejecutivo

Desarrollar una infraestructura digital institucional que permita
publicar, versionar, evaluar y legitimar recursos de Inteligencia
Artificial aplicados a bioinformática y genética, bajo un modelo de
gobernanza automatizada y reputación basada en evidencia.

El sistema inicia como plataforma interna (CCG) y evoluciona hacia
apertura pública.

------------------------------------------------------------------------

# 2. Problema y Oportunidad

## Problema

-   Recursos IA dispersos e informales.
-   Falta de versionado institucional.
-   Ausencia de trazabilidad académica.
-   Dependencia exclusiva de GitHub.
-   Sin reconocimiento profesional cuantificable.

## Oportunidad

Crear infraestructura científica digital especializada que
profesionalice prompts y workflows, permita citación formal futura y
posicione al CCG como referente en IA aplicada.

------------------------------------------------------------------------

# 3. Stakeholders

  Stakeholder                   Rol
  ----------------------------- --------------------------------
  Investigadores CCG            Publican y reutilizan recursos
  Unidad de Bioinformática      Genera recursos iniciales
  Unidad TI                     Soporte técnico
  Dirección CCG                 Evaluación estratégica
  Estudiantes                   Usuarios secundarios
  Comunidad científica futura   Expansión pública

------------------------------------------------------------------------

# 4. Alcance

## In Scope -- MVP 

-   Biblioteca central.
-   Modelo Sandbox / Validated.
-   Versionado híbrido.
-   PID tipo DOI ligero.
-   Votos simples.
-   Métricas básicas.
-   Perfil público.
-   Registro institucional obligatorio.
-   GitHub link opcional.

## Out of Scope -- MVP

-   DOI real.
-   Ejecución de notebooks.
-   API pública.
-   Recomendador inteligente.
-   Mirror automático a GitHub.
-   Microservicios.

------------------------------------------------------------------------

# 5. Arquitectura del Sistema

## Principio

Arquitectura monolítica modular evolutiva.

## Stack Tecnológico

  Capa              Tecnología             Justificación
  ----------------- ---------------------- ------------------------------
  Frontend          Next.js                SEO + React maduro
  Backend           Django + DRF           Ecosistema Python científico
  Base de Datos     PostgreSQL             Estabilidad
  Infraestructura   Docker + VPS pública   Bajo costo
  Autenticación     Email institucional    Confianza académica

------------------------------------------------------------------------

# 6. Modelo de Versionado Híbrido

## source_type

-   internal
-   github_linked

## Versionado Interno

-   PID: ccg-ai:R-000123@v1.0.0
-   Inmutabilidad por versión
-   content_hash SHA-256
-   changelog obligatorio
-   citación automática

## GitHub Linked

Campos: - repo_url - tag (recomendado) - commit_sha (recomendado) -
license (obligatoria)

Para Validated se recomienda referencia fija.

------------------------------------------------------------------------

# 7. Identificador Persistente Tipo DOI Ligero

Formato: ccg-ai:R-000123@v1.2.0

Permite citación institucional y futura integración DOI.

------------------------------------------------------------------------

# 8. Modelo Sandbox / Validated

Promoción automática si: - ≥ 10 votos - ≥ 50 usos - ≥ 2 semanas - 0
reportes críticos

Revisión humana opcional.

------------------------------------------------------------------------

# 9. Requisitos Funcionales

## Biblioteca

-   Filtros por categoría
-   Filtros por estado
-   Búsqueda textual

## Publicación

Wizard 5 pasos: 1. Metadatos 2. Tipo de fuente 3. Instrucciones 4.
Ejemplo mínimo 5. Licencia

## Perfil Público

-   Recursos publicados
-   Recursos validados
-   Métricas acumuladas

------------------------------------------------------------------------

# 10. Requisitos No Funcionales

-   Seguridad CSRF
-   Logs auditables
-   Backups automáticos
-   Disponibilidad ≥ 99%

------------------------------------------------------------------------

# 11. Modelo de Datos Conceptual

Entidades: - Usuario - Recurso - ResourceVersion - Voto - Reporte -
Métrica

Relaciones: - Usuario 1:N Recurso - Recurso 1:N Version - Usuario N:M
Recurso (Voto)

------------------------------------------------------------------------

# 12. Roadmap Evolutivo

## Fase 1 -- MVP

Infraestructura sólida.

## Fase 2 -- Expansión

-   Enlaces a notebooks
-   Ranking avanzado
-   Métricas mejoradas

## Fase 3 -- Inteligencia

-   Recomendador
-   Búsqueda semántica
-   API pública

------------------------------------------------------------------------

# 13. KPIs

  Indicador             Meta Año 1
  --------------------- ------------
  Recursos              50
  Usuarios activos      20
  \% Validated          ≥20%
  Participación votos   ≥30%

------------------------------------------------------------------------

# 14. Riesgos y Mitigaciones

  Riesgo               Mitigación
  -------------------- ----------------------------
  Baja adopción        Incentivos internos
  Dependencia GitHub   Versionado interno robusto
  Sobreingeniería      Enfoque modular

------------------------------------------------------------------------

# 15. Estrategia de Sostenibilidad

-   Infraestructura pública
-   Evolución basada en métricas
-   Comunidad académica activa

------------------------------------------------------------------------

# 16. Criterios Globales de Aceptación

-   Plataforma estable
-   Usuarios activos reales
-   Recursos reutilizados
-   Promociones a Validated
-   Integración en al menos un curso

------------------------------------------------------------------------

Documento técnico completo para evaluación institucional y desarrollo.
