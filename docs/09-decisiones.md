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

1. Clave en .env local + variables de entorno de la plataforma; logs y BD bajo Minimización de Datos (LOPDP): La clave nunca toca el repositorio Git ni llega al cliente. Los logs y SQLite solo guardan métricas operativas (tokens, tiempo de respuesta, status) y UUIDs anónimos de sesión, sin persistir nombres, cédulas ni síntomas identificables.

2. Clave en el frontend con llamadas directas al proveedor: Descartada de inmediato porque expone la credencial en el navegador cliente, vulnerando la seguridad de la cuota y reprobando el criterio de integración (nota 0).

3. Base de datos con cifrado de datos personales en reposo: Descartada por complejidad innecesaria, ya que un servicio de orientación preventiva y triaje de emergencia no requiere identificar nominalmente al ciudadano para salvar su vida.

### Decisión

Usaremos la configuración de Clave en .env local + variables de entorno de la plataforma, y mantendremos logs estructurados y base de datos SQLite bajo la Política de Minimización de Datos (LOPDP) con enmascaramiento irreversible de PII. El sistema solo registrará métricas operativas y descartará cualquier dato de identidad asociado al ciudadano.

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

## ADR · Diseño del agente de alcance controlado

*Taller de la Clase 3 · 28 de octubre de 2026 · Grupo 5 · Orientación sobre dengue*
*Integrantes: Wilson Salinas, Rafael Minaya, Luis Caguana*

### Contexto
El producto necesita, además de responder con nuestros documentos (RAG), ejecutar acciones. Un agente da vueltas pidiendo funciones; debemos acotar qué puede pedir, cuántas vueltas puede dar y qué acciones requieren confirmación humana.

### Decisión
- **Meta:** Orientar e informar sobre signos de alarma para Dengue y Arbovirosis
- **Se considera terminada cuando:** Cuando se detecta signos de alarmas, se recomienda no automedicarse, acercarse a un centro de salud mas cercano o llamar al servicio de emergencia 911
- **Usuario:** Ciudadanos y Familiar del enfermo

| Herramienta | Qué hace | Nivel | Por qué |
|---|---|---|---|
| `consultar_guia_msp` | Busca en la guía del MSP | Libre | Solo lee |
| `evaluar_signos_alarma` | Compara los síntomas con la lista oficial | Libre | Regla determinista, no diagnóstico |
| `buscar_centro_salud` | Busca el centro de salud más cercano | Libre | Solo lee |
| `notificar_contacto_emergencia` | Avisa a un contacto de emergencia | Con confirmación | Llega a otra persona |
| `diagnosticar` | Emite un diagnóstico médico | Fuera de la lista | Solo lo hace un profesional de salud |

- **MAX_ITER = 6.** Al llegar al tope el agente responde: «No puedo resolver la consulta, este asistente es dedicado solo para Dengue y Arbovirosis»
- **Parámetros en config/:** `respuesta` (Cambia en cada consulta); `se_abstiene` (Cambia si no se habla del tema); `derivar_a` (Verdadero si encuentra un signo de alarma); `fuentes` (Es de acuerdo donde encuentra la información en la base vectorial); `documento` (Es de acuerdo donde encuentra la información en la base vectorial); `seccion` (Es de acuerdo donde encuentra la información en la base vectorial); `proveedor` (Que modelo esta disponible para responder)
- **Herramienta especificada en el taller:** `consultar_guia_msp` (esquema Pydantic, prueba pytest y config generados).

### Pruebas en el simulador del bucle
- ✔ A · Camino feliz (5 vueltas)
- ✔ B · Fuera de alcance (6 vueltas)
- ✔ C · El tope (6 vueltas)
- ✔ D · Inyección en un documento (2 vueltas; control: Protegió de enviar la notificación de correo a una dirección sospechosa)

### Seguridad
- Entradas no confiables: Los documentos que indexa su RAG; Lo que escribe el usuario; Lo que devuelve cada herramienta (incluida la búsqueda); Páginas web o APIs externas; Archivos que sube el usuario; Correos o mensajes de terceros.
- Ningún texto leído otorga permisos: los permisos son PERMITIDAS, MAX_ITER y REQUIEREN_OK, en el código.
- La confirmación muestra los argumentos reales (qué se hará y a quién).

### Consecuencias
- Las herramientas «fuera de la lista» no se implementan como herramientas del agente.
- Cada herramienta tiene esquema Pydantic, implementación determinista y prueba con pytest.
- Pendiente para la Entrega 3: implementar las funciones, el botón de confirmación en la interfaz y la evidencia de inyección en docs/evidencias/semana-3/.

# ADR-0006 · Plataforma de despliegue

- Estado: aceptada
- Fecha: 4/11/2026
- Grupo 5 · Orientación sobre dengue

