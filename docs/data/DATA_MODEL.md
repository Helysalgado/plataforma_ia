# DATA MODEL — BioAI Hub

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Versión:** 1.0  
**Fecha:** 2026-02-16  
**Fase:** FASE 4 — Modelo de Datos  
**Rol activo:** Data Architect + Backend Engineer

---

## 1. VISIÓN GENERAL

### 1.1 Principios de Diseño
1. **Normalización:** 3FN (Third Normal Form) para evitar redundancia
2. **Integridad Referencial:** FK con ON DELETE apropiados
3. **Performance:** Índices en columnas de búsqueda frecuente
4. **Auditoría:** Timestamps (created_at, updated_at) en todas las tablas
5. **Soft Delete:** Flag deleted_at para auditoría (no DELETE físico)
6. **UUIDs:** Primary keys como UUID v4 para seguridad y distribuibilidad

### 1.2 Convenciones
- **Nombres de tablas:** snake_case, plural (ej: `users`, `resource_versions`)
- **Primary Keys:** `id` (UUID)
- **Foreign Keys:** `<tabla>_id` (ej: `owner_id`, `resource_id`)
- **Timestamps:** `created_at`, `updated_at`, `deleted_at` (nullable)
- **Booleanos:** `is_<condición>` (ej: `is_active`, `is_latest`)

---

## 2. DIAGRAMA ENTIDAD-RELACIÓN (ERD)

Ver diagrama detallado en [`diagrams/er.mmd`](diagrams/er.mmd)

**Entidades principales:**
1. **User** (usuarios autenticados)
2. **Role** (roles del sistema)
3. **Resource** (recursos publicados)
4. **ResourceVersion** (versiones de recursos)
5. **Vote** (votos a recursos)
6. **Notification** (notificaciones in-app)
7. *(Opcional MVP)* **Report** (reportes de contenido)

---

## 3. ENTIDADES DETALLADAS

### 3.1 ENTIDAD: users

**Descripción:** Usuarios registrados en la plataforma

**Tabla:** `users`

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL, DEFAULT uuid_generate_v4() | Identificador único |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Email del usuario |
| `password_hash` | VARCHAR(255) | NOT NULL | Hash bcrypt de contraseña |
| `name` | VARCHAR(200) | NOT NULL | Nombre completo |
| `avatar_url` | TEXT | NULL | URL del avatar (Gravatar o custom) |
| `bio` | TEXT | NULL, CHECK(LENGTH(bio) <= 500) | Biografía corta |
| `email_verified_at` | TIMESTAMP | NULL, INDEX | Timestamp de verificación |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Usuario activo o suspendido |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha de registro |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Última actualización |

**Índices:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_email_verified ON users(email_verified_at) WHERE email_verified_at IS NOT NULL;
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**Constraints:**
```sql
ALTER TABLE users ADD CONSTRAINT check_email_format 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users ADD CONSTRAINT check_name_not_empty 
CHECK (LENGTH(TRIM(name)) > 0);
```

**Relaciones:**
- `roles` (M2M via `user_roles`)
- `resources` (1:N) — recursos creados por el usuario
- `votes` (1:N) — votos emitidos por el usuario
- `notifications` (1:N) — notificaciones recibidas

**Notas:**
- `password_hash`: bcrypt con Django (rounds=12)
- `email_verified_at`: NULL hasta que usuario verifique email
- `is_active`: FALSE si admin suspende cuenta

---

### 3.2 ENTIDAD: roles

**Descripción:** Roles del sistema (Admin, User, Reviewer, Moderator)

**Tabla:** `roles`

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL | Identificador único |
| `name` | VARCHAR(50) | UNIQUE, NOT NULL | Nombre del rol (Admin, User) |
| `description` | TEXT | NULL | Descripción del rol |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha de creación |

**Índices:**
```sql
CREATE UNIQUE INDEX idx_roles_name ON roles(name);
```

**Relaciones:**
- `users` (M2M via `user_roles`)

**Datos seed (MVP):**
```sql
INSERT INTO roles (id, name, description) VALUES
  (gen_random_uuid(), 'Admin', 'Full access to all resources and admin panel'),
  (gen_random_uuid(), 'User', 'Standard user, can publish and interact with resources');
```

---

