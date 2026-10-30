# GuíaVital · Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis

> **Nombre Oficial / Nombre Corto (`APP_NAME`):** `GuíaVital`  
> **Versión Actual:** `0.2.0` (SemVer)  
> **Caso:** 05 - Grupo 5 · Seminario de Titulación UNIANDES  
> **Repositorio:** `https://github.com/UNIPI6TO/PROY_GRADUACION_ASISTENTE_MEDICO_APP`

---

## Equipo

| Integrante | Rol |
|---|---|
| **Luis Cahuana** | Tech Lead |
| **Wilson Salinas** | Builder |
| **Rafael Minaya** | QA / Seguridad |

---

## Propósito del Sistema

**GuíaVital** es un asistente conversacional de orientación preventiva en salud pública y triaje determinista de signos de alarma frente al dengue y arbovirosis en el Ecuador (zonas endémicas de la Costa y Amazonía). Está sustentado de manera estricta y exclusiva en los lineamientos oficiales del **Ministerio de Salud Pública del Ecuador (MSP)** y la **Organización Panamericana de la Salud (OPS/OMS)**.

### Alcance Positivo
- **Orientación informativa contextualizada:** Responde consultas sobre prevención, erradicación de criaderos del mosquito *Aedes aegypti*, hidratación oral, fases de la enfermedad y síntomas habituales según las guías del MSP y la OPS.
- **Trazabilidad y abstención responsable:** Estructura cada respuesta en JSON validado (`RespuestaAsistente`), indicando explícitamente si el sistema debe abstenerse (`se_abstiene: true`), a qué entidad derivar (`derivar_a`) y las fuentes documentales (`fuentes`).
- **Checklist determinista de signos de alarma:** Triaje algorítmico interactivo en interfaz para evaluar signos de peligro (dolor abdominal intenso y continuo, vómitos persistentes, sangrado de mucosas, letargo o irritabilidad, hipotensión postural/mareos, dificultad respiratoria) sin delegar el cálculo de riesgo al LLM.
- **Derivación médica inmediata:** Ante la detección de cualquier signo de alarma o grupo de riesgo (embarazadas, lactantes, adultos mayores o personas con comorbilidades), indica acudir de inmediato al **Centro de Salud MSP** más cercano o llamar al **ECU-911**.
- **Memoria conversacional aislada por sesión:** Persistencia multi-turno en SQLite (`data/historial.db`) asociada únicamente a un identificador anónimo de sesión (`idSesion`).
- **Endpoints de gestión operativa:** Diagnóstico de salud (`GET /manage/health`) y metadatos con validación SemVer (`GET /manage/info`).

### Alcance Negativo Estricto (Guardrails)
- **NUNCA** emite diagnósticos médicos ni confirma o descarta enfermedades.
- **NUNCA** prescribe ni recomienda fármacos, dosis o remedios caseros (advierte explícitamente contra la automedicación con aspirina, ibuprofeno, naproxeno, diclofenaco, metamizol, corticoides o antibióticos).
- **NUNCA** reemplaza la consulta médica presencial ni exámenes de laboratorio.
- **NUNCA** almacena ni registra datos personales identificables (arquitectura *Zero-PII* alineada con la LOPDP de Ecuador).

---

## Arquitectura y Tecnologías

