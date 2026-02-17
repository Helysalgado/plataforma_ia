# DEPLOYMENT GUIDE — BioAI Hub to bioai.ccg.unam.mx

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Servidor:** bioai.ccg.unam.mx  
**Stack:** Django + Next.js + PostgreSQL + Nginx + Let's Encrypt  
**Fecha:** 2026-02-17

---

## 📋 TABLA DE CONTENIDOS

1. [Pre-requisitos](#pre-requisitos)
2. [Preparación del Servidor](#preparación-del-servidor)
3. [Configuración Inicial](#configuración-inicial)
4. [Setup SSL](#setup-ssl)
5. [Deployment](#deployment)
6. [Post-Deployment](#post-deployment)
7. [CI/CD con GitHub Actions](#cicd-con-github-actions)
8. [Troubleshooting](#troubleshooting)
9. [Rollback](#rollback)
10. [Maintenance](#maintenance)

---

## 1. PRE-REQUISITOS

### Servidor
- ✅ **OS:** Ubuntu 22.04 LTS o superior
- ✅ **RAM:** Mínimo 4GB (recomendado 8GB)
- ✅ **Disk:** 50GB disponibles
- ✅ **CPU:** 2 cores mínimo

### DNS
- ✅ Registro A: `bioai.ccg.unam.mx` → IP del servidor
- ✅ Registro A: `www.bioai.ccg.unam.mx` → IP del servidor
- ✅ TTL configurado (recomendado: 300s)

### Firewall
```bash
# Puertos a abrir
80/tcp   - HTTP (para ACME challenge)
443/tcp  - HTTPS (producción)
22/tcp   - SSH (administración)
```

### Software Necesario
- Docker 24.0+
- Docker Compose 2.20+
- Git 2.30+
- Certbot (para SSL)

---

## 2. PREPARACIÓN DEL SERVIDOR

### 2.1 Conectar al Servidor
```bash
ssh usuario@bioai.ccg.unam.mx
```

### 2.2 Actualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 2.3 Instalar Docker
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Verificar instalación
docker --version
```

### 2.4 Instalar Docker Compose
```bash
# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar
docker-compose --version
```

### 2.5 Configurar Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

---

## 3. CONFIGURACIÓN INICIAL

### 3.1 Crear Usuario de Deployment
```bash
# Crear usuario deploy
sudo adduser deploy
sudo usermod -aG docker deploy
sudo usermod -aG sudo deploy

# Cambiar a usuario deploy
su - deploy
```

### 3.2 Configurar SSH Key
```bash
# En tu máquina local
ssh-keygen -t ed25519 -C "deploy@bioai"

# Copiar clave pública al servidor
ssh-copy-id deploy@bioai.ccg.unam.mx

# Verificar acceso sin contraseña
ssh deploy@bioai.ccg.unam.mx
```

### 3.3 Clonar Repositorio
```bash
# Crear directorio de deployment
sudo mkdir -p /var/www/bioai
sudo chown deploy:deploy /var/www/bioai

# Clonar proyecto
cd /var/www
git clone https://github.com/heladia/plataforma_ia.git bioai
cd bioai
```

### 3.4 Configurar Variables de Entorno
```bash
# Copiar ejemplo
cp .env.example .env.production

# Editar con valores de producción
nano .env.production
```

**Variables críticas a configurar:**
```bash
# Security
SECRET_KEY=           # Generar nuevo: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
JWT_SECRET_KEY=       # Generar nuevo: python -c "import secrets; print(secrets.token_urlsafe(32))"

# Database
POSTGRES_PASSWORD=    # Generar contraseña fuerte

# Email
EMAIL_HOST_USER=      # email@ccg.unam.mx
EMAIL_HOST_PASSWORD=  # App password

# Admin
DJANGO_SUPERUSER_EMAIL=    # admin@ccg.unam.mx
DJANGO_SUPERUSER_PASSWORD= # Contraseña fuerte
```

---

## 4. SETUP SSL

### 4.1 Verificar DNS
```bash
# Verificar que el dominio apunta al servidor
dig bioai.ccg.unam.mx +short
ping bioai.ccg.unam.mx
```

### 4.2 Ejecutar Script de SSL
```bash
cd /var/www/bioai
sudo ./scripts/setup-ssl.sh
```

**El script automáticamente:**
- ✅ Crea directorios necesarios
- ✅ Inicia Nginx temporal
- ✅ Obtiene certificados de Let's Encrypt
- ✅ Configura auto-renewal (cron daily)

### 4.3 Verificar Certificados
```bash
ls -la certbot/conf/live/bioai.ccg.unam.mx/

# Debes ver:
# - cert.pem
# - chain.pem
# - fullchain.pem
# - privkey.pem
```

---

## 5. DEPLOYMENT

### 5.1 Build y Start de Servicios
```bash
cd /var/www/bioai

# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

### 5.2 Verificar Servicios
```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Ver estado
docker-compose -f docker-compose.prod.yml ps

# Debes ver 5 contenedores:
# - bioai_db_prod       (healthy)
# - bioai_backend_prod  (healthy)
# - bioai_frontend_prod (healthy)
# - bioai_nginx_prod    (healthy)
# - bioai_certbot       (exited 0)
```

### 5.3 Ejecutar Migraciones
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### 5.4 Crear Superusuario
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

### 5.5 Collectstatic
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

---

## 6. POST-DEPLOYMENT

### 6.1 Verificar Endpoints
```bash
# Backend health
curl https://bioai.ccg.unam.mx/api/health/

# Frontend
curl -I https://bioai.ccg.unam.mx/

# Admin
curl -I https://bioai.ccg.unam.mx/admin/
```

### 6.2 Pruebas Manuales
1. **Abrir navegador:** https://bioai.ccg.unam.mx
2. **Verificar registro:** Crear cuenta de prueba
3. **Verificar login:** Iniciar sesión
4. **Verificar explore:** Navegar catálogo
5. **Verificar publish:** Publicar recurso de prueba

### 6.3 Configurar Backups
```bash
# Crear script de backup
sudo nano /usr/local/bin/backup-bioai.sh
```

```bash
#!/bin/bash
# Backup script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/bioai"
mkdir -p $BACKUP_DIR

# Database backup
docker-compose -f /var/www/bioai/docker-compose.prod.yml exec -T db \
    pg_dump -U bioai_user bioai_prod > $BACKUP_DIR/db_$DATE.sql

# Compress
gzip $BACKUP_DIR/db_$DATE.sql

# Cleanup (keep last 30 days)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
```

```bash
# Hacer ejecutable
sudo chmod +x /usr/local/bin/backup-bioai.sh

# Agregar a cron (daily at 3 AM)
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/backup-bioai.sh >> /var/log/bioai-backup.log 2>&1") | crontab -
```

### 6.4 Configurar Monitoring (Opcional)
```bash
# Instalar Prometheus Node Exporter
docker run -d \
  --name node-exporter \
  --net="host" \
  --pid="host" \
  -v "/:/host:ro,rslave" \
  prom/node-exporter \
  --path.rootfs=/host
```

---

## 7. CI/CD CON GITHUB ACTIONS

### 7.1 Configurar GitHub Secrets

En GitHub: `Settings → Secrets and variables → Actions`

Agregar los siguientes secrets:

```
DEPLOY_SSH_KEY       # Clave privada SSH del usuario deploy
DEPLOY_HOST          # bioai.ccg.unam.mx
DEPLOY_USER          # deploy
DEPLOY_PATH          # /var/www/bioai
SLACK_WEBHOOK        # (Opcional) URL de webhook de Slack
```

### 7.2 Generar SSH Key para GitHub Actions
```bash
# En el servidor
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy_key

# Agregar a authorized_keys
cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys

# Copiar clave privada
cat ~/.ssh/github_deploy_key
# Copiar TODA la salida y agregarla como DEPLOY_SSH_KEY en GitHub
```

### 7.3 Test Deployment Manual
```bash
# Trigger manual deployment
# En GitHub: Actions → CD - Deploy to Production → Run workflow
```

### 7.4 Auto-Deployment
- ✅ **CI:** Se ejecuta en cada push/PR (lint + tests)
- ✅ **CD:** Se ejecuta solo en push a `main`
- ✅ **Manual:** Disponible vía workflow_dispatch

---

## 8. TROUBLESHOOTING

### 8.1 Contenedor No Inicia
```bash
# Ver logs específicos
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs nginx

# Verificar health
docker inspect --format='{{json .State.Health}}' bioai_backend_prod | jq
```

### 8.2 Error de Certificados SSL
```bash
# Renovar manualmente
docker-compose -f docker-compose.prod.yml run --rm certbot renew

# Reload Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### 8.3 Error de Base de Datos
```bash
# Acceder a PostgreSQL
docker-compose -f docker-compose.prod.yml exec db psql -U bioai_user -d bioai_prod

# Ver conexiones activas
SELECT * FROM pg_stat_activity;

# Restart database
docker-compose -f docker-compose.prod.yml restart db
```

### 8.4 Performance Issues
```bash
# Ver uso de recursos
docker stats

# Ver logs de Nginx (slow queries)
tail -f logs/nginx/bioai_access.log | grep "request_time"

# Ver procesos backend
docker-compose -f docker-compose.prod.yml exec backend ps aux
```

---

## 9. ROLLBACK

### 9.1 Rollback Rápido (Git)
```bash
cd /var/www/bioai

# Ver commits recientes
git log --oneline -10

# Rollback a commit anterior
git reset --hard <commit-hash>

# Rebuild y restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### 9.2 Rollback de Base de Datos
```bash
# Restaurar desde backup
gunzip -c /var/backups/bioai/db_20260216_030000.sql.gz | \
docker-compose -f docker-compose.prod.yml exec -T db \
    psql -U bioai_user -d bioai_prod
```

### 9.3 Rollback via GitHub Actions
```bash
# En GitHub: Actions → CD - Deploy → Run workflow
# Seleccionar "Rollback" en el menú
```

---

## 10. MAINTENANCE

### 10.1 Actualizaciones Regulares
```bash
# Actualizar código
cd /var/www/bioai
git pull origin main

# Rebuild solo si cambió código
docker-compose -f docker-compose.prod.yml up -d --build

# Migrar DB si necesario
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### 10.2 Limpieza de Docker
```bash
# Eliminar imágenes no usadas
docker image prune -a

# Eliminar volúmenes huérfanos
docker volume prune

# Espacio usado
docker system df
```

### 10.3 Logs Rotation
```bash
# Configurar logrotate
sudo nano /etc/logrotate.d/bioai
```

```
/var/www/bioai/logs/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        docker-compose -f /var/www/bioai/docker-compose.prod.yml exec nginx nginx -s reload
    endscript
}
```

### 10.4 Renovación SSL Automática
```bash
# Ya configurado en setup-ssl.sh
# Verificar cron
crontab -l | grep renew

# Test manual
./scripts/renew-ssl.sh
```

---

## 📊 CHECKLIST DE DEPLOYMENT

### Pre-Deployment
- [ ] DNS configurado y propagado
- [ ] Servidor preparado (Docker, firewall)
- [ ] Repositorio clonado
- [ ] .env.production configurado
- [ ] GitHub Secrets configurados

### Deployment
- [ ] SSL certificados obtenidos
- [ ] Servicios iniciados (docker-compose up)
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Static files collected

### Verificación
- [ ] Health checks passing (4/4)
- [ ] Endpoints respondiendo (backend + frontend)
- [ ] HTTPS funcionando (SSL válido)
- [ ] Login/Register funcionando
- [ ] Publish recurso funcionando

### Post-Deployment
- [ ] Backups configurados (cron daily)
- [ ] Monitoring configurado
- [ ] Logs rotation configurado
- [ ] CI/CD testeado (GitHub Actions)
- [ ] Documentación actualizada

---

## 🆘 SOPORTE

### Logs Útiles
```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# Nginx access logs
tail -f logs/nginx/bioai_access.log

# System logs
journalctl -u docker -f
```

### Contactos
- **DevOps:** heladia@ccg.unam.mx
- **Documentación:** `/var/www/bioai/docs/`
- **GitHub Issues:** https://github.com/heladia/plataforma_ia/issues

---

## ✅ DEPLOYMENT COMPLETADO

Una vez completados todos los pasos, el proyecto BioAI Hub estará:

✅ **Desplegado:** https://bioai.ccg.unam.mx  
✅ **SSL:** Certificado válido (auto-renovable)  
✅ **CI/CD:** GitHub Actions configurado  
✅ **Backups:** Automáticos (daily)  
✅ **Monitoring:** Health checks activos  

**Próximos pasos:** Monitorear logs las primeras 24-48h y ajustar recursos según necesidad.

---

**Última actualización:** 2026-02-17  
**Versión:** 1.0.0  
**Estado:** Production-Ready ✅