### 3.3 ENTIDAD: user_roles (Tabla Pivot M2M)

**Descripción:** Relación Many-to-Many entre usuarios y roles

**Tabla:** `user_roles`

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL | Identificador único |
| `user_id` | UUID | FK users(id) ON DELETE CASCADE, NOT NULL | Usuario |
| `role_id` | UUID | FK roles(id) ON DELETE CASCADE, NOT NULL | Rol |
| `assigned_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha de asignación |

**Índices:**
```sql
CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_user_roles_role ON user_roles(role_id);
CREATE UNIQUE INDEX idx_user_roles_unique ON user_roles(user_id, role_id);
```

**Constraints:**
```sql
ALTER TABLE user_roles ADD CONSTRAINT fk_user_roles_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE user_roles ADD CONSTRAINT fk_user_roles_role 
FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE;
```

---

### 3.4 ENTIDAD: resources

**Descripción:** Recursos publicados (wrapper de versiones)

**Tabla:** `resources`

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL | Identificador único |
| `owner_id` | UUID | FK users(id) ON DELETE CASCADE, NOT NULL, INDEX | Creador del recurso |
| `source_type` | VARCHAR(20) | NOT NULL, CHECK(source_type IN ('Internal', 'GitHub-Linked')) | Tipo de fuente |
| `derived_from_resource_id` | UUID | FK resources(id) ON DELETE SET NULL, NULL | Recurso original (si fork) |
| `derived_from_version_id` | UUID | FK resource_versions(id) ON DELETE SET NULL, NULL | Versión original (si fork) |
| `forks_count` | INTEGER | NOT NULL, DEFAULT 0, CHECK(forks_count >= 0) | Contador de forks |
| `deleted_at` | TIMESTAMP | NULL, INDEX | Soft delete timestamp |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW(), INDEX | Fecha de creación |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Última actualización |

**Índices:**
```sql
CREATE INDEX idx_resources_owner ON resources(owner_id, created_at DESC);
CREATE INDEX idx_resources_deleted ON resources(deleted_at) WHERE deleted_at IS NOT NULL;
CREATE INDEX idx_resources_created ON resources(created_at DESC);
CREATE INDEX idx_resources_derived_from ON resources(derived_from_resource_id) WHERE derived_from_resource_id IS NOT NULL;
```

**Constraints:**
```sql
ALTER TABLE resources ADD CONSTRAINT fk_resources_owner 
FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE resources ADD CONSTRAINT fk_resources_derived_resource 
FOREIGN KEY (derived_from_resource_id) REFERENCES resources(id) ON DELETE SET NULL;

