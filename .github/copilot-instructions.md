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
Al sugerir o generar títulos, descripciones y comentarios de Pull Requests:

1. **Idioma OBLIGATORIO:** Español.
2. **Sugerencia del Título:**
   - Debe ser conciso, claro y descriptivo en español (formato recomendado: `tipo(ámbito): descripción en español`).
3. **Comentarios de Commits a Fusionar (OBLIGATORIO):**
   - Debe incluir y mostrar el listado con los comentarios/mensajes de todos los commits que componen la rama y que se van a fusionar.
4. **Estructura sugerida para la Descripción del PR:**
   - **Resumen general:** Breve explicación en español del objetivo y los cambios del PR.
   - **Commits a fusionar:** Listado de los commits incluidos con sus respectivos mensajes/comentarios.
   - **Impacto / Componentes afectados:** Módulos o archivos modificados.
   - **Pruebas y verificación:** Validación y pruebas realizadas.