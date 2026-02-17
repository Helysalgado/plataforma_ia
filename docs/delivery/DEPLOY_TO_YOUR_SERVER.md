# Despliegue en Tu Servidor Existente

**Objetivo**: Desplegar BioAI Hub en tu servidor actual  
**Tiempo estimado**: 1-2 horas  
**Prerequisitos**: Servidor con acceso SSH

---

## 📋 Información Necesaria

Antes de empezar, necesito saber sobre tu servidor:

### Información del Servidor

```
🖥️  IP del servidor: _________________
🔑 Usuario SSH: _________________
🌐 Dominio (si tienes): _________________
💻 Sistema Operativo: _________________
🐳 ¿Tiene Docker instalado?: Sí / No
🔒 ¿Tiene acceso root/sudo?: Sí / No
```

---

## 🚀 Guía Rápida (Asumiendo Ubuntu + Docker)

### Paso 1: Conectar al Servidor

```bash
# Desde tu terminal local
ssh usuario@ip-del-servidor

# Ejemplo:
ssh heladia@123.45.67.89
```

---

### Paso 2: Instalar Docker (si no lo tiene)

```bash
# Verificar si Docker está instalado
docker --version

# Si NO está instalado:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose -y

# Agregar tu usuario al grupo docker
sudo usermod -aG docker $USER

# Cerrar sesión y volver a entrar
exit
ssh usuario@ip-del-servidor

# Verificar
docker --version
docker-compose --version
```

---

### Paso 3: Clonar el Repositorio

```bash
# En el servidor
cd ~
git clone https://github.com/Helysalgado/plataforma_ia.git
cd plataforma_ia
```

---

### Paso 4: Configurar Variables de Entorno

```bash
# Backend
cp backend/.env.example backend/.env
nano backend/.env
```

**Edita estos valores importantes**:

```env
# Django
SECRET_KEY=CAMBIAR-POR-SECRET-KEY-SEGURO
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,ip-del-servidor

# Database
DATABASE_URL=postgresql://bioai_user:password_segura@db:5432/bioai_prod

# JWT
JWT_SECRET_KEY=OTRO-SECRET-KEY-DIFERENTE

# CORS
CORS_ALLOWED_ORIGINS=https://tu-dominio.com
```

```bash
# Frontend
cp frontend/.env.example frontend/.env.local
nano frontend/.env.local
```

```env
NEXT_PUBLIC_API_URL=https://tu-dominio.com/api
NEXT_PUBLIC_SITE_URL=https://tu-dominio.com
```

---

### Paso 5: Iniciar con Docker Compose

```bash
# Construir e iniciar servicios
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Verificar que todo esté corriendo
docker-compose ps
```

Deberías ver 3 servicios corriendo:
- `bioai_backend` (Django)
- `bioai_frontend` (Next.js)
- `bioai_db` (PostgreSQL)

---

### Paso 6: Ejecutar Migraciones

```bash
# Ejecutar migraciones de base de datos
docker-compose exec backend python manage.py migrate

# Crear superusuario (admin)
docker-compose exec backend python manage.py createsuperuser
# Te pedirá: email, nombre, password

# Seed roles iniciales
docker-compose exec backend python manage.py seed_roles
```

---

### Paso 7: Verificar Funcionamiento

```bash
# Verificar backend
curl http://localhost:8000/api/

# Verificar frontend
curl http://localhost:3000/

# Ver logs si hay errores
docker-compose logs backend
docker-compose logs frontend
```

---

## 🌐 Configurar Acceso Externo

### Opción A: Acceso Directo por IP (Temporal)

Si solo quieres probar rápidamente:

```bash
# Abrir puertos en firewall
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 8000/tcp  # Backend (API)

# Actualizar CORS en backend/.env
CORS_ALLOWED_ORIGINS=http://ip-del-servidor:3000

# Reiniciar servicios
docker-compose restart
```

**Acceso**:
- Frontend: `http://ip-del-servidor:3000`
- API: `http://ip-del-servidor:8000/api`

⚠️ **Nota**: Esta opción es solo para pruebas. Para producción, usa Nginx con dominio.

---

### Opción B: Con Nginx y Dominio (Recomendado)

#### 1. Instalar Nginx

```bash
sudo apt update
sudo apt install nginx -y
```

#### 2. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/bioai
```

**Contenido**:

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    client_max_body_size 50M;

    # API Backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3. Activar Configuración

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/bioai /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx

# Habilitar al inicio
sudo systemctl enable nginx
```

#### 4. Configurar Firewall

```bash
# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH

# Habilitar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

---

### Opción C: Con SSL/HTTPS (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Certbot configurará Nginx automáticamente para HTTPS

# Verificar renovación automática
sudo certbot renew --dry-run
```

**Resultado**: Tu app estará en `https://tu-dominio.com` 🎉

---

## 📝 Configuración de Dominio

### Si tienes dominio propio

1. **Ve a tu proveedor de DNS** (Namecheap, GoDaddy, Cloudflare, etc.)

2. **Agrega registro A**:
   ```
   Type: A
   Name: @
   Value: IP-de-tu-servidor
   TTL: 3600
   ```

3. **Agrega registro A para www**:
   ```
   Type: A
   Name: www
   Value: IP-de-tu-servidor
   TTL: 3600
   ```

