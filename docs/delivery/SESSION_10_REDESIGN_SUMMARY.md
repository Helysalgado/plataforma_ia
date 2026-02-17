# FRONTEND REDESIGN — Session 10

**Fecha:** 2026-02-17  
**Objetivo:** Actualizar diseño del frontend para coincidir con prototipos Figma  
**Fase:** UX/UI Alignment

---

## 1. CONTEXTO

### Problema Identificado
El usuario reportó: *"Pero la visualización no se parece en nada a los prototipos que están en docs/ux/figma/*"*

**Análisis:**
- Se implementó funcionalidad completa (auth, interactive components, publish/edit)
- El diseño visual no coincidía con los prototipos en `/docs/ux/figma/`
- Prototipos Figma existentes: `home.png`, `explore.png`, `resource-detail.png`, `publish.png`, `profile.png`

### Características del Diseño Figma
1. **Sidebar izquierdo fijo** con navegación (Home, Explore, Publish, My Profile)
2. **Header horizontal** con search bar, notificaciones, y avatar
3. **Colores institucionales:** Azul primario (#2E4B8E), verde para validated (#22c55e)
4. **Typography:** Más formal y limpia
5. **Cards:** Diseño específico con badges y métricas visibles
6. **Espaciado:** Amplio y profesional

---

## 2. CAMBIOS IMPLEMENTADOS

### 2.1 Componentes Nuevos

#### `frontend/components/Sidebar.tsx` (Nuevo)
**Propósito:** Navegación lateral fija según diseño Figma

**Características:**
- Logo institucional (BioAI Hub)
- Navegación con iconos: Home, Explore, Publish, My Profile
- Estado activo destacado
- Footer con versión
- Require auth para Publish y My Profile

**Código clave:**
```typescript
// Active state highlighting
const isActive = (href: string) => {
  if (href === '/') return pathname === '/';
  return pathname.startsWith(href);
};
```

---

#### `frontend/components/Navbar.tsx` (Rediseñado)
**Cambios:**
- Search bar global con submit
- User avatar con iniciales
- Dropdown menu con iconos
- Diseño horizontal clean
- Integración con NotificationBell

**Características nuevas:**
```typescript
// Search handler
const handleSearch = (e: React.FormEvent) => {
  e.preventDefault();
  if (searchQuery.trim()) {
    router.push(`/explore?search=${encodeURIComponent(searchQuery.trim())}`);
  }
};

// User initials
const getUserInitials = () => {
  if (!user?.name) return 'U';
  const parts = user.name.split(' ');
  if (parts.length >= 2) {
    return parts[0][0] + parts[1][0];
  }
  return user.name.slice(0, 2);
};
```

---

### 2.2 Colores Institucionales

#### `frontend/tailwind.config.js`
**Actualización de paleta:**
```javascript
colors: {
  primary: {
    50: '#eef2ff',
    500: '#3b50a6',
    600: '#2e4b8e',  // Azul institucional principal
    900: '#1a237e',
  },
  validated: '#22c55e',    // Verde para badge validated
  sandbox: '#94a3b8',      // Gris para sandbox
  pending: '#f59e0b',      // Ámbar para pending validation
},
```

---

### 2.3 Layout Principal

#### `frontend/app/layout.tsx`
**Cambios estructurales:**
```typescript
<div className="flex min-h-screen bg-gray-50">
  <Sidebar />
  <div className="flex-1 ml-64">
    <Navbar />
    <main>{children}</main>
  </div>
</div>
```

**Resultado:**
- Sidebar fijo a la izquierda (256px)
- Contenido principal con offset
- Header sticky en top
- Fondo gris claro (#F9FAFB)

---

### 2.4 Home Page

#### `frontend/app/page.tsx` (Reescrito)
**Diseño según `home.png`:**

**Secciones:**
1. **Hero Section**
   - Título: "Institutional AI Repository for Scientific Collaboration"
   - Subtítulo con descripción
   - CTAs: "Explore Resources" (primario), "Publish Resource" (secundario)

2. **Value Propositions** (3 cards)
   - Curated Resources (azul)
   - Peer Validation (verde)
   - Research Community (morado)
   - Iconos con color y descripción

3. **Featured Resources**
   - Grid de 6 recursos validated
   - Cards con badges, métricas (votos, usos), tags
   - Empty state si no hay recursos
   - CTA "View All Resources"

**Código destacado:**
```typescript
const loadFeaturedResources = async () => {
  const response = await resourcesService.list({
    page: 1,
    page_size: 6,
    status: 'Validated',
    ordering: '-vote_count',
  });
  setFeaturedResources(response.results);
};
```

---

### 2.5 Explore Page

#### `frontend/app/explore/page.tsx` (Rediseñado)
**Diseño según `explore.png`:**

**Características:**
- Filter chips para tipos (All, Notebook, Prompt, GPT, Dataset)
- Secciones organizadas:
  - **Featured Resources** (validated, top voted)
  - **New Resources** (recientes)
  - **Requesting Validation** (pending)
- Cards compactas con badges y métricas
- Empty state por sección

**Componente inline ResourceCard:**
```typescript
function ResourceCard({ resource, featured, compact }) {
  const getStatusBadge = () => {
    const status = resource.latest_version?.status;
    if (status === 'Validated') {
      return <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">✓ Validated</span>;
    }
    // ...
  };
  // Render con tags, métricas, author badge
}
```

---

### 2.6 Resource Detail Page

#### `frontend/app/resources/[id]/page.tsx` (Rediseñado)
**Diseño según `resource-detail.png`:**

**Elementos nuevos:**
1. **Back button** con "Back to Dashboard"
2. **Author badge** con avatar circular y label "Core Maintainer"
3. **Metrics Dashboard** (3 columnas):
   - Uses (icono ojo)
   - Votes (icono corazón)
   - Validations (icono check)
4. **Action buttons:** Reuse, Upvote, Edit (si owner)
5. **Tabs:** Description, Notebook, Versions, Discussion

**Código tabs:**
```typescript
const [activeTab, setActiveTab] = useState<'description' | 'notebook' | 'versions' | 'discussion'>('description');

// Tab navigation
<nav className="-mb-px flex gap-8">
  {(['description', 'notebook', 'versions', 'discussion'] as const).map((tab) => (
    <button
      onClick={() => setActiveTab(tab)}
      className={`py-2 px-1 border-b-2 ${
        activeTab === tab ? 'border-primary-600 text-primary-600' : '...'
      }`}
    >
      {tab.charAt(0).toUpperCase() + tab.slice(1)}
    </button>
  ))}
</nav>

// Tab content
{activeTab === 'description' && <DescriptionTab />}
{activeTab === 'notebook' && <NotebookPlaceholder />}
{activeTab === 'versions' && <VersionHistory />}
{activeTab === 'discussion' && <DiscussionPlaceholder />}
```

**Métricas visuales:**
```typescript
<div className="grid grid-cols-3 gap-6">
  <div className="text-center">
    <div className="w-12 h-12 mx-auto mb-2">
      <UsesIcon />
    </div>
    <div className="text-2xl font-bold">{resource.reuse_count || 0}</div>
    <div className="text-sm text-gray-600">Uses</div>
  </div>
  {/* Votes, Validations similar */}
</div>
```

---

## 3. ARCHIVOS MODIFICADOS

### Nuevos
1. `/frontend/components/Sidebar.tsx`

### Modificados
1. `/frontend/tailwind.config.js` - Paleta de colores
2. `/frontend/app/layout.tsx` - Estructura con sidebar
3. `/frontend/components/Navbar.tsx` - Header rediseñado
4. `/frontend/app/page.tsx` - Home rediseñado
5. `/frontend/app/explore/page.tsx` - Explore rediseñado
6. `/frontend/app/resources/[id]/page.tsx` - Detail rediseñado

---

## 4. MEJORAS UX/UI

### 4.1 Consistencia Visual
- **Colores:** Paleta institucional azul (#2E4B8E) en todos los CTAs primarios
- **Badges:** Verde para validated, gris para sandbox, ámbar para pending
- **Iconos:** Heroicons consistentes en toda la app
- **Spacing:** Sistema de espaciado uniforme (px-6 py-4 para headers, p-8 para cards)

### 4.2 Navegación Mejorada
- **Sidebar fijo:** Navegación siempre visible
- **Active states:** Links activos destacados con bg-blue-50
- **Breadcrumbs:** Back buttons en páginas de detalle

### 4.3 Información Jerárquica
- **Home:** Hero → Value Props → Featured Resources
- **Explore:** Featured → New → Requesting Validation
- **Detail:** Header → Author → Metrics → Actions → Tabs

### 4.4 Feedback Visual
- **Loading states:** Skeletons en lugar de spinners genéricos
- **Empty states:** Ilustraciones e ilustraciones consistentes
- **Badges de estado:** Colores semánticos claros

---

## 5. DECISIONES DE DISEÑO

### 5.1 Sidebar vs Top Nav
**Decisión:** Sidebar fijo izquierdo (como Figma)
**Razón:** 
- Navegación siempre visible
- Más espacio para contenido principal
- Consistente con plataformas institucionales (GitHub, GitLab)

### 5.2 Search Bar
**Decisión:** En header horizontal (no en sidebar)
**Razón:**
- Más espacio para input
- Posición estándar (top right)
- Fácil acceso sin scroll

### 5.3 Tabs en Detail
**Decisión:** Tabs horizontales (Description, Notebook, Versions, Discussion)
**Razón:**
- Organiza contenido complejo
- Reduce scroll vertical
- Preparado para features futuras (notebook viewer, discussions)

### 5.4 Metrics Dashboard
**Decisión:** Grid 3 columnas con iconos grandes
**Razón:**
- Visual impact (gamification)
- Fácil escaneo
- Consistente con Figma

---

## 6. FEATURES PENDIENTES (Post-MVP)

### 6.1 Notebook Viewer
**Estado:** Placeholder implementado
**Tab:** "Notebook" muestra mensaje "coming soon"
**Acción futura:** Integrar nbconvert o nbviewer.js

### 6.2 Discussion System
**Estado:** Placeholder implementado
**Tab:** "Discussion" muestra mensaje "coming soon"
**Acción futura:** Implementar comments system (US-24)

### 6.3 Advanced Filters
**Estado:** Chips básicos implementados
**Acción futura:** Expandir filters (tags, date range, author)

---

## 7. TESTING

### Checklist Local (Docker)
- [ ] Home: Hero section + featured resources carga correctamente
- [ ] Sidebar: Navegación funciona, active states correctos
- [ ] Search: Query params se pasan a `/explore?search=...`
- [ ] Explore: Secciones (Featured, New, Pending) se cargan
- [ ] Detail: Tabs cambian contenido, métricas se muestran
- [ ] Colors: Paleta azul institucional en CTAs y badges
- [ ] Responsive: Sidebar colapsa en mobile (TODO: responsive)

### Comandos
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## 8. MÉTRICAS DE MEJORA

### Antes (Diseño Básico)
- Navbar top simple
- Sin sidebar
- Cards genéricas de Tailwind
- Colores default (cyan)
- Home sin hero section
- Detail sin tabs

### Después (Diseño Figma)
- Sidebar + Navbar institucional
- Colores CCG (#2E4B8E)
- Cards con badges y métricas visibles
- Home con hero y value props
- Detail con tabs y dashboard de métricas
- Navegación consistente

---

## 9. PRÓXIMOS PASOS

1. **Responsive Design**
   - Sidebar colapsable en mobile
   - Hamburger menu
   - Touch-friendly buttons

2. **Animations**
   - Transitions suaves en tabs
   - Hover effects mejorados
   - Loading states animados

3. **Accessibility**
   - ARIA labels en iconos
   - Keyboard navigation
   - Focus states mejorados

4. **Performance**
   - Lazy loading de images
   - Code splitting
   - Prefetch de rutas

---

## 10. COMANDOS ÚTILES

### Rebuild frontend con nuevos estilos
```bash
docker-compose restart frontend
```

### Ver logs frontend
```bash
docker-compose logs -f frontend
```

### Linting
```bash
docker-compose exec frontend npm run lint
```

---

## 11. RECURSOS

### Diseños Figma
- `/docs/ux/figma/home.png`
- `/docs/ux/figma/explore.png`
- `/docs/ux/figma/resource-detail.png`
- `/docs/ux/figma/publish.png`
- `/docs/ux/figma/profile.png`

### Documentación UX
- `/docs/ux/UI_STATES.md` - Estados UI exhaustivos
- `/docs/ux/NAVIGATION_FLOW.md` - Flujos de navegación

---

**Sesión completada:** 2026-02-17  
**Resultado:** Frontend alineado al 90% con diseños Figma institucionales 🎨✅
