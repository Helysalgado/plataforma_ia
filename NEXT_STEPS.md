# Next Steps - Plataforma CCG IA

**Última actualización**: 2026-02-17  
**Estado actual**: MVP Core completado, Profile Page funcionando  
**Próxima sesión**: Completar funcionalidades pendientes y preparar para producción

---

## 📊 Estado Actual del Proyecto

### ✅ Completado (MVP Core)

#### Backend
- [x] Autenticación y autorización (JWT)
- [x] CRUD de recursos con versionado
- [x] Sistema de votos
- [x] Sistema de forks/derivaciones
- [x] Notificaciones básicas
- [x] Endpoints de perfil de usuario (`/api/users/:id/`, `/api/users/:id/resources/`)
- [x] Validación de recursos (backend)

#### Frontend
- [x] Diseño completo según Figma
- [x] Home page con hero y featured resources
- [x] Explore page con filtros y secciones
- [x] Resource detail page con tabs
- [x] Publish page (formulario de publicación)
- [x] Profile page con métricas y recursos
- [x] Sidebar navigation
- [x] Navbar con search y user menu
- [x] Sistema de notificaciones (UI)

#### Infraestructura
- [x] Docker Compose para desarrollo
- [x] PostgreSQL configurado
- [x] Hot reload en frontend y backend
- [x] Variables de entorno

---

## 🎯 Prioridades para Próxima Sesión

### Opción A: Completar Funcionalidades Core ⭐ (Recomendado)

#### 1. Admin Validation UI (Alta Prioridad)
**Objetivo**: Permitir a admins validar/rechazar recursos desde el frontend

**Backend** (ya existe):
- ✅ Endpoint: `POST /api/resources/:id/validate/`
- ✅ Permisos: Solo admins

**Frontend** (pendiente):
- [ ] Crear página `/admin/validation`
- [ ] Lista de recursos pendientes de validación
- [ ] Botones "Approve" / "Reject" por recurso
- [ ] Modal de confirmación con razón de rechazo
- [ ] Notificación al owner cuando se valida/rechaza

**Archivos a crear/modificar**:
```
frontend/app/admin/validation/page.tsx (nuevo)
frontend/services/resources.ts (agregar método validateResource)
```

**Estimación**: 2-3 horas

---

#### 2. Responsive Design (Media Prioridad)
**Objetivo**: Hacer la plataforma usable en móviles y tablets

**Pendiente**:
- [ ] Sidebar colapsable en móviles
- [ ] Hamburger menu
- [ ] Ajustar grids de recursos (3 cols → 2 cols → 1 col)
- [ ] Ajustar navbar para móviles
- [ ] Probar en diferentes tamaños de pantalla

**Archivos a modificar**:
```
frontend/components/Sidebar.tsx
frontend/components/Navbar.tsx
frontend/app/*/page.tsx (ajustar grids)
```

**Breakpoints a usar**:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

**Estimación**: 3-4 horas

---

#### 3. Notebook Viewer Integration (Media Prioridad)
**Objetivo**: Visualizar notebooks directamente en la plataforma

**Opciones**:
- **Opción A**: Usar `@nteract/notebook-render` (React component)
- **Opción B**: Usar iframe con nbviewer
- **Opción C**: Renderizar con backend (nbconvert)

**Recomendación**: Opción A (más control, mejor UX)

**Pendiente**:
- [ ] Instalar dependencia: `npm install @nteract/notebook-render`
- [ ] Crear componente `NotebookViewer.tsx`
- [ ] Integrar en tab "Notebook" de resource detail
- [ ] Manejar errores de renderizado
- [ ] Agregar loading state

**Archivos a crear/modificar**:
```
frontend/components/NotebookViewer.tsx (nuevo)
frontend/app/resources/[id]/page.tsx (modificar tab Notebook)
```

**Estimación**: 2-3 horas

---

#### 4. Discussion/Comments System (Baja Prioridad)
**Objetivo**: Permitir comentarios en recursos

**Backend** (pendiente):
- [ ] Modelo `Comment` (user, resource, content, parent_comment)
- [ ] Endpoints:
  - `GET /api/resources/:id/comments/`
  - `POST /api/resources/:id/comments/`
  - `DELETE /api/comments/:id/`
- [ ] Notificaciones cuando alguien comenta

**Frontend** (pendiente):
- [ ] Componente `CommentList.tsx`
- [ ] Componente `CommentForm.tsx`
- [ ] Integrar en tab "Discussion" de resource detail
- [ ] Soporte para respuestas (threading)

**Estimación**: 6-8 horas

---

### Opción B: Testing y Calidad 🧪

#### 1. E2E Tests Completos
**Objetivo**: Cubrir todos los flujos principales con tests automatizados

**Pendiente**:
- [ ] Test: Profile page (ver métricas, recursos publicados)
- [ ] Test: Admin validation flow
- [ ] Test: Fork de recurso
- [ ] Test: Notificaciones
- [ ] Test: Search functionality
- [ ] Actualizar tests existentes con nuevos selectores

**Archivos**:
```
frontend/e2e/tests/profile.spec.ts (nuevo)
frontend/e2e/tests/admin-validation.spec.ts (nuevo)
frontend/e2e/tests/fork-resource.spec.ts (nuevo)
frontend/e2e/tests/basic-flow.spec.ts (actualizar)
```

**Estimación**: 4-6 horas

---

#### 2. Unit Tests Backend
**Objetivo**: Aumentar cobertura de tests unitarios

**Pendiente**:
- [ ] Tests para `views_users.py` (nuevos endpoints)
- [ ] Tests para cálculo de métricas
- [ ] Tests para filtrado por status
- [ ] Tests de edge cases (usuario sin recursos, etc.)

**Archivos**:
```
backend/apps/authentication/tests/test_views_users.py (nuevo)
```

**Estimación**: 3-4 horas

---

#### 3. Linter y Code Quality
**Objetivo**: Asegurar calidad y consistencia del código

**Pendiente**:
- [ ] Configurar ESLint rules más estrictas
- [ ] Configurar Prettier
- [ ] Agregar pre-commit hooks (husky)
- [ ] Corregir warnings existentes
- [ ] Agregar type checking estricto (TypeScript)

**Estimación**: 2-3 horas

---

### Opción C: Mejoras de UX/UI ✨

#### 1. Profile Page Enhancements
**Objetivo**: Mejorar la página de perfil con más información

**Pendiente**:
- [ ] Agregar tabs: "Resources" / "Activity" / "Stats"
- [ ] Tab Activity: mostrar historial (votos dados, recursos publicados, etc.)
- [ ] Tab Stats: gráficas de actividad (Chart.js o Recharts)
- [ ] Botón "Edit Profile" (solo en propio perfil)
- [ ] Modal de edición de perfil (nombre, bio, avatar)
- [ ] Badges/achievements del usuario

**Archivos a modificar**:
```
frontend/app/profile/[[...id]]/page.tsx
frontend/components/ProfileTabs.tsx (nuevo)
frontend/components/EditProfileModal.tsx (nuevo)
```

**Estimación**: 4-5 horas

---

#### 2. Advanced Search
**Objetivo**: Mejorar el buscador con filtros avanzados

**Pendiente**:
- [ ] Página dedicada de búsqueda `/search`
- [ ] Filtros: tipo, status, tags, autor, fecha
- [ ] Ordenamiento: relevancia, fecha, votos
- [ ] Búsqueda en tiempo real (debounced)
- [ ] Historial de búsquedas
- [ ] Sugerencias de búsqueda

**Backend** (pendiente):
- [ ] Endpoint de búsqueda avanzada
- [ ] Full-text search (PostgreSQL)
- [ ] Índices de búsqueda

**Estimación**: 6-8 horas

---

#### 3. Loading States & Animations
**Objetivo**: Mejorar la percepción de velocidad y fluidez

**Pendiente**:
- [ ] Skeleton loaders para todas las páginas
- [ ] Transiciones suaves entre páginas
- [ ] Animaciones de hover mejoradas
- [ ] Progress indicators para acciones largas
- [ ] Optimistic UI updates (votar sin esperar respuesta)

**Estimación**: 3-4 horas

---

### Opción D: Deploy y Producción 🚀

#### 1. Preparación para Deploy
**Objetivo**: Configurar entornos de staging y producción