4. **Espera propagación**: 5 minutos - 24 horas

---

### Si necesitas dominio institucional (bioai.ccg.unam.mx)

**Contactar a**:
- Área de sistemas de CCG-UNAM
- Solicitar subdominio
- Proporcionar IP del servidor

---

## 🔧 Comandos Útiles de Mantenimiento

### Ver Estado de Servicios

```bash
# Ver contenedores corriendo
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs específicos
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Ver uso de recursos
docker stats
```

---

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar servicio específico
docker-compose restart backend
docker-compose restart frontend

# Rebuild completo (después de cambios en código)
docker-compose down
docker-compose up -d --build
```

---

### Actualizar Aplicación

```bash
cd ~/plataforma_ia

# Pull últimos cambios
git pull origin main

# Rebuild y restart
docker-compose down
docker-compose up -d --build

# Ejecutar migraciones (si hay)
docker-compose exec backend python manage.py migrate

# Verificar
docker-compose ps
docker-compose logs -f
```

---

### Backups

```bash
# Backup de base de datos
docker-compose exec -T db pg_dump -U postgres bioai_dev > backup_$(date +%Y%m%d).sql

# Backup de media files (si tienes uploads)
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Restaurar backup
docker-compose exec -T db psql -U postgres bioai_dev < backup_20260217.sql
```

---

## 🐛 Troubleshooting

### Problema: No puedo conectarme al servidor

```bash
# Verificar que el servidor esté encendido
ping ip-del-servidor

# Verificar puerto SSH
telnet ip-del-servidor 22

# Verificar firewall
sudo ufw status
```

---

### Problema: Docker no inicia

```bash
# Ver logs del sistema
sudo journalctl -u docker

# Reiniciar Docker
sudo systemctl restart docker

# Verificar espacio en disco
df -h
```

---

### Problema: Servicios no responden

```bash
# Ver logs detallados
docker-compose logs --tail=100 backend

# Verificar puertos
sudo netstat -tulpn | grep -E '3000|8000|5432'

# Verificar que los contenedores estén corriendo
docker-compose ps

# Reiniciar servicios
docker-compose restart
```

---

### Problema: Error 502 Bad Gateway (Nginx)

```bash
# Verificar que backend esté corriendo
curl http://localhost:8000/api/

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Verificar configuración de Nginx
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## 📊 Monitoreo Básico

### Verificar Salud de la Aplicación

```bash
# Crear script de health check
nano ~/health_check.sh
```

```bash
#!/bin/bash

echo "🔍 Health Check - $(date)"
echo "================================"

# Frontend
echo "Frontend:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000/

# Backend API
echo "Backend API:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/api/

# Database
echo "Database:"
docker-compose exec -T db pg_isready -U postgres

# Disk space
echo -e "\nDisk Space:"
df -h | grep -E '/$|/var'

# Memory
echo -e "\nMemory:"
free -h

# Docker containers
echo -e "\nDocker Containers:"
docker-compose ps

echo "================================"
```

```bash
chmod +x ~/health_check.sh
./health_check.sh
```

---

## 🔐 Seguridad Básica

### 1. Cambiar Puerto SSH (Opcional)

```bash
sudo nano /etc/ssh/sshd_config
# Cambiar: Port 22 → Port 2222
sudo systemctl restart sshd
```

### 2. Deshabilitar Login Root

```bash
sudo nano /etc/ssh/sshd_config
# Cambiar: PermitRootLogin yes → PermitRootLogin no
sudo systemctl restart sshd
```

### 3. Configurar Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## 📋 Checklist de Despliegue

### Preparación
- [ ] Acceso SSH al servidor verificado
- [ ] Docker instalado
- [ ] Docker Compose instalado
- [ ] Repositorio clonado
- [ ] Variables de entorno configuradas

### Despliegue
- [ ] Servicios iniciados con docker-compose
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Roles iniciales creados
- [ ] Frontend accesible (localhost:3000)
- [ ] Backend accesible (localhost:8000)

### Acceso Externo
- [ ] Nginx instalado y configurado
- [ ] Firewall configurado
- [ ] Dominio apuntando al servidor
- [ ] SSL/HTTPS configurado (Let's Encrypt)
- [ ] Aplicación accesible desde internet

### Seguridad
- [ ] DEBUG=False en producción
- [ ] SECRET_KEY cambiado
- [ ] ALLOWED_HOSTS configurado
- [ ] CORS configurado correctamente
- [ ] Firewall habilitado
- [ ] Backups configurados

---

## 🎯 Próximos Pasos

**Dime sobre tu servidor**:

1. ¿Qué sistema operativo tiene? (Ubuntu, CentOS, Debian, etc.)
2. ¿Ya tiene Docker instalado?
3. ¿Tienes acceso root/sudo?
4. ¿Tienes un dominio configurado o usarás la IP?
5. ¿Qué proveedor es? (DigitalOcean, AWS, servidor propio, etc.)

Con esta información, puedo darte **instrucciones específicas** para tu caso.

---

## 📞 Ayuda Adicional

Si necesitas ayuda con:
- Configuración específica de tu servidor
- Problemas de permisos
- Configuración de dominio
- SSL/HTTPS
- Optimización de performance

Solo dime qué necesitas y te guío paso a paso.

---

**¿Cuál es la configuración de tu servidor?** 🖥️
