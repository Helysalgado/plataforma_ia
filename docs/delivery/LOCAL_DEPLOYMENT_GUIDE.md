# 🚀 DEPLOYMENT LOCAL - Guía Rápida

**Estado:** Commits pusheados exitosamente a GitHub ✅

---

## ✅ PASO 1: VERIFICAR CI EN GITHUB

Abre en tu navegador:
```
https://github.com/Helysalgado/plataforma_ia/actions
```

**Deberías ver:**
- ✅ Workflow "CI - Lint and Test" ejecutándose
- Jobs: backend-lint-test, frontend-lint-test, docker-build

**Tiempo estimado:** 5-10 minutos

---

## 🐳 PASO 2: INICIAR SERVICIOS LOCALES

### 2.1 Verificar Docker Desktop
```bash
# Asegúrate que Docker Desktop está corriendo
docker ps
```

### 2.2 Crear archivo .env
```bash
cd /Users/heladia/Library/CloudStorage/GoogleDrive-heladia@ccg.unam.mx/Mi\ unidad/github-repos-projects/plataforma_ia

# Copiar .env.example
cp .env.example .env

# Editar valores básicos (puedes usar valores de desarrollo)
nano .env
```

**Valores mínimos requeridos en `.env`:**
```bash
# General
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://bioai:bioai123@db:5432/bioai_dev
POSTGRES_DB=bioai_dev
POSTGRES_USER=bioai
POSTGRES_PASSWORD=bioai123

# Email (opcional para testing local)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# JWT
JWT_SECRET_KEY=dev-jwt-secret-key
```

### 2.3 Levantar servicios
```bash
# Build e iniciar todos los servicios
docker-compose up -d --build

# Ver logs (Ctrl+C para salir)
docker-compose logs -f
```

**Servicios que deben iniciar:**
- ✅ db (PostgreSQL)
- ✅ backend (Django)
- ✅ frontend (Next.js)

### 2.4 Ejecutar migraciones
```bash
# Esperar 30 segundos a que DB esté lista, luego:
docker-compose exec backend python manage.py migrate
```

### 2.5 Crear superusuario
```bash
docker-compose exec backend python manage.py createsuperuser

# Ingresar:
Email: admin@test.com
Name: Admin Local
Password: admin123 (o el que prefieras)
```

### 2.6 Verificar servicios
```bash
# Ver estado de contenedores
docker-compose ps

# Deberían estar "healthy" o "running"
```

---

## 🧪 PASO 3: TESTING LOCAL

### 3.1 Acceder a la aplicación

Abre en tu navegador:

- **Frontend:** http://localhost:3000
- **Backend Admin:** http://localhost:8000/admin
- **API Explorer:** http://localhost:8000/api/

### 3.2 Checklist de Testing

#### ✅ Backend
```
☐ Acceder a /admin con superusuario
☐ Verificar que cargan los modelos
☐ Crear recurso de prueba desde admin
```

#### ✅ Frontend - Flujo Completo
```
☐ Landing page carga correctamente
☐ Click "Explorar" → Ver catálogo
☐ Click "Registrarse"
☐ Llenar formulario de registro
   - Email: test@test.com
   - Nombre: Usuario Test
   - Password: Test123!
   - Confirmar password
☐ Ver mensaje de éxito (verificar email)
☐ Click "Ir a iniciar sesión"
☐ Login con test@test.com / Test123!
☐ Navegar a /explore
☐ Ver recursos (si hay alguno creado en admin)
☐ Click en un recurso → Ver detalle
☐ Click "Votar" → Ver toast de éxito
☐ Click "Reutilizar" → Ver modal de confirmación
☐ Click "Publicar" en navbar
☐ Llenar formulario de publicación
   - Título: "Test Resource Local"
   - Descripción: "Testing deployment local"
   - Tipo: Prompt
   - Tags: test, local
   - Content: "Test content"
☐ Publicar → Redirige a detalle
☐ Click "Editar" → Modificar descripción
☐ Guardar cambios → Ver toast de éxito
☐ Click campana de notificaciones → Ver dropdown
☐ Click en tu nombre → Ver menú usuario
☐ Click "Cerrar sesión" → Redirect a home
```