ALTER TABLE resources ADD CONSTRAINT fk_resources_derived_version 
FOREIGN KEY (derived_from_version_id) REFERENCES resource_versions(id) ON DELETE SET NULL;
```

**Relaciones:**
- `owner` (N:1 → users)
- `versions` (1:N → resource_versions)
- `derived_from_resource` (N:1 → resources, self-referencing)
- `derived_from_version` (N:1 → resource_versions)
- `votes` (1:N → votes)

**Notas:**
- `deleted_at`: NULL si activo, timestamp si eliminado (soft delete)
- `forks_count`: Desnormalizado para performance (incrementado al crear fork)

---

### 3.5 ENTIDAD: resource_versions

**Descripción:** Versiones de recursos (contenido versionable)

**Tabla:** `resource_versions`

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL | Identificador único |
| `resource_id` | UUID | FK resources(id) ON DELETE CASCADE, NOT NULL, INDEX | Recurso padre |
| `version_number` | VARCHAR(20) | NOT NULL, CHECK(version_number ~ '^\d+\.\d+\.\d+$') | Versión semántica (1.0.0) |
| `title` | VARCHAR(200) | NOT NULL, INDEX | Título del recurso |
| `description` | TEXT | NOT NULL | Descripción (markdown) |
| `type` | VARCHAR(50) | NOT NULL, CHECK(type IN ('Prompt', 'Workflow', 'Notebook', 'Dataset', 'Tool', 'Other')) | Tipo de recurso |
| `tags` | JSONB | NOT NULL, DEFAULT '[]', INDEX(USING GIN) | Tags (array JSON) |
| `content` | TEXT | NULL | Contenido (si Internal) |
| `content_hash` | VARCHAR(64) | NULL | SHA256 hash (si Internal) |
| `repo_url` | TEXT | NULL | URL GitHub (si GitHub-Linked) |
| `repo_tag` | VARCHAR(100) | NULL | Tag Git (si GitHub-Linked) |
| `repo_commit_sha` | VARCHAR(40) | NULL | Commit SHA (si GitHub-Linked) |
| `license` | VARCHAR(50) | NULL | Licencia (si GitHub-Linked) |
| `example` | TEXT | NULL | Ejemplo de uso |
| `changelog` | TEXT | NULL | Changelog de esta versión |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'Sandbox', INDEX, CHECK(status IN ('Sandbox', 'Pending Validation', 'Validated')) | Estado de validación |
| `validated_at` | TIMESTAMP | NULL | Timestamp de validación |
| `is_latest` | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Es la versión más reciente |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW(), INDEX | Fecha de creación |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Última actualización |

**Índices:**
```sql
CREATE INDEX idx_versions_resource ON resource_versions(resource_id, created_at DESC);
CREATE INDEX idx_versions_latest ON resource_versions(resource_id, is_latest) WHERE is_latest = TRUE;
CREATE INDEX idx_versions_status ON resource_versions(status);
CREATE INDEX idx_versions_validated ON resource_versions(validated_at DESC) WHERE validated_at IS NOT NULL;
CREATE INDEX idx_versions_title ON resource_versions USING gin(to_tsvector('english', title));
CREATE INDEX idx_versions_tags ON resource_versions USING gin(tags);
CREATE INDEX idx_versions_created ON resource_versions(created_at DESC);
```

**Constraints:**
```sql
ALTER TABLE resource_versions ADD CONSTRAINT fk_versions_resource 
FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE;

ALTER TABLE resource_versions ADD CONSTRAINT unique_resource_version 
UNIQUE (resource_id, version_number);

-- Content obligatorio si Internal
ALTER TABLE resource_versions ADD CONSTRAINT check_internal_has_content 
CHECK (
  (SELECT source_type FROM resources WHERE id = resource_id) != 'Internal' 
  OR content IS NOT NULL
);

-- Repo URL y license obligatorios si GitHub-Linked
ALTER TABLE resource_versions ADD CONSTRAINT check_github_has_repo 
CHECK (
  (SELECT source_type FROM resources WHERE id = resource_id) != 'GitHub-Linked' 
  OR (repo_url IS NOT NULL AND license IS NOT NULL)
);

-- Solo 1 versión con is_latest=TRUE por recurso (enforced en Service Layer)
```

**Relaciones:**
- `resource` (N:1 → resources)

**Notas:**
- `tags`: JSONB para búsqueda eficiente con GIN index
- `content_hash`: SHA256 para detección de duplicados y verificación de integridad
- `is_latest`: Solo 1 versión por recurso debe tener `TRUE` (gestión en Service Layer con transacciones)
- `version_number`: Formato semántico MAJOR.MINOR.PATCH (ej: "1.0.0", "1.1.0")

---

### 3.6 ENTIDAD: votes

**Descripción:** Votos de usuarios a recursos

**Tabla:** `votes`

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL | Identificador único |
| `user_id` | UUID | FK users(id) ON DELETE CASCADE, NOT NULL | Usuario que vota |
| `resource_id` | UUID | FK resources(id) ON DELETE CASCADE, NOT NULL | Recurso votado |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha del voto |

**Índices:**
```sql
CREATE INDEX idx_votes_user ON votes(user_id);
CREATE INDEX idx_votes_resource ON votes(resource_id);
CREATE UNIQUE INDEX idx_votes_unique ON votes(user_id, resource_id);
```

**Constraints:**
```sql
ALTER TABLE votes ADD CONSTRAINT fk_votes_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE votes ADD CONSTRAINT fk_votes_resource 
FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE;

