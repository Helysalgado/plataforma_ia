# ADR-002: Versionado de Recursos

**Estado:** Aceptado  
**Fecha:** 2026-02-16  
**Decisor(es):** Tech Lead, Product Manager  
**Contexto:** FASE 3 — Diseño Técnico

---

## Contexto y Problema

BioAI Hub requiere un sistema de versionado que:
1. Permita editar recursos después de publicados
2. Mantenga inmutabilidad de versiones **Validated** (crítico para citación académica)
3. Soporte trazabilidad histórica (changelog)
4. Sea comprensible para usuarios no técnicos
5. Permita identificadores persistentes (PID) por versión

**Decisión requerida:** ¿Cómo diseñar el sistema de versionado?

---

## Requisitos Clave

### Funcionales:
1. **FR-1:** Editar recurso con última versión **Sandbox** → actualizar in-place
2. **FR-2:** Editar recurso con última versión **Validated** → crear nueva versión (vNext)
3. **FR-3:** Versiones Validated son **inmutables** (no se pueden editar)
4. **FR-4:** Cada versión tiene PID único: `ccg-ai:R-000123@v1.0.0`
5. **FR-5:** Historial de versiones navegable
6. **FR-6:** Validación es por **versión**, no por recurso completo

### No Funcionales:
1. **NFR-1:** Performance: Obtener última versión en <50ms (query simple)
2. **NFR-2:** Storage: No duplicar contenido innecesariamente
3. **NFR-3:** UX: Flujo de versionado claro y no confuso

---

## Opciones Consideradas

### Opción 1: Versionado por Copia Completa (Full Copy)
**Descripción:** Cada versión es una copia completa e independiente del recurso

**Modelo:**
```python
class Resource(models.Model):
    id = UUIDField(primary_key=True)
    owner = ForeignKey(User)
    # Metadatos compartidos...

class ResourceVersion(models.Model):
    id = UUIDField(primary_key=True)
    resource = ForeignKey(Resource, related_name='versions')
    version_number = CharField(max_length=20)  # "1.0.0"
    
    # TODOS los datos del recurso se copian aquí:
    title = CharField(max_length=200)
    description = TextField()
    content = TextField(null=True, blank=True)
    repo_url = URLField(null=True, blank=True)
    tags = JSONField(default=list)
    type = CharField(choices=...)
    source_type = CharField(choices=...)
    # ... todos los campos
    
    status = CharField(choices=['Sandbox', 'Validated', ...])
    validated_at = DateTimeField(null=True, blank=True)
    is_latest = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
```

**Pros:**
- ✅ Inmutabilidad total por diseño (cada versión es independiente)
- ✅ Queries simples (no joins complejos)
- ✅ Fácil de entender (cada versión es autónoma)

**Contras:**
- ❌ Duplicación de datos (storage ineficiente)
- ❌ Si se agrega campo a Resource, debe agregarse a ResourceVersion también
- ❌ Posible inconsistencia entre versiones (ej: tags compartidos vs por versión)

---

### Opción 2: Versionado Incremental (Delta-based)
**Descripción:** Solo guardar cambios (deltas) entre versiones

**Modelo:**
```python
class Resource(models.Model):
    id = UUIDField(primary_key=True)
    owner = ForeignKey(User)
    current_version_id = ForeignKey('ResourceVersion', null=True)
    # Metadatos base...

class ResourceVersion(models.Model):
    id = UUIDField(primary_key=True)
    resource = ForeignKey(Resource)
    version_number = CharField(max_length=20)
    parent_version = ForeignKey('self', null=True, blank=True)  # Versión anterior
    
    # Solo almacenar cambios (delta):
    delta = JSONField()  # { "title": "new title", "description": "new desc" }
    
    status = CharField(choices=...)
    created_at = DateTimeField(auto_now_add=True)
```

**Pros:**
- ✅ Storage eficiente (solo guarda cambios)
- ✅ Historial completo de cambios (audit trail)

**Contras:**
- ❌ **Complejidad:** Reconstruir versión completa requiere aplicar todos los deltas desde v1
- ❌ Performance degradada con muchas versiones (reconstrucción lenta)
- ❌ Difícil de implementar correctamente (bugs sutiles)
- ❌ No apropiado para MVP

---

