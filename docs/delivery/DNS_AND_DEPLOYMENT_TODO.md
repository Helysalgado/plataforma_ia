# TODO: DNS & Deployment - BioAI Hub

## Estado Actual
- ✅ Backend: 100% completo
- ✅ Frontend: 90% completo
- ✅ CI/CD: 100% configurado
- ✅ Deployment docs: 100% completo
- ⏳ DNS: **PENDIENTE** (bioai.ccg.unam.mx)

---

## PLAN DE ACCIÓN

### AHORA (Sin DNS) - 1h

#### 1. Push a GitHub ✅
```bash
cd /Users/heladia/Library/CloudStorage/GoogleDrive-heladia@ccg.unam.mx/Mi\ unidad/github-repos-projects/plataforma_ia
git push origin main
```

**Resultado esperado:**
- CI workflow se ejecuta (lint + tests)
- Verificar en: https://github.com/[usuario]/plataforma_ia/actions

#### 2. Deploy Local para Testing ✅
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar salud
docker-compose ps

# Acceder:
Frontend: http://localhost:3000
Backend: http://localhost:8000/admin
API: http://localhost:8000/api/
```

#### 3. Testing Completo ✅
```
☐ Register nuevo usuario
☐ Verificar email (check logs)
☐ Login
☐ Explorar catálogo
☐ Publicar recurso
☐ Votar recurso
☐ Fork recurso
☐ Editar recurso
☐ Notificaciones
☐ Logout
```

#### 4. Fix Issues (si hay) ✅
- Revisar logs
- Fix y commit
- Re-deploy local
- Re-test

---

### MIENTRAS TANTO: Solicitar DNS (2-5 días)

#### Contactar IT/Redes CCG
**Para:** soporte-it@ccg.unam.mx (o equivalente)

**Asunto:** Solicitud de DNS y Servidor para BioAI Hub

**Cuerpo:**
```
Estimado equipo de IT,

Solicito apoyo para configurar infraestructura del proyecto BioAI Hub:

1. Registro DNS:
   - Dominio: bioai.ccg.unam.mx
   - Tipo: A record
   - IP: [IP del servidor asignado]
   - TTL: 300 segundos

   - Dominio: www.bioai.ccg.unam.mx
   - Tipo: CNAME
   - Apunta a: bioai.ccg.unam.mx

2. Firewall (en IP del servidor):
   - Puerto 80/tcp (HTTP - Let's Encrypt)
   - Puerto 443/tcp (HTTPS - aplicación)
   - Puerto 22/tcp (SSH - administración)

3. Servidor (si no está asignado):
   - OS: Ubuntu 22.04 LTS
   - RAM: 8GB
   - Disk: 50GB
   - CPU: 2 cores
   - IP estática
   - Acceso SSH para usuario: [tu-usuario]

Proyecto: Plataforma institucional para gestión de recursos de IA
Responsable: Heladia Salgado (heladia@ccg.unam.mx)

¿Cuál es el tiempo estimado?

Gracias,
Heladia
```

---

### CUANDO DNS ESTÉ LISTO (2h)

#### 1. Verificar DNS
```bash
dig bioai.ccg.unam.mx +short
ping bioai.ccg.unam.mx
```

#### 2. Actualizar Configs
```bash
# En servidor
cd /var/www/bioai
nano .env.production

# Cambiar:
ALLOWED_HOSTS=bioai.ccg.unam.mx,www.bioai.ccg.unam.mx
CORS_ALLOWED_ORIGINS=https://bioai.ccg.unam.mx
NEXT_PUBLIC_API_URL=https://bioai.ccg.unam.mx/api
```

#### 3. Setup SSL
```bash
sudo ./scripts/setup-ssl.sh
```

#### 4. Deploy Producción
```bash
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

#### 5. Verificar
```bash
curl -I https://bioai.ccg.unam.mx/api/health/
curl -I https://bioai.ccg.unam.mx/
```

#### 6. Testing en Producción
- Mismo checklist de testing local
- Verificar HTTPS (candado verde)
- Test desde diferentes redes

---

## ALTERNATIVA: Deploy Temporal con IP

Si urge demo antes de DNS:

```bash
# Configurar con IP directa
ALLOWED_HOSTS=<IP-servidor>,localhost
CORS_ALLOWED_ORIGINS=http://<IP-servidor>:3000

# Deploy sin SSL
docker-compose up -d

# Acceder:
http://<IP-servidor>:3000
```

**Nota:** Sin dominio no hay SSL (no recomendado para producción)

---

## TIMELINE ESTIMADO

```
Día 1 (Hoy):
  ✅ Push a GitHub
  ✅ CI/CD verification
  ✅ Deploy local testing
  ✅ Solicitud DNS a IT

Día 2-5:
  ⏳ Espera respuesta IT
  ✅ Demo local para stakeholders
  ✅ Fix issues encontrados

Día 6-7:
  ✅ DNS propagado
  ✅ Setup SSL
  ✅ Deploy producción
  ✅ Testing final
  ✅ Anuncio oficial

Total: ~1 semana
```

---

## SIGUIENTE PASO INMEDIATO

```bash
# 1. Push commits
git push origin main

# 2. Ver CI en GitHub
# https://github.com/[usuario]/plataforma_ia/actions

# 3. Deploy local
docker-compose up -d
```

---

**Creado:** 2026-02-17  
**Estado:** Listo para push y deploy local  
**Bloqueador:** DNS (2-5 días estimados)
