# Despliegue Temporal para Revisión - BioAI Hub

**Objetivo**: Desplegar rápidamente para que evaluadores puedan revisar  
**Tiempo**: 30-45 minutos  
**Acceso**: Por IP del servidor (sin dominio)  
**Duración**: Temporal (para revisión/evaluación)

---

## 📋 Requerimientos del Servidor

### Mínimos (para revisión temporal)

```
💻 Sistema Operativo: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
🧠 RAM: 4 GB mínimo (8 GB recomendado)
💾 Disco: 20 GB libres mínimo
🔌 CPU: 2 cores mínimo
🌐 Conexión: Internet estable
🔑 Acceso: SSH con sudo
```

### Software Necesario

```
✅ Docker 20.10+
✅ Docker Compose 2.0+
✅ Git
✅ Puertos disponibles: 3000, 8000, 5432
```

---

## 🚀 Guía de Despliegue Rápido (Sin Dominio)

### Paso 1: Verificar Acceso al Servidor

```bash
# Desde tu computadora local
ssh usuario@IP-DEL-SERVIDOR

# Ejemplo:
ssh heladia@192.168.1.100
```

**Si no tienes acceso SSH**, pídelo al administrador del servidor.

---

### Paso 2: Verificar/Instalar Docker

```bash
# Verificar si Docker está instalado
docker --version
docker-compose --version

# Si NO están instalados, ejecutar:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose -y

# Agregar tu usuario al grupo docker
sudo usermod -aG docker $USER

# IMPORTANTE: Cerrar sesión y volver a entrar
exit
ssh usuario@IP-DEL-SERVIDOR

# Verificar que funcione sin sudo
docker ps
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

### Paso 4: Configurar Variables de Entorno (Simplificado)

```bash
# Backend
cat > backend/.env << 'EOF'
# Django
SECRET_KEY=temp-secret-key-for-review-only-change-for-production
DEBUG=False
ALLOWED_HOSTS=*

# Database (Docker interno)
DATABASE_URL=postgresql://postgres:postgres@db:5432/bioai_dev

# JWT
JWT_SECRET_KEY=temp-jwt-secret-for-review-only
JWT_ACCESS_TOKEN_LIFETIME=1440
JWT_REFRESH_TOKEN_LIFETIME=10080

# Email (console para revisión)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# CORS (permitir todo para revisión temporal)
CORS_ALLOWED_ORIGINS=*
CORS_ALLOW_ALL_ORIGINS=True
EOF
```

```bash
# Frontend
cat > frontend/.env.local << 'EOF'
# Usar IP del servidor
NEXT_PUBLIC_API_URL=http://IP-DEL-SERVIDOR:8000/api
NEXT_PUBLIC_SITE_URL=http://IP-DEL-SERVIDOR:3000
EOF
```

**⚠️ IMPORTANTE**: Reemplaza `IP-DEL-SERVIDOR` con la IP real de tu servidor.

---

### Paso 5: Abrir Puertos en Firewall

```bash
# Verificar si hay firewall activo
sudo ufw status

# Si está activo, abrir puertos necesarios
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 3000/tcp   # Frontend
sudo ufw allow 8000/tcp   # Backend

# Si el firewall no está activo, no es necesario hacer nada
```

---

### Paso 6: Iniciar Aplicación

```bash
cd ~/plataforma_ia

# Construir e iniciar servicios
docker-compose up -d --build

# Esto tomará 5-10 minutos la primera vez
# Ver progreso:
docker-compose logs -f
```

**Espera a ver**:
```
bioai_backend  | Starting development server at http://0.0.0.0:8000/
bioai_frontend | ✓ Ready in 1.2s
```

Presiona `Ctrl+C` para salir de los logs.

---

### Paso 7: Ejecutar Migraciones y Crear Datos Iniciales

```bash
# Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario (admin)
docker-compose exec backend python manage.py createsuperuser
```

**Te pedirá**:
```
Email: admin@test.local
Name: Admin User
Password: [elige una contraseña]
Password (again): [repite la contraseña]
```

```bash
# Crear roles iniciales
docker-compose exec backend python manage.py seed_roles

# Crear usuario demo (opcional)
docker-compose exec backend python manage.py shell -c "
from apps.authentication.models import User
from django.utils import timezone

# Crear usuario demo si no existe
if not User.objects.filter(email='demo@example.com').exists():
    demo = User.objects.create_user(
        email='demo@example.com',
        name='Demo User',
        password='Demo123!'
    )
    demo.email_verified_at = timezone.now()
    demo.save()
    print('✅ Usuario demo creado')