| Componente | Tecnología | Descripción |
|---|---|---|
| **Frontend** | React 19 + TypeScript + Vite | Interfaz web accesible (WCAG 2.2), máquina de 7 estados, soporte SSE, cancelación con `AbortController`, sanitización XSS (`DOMPurify`) y checklist determinista de signos de alarma |
| **Backend API** | FastAPI (Python 3.12+) + Pydantic v2 | API RESTful con inyección de dependencias (`Depends`), validación estricta (`extra="forbid"`) y errores estándar **RFC 9457** (`application/problem+json`) |
| **Cliente LLM Resiliente** | SDK `openai` (compatible con Gemini y Groq) | Salida estructurada JSON validada, 1 intento de autocorrección automática, reintentos con espera exponencial + *jitter*, respeto de `Retry-After` y conmutación automática (*fallback*) |
| **Proveedor Principal** | Google Gemini (`gemini-3.8-flash` / `gemini-2.0-flash`) | Generación principal de orientación preventiva con baja temperatura |
| **Proveedor de Respaldo** | Groq (`openai/gpt-oss-20b` / `llama-3.1-8b-instant`) | Conmutación automática ante caídas, errores definitivos o *timeouts* del proveedor principal |
| **Base Vectorial (RAG)** | ChromaDB (`chromadb`) local persistente | Colección `guia_vital_dengue` con espacio métrico coseno (`cosine`), persistencia local en SQLite + HNSW sin costos de nube |
| **Modelo de Embeddings** | `intfloat/multilingual-e5-small` | Modelo denso multilingüe optimizado en español (384 dimensiones, asimétrico con prefijos `query: ` y `passage: `) |
| **Pipeline de Ingesta** | PyMuPDF (`fitz`) + Chunking Jerárquico | Limpieza de marcas de agua, delimitación exacta por regex, inyección de encabezado contextual y exportación a `data/processed/` |
| **Persistencia** | SQLite (`data/historial.db`) | Almacenamiento de los últimos turnos por `idSesion` mediante consultas parametrizadas |
| **Seguridad (OWASP LLM)** | `app/services/seguridad.py` + CORS | Delimitación anti-inyección (`<consulta_usuario>`), límite de tasa por sesión (`429 Too Many Requests` + `Retry-After`) y CORS restringido |
| **Observabilidad** | `logs/llm.jsonl` | Registro estructurado en JSON Lines con proveedor, modelo, latencia, intentos y tokens consumidos (sin texto del usuario ni PII) |

---

## Estructura del Proyecto

```text
PROY_GRADUACION_ASISTENTE_MEDICO_APP/
├── app/
│   ├── main.py                  # Aplicación FastAPI, endpoints v1, v2 y herramientas (/herramientas/signos-alarma)
│   ├── flujo.py                 # Cinta de automatización de 7 estaciones con umbral de confianza (0.85)
│   ├── config.py                # Carga de variables de entorno (.env), catálogo de proveedores y config/parametros.yaml
│   ├── schemas.py               # Contratos Pydantic estrictos (Solicitud, RespuestaAsistente, RespuestaChat, RespuestaChatV2)
│   ├── prompts/                 # Prompts del sistema versionados (system_v1.md a system_v4.md, system_agente.md)
│   ├── repositorio/
│   │   └── historial.py         # RepositorioHistorial en SQLite aislado por idSesion
│   ├── services/
│   │   ├── llm.py               # ClienteLLM con reintentos, backoff exponencial, validación JSON, tools y fallback
│   │   ├── retriever.py         # BuscadorVectorial en ChromaDB con prefijos E5, filtros de vigencia y búsqueda híbrida
│   │   ├── agent.py             # Bucle del Agente de Alcance Controlado (PERMITIDAS, REQUIEREN_OK, MAX_ITER = 6)
│   │   └── seguridad.py         # LimitadorTasa (ventana deslizante) y delimitación contra Prompt Injection
│   └── tools/                   # Herramientas modulares de alcance controlado (una por archivo)
│       ├── consultar_guia_msp.py         # Libre: Búsqueda documental RAG en guías clínicas oficiales del MSP
│       ├── evaluar_signos_alarma.py     # Libre: Comparación determinista contra signos de alarma del MSP (Modelos HttpIn/Out)
│       ├── buscar_centro_salud.py       # Libre: GeoSalud Ecuador con Haversine y filtro de Emergencia 24h
│       └── notificar_contacto_emergencia.py # Con confirmación: Aviso a familiar/contacto (requiere autorización humana)
├── bruno/
│   └── GuiaVital/               # Colección de pruebas manuales para Bruno API Client (ignorada en Git)
│       ├── environments/        # Entornos Local (127.0.0.1:8000) y Nube
│       └── *.bru                # Peticiones preconfiguradas (Health, Info, Signos de Alarma 200/422, Chat V2)
├── config/
│   └── parametros.yaml          # Parámetros operativos desacoplados (umbral_confianza: 0.85, signos oficiales, topes)
├── frontend/
│   ├── src/
│   │   ├── api/                 # Cliente HTTP/SSE tipado (esquema OpenAPI), sanitización y manejo de errores RFC 9457
│   │   ├── components/          # Componentes UI (MensajeChat, ChecklistSignosAlarma, AlertaEstado)
│   │   ├── types/               # Máquina de 7 estados de interfaz
│   │   ├── App.tsx              # Vista principal del asistente GuíaVital
│   │   └── main.tsx             # Punto de entrada React
│   ├── scripts/
│   │   └── verificar-secretos.mjs # Auditoría automática contra exposición de claves en el bundle frontend
│   ├── tests/                   # Suite Vitest + Testing Library + MSW
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   ├── ingest.py                # Pipeline de ingesta reproducible (PDFs -> Chunks semánticos -> ChromaDB)
│   ├── primera_llamada.py       # Script de prueba rápida de conexión con el proveedor LLM
│   ├── servidor_simulado.py     # Proveedor local falso compatible con OpenAI para simular 429, lentitud y JSON roto
│   ├── demo_429.py              # Demostración en vivo de resiliencia ante errores 429 con y sin ClienteLLM
│   └── semver_bumper.py         # Automatización de versionado SemVer para CI/CD
├── data/
│   ├── raw/                     # Guías clínicas oficiales (Guia-dengue-OPS-2016.pdf, manual_de_procedimientos_sive-alerta.pdf)
│   ├── processed/               # fragmentos.md y fragmentos.json (161 fragmentos exportados y trazables)
│   ├── geosalud_ecuador.json    # Catálogo georreferenciado de establecimientos de salud
│   └── historial.db             # Base de datos SQLite generada en ejecución
├── chroma_db/                   # Base de datos vectorial persistente (161 fragmentos indexados con HNSW + SQLite)
├── eval/
│   ├── casos_flujo.jsonl        # Conjunto dorado de 20 casos para calibración de la cinta (0 errores silenciosos)
│   ├── preguntas_rag.jsonl      # 20 preguntas de evaluación RAG (15 documentadas, 5 de abstención controlada)
│   ├── evaluar.py               # Evaluador integral de metas de calidad para CI (RAG top-3 >= 85%, cinta <= 30% revisión)
│   ├── preguntas.csv            # Conjunto de 20 preguntas clínicas de referencia con validación Hit@k
│   ├── run_eval.py              # Evaluador de recuperación vectorial (Hit@1 = 85%, Hit@5 = 100%)
│   └── entradas_prompts.csv     # Conjunto de entradas para evaluación comparativa de prompts
├── tests/                       # Pruebas automatizadas del backend con pytest y dobles (mocks)
│   ├── test_flujo.py            # Pruebas de confianza, umbral (0.85) y decisiones de desvío de la cinta
│   ├── test_endpoint_signos_alarma.py # Pruebas del endpoint HTTP determinista (casos 200 y validación 422)
│   ├── test_dengue.py           # Pruebas de /api/v1/chat, memoria SQLite, rate limit y seguridad
│   ├── test_api_v2.py           # Pruebas funcionales de endpoints v2 (/api/v2/chat y /api/v2/chat/confirmar)
│   ├── test_agent.py            # Pruebas del bucle del agente (camino feliz, lista cerrada, tope y confirmación)
│   ├── test_consultar_guia_msp.py # Pruebas de herramienta RAG con Pydantic y determinismo
│   ├── test_evaluar_signos_alarma.py # Pruebas deterministas de detección de signos de alarma
│   ├── test_buscar_centro_salud.py # Pruebas de GeoSalud con orden por distancia Haversine
│   ├── test_retriever.py        # Pruebas de ingesta, prefijos E5, código exacto y filtro de vigencia
│   ├── test_llm.py              # Pruebas unitarias de ClienteLLM (reintentos, backoff, fallback, validación JSON)
│   ├── test_main.py             # Pruebas de /manage/health y /manage/info
│   └── test_semver_bumper.py    # Pruebas del calculador de versiones SemVer
├── docs/                        # Documentación de ingeniería (01-propuesta a 11-plan-de-calidad y evidencias)
├── .env.example                 # Plantilla de variables de entorno del backend
├── requirements.txt             # Dependencias bloqueadas del backend Python
└── README.md
```

---

## Instalación y Configuración

### Requisitos Previos
- **Python 3.12+** (compatible con Python 3.11+)
- **Node.js 20+** y **npm** (para el frontend en React + Vite)

### 1. Configurar el Backend

1. Instalar las dependencias de Python desde la raíz del proyecto:
```bash
pip install -r requirements.txt
```

2. Crear el archivo `.env` a partir de la plantilla `.env.example`:
```bash
cp .env.example .env
```

3. Configurar las variables de entorno en `.env`:

| Variable | Ejemplo / Por Defecto | Descripción |
|---|---|---|
| `LLM_PROVIDER` | `gemini` | Proveedor principal (`gemini`, `groq` o `simulado`) |
| `LLM_MODEL` | `gemini-3.8-flash` | Modelo principal de Gemini |
| `GEMINI_API_KEY` | `AIzaSy...` | Clave de API de Google AI Studio (obligatoria si `LLM_PROVIDER=gemini`) |
| `LLM_FALLBACK_PROVIDER` | `groq` | Proveedor de respaldo opcional (`groq` o `gemini`) |
| `LLM_FALLBACK_MODEL` | `openai/gpt-oss-20b` | Modelo del proveedor de respaldo |
| `GROQ_API_KEY` | `gsk_...` | Clave de API de Groq (obligatoria si se activa `groq`) |
| `LLM_TIMEOUT_SECONDS` | `30` | Tiempo máximo de espera por llamada al proveedor (segundos) |
| `LLM_MAX_OUTPUT_TOKENS` | `2048` | Límite máximo de tokens de salida |
| `RATE_LIMIT_PER_MINUTE` | `10` | Solicitudes máximas por minuto por `idSesion` |
| `HISTORIAL_DB` | `data/historial.db` | Ruta del archivo SQLite para el historial de sesiones |
| `CORS_ORIGINS` | `http://localhost:8501,http://localhost:5173` | Orígenes permitidos por CORS separados por coma |

### 2. Configurar el Frontend

1. Ingresar al directorio `frontend/` e instalar dependencias:
```bash
cd frontend
npm install
```

2. (Opcional) Crear el archivo `frontend/.env` a partir de `frontend/.env.example`:
```bash
cp .env.example .env
```
> **Regla de Seguridad (OWASP LLM02):** `frontend/.env` solo debe contener `VITE_API_URL=http://localhost:8000`. **NUNCA** coloque claves de API (`GEMINI_API_KEY`, `GROQ_API_KEY`) en el frontend.

---

## Cómo Ejecutar el Sistema

### 1. Levantar el Backend (FastAPI)
Desde la raíz del proyecto:
```bash
uvicorn app.main:app --reload --port 8000
```
- **API Base:** `http://localhost:8000`
- **Documentación Interactiva (Swagger UI):** `http://localhost:8000/docs`
- **Esquema OpenAPI:** `http://localhost:8000/openapi.json`

### 2. Levantar el Frontend (React + Vite)
En una nueva terminal, dentro de la carpeta `frontend/`:
```bash
cd frontend
npm run dev
```
- **Aplicación Web:** `http://localhost:5173`

### 3. Scripts de Demostración y Resiliencia
- **Primera llamada al modelo:**
  ```bash
  python scripts/primera_llamada.py
  ```
- **Demostración en vivo de manejo de errores `429` (sin gastar cuota real, usando servidor simulado):**
  ```bash
  python scripts/demo_429.py
  ```
- **Servidor simulado independiente (en `http://127.0.0.1:8099/v1`):**
  ```bash
  python scripts/servidor_simulado.py --limite 5 --ventana 10
  ```

### 4. Ingesta y Evaluación de la Base Vectorial (RAG)
- **Ejecutar el pipeline de ingesta reproducible (PDFs oficiales -> ChromaDB):**
  ```bash
  python -m scripts.ingest
  ```
- **Ejecutar la evaluación cuantitativa de recuperación vectorial (Hit@1 y Hit@5):**
  ```bash
  python -m eval.run_eval
  ```

---

## Endpoints de la API

