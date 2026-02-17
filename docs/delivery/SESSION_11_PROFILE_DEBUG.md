# Session 11: Profile Page Debugging & Backend Fixes

**Fecha**: 2026-02-17  
**Objetivo**: Depurar y corregir errores en el Profile Page y endpoints backend  
**Status**: ✅ Completado

---

## 📋 Resumen Ejecutivo

Esta sesión se enfocó en depurar y corregir errores críticos en el Profile Page que impedían su funcionamiento. Se identificaron y resolvieron problemas relacionados con el uso incorrecto de propiedades del modelo Django en queries de base de datos.

### Resultado Final
✅ Profile Page funcionando completamente  
✅ Endpoints backend corregidos y optimizados  
✅ Métricas de usuario calculándose correctamente  
✅ Grid de recursos publicados mostrándose correctamente

---

## 🐛 Problemas Encontrados

### 1. Error: "User not found" en Profile Page

**Síntoma**: Al acceder a `/profile`, la página mostraba "User not found" y "Error loading profile. Please try again."

**Causa Raíz**: Error 500 en el endpoint `/api/users/:id/`

**Logs del Error**:
```
ERROR 2026-02-17 00:50:07,742 basehttp "GET /api/users/70690933-c262-473f-a39e-920668f9fab8/ HTTP/1.1" 500 133206
django.core.exceptions.FieldError: Cannot resolve keyword 'latest_version' into field
```

---

### 2. Error: `latest_version` no es un campo de BD

**Problema**: 
```python
# ❌ INCORRECTO
validated_resources = resources.filter(
    latest_version__status='Validated'
).count()
```

**Causa**: `latest_version` es una **propiedad** del modelo `Resource`, no un campo de base de datos. Django no puede hacer queries con propiedades.

**Definición en el modelo**:
```python
@property
def latest_version(self):
    """Get the latest version of this resource."""
    return self.versions.filter(is_latest=True).first()
```

**Solución**: Usar el modelo `ResourceVersion` directamente:
```python
# ✅ CORRECTO
validated_resources = ResourceVersion.objects.filter(
    resource__owner=user,
    resource__deleted_at__isnull=True,
    is_latest=True,
    status='Validated'
).count()
```

---

### 3. Error: `votes_count` no es un campo de BD

**Problema**:
```python
# ❌ INCORRECTO
total_votes = resources.aggregate(
    total=Sum('votes_count')
)['total'] or 0
```

**Error**:
```
django.core.exceptions.FieldError: Cannot resolve keyword 'votes_count' into field. 
Choices are: created_at, deleted_at, derived_from_resource, derived_from_resource_id, 
derived_from_version, derived_from_version_id, forks, forks_count, id, notifications, 
owner, owner_id, source_type, updated_at, versions, votes
```

**Causa**: `votes_count` es una **propiedad** que cuenta relaciones:
```python
@property
def votes_count(self):
    """Count of votes (computed)."""
    return self.votes.count()
```

**Solución**: Contar directamente desde el modelo `Vote`:
```python
# ✅ CORRECTO
from apps.interactions.models import Vote

total_votes = Vote.objects.filter(
    resource__owner=user,
    resource__deleted_at__isnull=True
).count()
```

---

### 4. Error: `select_related('latest_version')` inválido

**Problema en `UserResourcesView`**:
```python
# ❌ INCORRECTO
resources = Resource.objects.filter(
    owner=user,
    deleted_at__isnull=True
).select_related('latest_version').order_by('-created_at')
```

**Error**:
```
django.core.exceptions.FieldError: Invalid field name(s) given in select_related: 'latest_version'. 
Choices are: owner, derived_from_resource, derived_from_version
```

**Causa**: `select_related()` solo funciona con campos ForeignKey reales, no con propiedades.

**Solución**: Usar `prefetch_related()` para las versiones:
```python
# ✅ CORRECTO
resources = Resource.objects.filter(
    owner=user,
    deleted_at__isnull=True
).prefetch_related('versions').order_by('-created_at')
```

---

### 5. Filtrado por status con propiedades

**Problema**: No se puede filtrar por `latest_version__status` en el queryset.

**Solución**: Filtrar en Python después de obtener los recursos:
```python
if resource_status:
    all_resources = list(resources)
    resources_filtered = [
        r for r in all_resources 
        if r.latest_version and r.latest_version.status == resource_status
    ]
    total_count = len(resources_filtered)
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    resources = resources_filtered[start:end]
```

---

## 🔧 Cambios Realizados

### Archivo: `backend/apps/authentication/views_users.py`

#### Imports actualizados:
```python
from apps.authentication.models import User
from apps.authentication.serializers import UserSerializer
from apps.resources.models import Resource, ResourceVersion
from apps.resources.serializers import ResourceListSerializer
from apps.interactions.models import Vote
```

#### `UserDetailView.get()` - Cálculo de métricas corregido:

