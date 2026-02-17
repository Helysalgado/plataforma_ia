# Guía de Despliegue a Producción - BioAI Hub

**Fecha**: 2026-02-17  
**Versión**: 1.0  
**Objetivo**: Desplegar la aplicación en un servidor web accesible públicamente

---

## 📋 Índice

1. [Opciones de Hosting](#opciones-de-hosting)
2. [Opción Recomendada: VPS con Docker](#opción-recomendada-vps-con-docker)
3. [Alternativa: Servicios Cloud Separados](#alternativa-servicios-cloud-separados)
4. [Preparación Pre-Despliegue](#preparación-pre-despliegue)
5. [Despliegue Paso a Paso](#despliegue-paso-a-paso)
6. [Configuración de Dominio](#configuración-de-dominio)
7. [SSL/HTTPS](#sslhttps)
8. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

---

## 🌐 Opciones de Hosting

### Opción 1: VPS (Virtual Private Server) ⭐ Recomendada

**Proveedores**:
- **DigitalOcean** - $12-24/mes (Droplet)
- **Linode/Akamai** - $12-24/mes
- **Vultr** - $12-24/mes
- **AWS Lightsail** - $10-20/mes
- **Google Cloud Compute Engine** - $15-30/mes

**Ventajas**:
- ✅ Control total del servidor
- ✅ Fácil con Docker Compose
- ✅ Costo predecible
- ✅ Escalable
- ✅ Ideal para proyectos académicos

**Desventajas**:
- ⚠️ Requiere configuración inicial
- ⚠️ Responsable de mantenimiento

**Especificaciones mínimas**:
- **CPU**: 2 vCPUs
- **RAM**: 4 GB
- **Disco**: 80 GB SSD
- **OS**: Ubuntu 22.04 LTS

---

### Opción 2: Servicios Cloud Separados

**Frontend**: Vercel/Netlify (gratis)  
**Backend**: Railway/Render ($5-10/mes)  
**Base de datos**: Supabase/Neon (gratis hasta cierto límite)

**Ventajas**:
- ✅ Despliegue automático desde Git
- ✅ Escalado automático
- ✅ Menor mantenimiento
- ✅ Tier gratuito disponible

**Desventajas**:
- ⚠️ Más complejo de configurar
- ⚠️ Costos pueden aumentar
- ⚠️ Menos control

---

### Opción 3: Servidor Institucional (CCG-UNAM)

Si CCG tiene infraestructura:

**Ventajas**:
- ✅ Sin costo adicional
- ✅ Dominio institucional (.unam.mx)
- ✅ Soporte interno
- ✅ Cumplimiento institucional

**Desventajas**:
- ⚠️ Requiere aprobación
- ⚠️ Procesos burocráticos
- ⚠️ Posibles limitaciones técnicas

**Contacto**: Área de sistemas de CCG

---

## 🚀 Opción Recomendada: VPS con Docker

Esta es la opción más práctica para tu proyecto.

### Paso 1: Crear VPS

#### En DigitalOcean (Ejemplo)

1. **Crear cuenta**: https://www.digitalocean.com/
2. **Crear Droplet**:
   - Image: Ubuntu 22.04 LTS
   - Plan: Basic - $24/mes (4GB RAM, 2 vCPUs, 80GB SSD)
   - Datacenter: New York o San Francisco (más cercano a México)
   - Authentication: SSH Key (recomendado) o Password
   - Hostname: `bioai-production`

3. **Obtener IP**: Anota la IP pública (ej: `123.45.67.89`)

---

### Paso 2: Conectar al Servidor

```bash
# Desde tu terminal local
ssh root@123.45.67.89

# Si usas SSH key
ssh -i ~/.ssh/id_rsa root@123.45.67.89
```

---

### Paso 3: Configurar Servidor

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose -y

# Verificar instalación
docker --version
docker-compose --version

# Crear usuario no-root (seguridad)
adduser bioai
usermod -aG sudo bioai
usermod -aG docker bioai

# Cambiar a usuario bioai
su - bioai
```

---

### Paso 4: Clonar Repositorio

```bash
# Como usuario bioai
cd ~
git clone https://github.com/Helysalgado/plataforma_ia.git
cd plataforma_ia
```

---

### Paso 5: Configurar Variables de Entorno

```bash
# Backend
cp backend/.env.example backend/.env
nano backend/.env
```

**Configuración de producción** (`backend/.env`):

```env
# Django
SECRET_KEY=tu-secret-key-super-segura-aqui-cambiar-esto
DEBUG=False
ALLOWED_HOSTS=bioai.ccg.unam.mx,123.45.67.89

# Database (usar PostgreSQL en Docker)
DATABASE_URL=postgresql://bioai_user:password_segura@db:5432/bioai_prod

# JWT
JWT_SECRET_KEY=otro-secret-key-diferente-aqui
JWT_ACCESS_TOKEN_LIFETIME=1440
JWT_REFRESH_TOKEN_LIFETIME=10080

# Email (configurar SMTP real)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# CORS (tu dominio)
CORS_ALLOWED_ORIGINS=https://bioai.ccg.unam.mx

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Frontend** (`frontend/.env.local`):

```env
# API Backend (tu dominio)
NEXT_PUBLIC_API_URL=https://bioai.ccg.unam.mx/api

# Public URL
NEXT_PUBLIC_SITE_URL=https://bioai.ccg.unam.mx
```

---

### Paso 6: Crear Docker Compose para Producción

```bash
nano docker-compose.prod.yml
```

**Contenido** (`docker-compose.prod.yml`):

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: bioai_db_prod
    environment:
      POSTGRES_DB: bioai_prod
      POSTGRES_USER: bioai_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - bioai_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: bioai_backend_prod
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - ./backend/.env
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - bioai_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: bioai_frontend_prod
    environment:
      - NODE_ENV=production
    env_file:
      - ./frontend/.env.local
    restart: unless-stopped
    networks:
      - bioai_network

  nginx:
    image: nginx:alpine
    container_name: bioai_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    networks:
      - bioai_network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  bioai_network:
    driver: bridge
```

---

### Paso 7: Crear Dockerfiles de Producción

**Backend** (`backend/Dockerfile.prod`):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiar código
COPY . .

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

**Frontend** (`frontend/Dockerfile.prod`):

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package*.json ./
RUN npm ci

# Copiar código
COPY . .

# Build
RUN npm run build

# Producción
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["npm", "start"]
```

---

### Paso 8: Configurar Nginx

```bash
mkdir -p nginx
nano nginx/nginx.conf
```

**Contenido** (`nginx/nginx.conf`):

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name bioai.ccg.unam.mx;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name bioai.ccg.unam.mx;

        # SSL Certificates (Let's Encrypt)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # SSL Configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Client Max Body Size (para uploads)
        client_max_body_size 50M;

        # API Backend
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Django Admin
        location /admin/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files (Django)
        location /static/ {
            alias /app/staticfiles/;
        }

        # Media files (uploads)
        location /media/ {
            alias /app/media/;
        }

        # Frontend (Next.js)
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support (si usas)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

---

### Paso 9: Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado (antes de iniciar Nginx en Docker)
sudo certbot certonly --standalone -d bioai.ccg.unam.mx

# Los certificados estarán en:
# /etc/letsencrypt/live/bioai.ccg.unam.mx/fullchain.pem
# /etc/letsencrypt/live/bioai.ccg.unam.mx/privkey.pem

# Copiar certificados a carpeta del proyecto
sudo mkdir -p ~/plataforma_ia/nginx/ssl
sudo cp /etc/letsencrypt/live/bioai.ccg.unam.mx/fullchain.pem ~/plataforma_ia/nginx/ssl/
sudo cp /etc/letsencrypt/live/bioai.ccg.unam.mx/privkey.pem ~/plataforma_ia/nginx/ssl/
sudo chown -R bioai:bioai ~/plataforma_ia/nginx/ssl

# Configurar renovación automática
sudo crontab -e
# Agregar línea:
0 3 * * * certbot renew --quiet && docker-compose -f ~/plataforma_ia/docker-compose.prod.yml restart nginx
```

---

### Paso 10: Iniciar Aplicación

```bash
cd ~/plataforma_ia

# Construir imágenes
docker-compose -f docker-compose.prod.yml build

# Iniciar servicios
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Crear superusuario
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Seed roles
docker-compose -f docker-compose.prod.yml exec backend python manage.py seed_roles

# Verificar que todo esté corriendo
docker-compose -f docker-compose.prod.yml ps
```

---

### Paso 11: Verificar Despliegue

```bash
# Verificar servicios
curl http://localhost:80  # Debe redirigir a HTTPS
curl https://bioai.ccg.unam.mx  # Debe mostrar frontend
curl https://bioai.ccg.unam.mx/api/  # Debe mostrar API

# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f nginx
```

---

## 🌍 Configuración de Dominio

### Opción A: Dominio Institucional (bioai.ccg.unam.mx)

**Contactar a**:
- Área de sistemas de CCG
- Solicitar subdominio: `bioai.ccg.unam.mx`
- Proporcionar IP del servidor: `123.45.67.89`

**Configuración DNS** (lo hace el área de sistemas):
```
Type: A
Name: bioai
Value: 123.45.67.89
TTL: 3600
```

---

### Opción B: Dominio Propio

**Registrar dominio** (ej: Namecheap, GoDaddy):
- Ejemplo: `bioai-hub.com`
- Costo: ~$10-15/año

**Configurar DNS**:
```
Type: A
Name: @
Value: 123.45.67.89
TTL: 3600

Type: A
Name: www
Value: 123.45.67.89
TTL: 3600
```

---

## 🔒 Seguridad Adicional

### Firewall (UFW)

```bash
# Habilitar firewall
sudo ufw enable

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Ver estado
sudo ufw status
```

---

### Fail2ban (Protección contra ataques)

```bash
# Instalar
sudo apt install fail2ban -y

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Habilitar
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

### Backups Automáticos

```bash
# Crear script de backup
nano ~/backup.sh
```

**Contenido**:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/bioai/backups"

mkdir -p $BACKUP_DIR

# Backup de base de datos
docker-compose -f ~/plataforma_ia/docker-compose.prod.yml exec -T db \
  pg_dump -U bioai_user bioai_prod > $BACKUP_DIR/db_$DATE.sql

# Backup de media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz ~/plataforma_ia/media

# Mantener solo últimos 7 días
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Hacer ejecutable
chmod +x ~/backup.sh

# Programar backup diario (3 AM)
crontab -e
# Agregar:
0 3 * * * /home/bioai/backup.sh >> /home/bioai/backup.log 2>&1
```

---

## 📊 Monitoreo

### Logs

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx

# Últimas 100 líneas
docker-compose -f docker-compose.prod.yml logs --tail=100
```

---

### Monitoreo de Recursos

```bash
# Uso de recursos de containers
docker stats

# Espacio en disco
df -h

# Memoria
free -h

# CPU
top
```

---

### Herramientas de Monitoreo (Opcional)

**Opciones**:
- **Uptime Robot** (gratis) - Monitoreo de disponibilidad
- **Sentry** (gratis tier) - Error tracking
- **New Relic** - Performance monitoring
- **Prometheus + Grafana** - Métricas detalladas

---

## 🔄 Actualizaciones

### Proceso de Actualización

```bash
cd ~/plataforma_ia

# Pull últimos cambios
git pull origin main

# Rebuild y restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Ejecutar migraciones si hay
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Verificar
docker-compose -f docker-compose.prod.yml ps
```

---

## 🆘 Troubleshooting

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker-compose -f docker-compose.prod.yml logs backend

# Verificar configuración
docker-compose -f docker-compose.prod.yml config

# Rebuild forzado
docker-compose -f docker-compose.prod.yml build --no-cache
```

---

### Problema: Error de conexión a BD

```bash
# Verificar que BD esté corriendo
docker-compose -f docker-compose.prod.yml ps db

# Conectar a BD manualmente
docker-compose -f docker-compose.prod.yml exec db psql -U bioai_user -d bioai_prod

# Ver logs de BD
docker-compose -f docker-compose.prod.yml logs db
```

---

### Problema: 502 Bad Gateway

```bash
# Verificar que backend esté corriendo
docker-compose -f docker-compose.prod.yml ps backend

# Ver logs de nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Verificar conectividad
docker-compose -f docker-compose.prod.yml exec nginx ping backend
```

---

## 📋 Checklist de Despliegue

### Pre-Despliegue
- [ ] Código en GitHub actualizado
- [ ] Variables de entorno configuradas
- [ ] Secrets generados (SECRET_KEY, JWT_SECRET)
- [ ] Email SMTP configurado
- [ ] Dominio registrado/solicitado

### Servidor
- [ ] VPS creado y accesible
- [ ] Docker instalado
- [ ] Docker Compose instalado
- [ ] Usuario no-root creado
- [ ] Firewall configurado

### Aplicación
- [ ] Repositorio clonado
- [ ] docker-compose.prod.yml creado
- [ ] Dockerfiles de producción creados
- [ ] Nginx configurado
- [ ] SSL/HTTPS configurado
- [ ] Servicios iniciados

### Post-Despliegue
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Roles iniciales creados
- [ ] Frontend accesible
- [ ] API funcionando
- [ ] Admin Django accesible
- [ ] Backups configurados
- [ ] Monitoreo configurado

---

## 💰 Estimación de Costos

### Opción VPS (DigitalOcean)
- **Servidor**: $24/mes (4GB RAM)
- **Dominio**: $12/año (~$1/mes)
- **Backups**: $5/mes (opcional)
- **Total**: ~$30/mes

### Opción Cloud Separado
- **Frontend** (Vercel): Gratis
- **Backend** (Railway): $10/mes
- **BD** (Supabase): Gratis (hasta 500MB)
- **Dominio**: $12/año (~$1/mes)
- **Total**: ~$11/mes

---

## 📞 Soporte

### Recursos
- **DigitalOcean Docs**: https://docs.digitalocean.com/
- **Docker Docs**: https://docs.docker.com/
- **Let's Encrypt**: https://letsencrypt.org/
- **Nginx Docs**: https://nginx.org/en/docs/

### Contacto CCG
- Área de sistemas para dominio institucional
- Soporte técnico interno

---

**¡Tu aplicación estará en producción!** 🚀

Sigue esta guía paso a paso y tendrás BioAI Hub corriendo en un servidor web accesible públicamente.
