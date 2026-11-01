# Changelog · GuíaVital
Todas las modificaciones notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

### Backend
- **Optimización de Tests RAG**: Implementación de fixture modular (`@pytest.fixture(scope="module")`) en `tests/test_retriever.py`, evitando la regeneración repetitiva de la base vectorial y reduciendo el tiempo de prueba a 2.8 s.
- **Desacoplamiento Arquitectónico**: Centralización de constantes de embeddings y base vectorial (`MODELO_EMBEDDINGS`, `NOMBRE_COLECCION`, `RUTA_CHROMA_DEFAULT`) en `app/config.py`, eliminando la dependencia de `app/` hacia la carpeta `scripts/`.

### DevOps e Infraestructura
- **Optimización de Contenedor Docker**: Configuración de PyTorch CPU (`--index-url https://download.pytorch.org/whl/cpu`) en `app/Dockerfile`, disminuyendo el peso de la imagen de ~3.2 GB a ~450 MB al evitar descargar paquetes CUDA/NVIDIA innecesarios en Cloud Run.
- **Reglas de Contexto Docker**: Actualización de `.dockerignore` para excluir fuentes crudas (`data/raw/`, `data/processed/`) y permitir el empaquetado de la base vectorial indexada (`!chroma_db/**`).
- **Pipeline CI/CD**: Compatibilidad en `.github/workflows/semver.yml` para autenticación con `BUMP_TOKEN` frente a ramas protegidas.

---

## [0.2.0-SNAPSHOT-RC1] - 2026-10-31 (Semana 3)

### Backend
- **Base Vectorial y RAG Clínico**:
  - Ingesta reproducible (`scripts/ingest.py`) de la Guía OPS Dengue 2016 y Manual SIVE-Alerta del MSP Ecuador (págs. 95-100, sección 8.2.3.2).
  - Chunking semántico estructurado preservando encabezados y metadatos clínicos (`codigo_cie10`, `vigente`, `origen`, `seccion`).
  - Base vectorial persistente con **ChromaDB** y distancia coseno.
  - Embeddings multilingües con `intfloat/multilingual-e5-small` y prefijos normativos (`passage: ` para corpus y `query: ` para consultas).
  - Búsqueda híbrida con filtro por código exacto (`where_document={'$contains': ...}`) y filtrado previo por vigencia (`where={'vigente': True}`).
  - Exportación estructurada a `data/processed/fragmentos.json` y `data/processed/fragmentos.md`.
- **Agente de Alcance Controlado v2**:
  - Endpoint `/api/v2/chat` con orquestación de llamadas a herramientas (*Function Calling*).
  - Registro de lista cerrada de herramientas:
    - `consultar_guia_msp`: Búsqueda de evidencia clínica en ChromaDB.
    - `evaluar_signos_alarma`: Clasificación y triaje determinista.
    - `buscar_centro_salud`: Localización GeoSalud por ciudad o proximidad GPS (Haversine).
    - `notificar_contacto_emergencia`: Envío simulado de alerta médica a familiares.
  - Mecanismo **Human-in-the-Loop (HITL)**: Pausa obligatoria del agente cuando se detecta una acción con efectos secundarios (`notificar_contacto_emergencia`) y reanudación controlada mediante `/api/v2/chat/confirmar`.
  - Salvaguarda anti bucle infinito: Tope estricto de 5 vueltas con respuesta segura al alcanzar el límite.
- **Automatización y Triaje Clínico**:
  - Cinta transportadora de 7 estaciones (`app/flujo.py`) para triaje automatizado con cálculo de confianza clínica (umbral `0.85`).
  - Desvío a **Revisión Médica Humana** ante consultas vagas, intenciones ambiguas o baja confianza.
  - Endpoint HTTP `/herramientas/signos-alarma` para evaluación determinista con esquemas Pydantic estrictos.
- **Evaluación y Calidad**:
  - Pruebas automatizadas de agente, herramientas deterministas, retriever y cinta de automatización (`test_agent.py`, `test_retriever.py`, `test_flujo.py`, etc.).
  - Banco de preguntas doradas para benchmarking de RAG en `eval/`.

