# Instrucciones del Repositorio para GitHub Copilot

## Estilo y Generación de Mensajes de Commit
Al generar sugerencias de mensajes de commit en GitHub Desktop y extensiones de desarrollo:

1. **Idioma OBLIGATORIO:** Español.
2. **Estándar OBLIGATORIO:** Conventional Commits (formato: `<tipo>: <descripción concisa en español>`).
3. **Tipos válidos:**
   - `docs:` Cambios o adiciones en documentación técnica y especificaciones (archivos en `docs/` o README).
   - `feat:` Nuevas funcionalidades o endpoints (FastAPI, frontend, herramientas del agente).
   - `fix:` Corrección de errores o bugs.
   - `chore:` Tareas de mantenimiento, dependencias, `.gitignore`, `.gitattributes`, configuración.
   - `refactor:` Reestructuración de código sin alterar funcionalidad externa.
   - `test:` Pruebas unitarias o de integración.
4. **Formato del título:**
   - En minúsculas después de los dos puntos.
   - Verbo en tiempo presente/infinitivo (ej. `docs: documentar flujo de datos y arquitectura GCP`).
   - Longitud máxima del título: 72 caracteres.
   - Sin punto final en el título.
5. **Cuerpo del commit (opcional):**
   - Si el commit abarca más de un cambio relevante, listar viñetas explicativas en español.
6. **Agregar al final de la descripción del comentario**
   - Hecho con asistencia de IA; revisado por:

---

## Estilo y Generación de Pull Requests (PR)
Al generar o sugerir el resumen de un Pull Request (mediante el botón de Copilot Summary o chat de Copilot):

1. **Idioma OBLIGATORIO:** Español para el título, resumen y todos los comentarios.
2. **Sugerencia del Título:**
   - Debe ser conciso, claro y descriptivo en español (formato recomendado: `tipo(ámbito): descripción breve en español`).
3. **Inclusión Obligatoria de los Commits a Fusionar:**
   - En el cuerpo del resumen generado, Copilot DEBE incluir explícitamente el encabezado:
     `### 📜 Commits a Fusionar`
     seguido de la lista textual con los mensajes/títulos de todos los commits que forman parte de la rama a fusionar (por ejemplo: `- tipo: mensaje del commit`).
4. **Estructura Completa que Copilot debe generar en su salida:**
   - `### 📋 Resumen de los Cambios` (breve descripción técnica en español).
   - `### 📜 Commits a Fusionar` (lista con los mensajes de cada commit de la rama).
   - `### 🔍 Impacto y Componentes Afectados` (lista de módulos o archivos modificados).
5. **Sin viñetas vacías:**
   - Nunca generar viñetas vacías sin contenido; cada sección debe contener su información correspondiente.