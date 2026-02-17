# Guía Rápida de Despliegue - Servicios Cloud

**Objetivo**: Desplegar BioAI Hub en 30 minutos usando servicios cloud  
**Dificultad**: Fácil  
**Costo**: ~$10-15/mes (o gratis con limitaciones)

---

## 🚀 Opción Más Rápida: Railway + Vercel

Esta es la forma **más rápida** de tener tu app en producción.

### Arquitectura

```
Frontend (Vercel) ──────> Backend (Railway) ──────> PostgreSQL (Railway)
     ↓                          ↓
  Next.js                  Django + DRF
  (gratis)                 ($10/mes)
```

---

## 📦 Paso 1: Desplegar Backend en Railway

### 1.1 Crear Cuenta

1. Ve a: https://railway.app/
2. Regístrate con GitHub
3. Conecta tu cuenta de GitHub

### 1.2 Crear Proyecto

1. Click en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Busca: `Helysalgado/plataforma_ia`
4. Autoriza acceso

### 1.3 Configurar Backend

1. Railway detectará automáticamente Django
2. **Agregar PostgreSQL**:
   - Click en "+ New"
   - Selecciona "Database" → "PostgreSQL"
   - Railway creará la BD automáticamente

3. **Configurar Variables de Entorno**:
   - Click en el servicio Backend
   - Ve a "Variables"
   - Agrega:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=genera-un-secret-key-seguro-aqui
DEBUG=False
ALLOWED_HOSTS=*.railway.app,bioai.ccg.unam.mx
DATABASE_URL=${{Postgres.DATABASE_URL}}
JWT_SECRET_KEY=otro-secret-key-diferente
CORS_ALLOWED_ORIGINS=https://tu-app.vercel.app
```

4. **Configurar Build**:
   - Root Directory: `/backend`
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

5. **Deploy**:
   - Railway desplegará automáticamente
   - Obtendrás una URL: `https://tu-backend.railway.app`

### 1.4 Ejecutar Migraciones

1. En Railway, ve a tu servicio Backend
2. Click en "Settings" → "Deploy"
3. En la terminal (o usando Railway CLI):

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link al proyecto
railway link

# Ejecutar migraciones
railway run python manage.py migrate

# Crear superusuario
railway run python manage.py createsuperuser

# Seed roles
railway run python manage.py seed_roles
```

---

## 🎨 Paso 2: Desplegar Frontend en Vercel

### 2.1 Crear Cuenta

1. Ve a: https://vercel.com/
2. Regístrate con GitHub
3. Conecta tu cuenta de GitHub

### 2.2 Importar Proyecto

1. Click en "Add New..." → "Project"
2. Selecciona: `Helysalgado/plataforma_ia`
3. Autoriza acceso

### 2.3 Configurar Frontend

1. **Framework Preset**: Next.js (detectado automáticamente)

2. **Root Directory**: `frontend`

3. **Build Command**: `npm run build`

4. **Output Directory**: `.next`

5. **Install Command**: `npm install`

6. **Environment Variables**:
   ```env
   NEXT_PUBLIC_API_URL=https://tu-backend.railway.app/api
   NEXT_PUBLIC_SITE_URL=https://tu-app.vercel.app
   ```

7. **Deploy**:
   - Click en "Deploy"
   - Vercel construirá y desplegará automáticamente
   - Obtendrás una URL: `https://tu-app.vercel.app`

---

## 🔗 Paso 3: Conectar Frontend y Backend

### 3.1 Actualizar CORS en Backend

En Railway, actualiza la variable de entorno:

```env
CORS_ALLOWED_ORIGINS=https://tu-app.vercel.app
```

Redeploy el backend.

### 3.2 Verificar Conexión

1. Abre: `https://tu-app.vercel.app`
2. Intenta registrarte
3. Verifica que la API responda

---

## 🌐 Paso 4: Dominio Personalizado (Opcional)

### En Vercel (Frontend)

1. Ve a tu proyecto en Vercel
2. Click en "Settings" → "Domains"
3. Agrega: `bioai.ccg.unam.mx`
4. Vercel te dará instrucciones DNS:
   ```
   Type: CNAME
   Name: bioai
   Value: cname.vercel-dns.com
   ```

### En Railway (Backend)