### Opción 3: Versionado Híbrido (Snapshot + Metadata Compartidos)
**Descripción:** Versiones son snapshots completos del contenido, pero metadatos inmutables se comparten a nivel de Resource

**Modelo:**
```python
class Resource(models.Model):
    id = UUIDField(primary_key=True)
    owner = ForeignKey(User)
    source_type = CharField(choices=['Internal', 'GitHub-Linked'])
    derived_from_resource = ForeignKey('self', null=True, blank=True)
    derived_from_version = ForeignKey('ResourceVersion', null=True, blank=True)
    forks_count = IntegerField(default=0)
    deleted_at = DateTimeField(null=True, blank=True)  # Soft delete
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class ResourceVersion(models.Model):
    id = UUIDField(primary_key=True)
    resource = ForeignKey(Resource, related_name='versions')
    version_number = CharField(max_length=20)  # "1.0.0" o "1.1.0"
    
    # Contenido versionable (puede cambiar entre versiones):
    title = CharField(max_length=200)
    description = TextField()
    type = CharField(choices=ResourceTypeChoices.choices)
    tags = JSONField(default=list)
    content = TextField(null=True, blank=True)  # Si Internal
    content_hash = CharField(max_length=64, null=True, blank=True)  # SHA256 si Internal
    repo_url = URLField(null=True, blank=True)  # Si GitHub-Linked
    repo_tag = CharField(max_length=100, null=True, blank=True)
    repo_commit_sha = CharField(max_length=40, null=True, blank=True)
    license = CharField(max_length=50, null=True, blank=True)
    example = TextField(null=True, blank=True)
    changelog = TextField(null=True, blank=True)  # Qué cambió en esta versión
    
    # Estado de validación (por versión):
    status = CharField(max_length=20, choices=ValidationStatusChoices.choices, default='Sandbox')
    validated_at = DateTimeField(null=True, blank=True)
    
    # Metadatos:
    is_latest = BooleanField(default=False, db_index=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resource_versions'
        unique_together = [('resource', 'version_number')]
        indexes = [
            models.Index(fields=['resource', 'is_latest']),
            models.Index(fields=['status']),
        ]
```

**Pros:**
- ✅ Balance entre simplicidad y eficiencia
- ✅ Inmutabilidad por versión (cada versión es snapshot completo)
- ✅ Metadatos compartidos (owner, derivation) en Resource
- ✅ Queries simples para latest version (`is_latest=True`)
- ✅ PID único por versión: `resource.id` + `version.version_number`

**Contras:**
- ⚠️ Duplicación parcial de datos (aceptable para MVP)
- ⚠️ Requiere gestión de `is_latest` flag

---

## Decisión

**Elegimos: Opción 3 — Versionado Híbrido (Snapshot + Metadata Compartidos)**

**Justificación:**
1. **Balance:** Simplicidad de implementación + performance adecuada
2. **Inmutabilidad:** Versiones Validated son inmutables por diseño (no se editan)
3. **MVP-friendly:** No requiere lógica compleja de deltas
4. **Escalable:** Si storage se vuelve problema, migrar a delta-based en futuro
5. **Citación académica:** PID por versión es claro (`ccg-ai:R-000123@v1.0.0`)

---

## Implementación Detallada

### 1. Algoritmo de Versionado

#### Caso A: Editar Recurso con Última Versión NO Validated

```python
# apps/resources/services.py

class VersioningService:
    @staticmethod
    @transaction.atomic
    def update_resource(resource, user, data):
        latest_version = resource.get_latest_version()
        
        if latest_version.status != 'Validated':
            # Update in-place (NO crear nueva versión)
            latest_version.title = data.get('title', latest_version.title)
            latest_version.description = data.get('description', latest_version.description)
            latest_version.tags = data.get('tags', latest_version.tags)
            # ... actualizar otros campos
            
            if resource.source_type == 'Internal' and 'content' in data:
                latest_version.content = data['content']
                latest_version.content_hash = hashlib.sha256(
                    data['content'].encode('utf-8')
                ).hexdigest()
            
            latest_version.updated_at = timezone.now()
            latest_version.save()
            
            return latest_version
        else:
            # Crear nueva versión (ver Caso B)
            return VersioningService.create_new_version(resource, data)
```

#### Caso B: Editar Recurso con Última Versión Validated

