Actúa como Tech Writer + Tech Lead.

Objetivo:
Generar y mantener un SPEC consolidado en:
- /docs/SYSTEM_SPEC_v1.0.md

Fuente:
Usa como input los documentos en /docs (product, ux, architecture, data, api, quality, delivery, infra, ai).
Este SPEC debe ser auto-contenido para evaluación institucional, pero sin duplicar todo: resume y enlaza.

Reglas:
- Mantén consistencia terminológica (nombres de módulos, entidades, endpoints).
- Incluye el flujo E2E prioritario con Must-Have y Should-Have.
- Incluye diagramas como código (Mermaid o PlantUML) embebidos o referenciados.
- Incluye trazabilidad: cada historia Must-Have debe mapear a:
  - pantalla UX
  - endpoint(s)
  - entidad(es)
  - test(s) (unit/integration/BDD/E2E)
- Si falta un documento clave, marca la sección como “PENDIENTE” y agrega una lista de preguntas/acciones.
- Termina con checklist de completitud del SPEC.

Salida:
1) Escribe /docs/SYSTEM_SPEC_v1.0.md completo.
2) Incluye una sección “Change Log” al final con fecha y resumen de cambios.