else:
    print('✅ Usuario demo ya existe')
"
```

---

### Paso 8: Verificar que Todo Funcione

```bash
# Verificar servicios
docker-compose ps

# Deberías ver 3 servicios "Up":
# bioai_backend    Up
# bioai_frontend   Up
# bioai_db         Up

# Verificar logs (sin errores)
docker-compose logs --tail=50
```

---

### Paso 9: Probar Acceso desde Tu Computadora

**Desde tu navegador**:

```
Frontend: http://IP-DEL-SERVIDOR:3000
Backend:  http://IP-DEL-SERVIDOR:8000/api
Admin:    http://IP-DEL-SERVIDOR:8000/admin
```

**Ejemplo**:
```
http://192.168.1.100:3000
http://192.168.1.100:8000/api
```

---

## 🔑 Credenciales para Evaluadores

### Cuenta Demo
```
URL:      http://IP-DEL-SERVIDOR:3000
Email:    demo@example.com
Password: Demo123!
```

### Cuenta Admin
```
URL:      http://IP-DEL-SERVIDOR:3000
Email:    [el que creaste en el paso 7]
Password: [la que elegiste]
```

---

## 📝 Compartir con Evaluadores

Crea un documento simple para compartir:

```markdown
# Acceso Temporal - BioAI Hub

URL: http://IP-DEL-SERVIDOR:3000

Credenciales Demo:
- Email: demo@example.com
- Password: Demo123!

Credenciales Admin:
- Email: admin@test.local
- Password: [solicitar]

Nota: Acceso temporal para revisión académica.
Disponible hasta: [fecha]
```

---

## 🛠️ Comandos Útiles

### Ver Logs en Tiempo Real

```bash
cd ~/plataforma_ia

# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

---

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar solo un servicio
docker-compose restart backend
docker-compose restart frontend
```

---

### Detener Servicios

```bash
# Detener (mantiene datos)
docker-compose stop

# Detener y eliminar contenedores (mantiene volúmenes/datos)
docker-compose down

# Iniciar de nuevo
docker-compose up -d
```

---

### Actualizar Código

```bash
cd ~/plataforma_ia

# Pull cambios
git pull origin main

# Rebuild y restart
docker-compose down
docker-compose up -d --build

# Ejecutar migraciones si hay
docker-compose exec backend python manage.py migrate
```

---

## 🐛 Problemas Comunes

### "Cannot connect to Docker daemon"

```bash
# Verificar que Docker esté corriendo
sudo systemctl status docker

# Iniciar Docker
sudo systemctl start docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
exit
# Volver a conectar por SSH
```

---

### "Port already in use"

```bash
# Ver qué está usando el puerto
sudo lsof -i :3000
sudo lsof -i :8000

# Matar proceso si es necesario
sudo kill -9 PID

# O cambiar puertos en docker-compose.yml
```

---

### "No puedo acceder desde mi navegador"

```bash
# Verificar que los servicios estén corriendo
docker-compose ps

# Verificar firewall
sudo ufw status

# Abrir puertos si están cerrados
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp

# Verificar que el servidor esté escuchando
sudo netstat -tulpn | grep -E '3000|8000'
```

---

## 📊 Verificación Rápida

Ejecuta este script para verificar todo:

```bash
# Crear script de verificación
cat > ~/check_bioai.sh << 'EOF'
#!/bin/bash

echo "🔍 Verificación BioAI Hub"
echo "=========================="

# Docker
echo "✓ Docker version:"
docker --version

# Servicios
echo -e "\n✓ Servicios corriendo:"
docker-compose ps

# Puertos
echo -e "\n✓ Puertos abiertos:"
sudo netstat -tulpn | grep -E '3000|8000|5432'

# Logs recientes
echo -e "\n✓ Últimos logs (errores):"
docker-compose logs --tail=10 | grep -i error || echo "Sin errores recientes"

# Espacio en disco
echo -e "\n✓ Espacio en disco:"
df -h | grep -E '/$'

# Memoria
echo -e "\n✓ Memoria disponible:"
free -h | grep Mem

echo "=========================="
echo "✅ Verificación completa"
EOF

chmod +x ~/check_bioai.sh
./check_bioai.sh
```

---

## 🎯 Resumen de Comandos

```bash
# 1. Conectar al servidor
ssh usuario@IP-DEL-SERVIDOR