### Frontend
- **Integración de Agente v2 y Arbovirosis**:
  - Soporte de contratos de API para respuestas del agente v2 y estados extendidos de atención.
  - Flujo de interacción para confirmación de acciones Human-in-the-Loop.
  - Componentes de checklist actualizados con parámetros de vigilancia clínica.

### DevOps e Infraestructura
- Configuración de proxy OIDC en el contenedor frontend para comunicación segura con el backend privado en Cloud Run.

---

## [0.1.1] - 2026-10-24 (Semana 2)

### Backend
- **Cliente LLM Resiliente (`app/services/llm.py`)**:
  - Adaptador unificado para Gemini (`gemini-3.8-flash`) y Groq (`openai/gpt-oss-20b`) bajo el estándar de OpenAI.
  - Validación de salida en JSON estricto con Pydantic y reintento con mensaje de autocorrección.
  - Manejo de fallos transitorios (HTTP 429, timeouts, caídas) con reintentos exponenciales y jitter aleatorio.
  - Mecanismo de *Failover* automático con conmutación al proveedor de respaldo.
  - Registro de auditoría anónimo en `logs/llm.jsonl` (latencia, tokens de entrada/salida y fallos).
- **Seguridad y Persistencia (`app/services/seguridad.py`, `app/repositorio/historial.py`)**:
  - Memoria conversacional multi-turno aislada por `idSesion` con base SQLite (`historial.db`).
  - Protección contra *Prompt Injection* delimitando la consulta con `<consulta_usuario>`.
  - Limitador de tasa (*Rate Limiter*) por sesión con ventana deslizante (HTTP 429 y cabecera `Retry-After`).
  - Formato de error conforme al estándar RFC 9457 (*Problem Details*).
- **Prompts Versionados**:
  - Iteraciones clínicas `system_v1.md` a `system_v4.md` con pautas de abstención y derivación a centros de salud.

### Frontend
- **Aplicación Web React + Vite + TypeScript**:
  - Interfaz gráfica conversacional para orientación sobre síntomas de dengue.
  - Componentes modulares: `Cabecera`, `MensajeChat`, `AlertaEstado` y `ChecklistSignosAlarma`.
  - Semáforo visual para clasificación de riesgo (sin alarma, vigilancia, signos de alarma).
  - Cliente API tipado (`cliente.ts`, `esquema.ts`) para consumo de `/api/v1/chat`.
- **Pruebas y Accesibilidad**:
  - Cobertura de pruebas unitarias y de integración con Vitest y `@testing-library/react`.
  - Verificación de accesibilidad web (a11y) y estados de carga/error.
  - Script de seguridad `verificar-secretos.mjs` para prevenir fugas de tokens en el build estático.

### DevOps e Infraestructura
- **Docker Frontend**: Creación de `frontend/Dockerfile` con servidor Nginx y plantilla `nginx.conf.template`.
- **GCP Cloud Run**: Workflows de aprovisionamiento de infraestructura (`infra-gcp.yml`) y despliegue continuo (`deploy-gcp.yml`) con Secret Manager.

---

## [0.1.0] - 2026-10-17 (Semana 1)

### Backend
- **Inicialización de la API FastAPI (`app/main.py`)**:
  - Endpoints operativos de observabilidad: `/manage/health` (Liveness y Readiness) y `/manage/info` (metadatos del servicio).
  - Cumplimiento de especificación SemVer 2.0 con validación por expresión regular.
  - Pruebas unitarias de endpoints base con `pytest`.

### Frontend
- **Definición de Requisitos y Maquetación Inicial**:
  - Especificación de interfaces de usuario y mapa de navegación para orientación ciudadana.
  - Diseño de requisitos para GeoSalud (catálogo inicial de centros de salud en Ecuador).

### DevOps e Infraestructura
- **Automatización de Versionado SemVer**:
  - Pipeline de GitHub Actions `semver.yml` que ejecuta suite de pruebas y calcula la siguiente versión mediante `scripts/semver_bumper.py` en Pull Requests.
- **Gobernanza del Repositorio**:
  - Guías de contribución, plantillas de Pull Request y cumplimiento de la especificación *Conventional Commits* con `AGENTS.md`.