## Contexto

- Embeddings: Con una API (Gemini, OpenAI…)
- Tarjeta disponible: Sí
- Backend: Python (FastAPI)
- Datos escritos en ejecución: No: solo lee un índice ya construido
- Administración de servidores: Sí

## Decisión

Google Cloud Run. Empaquetamos el backend en Docker con FastAPI, ChromaDB embebido y los pesos de intfloat/multilingual-e5-small (~470 MB). Google Cloud Run nos permite desplegar contenedores con 2 vCPU y 2 GiB de RAM (`--cpu=2`, `--memory=2Gi`), escala a cero instancias (`min-instances=0`) para no generar costos y se integra nativamente con GCP Secret Manager para proteger las llaves de Gemini y Groq.

## Alternativas descartadas

Descartamos AWS Lambda / Vercel Serverless por el límite estricto de tamaño de paquete (250 MB) que no soporta las dependencias de PyTorch y el modelo de embeddings (~470 MB). También descartamos máquinas virtuales tradicionales (GCP Compute Engine / EC2) por el costo fijo continuo 24/7 innecesario para un prototipo académico.

## Consecuencias

Aceptamos una latencia de arranque en frío (cold start) de aproximadamente 6 a 10 segundos al activarse desde 0 instancias mientras carga la memoria de la base vectorial. Además, aceptamos el sistema de archivos efímero del contenedor, lo cual mantiene la base de datos SQLite de historial anónimo acotada por sesión, operando dentro de la capa gratuita de GCP ($0).

---

## ADR-0007: Política de minimización de datos (LOPDP) y enmascaramiento de PII en persistencia

- **Estado:** Aceptado
- **Fecha:** 2026-11-08
- **Responsables:** Rafael Minaya, Luis Cahuana, Wilson Salinas
- **Modifica:** ADR-003

### Contexto

El sistema implementó la herramienta `notificar_contacto_emergencia`, donde el usuario puede ingresar voluntariamente el número telefónico de un familiar para ser alertado ante signos de alarma de dengue mediante un enlace de WhatsApp (`wa.me`). Aunque la intención es de auxilio médico vital, registrar el número de teléfono o correo en texto plano dentro de la base de datos `data/historial.db` contradice la promesa estricta de confidencialidad de la Ley Orgánica de Protección de Datos Personales (LOPDP de Ecuador, Registro Oficial Suplemento 459, 2021). Asimismo, se requiere transparentar que la base vectorial `chroma_db/chroma.sqlite3` almacena exclusivamente fragmentos de normas clínicas oficiales (161 fragmentos) y no datos personales de pacientes.

### Opciones consideradas

1. **Eliminar la herramienta de notificación de emergencia:** Elimina el riesgo de PII, pero priva al paciente con dengue grave de una vía rápida para alertar a un familiar y acudir al hospital.
2. **Almacenar el teléfono sin enmascarar:** Útil para auditoría forense, pero viola el principio de minimización de datos del Art. 10 de la LOPDP al retener datos personales innecesariamente en disco.
3. **Procesamiento volátil en memoria y enmascaramiento en persistencia (Elegida):**
   - El agente procesa el número real en memoria volátil de la sesión activa y se lo devuelve al navegador en la acción pendiente para que el usuario construya y abra su enlace `https://wa.me/593...`.
   - Antes de que `repo.guardar()` inserte el mensaje en `data/historial.db`, una función determinista `anonimizar_pii()` enmascara irreversiblemente el número (`099***67`) y correos electrónicos.
   - El backend nunca envía SMS ni contacta a terceros por su cuenta (simulación honesta en servidor; el envío real lo ejecuta el usuario desde su propio dispositivo).

### Decisión

Adoptar una **Política de Minimización de Datos Personales (Art. 10 y 11 LOPDP)** con excepción justificada de auxilio en emergencias médicas:
1. El sistema no solicita nombres ni cédulas.
2. Los teléfonos o correos ingresados para contacto de emergencia se mantienen en memoria durante el turno para permitir la apertura de WhatsApp en el navegador del usuario.
3. Al persistir el turno en `data/historial.db`, se enmascaran automáticamente (`099***67`). En disco nunca queda PII en texto plano.
4. La base `chroma_db/chroma.sqlite3` contiene exclusivamente guías médicas del MSP y OPS preindexadas en construcción, sin datos personales de ningún tipo.

### Consecuencias

- **Positivas:** Cumplimiento riguroso de la LOPDP y del checklist de la Entrega 4 del Seminario, sin sacrificar la funcionalidad de auxilio de WhatsApp para el paciente.
- **Negativas y riesgos:** Ninguna para el usuario final; en pruebas automatizadas y trazabilidad forense los turnos en BD se visualizan enmascarados, preservando la confidencialidad.