# 2. Clonar repo
git clone https://github.com/Helysalgado/plataforma_ia.git
cd plataforma_ia

# 3. Configurar .env (editar IP del servidor)
nano backend/.env
nano frontend/.env.local

# 4. Iniciar
docker-compose up -d --build

# 5. Migraciones
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py seed_roles

# 6. Verificar
docker-compose ps
docker-compose logs -f

# 7. Abrir navegador
# http://IP-DEL-SERVIDOR:3000
```

---

## ⏱️ Timeline Estimado

```
00:00 - Conectar al servidor (2 min)
00:02 - Instalar Docker si no lo tiene (10 min)
00:12 - Clonar repositorio (2 min)
00:14 - Configurar .env (5 min)
00:19 - docker-compose up --build (10 min)
00:29 - Ejecutar migraciones (3 min)
00:32 - Crear usuarios (3 min)
00:35 - Abrir puertos (2 min)
00:37 - Verificar acceso (3 min)
00:40 - ✅ LISTO
```

**Total**: ~40 minutos

---

## 📧 Información para Compartir

Una vez desplegado, comparte esto con tus evaluadores:

```
🌐 Acceso Temporal - BioAI Hub (Revisión)

URL: http://[IP-DEL-SERVIDOR]:3000

Credenciales Demo:
📧 Email: demo@example.com
🔑 Password: Demo123!

Credenciales Admin:
📧 Email: admin@test.local
🔑 Password: [solicitar por email]

⏰ Disponible: [fecha inicio] - [fecha fin]
📝 Propósito: Revisión académica temporal

Nota: Acceso por IP (sin HTTPS). Solo para revisión.
```

---

## ⚠️ Notas Importantes

### Para Revisión Temporal

✅ **Puedes usar**:
- Acceso por IP (http://IP:3000)
- Sin SSL/HTTPS (no es necesario para revisión)
- CORS abierto (CORS_ALLOW_ALL_ORIGINS=True)
- DEBUG=False (pero logs visibles)

❌ **NO usar para producción**:
- Sin HTTPS (datos sin encriptar)
- CORS abierto (inseguro)
- Puertos expuestos directamente
- Sin monitoreo
- Sin backups automáticos

### Seguridad Básica

```bash
# Cambiar contraseñas después de la revisión
docker-compose exec backend python manage.py changepassword admin@test.local

# O detener servicios cuando no se necesiten
docker-compose stop

# Reiniciar cuando sea necesario
docker-compose start
```

---

## 🔄 Después de la Revisión

### Opción 1: Mantener para Más Revisiones

```bash
# Detener servicios
docker-compose stop

# Iniciar cuando se necesite
docker-compose start
```

### Opción 2: Limpiar Completamente

```bash
# Detener y eliminar contenedores
docker-compose down

# Eliminar volúmenes (datos)
docker-compose down -v

# Eliminar repositorio
cd ~
rm -rf plataforma_ia
```

### Opción 3: Migrar a Producción

Cuando estés listo para producción real:
1. Configurar dominio
2. Instalar Nginx
3. Configurar SSL/HTTPS
4. Seguir guía: `DEPLOYMENT_GUIDE_PRODUCTION.md`

---

## 📋 Checklist Rápido

### Antes de Empezar
- [ ] Tengo acceso SSH al servidor
- [ ] Tengo la IP del servidor
- [ ] Tengo permisos sudo

### Durante Despliegue
- [ ] Docker instalado
- [ ] Repositorio clonado
- [ ] Variables .env configuradas con IP correcta
- [ ] Servicios iniciados
- [ ] Migraciones ejecutadas
- [ ] Usuarios creados (admin + demo)
- [ ] Puertos abiertos (3000, 8000)

### Verificación
- [ ] Frontend accesible: http://IP:3000
- [ ] Backend accesible: http://IP:8000/api
- [ ] Login funciona con usuario demo
- [ ] Admin accesible: http://IP:8000/admin

### Compartir
- [ ] IP y credenciales compartidas con evaluadores
- [ ] Fecha límite de revisión establecida
- [ ] Instrucciones básicas enviadas

---

## 🎯 Comandos Copy-Paste

### Script Completo de Instalación

Guarda esto como `deploy.sh` y ejecútalo:

```bash
#!/bin/bash

echo "🚀 Desplegando BioAI Hub para revisión temporal"
echo "================================================"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo apt install docker-compose -y
    sudo usermod -aG docker $USER
    echo "⚠️  Cierra sesión y vuelve a entrar, luego ejecuta este script de nuevo"
    exit 1
fi

# Clonar repo
if [ ! -d "plataforma_ia" ]; then
    echo "📥 Clonando repositorio..."
    git clone https://github.com/Helysalgado/plataforma_ia.git
fi

cd plataforma_ia

# Obtener IP del servidor
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "📍 IP del servidor: $SERVER_IP"

# Configurar backend
echo "⚙️  Configurando backend..."
cat > backend/.env << EOF
SECRET_KEY=temp-secret-key-for-review-only
DEBUG=False
ALLOWED_HOSTS=*
DATABASE_URL=postgresql://postgres:postgres@db:5432/bioai_dev
JWT_SECRET_KEY=temp-jwt-secret-for-review
JWT_ACCESS_TOKEN_LIFETIME=1440
JWT_REFRESH_TOKEN_LIFETIME=10080
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
CORS_ALLOW_ALL_ORIGINS=True
EOF

# Configurar frontend
echo "⚙️  Configurando frontend..."
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://$SERVER_IP:8000/api
NEXT_PUBLIC_SITE_URL=http://$SERVER_IP:3000
EOF

# Abrir puertos
echo "🔓 Abriendo puertos..."
sudo ufw allow 3000/tcp 2>/dev/null
sudo ufw allow 8000/tcp 2>/dev/null

# Iniciar servicios
echo "🐳 Iniciando servicios (esto tomará 5-10 minutos)..."
docker-compose up -d --build

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 30

# Ejecutar migraciones
echo "🗄️  Ejecutando migraciones..."
docker-compose exec -T backend python manage.py migrate

# Crear usuario demo
echo "👤 Creando usuario demo..."
docker-compose exec -T backend python manage.py shell << 'PYEOF'
from apps.authentication.models import User
from django.utils import timezone

if not User.objects.filter(email='demo@example.com').exists():
    demo = User.objects.create_user(
        email='demo@example.com',
        name='Demo User',
        password='Demo123!'
    )
    demo.email_verified_at = timezone.now()
    demo.save()
    print('✅ Usuario demo creado')
else:
    print('✅ Usuario demo ya existe')
PYEOF

# Seed roles
echo "🎭 Creando roles..."
docker-compose exec -T backend python manage.py seed_roles

# Resumen
echo ""
echo "================================================"
echo "✅ Despliegue completado!"
echo "================================================"
echo ""
echo "🌐 Acceso:"
echo "   Frontend: http://$SERVER_IP:3000"
echo "   Backend:  http://$SERVER_IP:8000/api"
echo "   Admin:    http://$SERVER_IP:8000/admin"
echo ""
echo "🔑 Credenciales Demo:"
echo "   Email:    demo@example.com"
echo "   Password: Demo123!"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs:     docker-compose logs -f"
echo "   Reiniciar:    docker-compose restart"
echo "   Detener:      docker-compose stop"
echo "   Ver estado:   docker-compose ps"
echo ""
echo "================================================"
```

---

## 💾 Guardar y Ejecutar Script

```bash
# En el servidor, crear el script
nano ~/deploy.sh

# Pegar el contenido de arriba

# Hacer ejecutable
chmod +x ~/deploy.sh

# Ejecutar
./deploy.sh
```

---

## 🎬 Resumen Ultra-Rápido

Si ya tienes Docker instalado:

```bash
# 1. Conectar
ssh usuario@IP-DEL-SERVIDOR

# 2. Clonar
git clone https://github.com/Helysalgado/plataforma_ia.git
cd plataforma_ia

# 3. Configurar (reemplaza IP_DEL_SERVIDOR)
echo "NEXT_PUBLIC_API_URL=http://IP_DEL_SERVIDOR:8000/api" > frontend/.env.local
echo "NEXT_PUBLIC_SITE_URL=http://IP_DEL_SERVIDOR:3000" >> frontend/.env.local
cp backend/.env.example backend/.env

# 4. Iniciar
docker-compose up -d --build

# 5. Setup
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py seed_roles

# 6. Abrir navegador
# http://IP_DEL_SERVIDOR:3000
```

**Tiempo**: 15-20 minutos (si Docker ya está instalado)

---

## 📞 ¿Necesitas Ayuda?

Dime:
1. ¿Qué sistema operativo tiene tu servidor?
2. ¿Ya tiene Docker instalado?
3. ¿Cuál es la IP del servidor?

Y te daré comandos específicos para tu caso.

---

**¡Listo para desplegar!** 🚀

Sigue el script automático o los comandos manuales según prefieras.