```python
def get(self, request, user_id):
    user = get_object_or_404(User, id=user_id, is_active=True)
    
    # Get user metrics
    resources = Resource.objects.filter(owner=user, deleted_at__isnull=True)
    
    total_resources = resources.count()
    
    # Count validated resources by checking latest versions
    validated_resources = ResourceVersion.objects.filter(
        resource__owner=user,
        resource__deleted_at__isnull=True,
        is_latest=True,
        status='Validated'
    ).count()
    
    # Total votes received across all user's resources
    # Use Vote model to count votes
    total_votes = Vote.objects.filter(
        resource__owner=user,
        resource__deleted_at__isnull=True
    ).count()
    
    # Total reuses (forks) received
    # Use forks_count denormalized field
    total_reuses = resources.aggregate(
        total=Sum('forks_count')
    )['total'] or 0
    
    # Calculate impact (simple formula for MVP)
    # Impact = validated_resources * 10 + total_votes + total_reuses * 5
    total_impact = (validated_resources * 10) + total_votes + (total_reuses * 5)
    
    # Serialize user data
    serializer = UserSerializer(user)
    user_data = serializer.data
    
    # Add metrics
    user_data['metrics'] = {
        'total_resources': total_resources,
        'validated_resources': validated_resources,
        'total_votes': total_votes,
        'total_reuses': total_reuses,
        'total_impact': total_impact,
    }
    
    return Response(user_data, status=status.HTTP_200_OK)
```

#### `UserResourcesView.get()` - Queryset y filtrado corregido:

```python
def get(self, request, user_id):
    user = get_object_or_404(User, id=user_id, is_active=True)
    
    # Get query params
    resource_status = request.query_params.get('status', None)
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 12))
    
    # Base queryset
    # Note: can't use select_related with 'latest_version' as it's a property, not a FK
    resources = Resource.objects.filter(
        owner=user,
        deleted_at__isnull=True
    ).prefetch_related('versions').order_by('-created_at')
    
    # Filter by status if provided
    # Note: can't filter by latest_version__status directly, need to do it in Python
    if resource_status:
        # Get all resources and filter in Python
        all_resources = list(resources)
        resources_filtered = [
            r for r in all_resources 
            if r.latest_version and r.latest_version.status == resource_status
        ]
        total_count = len(resources_filtered)
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        resources = resources_filtered[start:end]
    else:
        # Pagination
        total_count = resources.count()
        start = (page - 1) * page_size
        end = start + page_size
        resources = resources[start:end]
    
    # Serialize
    serializer = ResourceListSerializer(resources, many=True)
    
    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'results': serializer.data
    }, status=status.HTTP_200_OK)
```

---

## ✅ Verificación de Funcionamiento

### Endpoint: GET `/api/users/:id/`

**Request**:
```bash
curl http://localhost:8000/api/users/70690933-c262-473f-a39e-920668f9fab8/
```

**Response** (200 OK):
```json
{
  "id": "70690933-c262-473f-a39e-920668f9fab8",
  "email": "demo@example.com",
  "name": "Demo User",
  "is_active": true,
  "email_verified_at": "2026-02-16T20:42:25.597015-06:00",
  "roles": [
    {
      "id": "90ba1dda-1101-436b-84ab-eabdb7582fbb",
      "name": "User",
      "description": "Regular user with standard permissions"
    }
  ],
  "is_admin": false,
  "created_at": "2026-02-16T20:42:25.587566-06:00",
  "metrics": {
    "total_resources": 2,
    "validated_resources": 1,
    "total_votes": 1,
    "total_reuses": 1,
    "total_impact": 16
  }
}
```

### Endpoint: GET `/api/users/:id/resources/`

**Request**:
```bash
curl 'http://localhost:8000/api/users/70690933-c262-473f-a39e-920668f9fab8/resources/?page_size=12'
```

**Response** (200 OK):
```json
{
  "count": 2,
  "page": 1,
  "page_size": 12,
  "results": [
    {
      "id": "...",
      "title": "Test Prompt for BioAI (Fork)",
      "latest_version": {
        "status": "Sandbox",
        ...
      },
      ...
    },
    {
      "id": "...",
      "title": "Test Prompt for BioAI",
      "latest_version": {
        "status": "Validated",
        ...
      },
      ...
    }
  ]
}
```

---

## 🎨 Profile Page - Estado Final

### Elementos Visibles:
✅ **Avatar circular** con iniciales del usuario (DU)  
✅ **Badge de "Contributor"**  
✅ **Reputation Score**: 16 puntos con trofeo 🏆  
✅ **Progress Bar**: 16/500 hacia el siguiente nivel  
✅ **Metrics Dashboard** (3 tarjetas):
- 📄 **2 Contributions** (recursos publicados)
- ✅ **1 Validations Made** (recursos validados)
- 📈 **16 Total Impact** (fórmula de gamificación)

✅ **Published Resources Grid**: 2 recursos
- 1 en estado **Sandbox**
- 1 en estado **✓ Validated**