| Método | Ruta | Descripción | Códigos de Respuesta |
|---|---|---|---|
| `POST` | `/herramientas/signos-alarma` | **Herramienta Determinista (Semana 3):** Evaluación algorítmica de signos de alarma de dengue según la Guía del MSP con modelos Pydantic de entrada y salida | `200 OK` (`EvaluarSignosAlarmaHttpOut`), `422 Unprocessable Content` |
| `POST` | `/api/v2/chat` | **v2 (Semana 3):** Agente de alcance controlado con Function Calling, hasta 6 iteraciones, herramientas modulares y parada por confirmación | `200 OK` (`RespuestaChatV2`), `422`, `429`, `503`, `500` |
| `POST` | `/api/v2/chat/confirmar` | **v2 (Semana 3):** Reanuda el agente tras la autorización o rechazo humano de una acción sensible | `200 OK` (`RespuestaChatV2`), `422`, `429`, `503`, `500` |
| `POST` | `/api/v1/chat` | **v1 (Semana 2):** Consulta de una sola llamada con memoria SQLite, delimitación anti-inyección, rate limit y salida JSON fija | `200 OK` (`RespuestaChat`), `422`, `429`, `503`, `500` |
| `GET` | `/manage/health` | Diagnóstico operativo de *Liveness* y *Readiness* | `200 OK` (`status: UP`), `503 Service Unavailable` (`status: DOWN`) |
| `GET` | `/manage/info` | Retorna el nombre oficial (`GuíaVital`) y versión validada bajo SemVer (`0.2.0`) | `200 OK` |

### Ejemplo de Herramienta Determinista (`POST /herramientas/signos-alarma`)

**Solicitud Válida (200 OK):**
```json
{
  "dias_fiebre": 4,
  "dolor_abdominal": true,
  "vomitos_persistentes": false,
  "sangrado": false,
  "edad": 34
}
```

**Respuesta (`200 OK`):**
```json
{
  "signos_presentes": 1,
  "nivel": "alarma",
  "recomendacion": "Acudir hoy al centro de salud más cercano",
  "fuente": "Guía de dengue del MSP, sección signos de alarma"
}
```

**Rechazo de Frontera Pydantic (`422 Unprocessable Content`):**
Al enviar un valor biológicamente imposible (ej. `"edad": 800` o `"dias_fiebre": 45`), Pydantic v2 intercepta la petición antes de que toque la lógica de negocio:
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "edad"],
      "msg": "Input should be less than or equal to 120",
      "input": 800,
      "ctx": { "le": 120 }
    }
  ]
}
```

---

### Cinta del Flujo Automatizado con Umbral (`app/flujo.py`)

Para procesos masivos de entrada no estructurada (como formularios web de triaje), GuíaVital implementa una **cinta fija de 7 estaciones** regulada por un umbral de confianza calibrado en `config/parametros.yaml` (`umbral_confianza: 0.85`):

```
[1. Disparador] ──> [2. Clasificar] ──> [3. Umbral >= 0.85?] ──┬─ SI ──> [4. Extraer] ──> [5. Reglas MSP] ──> [7. Actuar]
                                                                │
                                                                └─ NO ──> [6. Revisión Humana Médica]
