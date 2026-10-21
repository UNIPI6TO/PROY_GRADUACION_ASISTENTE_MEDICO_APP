# GuíaVital · Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis

> **Nombre Oficial / Nombre Corto (`APP_NAME`):** `GuíaVital`  
> **Versión Actual:** `0.1.0` (SemVer)  
> **Caso:** 05 - Grupo 5 · Seminario de Titulación UNIANDES

## Propósito
El propósito del sistema es servir como un canal digital directo, validado y accesible para la orientación informativa en salud pública y el triaje determinista de signos de alarma frente al dengue y arbovirosis en Ecuador (zonas endémicas de la Costa y Amazonía), sustentado de manera estricta y exclusiva en la documentación oficial del Ministerio de Salud Pública del Ecuador (MSP) y la Organización Panamericana de la Salud (OPS/OMS).

### Alcance Positivo
- **Orientación informativa contextualizada:** Responder consultas sobre medidas preventivas, erradicación de criaderos del mosquito *Aedes aegypti*, fases de la enfermedad y síntomas habituales, basándose de forma exclusiva en la documentación oficial del MSP y OPS.
- **Trazabilidad y citación documental obligatoria:** Cada respuesta generada incluye fuente oficial, documento, acápite y página de referencia.
- **Lista de verificación (Checklist) determinista de signos de alarma:** Triaje algorítmico guiado en código Python para evaluar la presencia de signos de peligro (dolor abdominal continuo, vómitos persistentes, sangrado de mucosas, letargo/irritabilidad, hipotensión postural, acumulación de líquidos).
- **Derivación médica inmediata:** Al detectar al menos un signo de alarma, el sistema interrumpe la orientación y genera instrucciones de traslado urgente al centro de salud más cercano o llamar al ECU-911.
- **Ubicación de establecimientos de salud:** Consulta mediante herramientas deterministas del catálogo georreferenciado oficial (`data/geosalud_ecuador.json`).
- **Endpoints de gestión operativa:** Endpoints `/manage/health` (diagnóstico de liveness y readiness) y `/manage/info` (información y versión SemVer).

### Alcance Negativo Estricto
- NUNCA emitirá diagnósticos médicos.
- NUNCA prescribirá ni recomendará fármacos, dosis o remedios caseros (con advertencia explícita contra aspirina, ibuprofeno y otros AINEs).
- NUNCA reemplazará la consulta clínica presencial ni exámenes de laboratorio.
- NUNCA calculará riesgos mediante el LLM en texto libre.

---

## Instalación

### Requisitos Previos
- Python 3.12 (especificado en `AGENTS.md`).

### Instalación del Backend
1. Instalar las dependencias oficiales del backend:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno:
Copiar `.env.example` a `.env` y configurar los valores requeridos (`APP_ENV`, `PORT`, `HOST`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `CHROMA_PERSIST_DIR`, `GEOSALUD_DATA_PATH`, `RELEVANCE_THRESHOLD`, `TOP_K_CHUNKS`).

### Instalación del Frontend
- **FALTA**: En los archivos del proyecto se menciona `frontend/` (Streamlit / Angular PWA), pero actualmente la carpeta y sus archivos de configuración y dependencias no existen en el repositorio.

### Instalación con Docker
- **FALTA**: En la estructura descrita en `AGENTS.md` se lista `Dockerfile`, pero el archivo no existe en el repositorio.

---

## Cómo Ejecutar

### Backend en Local
Para levantar el servidor backend con recarga automática:
```bash
uvicorn app.main:app --reload --port 8000
```

Endpoints disponibles:
- `GET /manage/health`: Estado de salud de la aplicación (Liveness y Readiness).
- `GET /manage/info`: Información y metadatos del sistema (retorna el nombre corto `GuíaVital` y la versión SemVer).

### Frontend
- **FALTA**: No existen archivos ejecutables de frontend en el repositorio.

### Ingesta de Datos
- **FALTA**: En la estructura de `AGENTS.md` se indica `scripts/ingest.py`, pero el script no existe en el repositorio.

---

## Cómo Probar

### Pruebas Unitarias del Backend
Ejecutar la suite de pruebas unitarias con pytest:
```bash
pytest -q
```

Para ejecución en modo detallado:
```bash
pytest -v
```

Pruebas implementadas en `tests/test_main.py`:
- `test_check_health_liveness_and_readiness_up`: Valida código HTTP 200 y estados "UP" en liveness y readiness.
- `test_check_health_readiness_down_on_failure`: Valida código HTTP 503 y estado "DOWN" en readiness ante falla de sonda dependiente.
- `test_get_info_semver_format_and_app_name`: Valida código HTTP 200, concordancia del nombre corto oficial (`GuíaVital`) y cumplimiento de la expresión regular SemVer.

### Pruebas de Evaluación RAG y Casos de Cálculo
- **FALTA**: En la estructura de `AGENTS.md` se listan `eval/preguntas.csv`, `eval/casos_calculo.csv` y `eval/run_eval.py`, pero la carpeta `eval/` no existe en el repositorio.
