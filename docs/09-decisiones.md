# 09. Registro de Decisiones de Arquitectura (ADRs)

Este documento registra las decisiones arquitectónicas clave adoptadas para el desarrollo de **GuíaVital / Alerta Dengue**, Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis (Caso 05 - Grupo 5, Seminario de Titulación UNIANDES).

---

## ADR-003: Manejo de claves de API y cumplimiento de la Ley de Protección de Datos Personales (LOPDP Ecuador)

- **Estado:** Aceptado
- **Fecha:** 2026-10-19
- **Responsable:** Rafael Minaya (QA / Seguridad)
- **Área:** Ciberseguridad / Cumplimiento Legal y Ético

### Contexto
El asistente atiende a ciudadanos y familiares que pueden ingresar datos sensibles de salud y nombres propios en las consultas. En el Ecuador rige la *Ley Orgánica de Protección de Datos Personales* (Registro Oficial Suplemento 459, 2021). Asimismo, la clave de API del LLM otorga acceso al servicio y no debe ser expuesta bajo ninguna circunstancia.

### Opciones Consideradas
1. **Clave de API en el frontend (`VITE_GEMINI_API_KEY`) y almacenamiento de chats con datos de usuario:**
   - *Ventaja:* Facilita una arquitectura sin backend dedicado (Serverless client-only).
   - *Desventaja y descarte:* **Inaceptable e inadmisible.** Las credenciales quedan expuestas en el bundle JS del cliente (violación de la regla de oro: calificación 0). Además, almacenar datos personales de salud de ciudadanos vulnera la LOPDP y expone a riesgos de fuga de información clínica sensible.
2. **Backend FastAPI con gestión de secretos vía `.env`, exclusión en Git, y arquitectura Zero-PII en base de datos (Elegida):**
   - *Ventaja:* Las claves residen exclusivamente en variables de entorno del servidor. El backend aplica filtros para no persistir nombres, cédulas ni ubicaciones exactas en la base de datos SQLite ni en los logs. Los logs solo registran métricas operativas (timestamp, milisegundos, tokens consumidos, código HTTP y longitud del mensaje).
   - *Desventaja:* Al no guardar el texto de las conversaciones de los usuarios con datos personales, la depuración de errores depende de réplicas en tests automatizados con datos sintéticos.
3. **Base de datos con cifrado de datos personales en reposo:**
   - *Ventaja:* Permite mantener el historial de los pacientes para consultas futuras.
   - *Desventaja y descarte:* Añade sobrecarga innecesaria para un asistente de orientación pública en el cual la recolección de identidad no es requerida para el objetivo de triaje preventivo.

### Decisión
Adoptar la arquitectura **Zero-PII con Secretos Aislados**:
1. Las claves de API residen en variables de entorno locales (`.env`), excluidas explícitamente en `.gitignore` y verificadas en el historial de commits.
2. La base de datos SQLite y los logs registran únicamente identificadores anónimos de sesión (*UUIDv4*), métricas de tokens y tiempos de respuesta.
3. Se incluye un aviso claro de privacidad y uso de IA en la pantalla inicial del frontend.

### Consecuencias
- **Positivas:** Cumplimiento estricto de la LOPDP de Ecuador, blindaje contra robo de cuotas de API y cero riesgo de fuga de datos clínicos identificables.
- **Negativas:** La trazabilidad de calidad debe apoyarse en el conjunto de evaluación sintético (`eval/preguntas.csv`) y pruebas automatizadas con mocks.

### Referencias
- Asamblea Nacional del Ecuador. (2021). *Ley Orgánica de Protección de Datos Personales*. Registro Oficial Suplemento 459.
- OWASP Foundation. (2025). *OWASP Top 10 for Large Language Model Applications 2025*.

---