```

* **Calibración con Conjunto Dorado (`eval/casos_flujo.jsonl`):** Sobre 20 casos clínicos reales, el flujo resuelve el **70% de forma automática**, deriva el **30% a revisión médica**, y garantiza estrictamente **0 errores silenciosos**.


### Agente de Alcance Controlado (v2)

El agente opera bajo **tres decisiones estrictas en código** (no delegadas al prompt ni modificables por el usuario o documentos):
1. **Lista cerrada (`PERMITIDAS`):** Solo puede invocar las herramientas registradas en `app/tools/` (`consultar_guia_msp`, `evaluar_signos_alarma`, `buscar_centro_salud`, `notificar_contacto_emergencia`). Cualquier función no listada (como `diagnosticar` o inventada) es rechazada automáticamente por el servidor con error.
2. **Tope de vueltas (`MAX_ITER = 6`):** Impide bucles infinitos y costos no planificados. Si alcanza la sexta iteración sin respuesta de texto, corta con mensaje de escape controlado.
3. **Confirmación humana (`REQUIEREN_OK`):** Acciones que modifican el exterior o salen del sistema (`notificar_contacto_emergencia`) pausan el bucle en `requiere_confirmacion`, mostrando destinatario y contenido en la UI para su aprobación o rechazo explícito.

### Ejemplo de Solicitud y Respuesta (`POST /api/v2/chat`)

**Solicitud:**
```json
{
  "idSesion": "sesion-ciudadano-02",
  "texto": "Vivo en Guayaquil, tengo vómitos constantes y dolor de abdomen muy fuerte. ¿A dónde voy?"
}
```

**Respuesta (`200 OK` - Estado Completado con Fuentes y Centros):**
```json
{
  "idSesion": "sesion-ciudadano-02",
  "estado": "completado",
  "respuesta": "Presenta signos de alarma críticos (dolor abdominal intenso y continuo, vómitos persistentes). Acuda inmediatamente al Hospital General Guasmo Sur (Av. Cacique Tomalá y Vía Perimetral) o al Hospital Universitario, ambos con Emergencia 24h activa. No se automedique.",
  "accion_pendiente": null,
  "fuentes": [
    {
      "documento": "Guia-dengue-OPS-2016.pdf",
      "seccion": "Signos de alarma y criterios de hospitalización"
    }
  ],
  "vueltas_usadas": 3
}
```

### Ejemplo de Solicitud y Respuesta (`POST /api/v1/chat`)

**Solicitud:**
```json
{
  "idSesion": "sesion-ciudadano-01",
  "texto": "Mi hijo tiene fiebre alta desde hace dos días y dolor abdominal continuo, ¿qué le puedo dar?"
}
```

**Respuesta (`200 OK`):**
```json
{
  "respuesta": "El dolor abdominal intenso y continuo es un signo de alarma crítico del dengue. No administre aspirina, ibuprofeno ni ningún medicamento sin prescripción médica. Acuda de inmediato al servicio de urgencias o centro de salud más cercano.",
  "se_abstiene": false,
  "derivar_a": "Centro de Salud MSP / Emergencias 911",
  "fuentes": [],
  "proveedor": "gemini"
}
```

> Todos los errores HTTP (`422`, `429`, `503`, `500`) se entregan bajo el estándar **RFC 9457 (`application/problem+json`)** sin filtrar trazas internas (*stack traces*) ni rutas del servidor.

---

## Cómo Probar

### 1. Pruebas Automatizadas del Backend (`pytest`)
Las pruebas del backend utilizan dobles (*mocks*) del cliente LLM, base de datos SQLite en memoria (`:memory:`) y relojes simulados, por lo que **se ejecutan en ~1.5 segundos sin conexión a internet ni consumo de cuota de API**:

```bash
pytest -q
```
Para salida detallada:
```bash
pytest -v
```

| Archivo de Prueba | Qué Valida |
|---|---|
| `tests/test_flujo.py` | Cinta de 7 estaciones (`app/flujo.py`): cálculo de confianza, compuerta por umbral 0.85, casos automáticos vs revisión y calibración sin errores silenciosos |
| `tests/test_endpoint_signos_alarma.py` | Endpoint HTTP determinista (`POST /herramientas/signos-alarma`): respuestas 200 (alarma, vigilancia, sin alarma) y validación Pydantic 422 |
| `tests/test_api_v2.py` | Endpoints v2 (`/api/v2/chat` y `/api/v2/chat/confirmar`): flujo conversacional del agente, respuesta directa y pausa para confirmación humana |
| `tests/test_agent.py` | Bucle del agente (`app/services/agent.py`): camino feliz, lista cerrada (rechazo de `diagnosticar`), corte por `MAX_ITER = 6` y flujo de confirmación |
| `tests/test_consultar_guia_msp.py` | Herramienta RAG: validación de longitud con Pydantic, conexión con `BuscadorVectorial` y determinismo de resultados |
| `tests/test_evaluar_signos_alarma.py` | Herramienta determinista: normalización de texto y cruce contra los signos de alarma oficiales de `config/parametros.yaml` |
| `tests/test_buscar_centro_salud.py` | Herramienta GeoSalud: filtro por ciudad, cálculo de distancias en km con Haversine y disponibilidad de Emergencia 24h |
| `tests/test_dengue.py` | Contrato `200` de `/api/v1/chat`, persistencia y memoria multi-turno en SQLite, aislamiento entre sesiones, *rate limit* `429` + cabecera `Retry-After`, delimitación `<consulta_usuario>`, validaciones `422`, errores `503`/`500` en formato RFC 9457 sin *stack trace*, abstención ante salida inválida y vigencia de `system_v4` |
| `tests/test_retriever.py` | Extracción de páginas 95 a 100 de SIVE-Alerta, exclusión de referencias bibliográficas de OPS 2016, asimetría de prefijos E5 (`query: ` / `passage: `), orden por distancia coseno, búsqueda híbrida por código exacto (`CIE-10 A 91`) y filtro por vigencia (`vigente: True`) |
| `tests/test_llm.py` | Validación de esquema JSON estricto, autocorrección en 1 intento, reintentos ante `429`/`503`/respuesta vacía, respeto de `Retry-After`, espera exponencial con *jitter* y conmutación al proveedor de respaldo |
| `tests/test_main.py` | Diagnóstico `/manage/health` (`200` UP / `503` DOWN) y cumplimiento de expresión regular SemVer en `/manage/info` |
| `tests/test_semver_bumper.py` | Reglas de incremento SemVer (*MAJOR*, *MINOR*, *PATCH*) según *Conventional Commits* y generación de versiones *SNAPSHOT-RC* |

### 2. Ejecutar Evaluación de Calidad en CI (`eval/evaluar.py`)
Evalúa cuantitativamente el acierto del RAG top-3 y la cinta de automatización con umbral de confianza:
```bash
python eval/evaluar.py
```
* **Salida esperada:** RAG acierto top-3: 87% | Flujo a revisión: 30% | Errores silenciosos: 0.

### 3. Inspeccionar la Confianza en Consola (`pytest -v -s`)
Permite visualizar caso por caso la confianza calculada y el comportamiento del umbral:
```bash
pytest tests/test_flujo.py -v -s
```

### 4. Pruebas Manuales con Bruno API Client
La colección de pruebas reside en `bruno/GuiaVital/` (excluida del repositorio vía `.gitignore`).
1. Abrir **Bruno** y seleccionar *Open Collection* apuntando a la carpeta `bruno/GuiaVital/`.
2. Seleccionar el entorno en la esquina superior derecha:
   - **`Local`:** `http://127.0.0.1:8000` (desarrollo local).
   - **`Nube`:** URL del backend desplegado en la nube.
