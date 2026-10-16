# Instrucciones del Repositorio para GitHub Copilot

## Estilo y Generación de Mensajes de Commit
Al generar sugerencias de mensajes de commit en GitHub Desktop, extensiones de desarrollo y herramientas de IA:

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
   - Verbo en tiempo presente/infinitivo (ej. `docs: documentar arquitectura y despliegue en gcp`).
   - Longitud máxima del título: 72 caracteres.
   - Sin punto final en el título.
5. **Cuerpo del mensaje (opcional):**
   - Si se requiere mayor detalle, agregar viñetas explicativas en español.
6. **Línea de cierre obligatoria al final:**
   - Agrega SIEMPRE al final del mensaje (en la descripción/cuerpo del commit) la siguiente línea exacta:
   `Hecho con asistencia de IA; revisado por WilsonSalinasFlores`