```python
@staticmethod
@transaction.atomic
def create_new_version(resource, data, changelog=None):
    latest_version = resource.get_latest_version()
    
    # Calcular nuevo version_number
    new_version_number = VersioningService.increment_version(
        latest_version.version_number
    )
    
    # Crear nueva versión (copia + cambios)
    new_version = ResourceVersion.objects.create(
        resource=resource,
        version_number=new_version_number,
        
        # Copiar campos que no cambiaron (o usar data si existe)
        title=data.get('title', latest_version.title),
        description=data.get('description', latest_version.description),
        type=data.get('type', latest_version.type),
        tags=data.get('tags', latest_version.tags),
        content=data.get('content', latest_version.content),
        repo_url=data.get('repo_url', latest_version.repo_url),
        repo_tag=data.get('repo_tag', latest_version.repo_tag),
        repo_commit_sha=data.get('repo_commit_sha', latest_version.repo_commit_sha),
        license=data.get('license', latest_version.license),
        example=data.get('example', latest_version.example),
        changelog=changelog,  # Qué cambió
        
        # Nueva versión comienza en Sandbox
        status='Sandbox',
        validated_at=None,
        
        is_latest=True,  # Esta es la nueva última versión
    )
    
    # Actualizar versión anterior
    latest_version.is_latest = False
    latest_version.save(update_fields=['is_latest'])
    
    return new_version
```

#### Version Numbering

**Estrategia:** Semantic Versioning simplificado (MAJOR.MINOR.PATCH)

```python
@staticmethod
def increment_version(current_version):
    """
    Incrementa version_number según tipo de cambio.
    
    Para MVP: Siempre incrementar MINOR (1.0.0 → 1.1.0)
    Post-MVP: Permitir usuario elegir tipo de incremento
    
    Args:
        current_version (str): "1.0.0"
    
    Returns:
        str: "1.1.0"
    """
    major, minor, patch = map(int, current_version.split('.'))
    
    # MVP: Siempre incrementar minor
    minor += 1
    
    return f"{major}.{minor}.{patch}"
```

**Alternativa Post-MVP:** Permitir usuario elegir:
- **Patch** (1.0.0 → 1.0.1): Cambios menores (typos, formato)
- **Minor** (1.0.0 → 1.1.0): Cambios moderados (mejoras, agregar contenido)
- **Major** (1.0.0 → 2.0.0): Cambios breaking (reestructuración completa)

---

### 2. Generación de PID (Persistent Identifier)

**Formato:** `ccg-ai:R-{resource_id}@v{version_number}`

**Ejemplo:** `ccg-ai:R-f47ac10b-58cc-4372-a567-0e02b2c3d479@v1.0.0`

```python
# apps/resources/models.py

class ResourceVersion(models.Model):
    # ...
    
    @property
    def pid(self):
        """
        Persistent Identifier tipo DOI ligero.
        
        Formato: ccg-ai:R-{resource_id}@v{version_number}
        Ejemplo: ccg-ai:R-000123@v1.0.0
        """
        resource_short_id = str(self.resource.id)[:8]  # Primeros 8 chars del UUID
        return f"ccg-ai:R-{resource_short_id}@v{self.version_number}"
    
    def get_citation(self):
        """
        Formato de citación académica.
        
        Ejemplo:
        García, A. (2026). Protein Folding Prompt. BioAI Hub.
        ccg-ai:R-f47ac10b@v1.0.0
        Retrieved from https://bioai.ccg.unam.mx/resources/f47ac10b-58cc-4372-a567-0e02b2c3d479
        """
        return f"{self.resource.owner.name} ({self.created_at.year}). {self.title}. BioAI Hub. {self.pid}. Retrieved from https://bioai.ccg.unam.mx/resources/{self.resource.id}"
```

---

### 3. Consultas Comunes (Queries)

#### Obtener Latest Version de un Recurso

```python
# Opción 1: Usar flag is_latest (más rápido)
latest_version = resource.versions.get(is_latest=True)

# Opción 2: Ordenar por created_at (más seguro si is_latest se desincroniza)
latest_version = resource.versions.order_by('-created_at').first()

# Opción 3: Método en modelo (RECOMENDADO)
class Resource(models.Model):
    # ...
    
    def get_latest_version(self):
        return self.versions.get(is_latest=True)
```

#### Listar Historial de Versiones

```python
# Todas las versiones, ordenadas por fecha (más reciente primero)
versions = resource.versions.order_by('-created_at')

# Solo versiones Validated
validated_versions = resource.versions.filter(status='Validated').order_by('-created_at')
```

#### Buscar Recursos por PID

```python
# Endpoint: GET /api/resources/pid/ccg-ai:R-f47ac10b@v1.0.0

def get_by_pid(pid):
    # Parse PID
    match = re.match(r'ccg-ai:R-([^@]+)@v(.+)', pid)
    if not match:
        raise ValueError("Invalid PID format")
    
    resource_short_id, version_number = match.groups()
    
    # Buscar resource por UUID que empiece con short_id
    resource = Resource.objects.filter(id__startswith=resource_short_id).first()
    if not resource:
        raise NotFound()
    
    # Buscar versión específica
    version = resource.versions.get(version_number=version_number)
    return version
```

---

### 4. UX: Banner Informativo al Editar

Cuando usuario intenta editar recurso con última versión **Validated**:

```typescript
// frontend/components/resource/EditResourceForm.tsx

useEffect(() => {
  if (latestVersion.status === 'Validated') {
    showBanner({
      type: 'warning',
      message: (
        <>
          ⚠️ Este recurso está <Badge>Validated</Badge>. 
          Al guardar cambios se creará una nueva versión (<strong>v{nextVersion}</strong>) 
          y el recurso volverá a estado <Badge variant="sandbox">Sandbox</Badge>.
          La versión anterior (<strong>v{latestVersion.version_number}</strong>) permanecerá Validated.
        </>
      ),
      actions: [
        { label: 'Entendido', onClick: () => dismissBanner() },
        { label: 'Cancelar Edición', onClick: () => router.back(), variant: 'outline' }
      ]
    });
  }
}, [latestVersion]);
```

---

### 5. Changelog Opcional

**MVP:** Changelog es **opcional** (textarea en formulario de edición)

**Post-MVP:** Changelog **recomendado** (mostrar warning si se deja vacío)

**Uso:**
- Mostrar en historial de versiones
- Ayudar a usuarios a entender qué cambió
- Facilitar decisión de qué versión usar

**Ejemplo:**
```
v1.1.0 (2026-02-10)
- Agregado soporte para AlphaFold 3
- Mejorada descripción de parámetros
- Corregido typo en ejemplo
```

---

## Flujos de Versionado

### Flujo 1: Publicar Recurso Nuevo

```
User → Completa formulario en /publish
    → ResourceService.create()
    → Crea Resource (id=R-123)
    → Crea ResourceVersion (version_number="1.0.0", is_latest=True, status="Sandbox")
    → PID generado: ccg-ai:R-123@v1.0.0
    ← Redirect a /resources/R-123
```

### Flujo 2: Editar Recurso en Sandbox

```
Owner → Click "Edit" en /resources/R-123
      → Formulario pre-llenado con datos de v1.0.0 (Sandbox)
      → Modifica título y descripción
      → Click "Save Changes"
      → VersioningService.update_resource()
      → Actualiza v1.0.0 in-place (NO crea nueva versión)
      → updated_at actualizado
      ← Redirect a /resources/R-123
```

### Flujo 3: Validar Recurso (Admin)

```
Admin → Click "Validate" en /resources/R-123
      → Modal confirmación
      → ValidationService.validate_manually()
      → ResourceVersion v1.0.0: status="Validated", validated_at=now()
      → Crea Notification para owner
      ← Badge cambia a "Validated" (verde)
```

### Flujo 4: Editar Recurso Validated (Crea Nueva Versión)

```
Owner → Click "Edit" en /resources/R-123 (latest=v1.0.0 Validated)
      → Banner: "Editar creará nueva versión v1.1.0"
      → Modifica contenido
      → (Opcional) Ingresa changelog: "Agregado soporte AlphaFold 3"
      → Click "Save Changes"
      → VersioningService.create_new_version()
      → Crea ResourceVersion v1.1.0 (status="Sandbox", is_latest=True)
      → ResourceVersion v1.0.0: is_latest=False (permanece Validated)
      ← Redirect a /resources/R-123 (muestra v1.1.0)
      ← Toast: "Nueva versión creada (v1.1.0). La versión anterior permanece Validated."
```

### Flujo 5: Ver Versión Específica