ALTER TABLE votes ADD CONSTRAINT unique_user_resource_vote 
UNIQUE (user_id, resource_id);
```

**Relaciones:**
- `user` (N:1 → users)
- `resource` (N:1 → resources)

**Notas:**
- Constraint UNIQUE asegura 1 voto por usuario por recurso
- Para desvotar: DELETE row (no toggle booleano, para simplificar queries de conteo)

---

### 3.7 ENTIDAD: notifications

**Descripción:** Notificaciones in-app para usuarios

**Tabla:** `notifications`

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL | Identificador único |
| `user_id` | UUID | FK users(id) ON DELETE CASCADE, NOT NULL, INDEX | Usuario destinatario |
| `type` | VARCHAR(50) | NOT NULL, CHECK(type IN ('ResourceValidated', 'ResourceForked', 'ValidationRevoked', 'ValidationRequested')) | Tipo de notificación |
| `resource_id` | UUID | FK resources(id) ON DELETE CASCADE, NULL | Recurso relacionado |
| `related_user_id` | UUID | FK users(id) ON DELETE SET NULL, NULL | Usuario relacionado (ej: quien forkeó) |
| `message` | TEXT | NOT NULL | Mensaje de la notificación |
| `read_at` | TIMESTAMP | NULL, INDEX | Timestamp de lectura |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW(), INDEX | Fecha de creación |

**Índices:**
```sql
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read_at) WHERE read_at IS NULL;
CREATE INDEX idx_notifications_resource ON notifications(resource_id) WHERE resource_id IS NOT NULL;
```

**Constraints:**
```sql
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE notifications ADD CONSTRAINT fk_notifications_resource 
FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE;

ALTER TABLE notifications ADD CONSTRAINT fk_notifications_related_user 
FOREIGN KEY (related_user_id) REFERENCES users(id) ON DELETE SET NULL;
```

**Relaciones:**
- `user` (N:1 → users) — destinatario
- `resource` (N:1 → resources) — recurso relacionado
- `related_user` (N:1 → users) — usuario que generó la notificación

**Notas:**
- `read_at`: NULL si no leída, timestamp si leída
- `related_user_id`: Ejemplo: en fork, es el usuario que forkeó
- Índice parcial en `read_at` para queries de notificaciones no leídas (más comunes)

---

### 3.8 ENTIDAD: reports (Opcional MVP)

**Descripción:** Reportes de contenido inapropiado

**Tabla:** `reports`

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL | Identificador único |
| `user_id` | UUID | FK users(id) ON DELETE CASCADE, NOT NULL | Usuario que reporta |
| `resource_id` | UUID | FK resources(id) ON DELETE CASCADE, NOT NULL | Recurso reportado |
| `reason` | VARCHAR(50) | NOT NULL, CHECK(reason IN ('Inappropriate', 'TechnicalError', 'Spam', 'Plagiarism', 'Other')) | Razón del reporte |
| `description` | TEXT | NOT NULL, CHECK(LENGTH(description) <= 500) | Descripción detallada |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'Pending', CHECK(status IN ('Pending', 'Resolved', 'Rejected')) | Estado del reporte |
| `resolved_by_user_id` | UUID | FK users(id) ON DELETE SET NULL, NULL | Admin que resolvió |
| `resolved_at` | TIMESTAMP | NULL | Timestamp de resolución |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW(), INDEX | Fecha de reporte |

**Índices:**
```sql
CREATE INDEX idx_reports_status ON reports(status, created_at DESC);
CREATE INDEX idx_reports_resource ON reports(resource_id);
CREATE INDEX idx_reports_user ON reports(user_id);
```

**Constraints:**
```sql
ALTER TABLE reports ADD CONSTRAINT fk_reports_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE reports ADD CONSTRAINT fk_reports_resource 
FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE;

ALTER TABLE reports ADD CONSTRAINT fk_reports_resolver 
FOREIGN KEY (resolved_by_user_id) REFERENCES users(id) ON DELETE SET NULL;
```

**Relaciones:**
- `user` (N:1 → users) — reportador
- `resource` (N:1 → resources) — recurso reportado
- `resolved_by` (N:1 → users) — admin que resolvió

**Notas:**
- Tabla opcional para MVP (recomendada para habilitar criterio de promoción automática)
- `status`: Pending (nuevo), Resolved (aceptado), Rejected (descartado)

---

## 4. MÉTRICAS AGREGADAS (DESNORMALIZADAS)

### 4.1 Contador de Votos

**Estrategia:** Calcular en tiempo real con query

```sql
-- No agregar columna votes_count en resources
-- Calcular dinámicamente:
SELECT COUNT(*) FROM votes WHERE resource_id = :resource_id;
```

**Justificación:** Evita complejidad de mantener contador sincronizado. Performance aceptable con índice en `votes(resource_id)`.

**Alternativa Post-MVP:** Agregar columna `votes_count` en `resources` y actualizar con triggers o signals.

---

### 4.2 Contador de Usos

**Estrategia:** Calcular combinado en Service Layer

```sql
-- Definición de "uso" (según TECH_AUDIT):
-- usos = views + forks + upvotes

