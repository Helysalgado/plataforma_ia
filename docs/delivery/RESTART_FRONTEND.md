# 🚨 INSTRUCCIONES PARA REINICIAR FRONTEND

## Problema Detectado
El diseño se ve roto porque el frontend container de Docker necesita recompilar después de agregar el nuevo componente `Sidebar.tsx`.

## Solución (ejecutar en tu terminal, fuera de Cursor)

### Opción 1: Reiniciar solo el frontend (más rápido)
```bash
cd "/Users/heladia/Library/CloudStorage/GoogleDrive-heladia@ccg.unam.mx/Mi unidad/github-repos-projects/plataforma_ia"

# Detener frontend
docker-compose stop frontend

# Reconstruir e iniciar frontend
docker-compose up -d --build frontend

# Ver logs en tiempo real (Ctrl+C para salir)
docker-compose logs -f frontend
```

**Espera a ver este mensaje:**
```
frontend  | ✓ Compiled in XXXms
frontend  | ○ Compiling / ...
frontend  | ✓ Compiled / in XXXms
```

### Opción 2: Reiniciar todo (si Opción 1 no funciona)
```bash
cd "/Users/heladia/Library/CloudStorage/GoogleDrive-heladia@ccg.unam.mx/Mi unidad/github-repos-projects/plataforma_ia"

# Detener todo
docker-compose down

# Reconstruir e iniciar
docker-compose up -d --build

# Ver logs
docker-compose logs -f
```

### Opción 3: Limpiar caché de Docker (si persiste el problema)
```bash
cd "/Users/heladia/Library/CloudStorage/GoogleDrive-heladia@ccg.unam.mx/Mi unidad/github-repos-projects/plataforma_ia"

# Limpiar y reconstruir
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d

# Ver logs
docker-compose logs -f frontend
```

## Verificación

Después de reiniciar, abre: **http://localhost:3000**

Deberías ver:
- ✅ Sidebar azul a la izquierda con logo "BioAI Hub"
- ✅ Navbar arriba con search bar
- ✅ Home page con hero section

## Si Aún No Funciona

Revisa los logs para ver errores específicos:
```bash
docker-compose logs frontend --tail 100
```

**Errores comunes:**
1. **"Module not found: Sidebar"** → Ejecutar Opción 3 (rebuild sin caché)
2. **"usePathname is not defined"** → Verificar que `'use client'` está en la primera línea de Sidebar.tsx
3. **Port 3000 already in use** → `lsof -ti:3000 | xargs kill` y reintentar

## ¿Qué Cambió?

**Archivos nuevos:**
- `frontend/components/Sidebar.tsx` ← Nuevo componente

**Archivos modificados:**
- `frontend/app/layout.tsx` ← Importa Sidebar
- `frontend/tailwind.config.js` ← Nuevos colores

**Docker necesita recompilar** porque:
1. Nuevo archivo TypeScript agregado
2. Next.js necesita re-buildear el bundle
3. Caché de node_modules puede estar desactualizado

---

**Tiempo estimado:** 2-3 minutos (Opción 1) o 5-7 minutos (Opción 2)

Una vez que veas el nuevo diseño, ¡avísame! 🎨✨