**Pendiente**:
- [ ] Dockerfile optimizado para producción
- [ ] docker-compose.prod.yml
- [ ] Configuración de NGINX como reverse proxy
- [ ] SSL/TLS certificates (Let's Encrypt)
- [ ] Variables de entorno de producción
- [ ] Secrets management (AWS Secrets Manager o similar)

**Estimación**: 4-6 horas

---

#### 2. CI/CD Pipeline
**Objetivo**: Automatizar testing y deploy

**Pendiente**:
- [ ] GitHub Actions workflow
- [ ] Stages: lint → test → build → deploy
- [ ] Deploy automático a staging en push a `main`
- [ ] Deploy manual a producción (con aprobación)
- [ ] Notificaciones de deploy (Slack/Discord)

**Archivos**:
```
.github/workflows/ci.yml (nuevo)
.github/workflows/deploy-staging.yml (nuevo)
.github/workflows/deploy-production.yml (nuevo)
```

**Estimación**: 4-5 horas

---

#### 3. Monitoring y Observability
**Objetivo**: Monitorear la aplicación en producción

**Pendiente**:
- [ ] Logging estructurado (JSON logs)
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (New Relic o similar)
- [ ] Health check endpoints
- [ ] Métricas de negocio (recursos publicados, usuarios activos, etc.)

**Estimación**: 3-4 horas

---

## 🐛 Bugs Conocidos

### Críticos
Ninguno conocido actualmente ✅

### Menores
1. **Notificaciones no se marcan como leídas**: El endpoint existe pero falta integrar en frontend
2. **Search bar no funciona**: Solo es UI, falta implementar búsqueda
3. **Tabs "Notebook" y "Discussion" vacíos**: Placeholders, pendiente implementación

---

## 🔧 Deuda Técnica

### Performance
1. **Filtrado por status en Python**: En `UserResourcesView`, se filtra en memoria. Para producción, considerar denormalizar `latest_version_id`.
2. **N+1 queries en algunos endpoints**: Revisar con Django Debug Toolbar.
3. **Sin caché**: Considerar Redis para cachear recursos populares.

### Seguridad
1. **Rate limiting**: Agregar throttling en endpoints públicos.
2. **Input sanitization**: Revisar que todos los inputs estén sanitizados.
3. **CORS**: Configurar correctamente para producción.

### Código
1. **Duplicación de lógica**: Algunos componentes tienen lógica similar (ResourceCard).
2. **Types incompletos**: Algunos tipos de TypeScript son `any`.
3. **Error handling inconsistente**: Estandarizar manejo de errores.

---

## 📚 Documentación Pendiente

### Técnica
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Architecture Decision Records (ADRs) actualizados
- [ ] Database schema diagram actualizado
- [ ] Deployment guide

### Usuario
- [ ] User manual (cómo usar la plataforma)
- [ ] Admin guide (cómo validar recursos)
- [ ] FAQ
- [ ] Video tutorials

---

## 🎓 Mejoras Futuras (Post-MVP)

### Funcionalidades
1. **Integración con GitHub**: Sincronizar recursos con repos
2. **CI/CD para recursos**: Validación automática con tests
3. **Versioning avanzado**: Comparar versiones, rollback
4. **Colaboración**: Múltiples autores por recurso
5. **Collections**: Agrupar recursos relacionados
6. **Recomendaciones**: Sistema de recomendación basado en ML
7. **Analytics**: Dashboard de métricas para admins
8. **API pública**: Permitir acceso programático

### Integraciones
1. **OAuth**: Login con Google, GitHub, ORCID
2. **Jupyter Hub**: Ejecutar notebooks directamente
3. **DOI**: Asignar DOIs a recursos validados
4. **Zenodo**: Backup automático en Zenodo

---

## 📋 Checklist para Próxima Sesión

### Antes de empezar:
- [ ] Revisar este documento completo
- [ ] Decidir qué opción seguir (A, B, C, o D)
- [ ] Verificar que el entorno local funcione
- [ ] Hacer pull de los últimos cambios
- [ ] Revisar issues en GitHub (si existen)

### Durante la sesión:
- [ ] Crear TODOs específicos para las tareas elegidas
- [ ] Implementar funcionalidades una por una
- [ ] Probar cada funcionalidad antes de continuar
- [ ] Documentar decisiones importantes
- [ ] Actualizar tests si es necesario

### Al finalizar:
- [ ] Actualizar este documento con progreso
- [ ] Actualizar AI_USAGE_LOG.md
- [ ] Commit y push de cambios
- [ ] Crear summary de la sesión

---

## 🎯 Recomendación para Próxima Sesión

**Sugerencia**: Seguir **Opción A** (Completar Funcionalidades Core)

**Razón**: 
1. Admin Validation UI es crítico para el flujo completo
2. Responsive design es importante para usabilidad
3. Estas funcionalidades completan el MVP de manera sólida
4. Después se puede pasar a testing (Opción B) antes de deploy

**Plan sugerido** (6-8 horas):
1. Admin Validation UI (2-3h)
2. Responsive Design (3-4h)
3. E2E Tests básicos (1-2h)
4. Documentación y push

---

## 📞 Contacto y Recursos

### Documentación del Proyecto
- `AGENTS.md` - Flujo de trabajo y convenciones
- `README.md` - Setup y comandos básicos
- `/docs/architecture/` - Arquitectura y ADRs
- `/docs/product/` - Épicas e historias de usuario
- `/docs/delivery/` - Summaries de sesiones

### Recursos Externos
- [Next.js Docs](https://nextjs.org/docs)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Playwright Testing](https://playwright.dev/)

---

**Documento vivo**: Actualizar después de cada sesión  
**Última revisión**: 2026-02-17  
**Próxima revisión**: Al inicio de la siguiente sesión