-- MVP: Simplificar a:
-- usos_count = forks_count (ya desnormalizado) + votes_count
```

**Post-MVP:** Agregar tabla `resource_views` para trackear visualizaciones.

---

## 5. FULL-TEXT SEARCH

### 5.1 Búsqueda en Título y Descripción

**Estrategia:** PostgreSQL Full-Text Search con tsvector

```sql
-- Crear columna computed para tsvector
ALTER TABLE resource_versions 
ADD COLUMN search_vector tsvector 
GENERATED ALWAYS AS (
  to_tsvector('english', title || ' ' || description)
) STORED;

-- Índice GIN para búsqueda rápida
CREATE INDEX idx_versions_search ON resource_versions USING gin(search_vector);

-- Query de búsqueda:
SELECT * FROM resource_versions 
WHERE search_vector @@ to_tsquery('english', 'protein & folding');
```

**Post-MVP:** Migrar a ElasticSearch para búsqueda más avanzada (typo tolerance, relevance scoring).

---

## 6. ESTRATEGIA DE MIGRACIONES

### 6.1 Herramienta

**Django Migrations** (evolutivo)

### 6.2 Proceso

```bash
# 1. Crear migración
python manage.py makemigrations <app_name>

# 2. Revisar SQL generado
python manage.py sqlmigrate <app_name> <migration_number>

# 3. Aplicar migración
python manage.py migrate

# 4. Rollback si es necesario
python manage.py migrate <app_name> <previous_migration>
```

### 6.3 Migrations Críticas (Orden)

```
1. 0001_initial_users.py          # Crear tabla users
2. 0002_initial_roles.py          # Crear tabla roles + seed data
3. 0003_user_roles.py             # Crear tabla pivot user_roles
4. 0004_initial_resources.py      # Crear tabla resources
5. 0005_initial_versions.py       # Crear tabla resource_versions
6. 0006_initial_votes.py          # Crear tabla votes
7. 0007_initial_notifications.py  # Crear tabla notifications
8. 0008_optional_reports.py       # Crear tabla reports (opcional)
9. 0009_add_indexes.py            # Agregar índices adicionales
10. 0010_add_fts.py               # Agregar full-text search
```

### 6.4 Buenas Prácticas

1. **Reversibles:** Siempre incluir `operations.RunSQL(..., reverse_sql=...)`
2. **Data Migrations:** Separar schema migrations de data migrations
3. **Squash:** Squash migrations después de cada release mayor
4. **Testing:** Ejecutar migrations en staging antes de producción
5. **Backups:** Backup de BD antes de migrations en producción

---

## 7. BACKUP Y RECOVERY

### 7.1 Estrategia de Backups

**Backups Automáticos:**
- **Diarios:** Full backup con pg_dump (retención 30 días)
- **Semanales:** Full backup archivado (retención 6 meses)

**Script de backup:**
```bash
#!/bin/bash
# /scripts/backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
DB_NAME="bioai_hub"

# Full backup con pg_dump
pg_dump -U postgres -h localhost -F c -b -v \
  -f "$BACKUP_DIR/bioai_hub_$DATE.dump" \
  $DB_NAME

# Comprimir
gzip "$BACKUP_DIR/bioai_hub_$DATE.dump"

# Eliminar backups antiguos (>30 días)
find $BACKUP_DIR -name "*.dump.gz" -mtime +30 -delete
```

**Cron job:**
```cron
0 2 * * * /scripts/backup_db.sh >> /var/log/backup_db.log 2>&1
```

### 7.2 Recovery

```bash
# Restaurar desde backup
gunzip bioai_hub_20260216_020000.dump.gz
pg_restore -U postgres -h localhost -d bioai_hub_restored \
  -v bioai_hub_20260216_020000.dump
