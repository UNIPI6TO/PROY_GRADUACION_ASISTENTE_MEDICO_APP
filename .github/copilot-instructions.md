# Instrucciones del Repositorio para GitHub Copilot

## Estilo y Generación de Mensajes de Commit
Al generar sugerencias de mensajes de commit en GitHub Desktop y extensiones de desarrollo:

1. **Idioma OBLIGATORIO:** Español.
2. **Estándar OBLIGATORIO:** Conventional Commits (formato: `<tipo>: (<scope>) <descripción concisa en español>`).
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
2. **Formato del título del PR:**
   - En minúsculas después de los dos puntos.
   - Verbo en tiempo presente/infinitivo (ej. `feat:(auth) agregar nueva funcionalidad de autenticación`).
   - El `scope` debe ir entre paréntesis inmediatamente después del tipo, sin espacios.
   - Ejemplo de título de PR: `feat:(auth) agregar nueva funcionalidad de autenticación`
   - Longitud máxima del título: 72 caracteres.
   - Sin punto final en el título.
3. **Cuerpo del PR (opcional):**
   - Si el PR abarca más de un cambio relevante, listar viñetas explicativas en español.
4. **Agregar al final de la descripción del PR**
   - Hecho con asistencia de IA; revisado por: