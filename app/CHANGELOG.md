# Changelog · Backend GuíaVital

Todas las modificaciones notables del backend de GuíaVital (API FastAPI, Agente Clínico, RAG, Base Vectorial y Herramientas) se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el backend se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

## [0.2.0-SNAPSHOT-RC5] - 2026-11-01

- chore: (config) quitar línea vacía final
- feat: (ci) mover quality gates a deploy y mejorar SemVer
- chore: (changelog) separar bitácoras por aplicación
- feat: separar CI/CD en tag y deploy por componente
- feat: (tools) filtrar RAG por distancia y simular notificación

## [0.2.0-SNAPSHOT-RC4] - 2026-11-01

- feat: (ci) mover quality gates a deploy y mejorar SemVer
- chore: (changelog) separar bitácoras por aplicación
- feat: separar CI/CD en tag y deploy por componente
- feat: (tools) filtrar RAG por distancia y simular notificación
- feat: (app) integrar agente v2 y arbovirosis

## [0.2.0-SNAPSHOT-RC2] - 2026-10-31

### Agente Clínico y Proveedores LLM
- **Soporte de Pensamiento y Firmas en Herramientas (Gemini)**: Serialización extendida de `tool_calls` en `app/services/agent.py` mediante `tc.model_dump(exclude_none=True)`, preservando `extra_content` (`thought_signature`) para compatibilidad multi-turno con Gemini 3.5 / Flash-Lite sin errores HTTP 400.
- **Resiliencia ante Límites de Tasa**: Prevención de saturación prematura del proveedor de respaldo (Groq) al estabilizar el flujo principal en Gemini.

### Base Vectorial y RAG
- **Optimización de Pruebas RAG**: Implementación de fixture con ámbito de módulo (`@pytest.fixture(scope="module")`) en `tests/test_retriever.py`, reduciendo el tiempo de ejecución a 2.8 s al evitar la reingesta repetitiva de PDFs.
- **Desacoplamiento Arquitectónico (SOLID)**: Centralización de constantes de embeddings y persistencia (`MODELO_EMBEDDINGS`, `NOMBRE_COLECCION`, `RUTA_CHROMA_DEFAULT`) en `app/config.py`, eliminando dependencias circulares entre el código de la API `app/` y la carpeta de utilidades `scripts/`.

### Seguridad y CORS
- **Control de Acceso HTTP**: Lista blanca estricta de orígenes locales (`localhost:5173`, `localhost:5174`, `127.0.0.1`) con métodos `GET`, `POST` y cabeceras autorizadas `Content-Type` y `Accept` en `app/main.py`.

---

## [0.2.0-SNAPSHOT-RC1] - 2026-10-31 (Semana 3)

### Base Vectorial y RAG Clínico
- **Ingesta Reproducible (`scripts/ingest.py`)**: Extracción estructurada de la Guía OPS Dengue 2016 y Manual SIVE-Alerta del MSP Ecuador (págs. 95-100, sección 8.2.3.2).
- **Chunking Semántico**: Segmentación preservando metadatos clínicos clave (`codigo_cie10`, `vigente`, `origen`, `seccion`, `pagina_inicio`, `pagina_fin`).
- **Base Vectorial ChromaDB**: Persistencia local con distancia coseno y colección `dengue_docs`.
- **Embeddings Multilingües**: Modelo `intfloat/multilingual-e5-small` con prefijos asimétricos normativos (`passage: ` para fragmentos y `query: ` para consultas).
- **Filtrado Clínico**: Búsqueda con filtro por documento exacto (`where_document={'$contains': ...}`) y prefiltrado estricto por vigencia (`where={'vigente': True}`).
- **Exportación de Artefactos**: Generación de `data/processed/fragmentos.json` y `data/processed/fragmentos.md` para auditoría médica.

### Agente de Alcance Controlado v2
- **Orquestación de Herramientas**: Endpoint `/api/v2/chat` con ciclo iterativo de llamadas a funciones (*Function Calling*).
- **Lista Cerrada de Herramientas**:
  - `consultar_guia_msp`: Búsqueda de evidencia clínica en ChromaDB.
  - `evaluar_signos_alarma`: Clasificación y triaje determinista por signos de alarma.
  - `buscar_centro_salud`: Consulta a GeoSalud por ciudad o proximidad GPS (Haversine).
  - `notificar_contacto_emergencia`: Envío simulado de alerta médica a familiares.
- **Human-in-the-Loop (HITL)**: Pausa obligatoria del agente cuando se detecta una acción con efectos secundarios (`notificar_contacto_emergencia`) y confirmación controlada mediante `/api/v2/chat/confirmar`.
- **Salvaguarda de Vueltas**: Límite estricto de 6 iteraciones con respuesta segura ante agotamiento de intentos.

### Automatización y Triaje
- **Cinta Transportadora de Triaje (`app/flujo.py`)**: Pipeline de 7 estaciones automatizadas con cálculo de confianza clínica (umbral `0.85`).
- **Desvío a Revisión Humana**: Enrutamiento a médicos ante consultas vagas, ambiguas o de baja confianza.
- **Endpoint Determinista**: `/herramientas/signos-alarma` para evaluación clínica sin alucinación.

---

## [0.1.1] - 2026-10-24 (Semana 2)

### Cliente LLM y Resiliencia (`app/services/llm.py`)
- **Adaptador Unificado**: Conexión agnóstica a Gemini (`gemini-3.8-flash`) y Groq (`openai/gpt-oss-20b`) bajo el estándar Chat Completions.
- **Validación Estricta de Esquemas**: Validación Pydantic con reintento automático y retroalimentación de errores.
- **Manejo de Errores Transitorios**: Reintentos con espera exponencial y jitter aleatorio ante errores 429, caídas y respuestas vacías.
- **Failover Automático**: Conmutación transparente al proveedor de respaldo cuando el principal falla.
- **Auditoría Anónima**: Registro estructurado en `logs/llm.jsonl` (latencia, tokens de entrada/salida y estado).

### Seguridad y Persistencia
- **Memoria Conversacional**: Aislamiento por `idSesion` con persistencia en SQLite (`historial.db`).
- **Protección contra Inyección de Prompts**: Delimitación defensiva de la entrada del usuario (`<consulta_usuario>`).
- **Limitador de Tasa (*Rate Limiter*)**: Ventana deslizante por sesión con respuesta HTTP 429 y cabecera `Retry-After`.
- **Estándar RFC 9457**: Formato de errores estandarizado (*Problem Details*).

### Prompts Clínicos
- Versiones estructuradas de prompts en `app/prompts/` (`system_v1.md` a `system_v4.md`) con abstención diagnóstica y derivación prioritaria.

---

## [0.1.0] - 2026-10-17 (Semana 1)

### Inicialización de la API FastAPI (`app/main.py`)
- Endpoints de observabilidad: `/manage/health` (Liveness y Readiness) y `/manage/info` (metadatos del servicio).
- Cumplimiento de especificación SemVer 2.0 con validación por expresión regular.
- Pruebas unitarias de endpoints base con `pytest`.
