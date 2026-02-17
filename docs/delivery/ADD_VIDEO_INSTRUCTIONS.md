# Instrucciones para Agregar Video Demostrativo

## 📹 Video Actual
- **Tamaño:** 84 MB
- **Ubicación:** Local (pendiente subir)

---

## 🎯 Opciones de Alojamiento

### Opción 1: Google Drive (Recomendado para ti)

**Ventajas:**
- Ya usas Google Drive para el proyecto
- Fácil de compartir con evaluadores
- Sin límites de tamaño
- Puedes actualizar el video sin cambiar el link

**Pasos:**

1. **Subir el video a Google Drive**
   ```
   - Abre Google Drive
   - Sube el archivo de video (84 MB)
   - Renombra a: "BioAI_Hub_Demo_v1.mp4" (o similar)
   ```

2. **Hacer el video público**
   ```
   - Clic derecho en el archivo → "Compartir"
   - En "Acceso general" → Cambiar a "Cualquiera con el enlace"
   - Permiso: "Visualizador"
   - Copiar enlace
   ```

3. **Obtener link directo para embed (opcional)**
   ```
   Link normal:
   https://drive.google.com/file/d/FILE_ID/view?usp=sharing
   
   Link para embed (si quieres):
   https://drive.google.com/file/d/FILE_ID/preview
   ```

4. **Actualizar README.md**
   
   Busca esta línea en `README.md`:
   ```markdown
   📹 **Video completo de funcionalidades:** [Próximamente - Subir a Google Drive o YouTube]
   ```
   
   Reemplaza con:
   ```markdown
   📹 **Video completo de funcionalidades:** [Ver en Google Drive](TU_LINK_AQUI)
   ```

---

### Opción 2: YouTube (Más profesional)

**Ventajas:**
- Mejor player de video
- Puedes agregar capítulos/timestamps
- Más fácil de compartir públicamente
- Estadísticas de visualización

**Pasos:**

1. **Subir a YouTube**
   ```
   - Ve a YouTube Studio
   - Clic en "Crear" → "Subir video"
   - Selecciona el archivo (84 MB)
   - Título: "BioAI Hub - Demo Plataforma Institucional IA"
   - Descripción: Incluir link al repo GitHub
   ```

2. **Configurar privacidad**
   ```
   - Visibilidad: "No listado" (solo quienes tengan el link)
   - O "Público" si quieres que sea descubrible
   ```

3. **Agregar capítulos (opcional pero recomendado)**
   ```
   En la descripción del video:
   0:00 - Introducción
   0:30 - Exploración de recursos
   2:00 - Sistema de votación
   3:30 - Publicación de recursos
   5:00 - Fork y reutilización
   6:30 - Perfil de usuario
   8:00 - Panel de administración
   ```

4. **Actualizar README.md**
   
   Reemplaza con:
   ```markdown
   ## 🎥 Video Demostrativo
   
   [![BioAI Hub Demo](https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
   
   *Demostración completa de las funcionalidades principales de BioAI Hub (X minutos)*
   ```

---

### Opción 3: Ambas (Recomendado para máxima accesibilidad)

1. **Google Drive:** Para respaldo y compartir con evaluadores internos
2. **YouTube:** Para el README y compartir públicamente

---

## 📝 Actualizar README.md

### Ubicación en el archivo
Línea aproximada: 20-30 (después de badges, antes de "Descripción")

### Contenido actual (placeholder):
```markdown
## 🎥 Video Demostrativo

📹 **Video completo de funcionalidades:** [Próximamente - Subir a Google Drive o YouTube]

**Funcionalidades demostradas:**
- Exploración y búsqueda de recursos
- Sistema de votación y validación
- Publicación de nuevos recursos
- Fork y reutilización con trazabilidad
- Perfil de usuario y estadísticas
- Panel de administración

> 📎 Para agregar el video: Sube a Google Drive (público) o YouTube (no listado) y actualiza este enlace
```

### Reemplazar con (Google Drive):
```markdown
## 🎥 Video Demostrativo

📹 **Video completo de funcionalidades:** [Ver Demo en Google Drive](https://drive.google.com/file/d/TU_FILE_ID/view?usp=sharing)

*Duración: X minutos | Última actualización: Feb 2026*

**Funcionalidades demostradas:**
- ✅ Exploración y búsqueda de recursos
- ✅ Sistema de votación y validación
- ✅ Publicación de nuevos recursos
- ✅ Fork y reutilización con trazabilidad
- ✅ Perfil de usuario y estadísticas
- ✅ Panel de administración
```

### O reemplazar con (YouTube):
```markdown
## 🎥 Video Demostrativo

[![BioAI Hub Demo](https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)

*Demostración completa de BioAI Hub - Plataforma Institucional de IA (X minutos)*

**Contenido del video:**
- 0:00 - Introducción y arquitectura
- 0:30 - Exploración de recursos
- 2:00 - Sistema de votación
- 3:30 - Publicación de recursos
- 5:00 - Fork y reutilización
- 6:30 - Perfil de usuario
- 8:00 - Panel de administración
```

---

## 🔄 Proceso Completo (Copy-Paste)

### Para Google Drive:

```bash
# 1. Después de subir a Drive y obtener el link, ejecutar:
cd ~/plataforma_ia

# 2. Editar README.md (reemplazar TU_LINK_AQUI con el link real)
# Buscar: "Próximamente - Subir a Google Drive o YouTube"
# Reemplazar con: "Ver Demo en Google Drive](TU_LINK_AQUI)"

# 3. Commit y push
git add README.md
git commit -m "docs: Add demo video link (Google Drive)"
git push origin main
```

### Para YouTube:

```bash
# 1. Después de subir a YouTube y obtener el VIDEO_ID, ejecutar:
cd ~/plataforma_ia

# 2. Editar README.md (reemplazar VIDEO_ID con el ID real)
# El ID está en la URL: youtube.com/watch?v=VIDEO_ID

# 3. Commit y push
git add README.md
git commit -m "docs: Add demo video with YouTube embed"
git push origin main
```

---

## 📋 Checklist

Antes de actualizar el README:

- [ ] Video subido a Google Drive o YouTube
- [ ] Link configurado como público/no listado
- [ ] Link probado en navegador incógnito
- [ ] Duración del video anotada
- [ ] Descripción del contenido actualizada
- [ ] README.md actualizado con el link correcto
- [ ] Cambios commiteados y pusheados

---

## 🎬 Recomendación Final

**Para tu caso (revisión académica):**

1. **Sube a Google Drive** (ya lo usas, más rápido)
2. **Actualiza README.md** con el link
3. **Opcional:** Si quieres más visibilidad, sube también a YouTube

**Link de referencia en README:**
- Actual: http://132.248.34.173:3000 (demo en vivo) ✅
- Video: [Pendiente agregar]

---

## 📞 ¿Necesitas Ayuda?

Si ya subiste el video y tienes el link, solo pásalo y actualizo el README automáticamente.

**Formato esperado:**
```
Google Drive: https://drive.google.com/file/d/XXXXX/view?usp=sharing
YouTube: https://www.youtube.com/watch?v=XXXXX
```