```
User → Click en "v1.0.0" en historial de versiones
     → GET /api/resources/R-123/versions/v1.0.0
     → Muestra contenido de v1.0.0 (Validated)
     → Botones Edit/Delete deshabilitados (no es latest)
     → Muestra badge "Validated" y "Historical Version"
```

---

## Validaciones y Constraints

### BD Constraints:
```sql
-- Unique constraint: No dos versiones con mismo version_number en un recurso
ALTER TABLE resource_versions
ADD CONSTRAINT unique_resource_version
UNIQUE (resource_id, version_number);

-- Check constraint: version_number formato válido (MAJOR.MINOR.PATCH)
ALTER TABLE resource_versions
ADD CONSTRAINT check_version_number_format
CHECK (version_number ~ '^\d+\.\d+\.\d+$');

-- Index para queries de latest version
CREATE INDEX idx_resource_latest ON resource_versions(resource_id, is_latest);
```

### Lógica de Negocio:
1. **Solo 1 versión con `is_latest=True` por recurso** (enforced en Service Layer)
2. **Versiones Validated NO se pueden editar** (enforced en Permission Class)
3. **Version number siempre crece** (no se puede retroceder a v1.0.0 después de v1.1.0)

---

## Riesgos y Mitigaciones

### Riesgo 1: Flag `is_latest` se desincroniza
**Escenario:** Bug en código actualiza `is_latest` incorrectamente, quedando 0 o 2+ versiones con `is_latest=True`

**Mitigación:**
- Usar transacciones (`@transaction.atomic`) en todas las operaciones de versionado
- Script de verificación periódico (cron job):
  ```python
  # Check: Cada recurso debe tener exactamente 1 versión con is_latest=True
  from django.db.models import Count
  
  problematic_resources = Resource.objects.annotate(
      latest_count=Count('versions', filter=Q(versions__is_latest=True))
  ).exclude(latest_count=1)
  
  if problematic_resources.exists():
      # Alertar y corregir
      for resource in problematic_resources:
          # Corregir: Marcar solo la más reciente como latest
          latest = resource.versions.order_by('-created_at').first()
          resource.versions.update(is_latest=False)
          latest.is_latest = True
          latest.save()
  ```

### Riesgo 2: Usuario confundido por versionado automático
**Escenario:** Usuario edita recurso Validated, no entiende por qué creó nueva versión

**Mitigación:**
- Banner informativo **claro** antes de editar (ver sección 4)
- Documentación en `/help` o tooltips
- Changelog recomendado (ayuda a entender cambios)

### Riesgo 3: Storage crece con muchas versiones
**Escenario:** Recursos con 50+ versiones ocupan mucho espacio (contenido duplicado)

**Mitigación:**
- MVP: Aceptable (pocas versiones esperadas)
- Post-MVP: Migrar a versionado incremental (delta-based) si es necesario
- Post-MVP: Límite de versiones por recurso (ej: max 20)

---

## Extensiones Futuras (Post-MVP)

1. **Comparación de Versiones (Diff):**
   - Vista side-by-side de v1.0.0 vs v1.1.0
   - Highlighting de cambios (similar a GitHub diff)

2. **Revertir a Versión Anterior:**
   - Crear nueva versión copiando contenido de versión anterior
   - Ejemplo: v1.2.0 revierte a v1.0.0 → crea v1.3.0 con contenido de v1.0.0

3. **Versión Numbering Flexible:**
   - Permitir usuario elegir tipo de incremento (patch/minor/major)
   - Auto-detección de tipo de cambio (IA)

4. **Branching (Experimental):**
   - Versiones paralelas (ej: v1.0.0-dev, v1.0.0-prod)
   - No prioritario, complejidad alta

---

## Métricas de Éxito

- ✅ Obtener latest version en <50ms (query simple con index)
- ✅ Crear nueva versión en <200ms (copia + insert)
- ✅ 0 bugs de desincronización `is_latest` en primeros 3 meses
- ✅ ≥80% de usuarios entienden flujo de versionado (encuesta post-MVP)

---

## Referencias

- [Semantic Versioning 2.0.0](https://semver.org/)
- [GitHub: How Git Works](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) (inspiración para snapshots)
- [Copy-on-Write Pattern](https://en.wikipedia.org/wiki/Copy-on-write)

---

**Decisión aprobada:** 2026-02-16  
**Implementación:** FASE 7 (Backend MVP)  
**Próximo ADR:** ADR-003 (RBAC Extensible)
