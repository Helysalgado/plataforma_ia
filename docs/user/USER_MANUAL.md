# Manual de Usuario - Plataforma CCG IA

**Versión**: 1.0 (MVP)  
**Fecha**: Febrero 2026  
**Audiencia**: Usuarios finales, testers, evaluadores externos

---

## 📖 Índice

1. [Introducción](#introducción)
2. [Acceso a la Plataforma](#acceso-a-la-plataforma)
3. [Cuenta de Prueba (Demo)](#cuenta-de-prueba-demo)
4. [Guía Rápida de Funcionalidades](#guía-rápida-de-funcionalidades)
5. [Tutoriales Paso a Paso](#tutoriales-paso-a-paso)
6. [Preguntas Frecuentes](#preguntas-frecuentes)
7. [Reporte de Problemas](#reporte-de-problemas)

---

## 🎯 Introducción

### ¿Qué es la Plataforma CCG IA?

La **Plataforma CCG IA** es un repositorio institucional para compartir, descubrir y reutilizar recursos de Inteligencia Artificial aplicados a Biología. Los recursos pueden ser:

- 🤖 **Prompts**: Instrucciones para modelos de lenguaje (LLMs)
- 🔄 **Workflows**: Flujos de trabajo automatizados
- 📓 **Notebooks**: Jupyter notebooks con análisis y código
- 📊 **Datasets**: Conjuntos de datos
- 🛠️ **Tools**: Herramientas y scripts

### ¿Para quién es esta plataforma?

- **Investigadores** que quieren compartir sus recursos de IA
- **Estudiantes** que buscan recursos validados para aprender
- **Desarrolladores** que quieren reutilizar y adaptar recursos existentes
- **Administradores** que validan y curan el contenido

### Características Principales

✅ **Explorar recursos** validados por la comunidad  
✅ **Publicar recursos** propios  
✅ **Votar recursos** útiles  
✅ **Hacer fork** (derivar) recursos para adaptarlos  
✅ **Sistema de reputación** basado en contribuciones  
✅ **Versionado** de recursos  
✅ **Notificaciones** de actividad relevante

---

## 🌐 Acceso a la Plataforma

### URL de Acceso

**Entorno Local (Desarrollo)**:
```
http://localhost:3000
```

**Entorno de Producción** (cuando esté disponible):
```
https://bioai.ccg.unam.mx
```

### Requisitos del Navegador

- ✅ Google Chrome (recomendado)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

**Versión mínima**: Navegadores modernos con soporte para ES6+

---

## 👤 Cuenta de Prueba (Demo)

Para facilitar las pruebas, hemos creado una cuenta de demostración con datos de ejemplo.

### Credenciales de Acceso

```
📧 Email:    demo@example.com
🔑 Password: Demo123!
```

### ¿Qué incluye la cuenta demo?

La cuenta **Demo User** ya tiene:
- ✅ 2 recursos publicados
- ✅ 1 recurso validado
- ✅ 1 voto recibido
- ✅ 1 fork recibido
- ✅ 16 puntos de reputación

Esto te permite explorar todas las funcionalidades sin tener que crear contenido desde cero.

### Otras Cuentas Disponibles

#### Cuenta de Administrador
```
📧 Email:    admin@example.com
🔑 Password: Admin123!
```
**Permisos**: Puede validar/rechazar recursos

---

## 🚀 Guía Rápida de Funcionalidades

### 1. Página de Inicio (Home)

**URL**: `/`

**Qué verás**:
- 🎯 Hero section con mensaje de bienvenida
- 💡 Propuestas de valor de la plataforma
- ⭐ Recursos destacados (Featured Resources)

**Acciones disponibles**:
- Ver recursos destacados
- Navegar a Explore para ver más recursos
- Registrarte o iniciar sesión

---

### 2. Explorar Recursos (Explore)

**URL**: `/explore`

**Qué verás**:
- 🔍 Filtros por tipo de recurso (Prompt, Workflow, Notebook, etc.)
- 📚 Secciones organizadas:
  - **Featured Resources**: Los más votados y validados
  - **New Resources**: Publicaciones recientes
  - **Requesting Validation**: Recursos pendientes de validación

**Acciones disponibles**:
- Filtrar por tipo de recurso
- Ver detalles de cualquier recurso
- Votar recursos (si estás autenticado)

---

### 3. Detalle de Recurso

**URL**: `/resources/:id`

**Qué verás**:
- 📝 Título y descripción del recurso
- 🏷️ Tags y categorías
- 👤 Información del autor
- 📊 Métricas (votos, usos, validaciones)
- 📑 Tabs con información:
  - **Description**: Descripción detallada
  - **Notebook**: Visualización del notebook (si aplica)
  - **Versions**: Historial de versiones
  - **Discussion**: Comentarios (próximamente)

**Acciones disponibles**:
- ❤️ **Vote**: Dar voto al recurso
- 🍴 **Fork**: Crear una copia para modificar
- ✏️ **Edit**: Editar (solo si eres el autor)

---

### 4. Publicar Recurso

**URL**: `/publish`  
**Requiere**: Estar autenticado

**Qué verás**:
- 📝 Formulario de publicación con campos:
  - Título
  - Descripción
  - Tipo de recurso
  - Tags
  - Contenido (según el tipo)

**Pasos para publicar**:
1. Completa todos los campos requeridos
2. Agrega tags relevantes
3. Haz clic en "Publish Resource"
4. Tu recurso se publicará en estado "Sandbox"
5. Un administrador lo revisará para validarlo

---

### 5. Mi Perfil (Profile)

**URL**: `/profile`  
**Requiere**: Estar autenticado

**Qué verás**:
- 👤 Avatar con tus iniciales
- 🏆 Puntos de reputación
- 📊 Barra de progreso al siguiente nivel
- 📈 Métricas:
  - **Contributions**: Recursos publicados
  - **Validations Made**: Recursos validados (si eres admin)
  - **Total Impact**: Impacto calculado
- 📚 Grid de tus recursos publicados

**Fórmula de Impact**:
```
Impact = (recursos_validados × 10) + votos_recibidos + (forks_recibidos × 5)
```

---

### 6. Notificaciones

**Ubicación**: Campana (🔔) en la barra superior  
**Requiere**: Estar autenticado

**Tipos de notificaciones**:
- ✅ Tu recurso fue validado
- ❌ Tu recurso fue rechazado
- ❤️ Alguien votó tu recurso
- 🍴 Alguien hizo fork de tu recurso
- 💬 Nuevo comentario (próximamente)

---

## 📚 Tutoriales Paso a Paso

### Tutorial 1: Explorar y Votar un Recurso

**Objetivo**: Encontrar un recurso útil y darle tu voto

**Pasos**:

1. **Inicia sesión**
   - Ve a la página de inicio
   - Haz clic en "Sign In" (arriba a la derecha)
   - Usa las credenciales demo:
     - Email: `demo@example.com`
     - Password: `Demo123!`

2. **Explora recursos**
   - En el sidebar (izquierda), haz clic en "Explore"
   - O haz clic en "Explore Resources" desde el home

3. **Filtra por tipo** (opcional)
   - En la parte superior, verás chips de filtro
   - Haz clic en "Prompt", "Workflow", etc. para filtrar

4. **Abre un recurso**
   - Haz clic en cualquier tarjeta de recurso
   - Se abrirá la página de detalle

5. **Lee la información**
   - Revisa la descripción
   - Mira las métricas (votos, usos)
   - Verifica el badge de estado (Validated/Sandbox)

6. **Vota el recurso**
   - Haz clic en el botón "Vote" (❤️)
   - Verás una confirmación
   - El contador de votos aumentará

**Resultado**: Has contribuido a la comunidad votando por un recurso útil.

---

### Tutorial 2: Publicar tu Primer Recurso

**Objetivo**: Publicar un prompt de ejemplo

**Pasos**:

1. **Inicia sesión** (si no lo has hecho)
   - Email: `demo@example.com`
   - Password: `Demo123!`

2. **Ve a la página de publicación**
   - En el sidebar, haz clic en "Publish"
   - O haz clic en tu avatar → "Publish Resource"

3. **Completa el formulario**
   - **Title**: "Mi Primer Prompt de Prueba"
   - **Description**: "Este es un prompt de ejemplo para análisis de secuencias de ADN"
   - **Resource Type**: Selecciona "Prompt"
   - **Tags**: Escribe "bioinformática, ADN, análisis" (presiona Enter después de cada tag)

4. **Agrega el contenido**
   - En el campo de contenido, escribe:
     ```
     Eres un experto en bioinformática. 
     Analiza la siguiente secuencia de ADN y proporciona:
     1. Composición de nucleótidos
     2. Posibles regiones codificantes
     3. Patrones relevantes
     
     Secuencia: {sequence}
     ```

5. **Publica**
   - Haz clic en "Publish Resource"
   - Verás una confirmación de éxito
   - Serás redirigido a la página de detalle

6. **Verifica tu publicación**
   - Notarás que el recurso está en estado "Sandbox"
   - Esto significa que está pendiente de validación
   - Un administrador lo revisará pronto

**Resultado**: Has publicado tu primer recurso en la plataforma.

---

### Tutorial 3: Hacer Fork de un Recurso

**Objetivo**: Crear una versión derivada de un recurso existente

**Pasos**:

1. **Encuentra un recurso para derivar**
   - Ve a "Explore"
   - Busca un recurso que te interese modificar
   - Abre su página de detalle

2. **Haz fork**
   - Haz clic en el botón "Fork" (🍴)
   - Verás un modal de confirmación

3. **Confirma el fork**
   - Haz clic en "Confirm Fork"
   - El sistema creará una copia

4. **Edita tu versión**
   - Serás redirigido a la página de edición
   - Modifica el título (agrega "- Mi Versión")
   - Ajusta la descripción
   - Modifica el contenido según tus necesidades

5. **Publica tu versión**
   - Haz clic en "Update Resource"
   - Tu fork ahora está publicado

6. **Verifica la derivación**
   - En la página de detalle, verás un badge "Forked from..."
   - El recurso original recibirá una notificación
   - El contador de forks aumentará en el original

**Resultado**: Has creado y publicado una versión derivada de un recurso existente.

---

### Tutorial 4: Ver tu Perfil y Métricas

**Objetivo**: Revisar tu actividad y reputación

**Pasos**:

1. **Accede a tu perfil**
   - Haz clic en tu avatar (arriba a la derecha)
   - Selecciona "My Profile"
   - O haz clic en "My Profile" en el sidebar

2. **Revisa tu información**
   - **Avatar**: Muestra tus iniciales
   - **Badge**: "Contributor" (o "Core Maintainer" si eres admin)
   - **Reputation**: Puntos totales de impacto

3. **Analiza tus métricas**
   - **Contributions**: Cuántos recursos has publicado
   - **Validations Made**: Cuántos recursos has validado (si eres admin)
   - **Total Impact**: Tu impacto calculado

4. **Revisa tus recursos**
   - Desplázate hacia abajo
   - Verás un grid con todos tus recursos publicados
   - Cada tarjeta muestra:
     - Estado (Validated/Sandbox/Pending)
     - Título
     - Tipo de recurso
     - Votos y forks recibidos

5. **Navega a un recurso**
   - Haz clic en cualquier tarjeta
   - Se abrirá la página de detalle
   - Desde ahí puedes editarlo (si es tuyo)

**Resultado**: Conoces tu perfil y métricas de contribución.

---

### Tutorial 5: Validar Recursos (Solo Administradores)

**Objetivo**: Aprobar o rechazar recursos pendientes

**Pasos**:

1. **Inicia sesión como admin**
   - Email: `admin@example.com`
   - Password: `Admin123!`

2. **Ve a la sección de validación**
   - En el sidebar, haz clic en "Admin" (si está visible)
   - O ve a `/admin/validation` (próximamente)

3. **Revisa recursos pendientes**
   - Verás una lista de recursos en estado "Pending"
   - Cada uno muestra:
     - Título y descripción
     - Autor
     - Fecha de publicación
     - Contenido completo

4. **Evalúa el recurso**
   - Lee la descripción
   - Revisa el contenido
   - Verifica que cumpla con los estándares de calidad

5. **Toma una decisión**
   - **Aprobar**:
     - Haz clic en "Approve"
     - El recurso cambiará a estado "Validated"
     - El autor recibirá una notificación
   - **Rechazar**:
     - Haz clic en "Reject"
     - Escribe una razón del rechazo
     - El autor recibirá la notificación con la razón

**Resultado**: Has validado recursos para la comunidad.

---

## ❓ Preguntas Frecuentes

### General

**P: ¿Necesito una cuenta para explorar recursos?**  
R: No, puedes explorar y ver recursos sin autenticarte. Sin embargo, necesitas una cuenta para votar, publicar, o hacer fork.

**P: ¿Cómo obtengo una cuenta?**  
R: Haz clic en "Sign Up" y completa el formulario de registro. Tu cuenta será activada inmediatamente.

**P: ¿Puedo usar la cuenta demo para pruebas?**  
R: Sí, la cuenta demo (`demo@example.com`) está disponible para que cualquiera pueda probar la plataforma.

---

### Recursos

**P: ¿Qué tipos de recursos puedo publicar?**  
R: Puedes publicar Prompts, Workflows, Notebooks, Datasets, Tools, y otros recursos relacionados con IA en Biología.

**P: ¿Qué significa "Sandbox" vs "Validated"?**  
R: 
- **Sandbox**: Recurso publicado pero no validado aún. Visible para todos pero con advertencia.
- **Validated**: Recurso revisado y aprobado por un administrador. Considerado de alta calidad.
- **Pending**: Recurso solicitando validación (solo visible para admins).

**P: ¿Cuánto tiempo tarda la validación?**  
R: Depende de la disponibilidad de los administradores. Típicamente entre 24-48 horas.

**P: ¿Puedo editar un recurso después de publicarlo?**  
R: Sí, puedes editar tus propios recursos en cualquier momento. Cada edición crea una nueva versión.

**P: ¿Qué pasa si mi recurso es rechazado?**  
R: Recibirás una notificación con la razón del rechazo. Puedes corregir los problemas y solicitar validación nuevamente.

---

### Votos y Forks

**P: ¿Puedo votar mi propio recurso?**  
R: No, no puedes votar tus propios recursos.

**P: ¿Puedo quitar mi voto?**  
R: Sí, haz clic nuevamente en el botón "Vote" para quitar tu voto.

**P: ¿Qué es un "fork"?**  
R: Un fork es una copia de un recurso que puedes modificar. Es útil para adaptar recursos existentes a tus necesidades.

**P: ¿El autor original es notificado cuando hago fork?**  
R: Sí, el autor recibe una notificación y su contador de forks aumenta.

---

### Reputación

**P: ¿Cómo se calcula mi reputación?**  
R: La fórmula es:
```
Impact = (recursos_validados × 10) + votos_recibidos + (forks_recibidos × 5)
```

**P: ¿Para qué sirve la reputación?**  
R: La reputación refleja tu contribución a la comunidad. En el futuro, puede desbloquear privilegios adicionales.

**P: ¿Puedo perder reputación?**  
R: Actualmente no, pero en futuras versiones podría haber penalizaciones por contenido de baja calidad.

---

### Técnicas

**P: ¿Qué navegador debo usar?**  
R: Recomendamos Google Chrome o Firefox en sus versiones más recientes.

**P: ¿La plataforma funciona en móviles?**  
R: La versión actual está optimizada para desktop. El soporte móvil completo llegará pronto.

**P: ¿Qué hago si encuentro un error?**  
R: Ver la sección [Reporte de Problemas](#reporte-de-problemas) más abajo.

---

## 🐛 Reporte de Problemas

### ¿Encontraste un bug?

Si encuentras algún problema, por favor repórtalo siguiendo estos pasos:

1. **Verifica que sea reproducible**
   - Intenta repetir el problema
   - Anota los pasos exactos

2. **Recopila información**
   - ¿Qué estabas haciendo cuando ocurrió?
   - ¿Qué esperabas que pasara?
   - ¿Qué pasó en realidad?
   - ¿Qué navegador y versión usas?
   - Captura de pantalla (si aplica)

3. **Reporta el problema**
   - **Email**: soporte@ccg.unam.mx
   - **GitHub Issues**: [Crear issue](https://github.com/ccg-unam/plataforma_ia/issues)

### Formato de Reporte

```markdown
**Título**: Descripción breve del problema

**Descripción**:
[Describe el problema en detalle]

**Pasos para reproducir**:
1. Ve a...
2. Haz clic en...
3. Observa que...

**Comportamiento esperado**:
[Qué esperabas que pasara]

**Comportamiento actual**:
[Qué pasó en realidad]

**Entorno**:
- Navegador: Chrome 120
- Sistema Operativo: macOS 14
- Cuenta: demo@example.com

**Capturas de pantalla**:
[Si aplica]
```

---

## 📊 Casos de Uso Recomendados para Pruebas

### Caso 1: Usuario Nuevo Explorando

**Objetivo**: Familiarizarse con la plataforma

**Flujo**:
1. Accede sin autenticarte
2. Explora la página de inicio
3. Ve a "Explore"
4. Filtra por diferentes tipos de recursos
5. Abre varios recursos y lee sus descripciones
6. Regístrate con una cuenta nueva
7. Vota algunos recursos
8. Revisa tus notificaciones

**Tiempo estimado**: 15-20 minutos

---

### Caso 2: Investigador Publicando Recursos

**Objetivo**: Publicar y gestionar recursos propios

**Flujo**:
1. Inicia sesión con cuenta demo
2. Ve a "Publish"
3. Publica 2-3 recursos de diferentes tipos
4. Revisa tu perfil para ver los recursos publicados
5. Edita uno de tus recursos
6. Verifica que las versiones se guarden correctamente

**Tiempo estimado**: 20-30 minutos

---

### Caso 3: Usuario Reutilizando Recursos

**Objetivo**: Encontrar y adaptar recursos existentes

**Flujo**:
1. Inicia sesión con cuenta demo
2. Busca un recurso interesante en "Explore"
3. Haz fork del recurso
4. Modifica el contenido
5. Publica tu versión
6. Verifica que el recurso original muestre el fork

**Tiempo estimado**: 15-20 minutos

---

### Caso 4: Administrador Validando

**Objetivo**: Validar recursos de la comunidad

**Flujo**:
1. Inicia sesión como admin
2. Ve a la sección de validación
3. Revisa recursos pendientes
4. Aprueba algunos recursos
5. Rechaza algún recurso con razón
6. Verifica que los autores reciban notificaciones

**Tiempo estimado**: 15-20 minutos

---

## 📝 Checklist de Pruebas

Use esta checklist para verificar que todas las funcionalidades principales funcionan:

### Autenticación
- [ ] Registro de nueva cuenta
- [ ] Login con credenciales correctas
- [ ] Login con credenciales incorrectas (debe fallar)
- [ ] Logout
- [ ] Verificación de email (si aplica)

### Exploración
- [ ] Ver página de inicio
- [ ] Ver recursos destacados
- [ ] Navegar a Explore
- [ ] Filtrar por tipo de recurso
- [ ] Ver detalle de un recurso
- [ ] Ver diferentes tabs (Description, Versions)

### Publicación
- [ ] Acceder a formulario de publicación
- [ ] Publicar un Prompt
- [ ] Publicar un Workflow
- [ ] Publicar un Notebook
- [ ] Ver recurso recién publicado

### Interacciones
- [ ] Votar un recurso
- [ ] Quitar voto
- [ ] Hacer fork de un recurso
- [ ] Editar recurso propio
- [ ] Ver notificaciones

### Perfil
- [ ] Ver perfil propio
- [ ] Ver perfil de otro usuario
- [ ] Verificar métricas correctas
- [ ] Ver recursos publicados en perfil

### Administración (solo admin)
- [ ] Ver recursos pendientes
- [ ] Aprobar un recurso
- [ ] Rechazar un recurso
- [ ] Verificar notificaciones enviadas

---

## 🎓 Glosario

**Fork**: Copia de un recurso que puedes modificar independientemente del original.

**Sandbox**: Estado inicial de un recurso publicado, antes de ser validado.

**Validated**: Estado de un recurso que ha sido revisado y aprobado por un administrador.

**Impact**: Métrica de reputación basada en contribuciones y engagement.

**Version**: Cada modificación de un recurso crea una nueva versión.

**Tag**: Etiqueta para categorizar y buscar recursos.

**Workflow**: Secuencia de pasos o proceso automatizado.

**Prompt**: Instrucción o plantilla para modelos de lenguaje.

**Notebook**: Jupyter notebook con código y análisis.

---

## 📞 Contacto y Soporte

### Soporte Técnico
- **Email**: soporte@ccg.unam.mx
- **Horario**: Lunes a Viernes, 9:00 - 18:00 hrs

### Documentación Adicional
- **Documentación Técnica**: `/docs/`
- **API Documentation**: `/docs/api/`
- **GitHub**: https://github.com/ccg-unam/plataforma_ia

### Comunidad
- **Slack**: #bioai-platform (próximamente)
- **Forum**: https://forum.ccg.unam.mx (próximamente)

---

## 📄 Licencia y Términos de Uso

Al usar esta plataforma, aceptas:
- Publicar solo contenido original o con la licencia apropiada
- Respetar los derechos de autor de otros usuarios
- No publicar contenido malicioso o inapropiado
- Cumplir con las políticas institucionales del CCG-UNAM

---

**Manual actualizado**: Febrero 2026  
**Versión de la plataforma**: 1.0 (MVP)  
**Próxima revisión**: Marzo 2026

---

¿Tienes sugerencias para mejorar este manual? Envíalas a: docs@ccg.unam.mx
