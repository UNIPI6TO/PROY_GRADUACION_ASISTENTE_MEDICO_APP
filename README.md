# GuíaVital · Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis

> **Nombre Oficial / Nombre Corto (`APP_NAME`):** `GuíaVital`  
> **Versión Actual:** `0.1.0` (SemVer)  
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
| **Persistencia** | SQLite (`data/historial.db`) | Almacenamiento de los últimos turnos por `idSesion` mediante consultas parametrizadas |
| **Seguridad (OWASP LLM)** | `app/services/seguridad.py` + CORS | Delimitación anti-inyección (`<consulta_usuario>`), límite de tasa por sesión (`429 Too Many Requests` + `Retry-After`) y CORS restringido |
| **Observabilidad** | `logs/llm.jsonl` | Registro estructurado en JSON Lines con proveedor, modelo, latencia, intentos y tokens consumidos (sin texto del usuario ni PII) |

---

## Estructura del Proyecto

```text
PROY_GRADUACION_ASISTENTE_MEDICO_APP/
├── app/
│   ├── main.py                  # Aplicación FastAPI, endpoints (/api/v1/chat, /manage/health, /manage/info) y manejadores RFC 9457
│   ├── config.py                # Carga y validación de variables de entorno (.env) y catálogo de proveedores (gemini, groq, simulado)
│   ├── schemas.py               # Contratos Pydantic estrictos (Solicitud, RespuestaAsistente, RespuestaChat, ProblemaRFC9457)
│   ├── prompts/                 # Prompts del sistema versionados (system_v1.md a system_v4.md)
│   ├── repositorio/
│   │   └── historial.py         # RepositorioHistorial en SQLite aislado por idSesion
│   └── services/
│       ├── llm.py               # ClienteLLM con reintentos, backoff exponencial, validación JSON y fallback
│       └── seguridad.py         # LimitadorTasa (ventana deslizante) y delimitación contra Prompt Injection
├── frontend/
│   ├── src/
│   │   ├── api/                 # Cliente HTTP/SSE tipado (esquema OpenAPI), sanitización y manejo de errores RFC 9457
│   │   ├── components/          # Componentes UI (MensajeChat, ChecklistSignosAlarma, AlertaEstado)
│   │   ├── types/               # Máquina de 7 estados de interfaz (inactiva, enviando, recibiendo, completa, revision, reintentar, error)
│   │   ├── App.tsx              # Vista principal del asistente GuíaVital
│   │   └── main.tsx             # Punto de entrada React
│   ├── scripts/
│   │   └── verificar-secretos.mjs # Auditoría automática contra exposición de claves en el bundle frontend
│   ├── tests/                   # Suite Vitest + Testing Library + MSW (cliente, estados, seguridad y accesibilidad)
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   ├── primera_llamada.py       # Script de prueba rápida de conexión con el proveedor LLM
│   ├── servidor_simulado.py     # Proveedor local falso compatible con OpenAI para simular 429, lentitud y JSON roto
│   ├── demo_429.py              # Demostración en vivo de resiliencia ante errores 429 con y sin ClienteLLM
│   └── semver_bumper.py         # Automatización de versionado SemVer para CI/CD
├── data/
│   ├── raw/                     # Guías clínicas oficiales (MSP y OPS/OMS) en PDF y análisis de preguntas
│   ├── geosalud_ecuador.json    # Catálogo georreferenciado de establecimientos de salud
│   └── historial.db             # Base de datos SQLite generada en ejecución
├── eval/
│   └── entradas_prompts.csv     # Conjunto de entradas para evaluación comparativa de prompts
├── tests/                       # Pruebas automatizadas del backend con pytest y dobles (mocks)
│   ├── test_dengue.py           # Pruebas de /api/v1/chat, memoria SQLite, rate limit y seguridad
│   ├── test_llm.py              # Pruebas unitarias de ClienteLLM (reintentos, backoff, fallback, validación JSON)
│   ├── test_main.py             # Pruebas de /manage/health y /manage/info
│   └── test_semver_bumper.py    # Pruebas del calculador de versiones SemVer
├── docs/                        # Documentación de ingeniería (01-propuesta a 09-decisiones y evidencias)
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

---

## Endpoints de la API

| Método | Ruta | Descripción | Códigos de Respuesta |
|---|---|---|---|
| `POST` | `/api/v1/chat` | Procesa una consulta ciudadana con memoria por `idSesion`, delimitadores anti-inyección, límite de tasa y salida estructurada validada | `200 OK` (`RespuestaChat`), `422` (Validación), `429` (Rate Limit + `Retry-After`), `503` (Proveedor no disponible), `500` (Error interno) |
| `GET` | `/manage/health` | Diagnóstico operativo de *Liveness* y *Readiness* | `200 OK` (`status: UP`), `503 Service Unavailable` (`status: DOWN`) |
| `GET` | `/manage/info` | Retorna el nombre oficial (`GuíaVital`) y versión validada bajo SemVer (`0.1.0`) | `200 OK` |

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
| `tests/test_dengue.py` | Contrato `200` de `/api/v1/chat`, persistencia y memoria multi-turno en SQLite, aislamiento entre sesiones, *rate limit* `429` + cabecera `Retry-After`, delimitación `<consulta_usuario>`, validaciones `422`, errores `503`/`500` en formato RFC 9457 sin *stack trace*, abstención ante salida inválida y vigencia de `system_v4` |
| `tests/test_llm.py` | Validación de esquema JSON estricto, autocorrección en 1 intento, reintentos ante `429`/`503`/respuesta vacía, respeto de `Retry-After`, espera exponencial con *jitter* y conmutación al proveedor de respaldo |
| `tests/test_main.py` | Diagnóstico `/manage/health` (`200` UP / `503` DOWN) y cumplimiento de expresión regular SemVer en `/manage/info` |
| `tests/test_semver_bumper.py` | Reglas de incremento SemVer (*MAJOR*, *MINOR*, *PATCH*) según *Conventional Commits* y generación de versiones *SNAPSHOT-RC* |

### 2. Pruebas Automatizadas del Frontend (`Vitest` + `MSW`)
Dentro del directorio `frontend/`:

```bash
cd frontend
npm test
```
Verificación de ausencia de secretos en el código y configuración del frontend:
```bash
npm run verify:secrets
```

| Archivo de Prueba | Qué Valida |
|---|---|
| `frontend/tests/cliente.test.ts` | Consumo tipado de `/api/v1/chat`, manejo de errores RFC 9457 (`422`, `429` con lectura de `Retry-After`, `503`), streaming SSE por POST y cancelación inmediata con `AbortController` |
| `frontend/tests/estados.test.ts` | Transiciones de la máquina de 7 estados (`inactiva`, `enviando`, `recibiendo`, `completa`, `revision`, `reintentar`, `error`), cuenta regresiva de reintento y parser de eventos SSE fragmentados |
| `frontend/tests/seguridad-y-ui.test.tsx` | Neutralización de payloads XSS en respuestas del modelo (OWASP LLM05), bloqueo de enlaces `javascript:`/`data:`, generación de sesión anónima en `sessionStorage`, anuncios WAI-ARIA (`role="alert"`) y activación del checklist determinista de signos de alarma |

---

## Documentación Adicional

En el directorio [`docs/`](docs/) se encuentra el detalle de ingeniería del sistema:
- [`docs/01-propuesta.md`](docs/01-propuesta.md): Propuesta y alcance del caso 05.
- [`docs/02-requisitos.md`](docs/02-requisitos.md): Requisitos funcionales, no funcionales y de seguridad.
- [`docs/03-arquitectura.md`](docs/03-arquitectura.md): Diagramas C4 (Contexto y Contenedores), capas del sistema y estrategia de pruebas.
- [`docs/04-fuentes.md`](docs/04-fuentes.md): Corpus normativo oficial del MSP y la OPS/OMS.
- [`docs/05-prompts.md`](docs/05-prompts.md): Evolución y evaluación comparativa de los prompts del sistema (`system_v1` a `system_v4`).
- [`docs/09-decisiones.md`](docs/09-decisiones.md): Registro de Decisiones de Arquitectura (ADRs 001 a 004).