```

---

## 8. PERFORMANCE TUNING

### 8.1 Connection Pooling

**pgBouncer** (recomendado para producción)

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
bioai_hub = host=localhost port=5432 dbname=bioai_hub

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
```

**Django settings:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bioai_hub',
        'USER': 'postgres',
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '6432',  # pgBouncer port
        'CONN_MAX_AGE': 600,  # 10 min
    }
}
```

### 8.2 Query Optimization

**Django ORM Best Practices:**

```python
# ✅ Bueno: select_related para FKs (1 query con JOIN)
resources = Resource.objects.select_related('owner').all()

# ✅ Bueno: prefetch_related para M2M y reverse FKs
users = User.objects.prefetch_related('roles').all()

# ❌ Malo: N+1 queries
resources = Resource.objects.all()
for resource in resources:
    print(resource.owner.name)  # Query por cada recurso

# ✅ Bueno: Agregaciones en BD
from django.db.models import Count
resources = Resource.objects.annotate(
    votes_count=Count('votes')
).all()
```

### 8.3 Índices Adicionales (si es necesario)

Monitorear queries lentas con:
```sql
-- Queries más lentas
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

Agregar índices según necesidad.

---

## 9. SEGURIDAD DE DATOS

### 9.1 Encriptación

**En reposo:**
- PostgreSQL: Encriptación de disco con LUKS (Linux) o FileVault (macOS)
- Backup files: Encriptados con GPG antes de almacenar

**En tránsito:**
- HTTPS obligatorio (Nginx + Let's Encrypt)
- PostgreSQL SSL connection (production)

### 9.2 Sensitive Data

**Datos sensibles:**
- `users.password_hash`: Nunca exponer en API (exclude en serializers)
- `users.email`: Solo visible para propio usuario o admin

**Django settings:**
```python
# apps/authentication/serializers.py

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password_hash']  # Nunca exponer
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Ocultar email si no es propio perfil o admin
        if request and request.user != instance and not request.user.is_admin:
            data.pop('email', None)
        
        return data
```

---

## 10. TESTING DE MODELO DE DATOS

### 10.1 Tests de Modelo (Unit Tests)

```python
# apps/resources/tests/test_models.py

from django.test import TestCase
from django.db import IntegrityError
from apps.authentication.models import User
from apps.resources.models import Resource, ResourceVersion

class ResourceVersionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', name='Test')
        self.resource = Resource.objects.create(
            owner=self.user,
            source_type='Internal'
        )
    
    def test_unique_version_number(self):
        """No se pueden crear 2 versiones con mismo version_number"""
        ResourceVersion.objects.create(
            resource=self.resource,
            version_number='1.0.0',
            title='Test',
            description='Test'
        )
        
        with self.assertRaises(IntegrityError):
            ResourceVersion.objects.create(
                resource=self.resource,
                version_number='1.0.0',  # Duplicado
                title='Test 2',
                description='Test 2'
            )
    
    def test_version_number_format(self):
        """Version number debe tener formato X.Y.Z"""
        with self.assertRaises(IntegrityError):
            ResourceVersion.objects.create(
                resource=self.resource,
                version_number='invalid',  # Formato inválido
                title='Test',
                description='Test'
            )
```

---

## 11. MÉTRICAS Y MONITORING

### 11.1 Tamaño de Tablas

```sql
-- Tamaño de cada tabla
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 11.2 Crecimiento Esperado (MVP)

| Tabla | Registros Año 1 | Tamaño Estimado |
|---|---|---|
| users | ~50 | <1 MB |
| resources | ~100 | <1 MB |
| resource_versions | ~150 (1.5 versiones/recurso promedio) | ~50 MB (con contenido) |
| votes | ~500 | <1 MB |
| notifications | ~1000 | ~2 MB |
| **TOTAL** | | **~55 MB** |

**Conclusión:** Storage no es problema para MVP. Escalar es viable.

---

## 12. CHANGELOG DEL MODELO

### v1.0 (2026-02-16)
- Modelo inicial con 7 entidades
- Índices optimizados para queries comunes
- Constraints de integridad referencial
- Estrategia de soft delete
- Full-text search en versiones

---

**Documento completado:** 2026-02-16  
**Siguiente artefacto:** ERD (Entity-Relationship Diagram) en Mermaid  
**Ubicación:** `/docs/data/diagrams/er.mmd`
