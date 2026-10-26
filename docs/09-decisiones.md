# Decisiones de arquitectura (ADR)

Proyecto: GuíaVital · Caso 05. Formato de Michael Nygard (2011). Un ADR no se borra: si una decisión cambia, se agrega uno nuevo y el anterior pasa a «Reemplazado».

## ADR-001: Proveedor y modelo generativo

- **Estado:** Propuesto
- **Fecha:** 2026-10-19
- **Responsables:** Wilson Salinas
- **Nota:** el contexto y las opciones partieron de la sugerencia de la plantilla.

### Contexto

En este proyecto exige implementar RAG sobre guías médicas extensas de la OPS y el MSP. Trabajamos con capas gratuitas, por lo que requerimos una ventana de contexto amplia para enviar los documentos y un límite de tokens por minuto (TPM) generoso para no sufrir errores 429 (Too Many Requests) constantemente. Además, la demostración requiere alta disponibilidad, obligando a tener un modelo de respaldo.

### Opciones consideradas

1. Groq (Llama 3.1): como principal y Gemini como respaldo. Ventaja: Groq es extremadamente veloz generando respuestas. Desventaja: Su capa gratuita tiene un límite estricto de 6,000 a 12,000 TPM. Al insertar las guías médicas en el prompt, agotaríamos el límite en 1 o 2 consultas.

2. Google AI Studio (Gemini 2.0 Flash): como principal y Groq como respaldo. Ventaja: Gemini ofrece 1 millón de TPM gratuitos y maneja hasta 2 millones de tokens de contexto, ideal para procesar RAG. Groq es excelente como "Plan B" para mantener el servicio arriba. Desventaja: Configurar dos proveedores requiere mayor esfuerzo en la clase envolvente (llm.py)

### Decisión

Usaremos Google AI Studio (Gemini 2.0 Flash) como proveedor principal y Groq (Llama 3.1 8B) como proveedor de respaldo, porque Gemini nos proporciona la capacidad de tokens gratuita necesaria para el análisis documental pesado (RAG), mientras que la latencia ultrabaja de Groq servirá como salvavidas si la cuota principal falla en plena sustentación.

### Consecuencias

**Positivas:** Capacidad masiva para procesamiento de guías sin costo y resiliencia total del sistema.

**Negativas y riesgos:** Incrementa la complejidad del backend al tener que unificar y estandarizar las respuestas de dos SDKs diferentes.

---

## ADR-002: Patrón de integración: workflow o agente

- **Estado:** Propuesto
- **Fecha:** 2026-10-19
- **Responsables:** Wilson Salinas
- **Nota:** el contexto y las opciones partieron de la sugerencia de la plantilla.

### Contexto

El asistente debe conversar de forma amigable para prevención, pero tiene una restricción crítica: debe aplicar una lista de verificación y derivar al paciente ante cualquier signo de alarma del dengue, sin inventar. Debemos decidir cuánta libertad darle al LLM sobre la ruta de atención.

### Opciones consideradas

1. Enrutamiento por tipo de consulta: Una clasificación inicial dirige la consulta. Si es sobre prevención, usa el sistema RAG; si el usuario reporta síntomas, enruta hacia un flujo determinista basado en reglas para evaluar el triaje. Ventaja: Control absoluto del flujo crítico, asegurando el 100% de derivaciones necesarias. Desventaja: Requiere programar y mantener una mayor lógica en el backend (FastAPI) para gestionar los estados de la conversación.
2. Agente con herramientas desde ahora: El LLM actúa de forma autónoma, analizando el contexto de la charla y decidiendo por sí mismo en qué momento ejecutar la función de evaluar signos de alarma. Ventaja: Conversación mucho más fluida, natural y requiere menos código estructural de ramificación. Desventaja: Riesgo inaceptable de seguridad médica por posibles "falsos negativos" (que el modelo alucine, malinterprete un síntoma grave y no derive al paciente).
3. Sin IA en esta parte (solo reglas): Eliminar el LLM para cualquier interacción que involucre síntomas y usar únicamente un cuestionario tradicional de botones o checkboxes en el frontend. Ventaja: 100% determinista, transparente y fácil de probar con pruebas unitarias. Desventaja: La experiencia del usuario se vuelve fría, rígida y como un formulario común, perdiendo el beneficio empático de un asistente conversacional de orientación.