3. Ejecutar las peticiones preparadas:
   - `01 - Health Check` (`GET /manage/health`)
   - `02 - App Info` (`GET /manage/info`)
   - `03 - Evaluar Signos Alarma (200 OK)` (`POST /herramientas/signos-alarma`)
   - `04 - Evaluar Signos Alarma (422 Error)` (`POST /herramientas/signos-alarma`)
   - `05 - Chat V2 (Agente)` (`POST /api/v2/chat`)

### 5. Pruebas Automatizadas del Frontend (`Vitest` + `MSW`)
Dentro del directorio `frontend/`:

```bash
cd frontend
npm test
```
Verificación de ausencia de secretos en el código y configuración del frontend:
```bash
npm run verify:secrets
```

---

## Documentación Adicional

En el directorio [`docs/`](docs/) se encuentra el detalle de ingeniería del sistema:
- [`docs/01-propuesta.md`](docs/01-propuesta.md): Propuesta y alcance del caso 05.
- [`docs/02-requisitos.md`](docs/02-requisitos.md): Requisitos funcionales, no funcionales y de seguridad.
- [`docs/03-arquitectura.md`](docs/03-arquitectura.md): Diagramas C4 (Contexto y Contenedores), capas del sistema y estrategia de pruebas.
- [`docs/04-fuentes.md`](docs/04-fuentes.md): Corpus normativo oficial del MSP y la OPS/OMS.
- [`docs/05-prompts.md`](docs/05-prompts.md): Evolución y evaluación comparativa de los prompts del sistema (`system_v1` a `system_v4`).
- [`docs/09-decisiones.md`](docs/09-decisiones.md): Registro de Decisiones de Arquitectura (ADRs 001 a 004).
- [`docs/10-automatizacion.md`](docs/10-automatizacion.md): **ADR de Flujo Automatizado con IA (Semana 3)**: decisiones sobre la cinta fija, umbral 0.85 y prevención de errores silenciosos.
- [`docs/11-plan-de-calidad.md`](docs/11-plan-de-calidad.md): **Plan de Calidad y Evaluación (Semana 3)**: métricas de RAG, agente, cinta y cobertura mínima en CI (>= 85%).
- [`docs/evidencias/semana-3/README.md`](docs/evidencias/semana-3/README.md): **Bitácora y Evidencias de la Semana 3**: ejecución de pruebas, resultados de `eval/evaluar.py` y guía de revisión.