### 3.3 Verificar Logs
```bash
# Si algo falla, revisar logs:
docker-compose logs backend | tail -100
docker-compose logs frontend | tail -100
docker-compose logs db | tail -100
```

---

## 🐛 TROUBLESHOOTING

### Problema: Contenedor no inicia
```bash
# Ver logs detallados
docker-compose logs [servicio]

# Reintentar
docker-compose restart [servicio]

# Rebuild si cambió código
docker-compose up -d --build [servicio]
```

### Problema: Error de conexión a DB
```bash
# Verificar que DB esté healthy
docker-compose ps

# Si no está ready, esperar 30 segundos más
sleep 30

# Reintentar migraciones
docker-compose exec backend python manage.py migrate
```

### Problema: Frontend no conecta a backend
```bash
# Verificar NEXT_PUBLIC_API_URL en .env
cat .env | grep NEXT_PUBLIC_API_URL

# Debe ser: http://localhost:8000/api

# Rebuild frontend
docker-compose up -d --build frontend
```

### Problema: Email verification
```bash
# En desarrollo, los emails se imprimen en logs
docker-compose logs backend | grep "verification"

# Copiar el token del link y usarlo manualmente
```

---

## 📊 VERIFICACIÓN FINAL

Si todo funciona correctamente, deberías tener:

✅ **GitHub Actions:** CI pasando (verde)  
✅ **Local - Backend:** http://localhost:8000/admin accesible  
✅ **Local - Frontend:** http://localhost:3000 accesible  
✅ **Local - Tests:** Todos los flujos funcionando  
✅ **Demo Ready:** Puedes mostrar la app funcionando  

---

## 🎯 PRÓXIMOS PASOS

### Mientras esperas DNS (2-5 días):

1. **Demo para stakeholders**
   - Mostrar app funcionando en localhost
   - Explicar features implementadas
   - Recibir feedback

2. **Solicitar DNS a IT** (si no lo hiciste)
   - Ver template en: `docs/delivery/DNS_AND_DEPLOYMENT_TODO.md`

3. **Monitorear CI/CD**
   - Cada push ejecutará tests automáticamente
   - Familiarizarse con GitHub Actions

4. **Fix issues** (si encuentras alguno)
   - Hacer cambios
   - Commit + push
   - Ver CI pasar
   - Re-deploy local

### Cuando DNS esté listo:

5. **Deploy a producción** (2 horas)
   - Seguir: `docs/delivery/DEPLOYMENT_GUIDE.md`
   - Setup SSL con script
   - Deploy con docker-compose.prod.yml
   - Testing en producción

---

## 🆘 AYUDA

Si algo no funciona:

1. **Ver logs:** `docker-compose logs -f`
2. **Revisar .env:** Verificar todas las variables
3. **Reiniciar todo:** `docker-compose down && docker-compose up -d --build`
4. **GitHub Issues:** Crear issue con logs y error

---

## ✅ CHECKLIST RÁPIDO

```bash
# 1. Verificar GitHub Actions
# https://github.com/Helysalgado/plataforma_ia/actions

# 2. Crear .env
cp .env.example .env
nano .env  # Configurar valores mínimos

# 3. Levantar servicios
docker-compose up -d --build

# 4. Migraciones
docker-compose exec backend python manage.py migrate

# 5. Superusuario
docker-compose exec backend python manage.py createsuperuser

# 6. Acceder
# http://localhost:3000

# 7. Testing completo
# Seguir checklist arriba

# 8. Demo para equipo
# Mostrar funcionando en localhost
```

---

**Última actualización:** 2026-02-17  
**Estado:** Listo para deploy local  
**CI Status:** https://github.com/Helysalgado/plataforma_ia/actions