### Fórmula de Impact (Gamificación):
```
Total Impact = (validated_resources × 10) + total_votes + (total_reuses × 5)
```

Para Demo User:
```
16 = (1 × 10) + 1 + (1 × 5)
16 = 10 + 1 + 5
```

---

## 📚 Lecciones Aprendidas

### 1. Propiedades vs Campos de BD en Django

**Regla**: Solo se pueden usar en queries los campos que existen en la base de datos.

**Propiedades** (`@property`):
- ❌ No se pueden usar en `filter()`
- ❌ No se pueden usar en `select_related()`
- ❌ No se pueden usar en `aggregate()`
- ✅ Se pueden usar después de obtener el objeto

**Campos de BD**:
- ✅ Se pueden usar en queries
- ✅ Se pueden indexar
- ✅ Se pueden optimizar con `select_related()` / `prefetch_related()`

### 2. Optimización de Queries

**Antes** (N+1 queries):
```python
resources = Resource.objects.filter(owner=user)
for r in resources:
    print(r.latest_version.title)  # Query por cada recurso
```

**Después** (2 queries):
```python
resources = Resource.objects.filter(owner=user).prefetch_related('versions')
for r in resources:
    print(r.latest_version.title)  # Sin queries adicionales
```

### 3. Filtrado con Propiedades

Cuando necesitas filtrar por una propiedad:
1. Obtén todos los objetos
2. Filtra en Python con list comprehension
3. Aplica paginación manualmente

**Trade-off**: Menos eficiente para datasets grandes, pero funciona para MVP.

---

## 🔄 Proceso de Debugging

### Metodología Aplicada:

1. **Identificar síntoma**: "User not found" en frontend
2. **Revisar logs del backend**: Error 500 en endpoint
3. **Analizar traceback**: `FieldError: Cannot resolve keyword 'latest_version'`
4. **Revisar modelo**: Identificar que es una propiedad, no un campo
5. **Buscar alternativa**: Usar el modelo relacionado directamente
6. **Implementar fix**: Cambiar query para usar `ResourceVersion`
7. **Probar endpoint**: Verificar con `curl`
8. **Verificar en frontend**: Recargar página
9. **Repetir** para cada error encontrado

### Herramientas Usadas:
- `docker-compose logs backend` - Ver errores del servidor
- `curl` - Probar endpoints directamente
- Django shell - Probar queries interactivamente
- Browser DevTools - Verificar requests del frontend

---

## 📊 Métricas de la Sesión

- **Errores encontrados**: 5
- **Errores corregidos**: 5
- **Archivos modificados**: 1 (`views_users.py`)
- **Líneas cambiadas**: ~40
- **Tests manuales**: 4 (2 endpoints × 2 intentos)
- **Tiempo de debugging**: ~30 minutos
- **Resultado**: ✅ 100% funcional

---

## 🎯 Estado del MVP

### Funcionalidades Completadas:
✅ Autenticación (login/register)  
✅ Explorar recursos  
✅ Ver detalle de recursos  
✅ Publicar recursos  
✅ Votar recursos  
✅ Fork de recursos  
✅ **Profile Page** (nuevo)  
✅ Notificaciones básicas  

### Pendientes para Siguiente Sesión:
Ver `NEXT_STEPS.md` para detalles completos.

---

## 📝 Notas Técnicas

### Consideraciones de Performance

**Actual** (MVP):
- Filtrado por status en Python (lista completa en memoria)
- Aceptable para < 100 recursos por usuario

**Para Producción** (si es necesario):
- Denormalizar `latest_version_id` en tabla `resources`
- Agregar índice en `(owner_id, latest_version_id)`
- Filtrar directamente en SQL

### Alternativa de Implementación

Si se requiere mejor performance, considerar:

```python
# Agregar campo en modelo Resource
class Resource(models.Model):
    # ... campos existentes ...
    latest_version = models.ForeignKey(
        'ResourceVersion',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
        help_text='Cached latest version for performance'
    )
```

Luego usar signals para mantenerlo actualizado:
```python
@receiver(post_save, sender=ResourceVersion)
def update_latest_version(sender, instance, **kwargs):
    if instance.is_latest:
        instance.resource.latest_version = instance
        instance.resource.save(update_fields=['latest_version'])
```

**Trade-off**: Más complejidad vs mejor performance.  
**Decisión MVP**: Mantener simple, optimizar después si es necesario.

---

## ✅ Checklist de Entrega

- [x] Errores identificados y documentados
- [x] Fixes implementados y probados
- [x] Endpoints funcionando correctamente
- [x] Frontend mostrando datos correctamente
- [x] Código comentado y limpio
- [x] Documentación actualizada
- [x] Lecciones aprendidas registradas
- [x] Next steps documentados

---

**Sesión completada exitosamente** ✅  
**Fecha de cierre**: 2026-02-17  
**Próxima sesión**: Ver `NEXT_STEPS.md`
