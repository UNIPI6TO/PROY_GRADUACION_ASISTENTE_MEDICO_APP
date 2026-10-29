# Decisiones de arquitectura (ADR)

Proyecto: GuíaVital · Caso 05. Formato de Michael Nygard (2011). Un ADR no se borra: si una decisión cambia, se agrega uno nuevo y el anterior pasa a «Reemplazado».

## ADR-001: Proveedor y modelo generativo

- **Estado:** Aprobado
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

- **Estado:** Aprobado
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

- **Estado:** Aprobado
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

---

## ADR-005: Base Vectorial Local Embebida con ChromaDB, intfloat/multilingual-e5-small y Segmentación Semántica Jerárquica

### Estado

Aceptado

### Fecha

2026-10-28

### Contexto

Para fundamentar las respuestas del asistente en la normativa clínica oficial de la OPS/OMS (2016) y del Ministerio de Salud Pública del Ecuador (SIVE-Alerta), se requiere una base vectorial (RAG) que permita recuperar fragmentos con alta precisión semántica, soporte búsqueda híbrida por códigos clínicos exactos (ej. `CIE-10 A90`, `CIE-10 A91`), filtre directrices por vigencia y opere sin costos de API externa ni latencias de red.

### Opciones consideradas

* **Opción A (APIs de Embeddings y Vector DB en la nube - OpenAI `text-embedding-3-small` + Pinecone):**
  * *Ventajas:* Alta calidad de embeddings y escalabilidad gestionada.
  * *Desventajas:* Costo recurrente en dólares por cada consulta, dependencia de conexión constante a internet, riesgo de latencia externa e incompatibilidad con pruebas automatizadas rápidas sin cuotas de API.
* **Opción B (Base Vectorial Local Embebida - ChromaDB + intfloat/multilingual-e5-small):**
  * *Ventajas:* Ejecución 100% local y gratuita; persistencia combinada en SQLite (metadatos y FTS5 para búsqueda exacta de texto) y HNSW en archivos binarios (cálculo de distancias coseno en milisegundos); modelo multilingüe de 384 dimensiones altamente optimizado para español; esquema asimétrico (`query:` / `passage:`) que maximiza la similitud pregunta-respuesta; desacoplamiento total en pruebas con dobles efímeros (`chromadb.EphemeralClient`).
  * *Desventajas:* Requiere almacenar los pesos del modelo en el entorno local (~470 MB) y ejecutar la inferencia de embeddings en CPU/GPU del servidor.

### Decisión

Se adopta la **Opción B**:
1. Motor de base vectorial: **ChromaDB persistente** (`chroma_db/`) con colección `guia_vital_dengue` y espacio métrico `cosine`.
2. Modelo de embeddings: **`intfloat/multilingual-e5-small`** (384 dimensiones) con prefijo asimétrico obligatorio `"passage: "` para pasajes indexados y `"query: "` para preguntas de usuarios.
3. Estrategia de corte: Segmentación semántica jerárquica guiada por encabezados clínicos, limpieza de marcas de agua, delimitación exacta por regex en SIVE-Alerta (págs. 95–100) y exclusión de la bibliografía de la Guía OPS 2016.
4. Trazabilidad: Exportación de los 161 fragmentos resultantes en Markdown estructurado (`data/processed/fragmentos.md`) y JSON (`data/processed/fragmentos.json`).

### Consecuencias

* **Positivas:**
  * Cero costos por llamadas a servicios de embeddings en la nube.
  * Privacidad total: las consultas no viajan a proveedores de embeddings externos.
  * Pruebas automatizadas inmediatas en `pytest` (~4 s) mediante inyección de mocks (`CarteroDeterminista` y cliente efímero en memoria).
  * Precisión comprobada: evaluación empírica con 20 preguntas clínicas en [eval/run_eval.py](../eval/run_eval.py) alcanzando **Hit@5 = 100%** y **Hit@1 = 85%**.
* **Negativas y riesgos:**
  * La primera ejecución requiere la descarga local de los pesos del modelo HuggingFace (~470 MB). En entornos sin internet debe configurarse `local_files_only=True` sobre la caché local.