1. Ve a tu servicio Backend
2. Click en "Settings" → "Networking"
3. Agrega dominio custom: `api.bioai.ccg.unam.mx`
4. Railway te dará instrucciones DNS:
   ```
   Type: CNAME
   Name: api.bioai
   Value: tu-backend.railway.app
   ```

### Actualizar Variables de Entorno

**Backend** (Railway):
```env
CORS_ALLOWED_ORIGINS=https://bioai.ccg.unam.mx
ALLOWED_HOSTS=api.bioai.ccg.unam.mx,*.railway.app
```

**Frontend** (Vercel):
```env
NEXT_PUBLIC_API_URL=https://api.bioai.ccg.unam.mx/api
NEXT_PUBLIC_SITE_URL=https://bioai.ccg.unam.mx
```

---

## ⚡ Alternativa Ultra-Rápida: Render

### Opción Todo-en-Uno en Render

**Render** puede desplegar todo desde un solo lugar:

1. **Crear cuenta**: https://render.com/
2. **Conectar GitHub**: Autoriza acceso al repo
3. **Crear servicios**:

#### Backend (Web Service)
```yaml
Name: bioai-backend
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn config.wsgi:application
Root Directory: backend
```

#### Frontend (Static Site o Web Service)
```yaml
Name: bioai-frontend
Environment: Node
Build Command: npm install && npm run build
Start Command: npm start
Root Directory: frontend
```

#### Database
```yaml
Name: bioai-db
Type: PostgreSQL
Plan: Free (hasta 1GB)
```

**Costo**: $7/mes por servicio web (backend + frontend = $14/mes)

---

## 🎯 Comparación de Opciones

| Opción | Costo/mes | Dificultad | Tiempo Setup | Control | Escalabilidad |
|--------|-----------|------------|--------------|---------|---------------|
| **VPS (DigitalOcean)** | $24 | Media | 2-3 horas | Alto | Alta |
| **Railway + Vercel** | $10-15 | Fácil | 30 min | Medio | Alta |
| **Render** | $14 | Fácil | 30 min | Medio | Alta |
| **Servidor CCG** | Gratis | Alta | Variable | Bajo | Media |

---

## 📋 Checklist Rápido

### Railway + Vercel (30 minutos)

- [ ] Crear cuenta en Railway (5 min)
- [ ] Desplegar backend + PostgreSQL (10 min)
- [ ] Ejecutar migraciones (5 min)
- [ ] Crear cuenta en Vercel (2 min)
- [ ] Desplegar frontend (5 min)
- [ ] Conectar frontend y backend (3 min)
- [ ] Verificar funcionamiento (5 min)

**Total**: ~35 minutos

---

## 🔧 Comandos Útiles

### Railway CLI

```bash
# Instalar
npm install -g @railway/cli

# Login
railway login

# Link proyecto
railway link

# Ver logs
railway logs

# Ejecutar comando
railway run python manage.py migrate

# Variables de entorno
railway variables
```

### Vercel CLI

```bash
# Instalar
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Ver logs
vercel logs

# Variables de entorno
vercel env ls
```

---

## 🎓 Recursos de Aprendizaje

### Tutoriales
- **Railway**: https://docs.railway.app/
- **Vercel**: https://vercel.com/docs
- **Render**: https://render.com/docs
- **DigitalOcean**: https://www.digitalocean.com/community/tutorials

### Videos
- "Deploy Django to Railway" (YouTube)
- "Deploy Next.js to Vercel" (YouTube)
- "Docker Deployment Guide" (YouTube)

---

## 💡 Recomendación Final

**Para MVP y pruebas**: Railway + Vercel (más rápido, más fácil)  
**Para producción seria**: VPS con Docker (más control, más económico a largo plazo)  
**Para uso institucional**: Servidor CCG (gratis, pero requiere aprobación)

---

## 📞 Soporte

Si tienes problemas:
- **Railway**: https://railway.app/help
- **Vercel**: https://vercel.com/support
- **Render**: https://render.com/docs/support

---

**¡Elige la opción que mejor se adapte a tus necesidades!** 🚀

Para guía detallada de VPS: Ver [`DEPLOYMENT_GUIDE_PRODUCTION.md`](DEPLOYMENT_GUIDE_PRODUCTION.md)