### Decisión

Usaremos un Patrón de Enrutamiento (Workflow), porque nos permite aprovechar la IA generativa para la educación y orientación sobre el dengue (con RAG), pero fuerza una ruta estricta controlada por código para la evaluación de signos de alarma, garantizando que el modelo no tome decisiones médicas por su cuenta.

### Consecuencias

**Positivas:** Garantizamos cero falsos negativos al detectar alarmas, cumpliendo el requerimiento de seguridad del paciente.

**Negativas y riesgos:** El desarrollo es más complejo al tener que conectar la respuesta de la IA con flujos de código tradicional dentro del mismo chat.

---

## ADR-003: Manejo de claves y datos personales

- **Estado:** Aceptado
- **Fecha:** 2026-10-19
- **Responsables:** Rafael Minaya

### Contexto

El backend llama al modelo con una clave de API. Los usuarios (Ciudadano, Familiar del Enfermo) pueden escribir datos personales de salud. En Ecuador rige la Ley Orgánica de Protección de Datos Personales (Registro Oficial Suplemento 459, 2021).

### Opciones consideradas

1. Clave en .env local + variables de entorno de la plataforma; logs y BD sin datos personales (Zero-PII): La clave nunca toca el repositorio Git ni llega al cliente. Los logs y SQLite solo guardan métricas operativas (tokens, tiempo de respuesta, status) y UUIDs anónimos de sesión, sin persistir nombres, cédulas ni síntomas identificables.

2. Clave en el frontend con llamadas directas al proveedor: Descartada de inmediato porque expone la credencial en el navegador cliente, vulnerando la seguridad de la cuota y reprobando el criterio de integración (nota 0).

3. Base de datos con cifrado de datos personales en reposo: Descartada por complejidad innecesaria, ya que un servicio de orientación preventiva y triaje de emergencia no requiere identificar nominalmente al ciudadano para salvar su vida.

### Decisión

Usaremos la configuración de Clave en .env local + variables de entorno de la plataforma, y mantendremos logs estructurados y base de datos SQLite sin datos personales (Zero-PII). El sistema solo registrará métricas operativas y descartará cualquier dato de identidad asociado al ciudadano.

### Consecuencias

**Positivas:** Garantizamos el cumplimiento ético y legal de la LOPDP en Ecuador, prevenimos robo de credenciales de API y protegemos la privacidad del paciente.

**Negativas y riesgos:** Se reduce la trazabilidad individual histórica; los errores deben depurarse mediante réplicas sintéticas en pruebas automatizadas.

---

## ADR-004: Signos de alarma por reglas, no por el modelo

- **Estado:** Propuesto
- **Fecha:** 2026-10-20
- **Responsables:** LUIS CAGUANA
- **Nota:** el contexto y las opciones partieron de la sugerencia de la plantilla.

### Contexto

El sistema debe brindar información sobre los síntomas del dengue y las medidas para prevenirlo. Se necesita decidir cómo garantizar que la información sea confiable y que las respuestas sean claras para los usuarios.

### Opciones consideradas

Opción A: Dejar que la inteligencia artificial genere todas las respuestas. Ventaja: ofrece explicaciones rápidas y personalizadas. Desventaja: puede proporcionar información incorrecta.



Opción B: Utilizar información previamente validada y reglas programadas, con apoyo de la inteligencia artificial. Ventaja: permite controlar y verificar el contenido. Desventaja: requiere actualizar periódicamente la información.

### Decisión

Usaremos información validada sobre los síntomas y la prevención del dengue, almacenada en el sistema. La inteligencia artificial ayudará a explicar esta información con palabras sencillas, pero no realizará diagnósticos médicos.

### Consecuencias

**Positivas:** información más confiable, respuestas consistentes y facilidad para realizar pruebas.

**Negativas y riesgos:** se necesita actualizar la información y programar reglas para comprobar las respuestas.
