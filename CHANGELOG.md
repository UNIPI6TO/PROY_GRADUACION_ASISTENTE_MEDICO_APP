# Changelog · GuíaVital

Todas las modificaciones notables de este proyecto se documentan de forma independiente para cada aplicación:

- 🖥️ **Backend (FastAPI, RAG, Agente Clínico, Base Vectorial)**: [app/CHANGELOG.md](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md)
- 🌐 **Frontend (React, Vite, TypeScript, Componentes)**: [frontend/CHANGELOG.md](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md)

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

---

## [0.6.1] - 2026-11-16

### Backend, Agente Clínico y Contenedor
- **Inclusión de Catálogo GeoSalud en Docker**: Empaquetado explícito de `data/geosalud_ecuador.json` en `app/Dockerfile` para garantizar disponibilidad de coordenadas y direcciones en Cloud Run.
- **Detección Proactiva de Ubicación**: Respaldo determinista en `app/services/agent.py` para identificar ciudades y provincias ecuatorianas mencionadas en la consulta y ejecutar `buscar_centro_salud` cuando el usuario requiere atención presencial.
- **Aseguramiento de Confirmación HITL**: Ejecución garantizada de las herramientas informativas antes de pausar el bucle en estado `requiere_confirmacion` para avisos de emergencia a contactos autorizados.

### Evaluación y Documentación
- **Actualización de Conjunto Dorado (`eval/preguntas.csv`)**: Consolidación de las 20 preguntas clínicas de referencia (`P01`–`P20`) alcanzando **Hit@1 = 90.0% (18/20)** y **Hit@5 = 100.0% (20/20)** en `eval/run_eval.py`, manteniendo **86.7% Top-3** y **100% citas** en `eval/evaluar.py`.

---

## [0.6.0] - 2026-11-16

### Agente Clínico, GeoSalud y Frontend
- **Búsqueda Mejorada y Enlaces a Google Maps**: Enriquecimiento de `app/tools/buscar_centro_salud.py` y `data/geosalud_ecuador.json` con horarios, cartera de servicios, direcciones verificadas y enlaces directos de navegación a Google Maps, renderizados de forma segura en `frontend/src/components/MensajeChat.tsx`.
- **Preparación de Avisos de Emergencia**: Instrucciones y detección de solicitudes de notificación telefónica con control estricto de alcance.
- **Materiales de Defensa y Simulador Interactivo**: Incorporación de presentación institucional en HTML/PPTX y simulador interactivo offline de tres casos clínicos en `docs/evidencias/semana-4/defensa/`.

---

## [0.5.2] - 2026-11-10

### Triaje Clínico, Privacidad LOPDP e Infraestructura
- **Detección Clínica de Síntomas Incompletos (`app/flujo.py`)**: Refactorización de la estación de vaguedad para evaluar ausencia de temporalidad y de signos de alarma asociados (`30%` de desvío a revisión médica, `0` errores silenciosos).
- **Minimización de Datos y Anonimización PII (`LOPDP`)**: Enmascaramiento irreversible (`anonimizar_pii()`) de números telefónicos y correos electrónicos antes de persistir en SQLite (`data/historial.db`), con aviso transparente en `Cabecera.tsx`.
- **Infraestructura Cloud Run y CI/CD**: Escalamiento a **2 vCPU y 2 GiB RAM**, optimización de imagen Docker con PyTorch CPU y certificación de 16 pruebas de humo (`tests/smoke.py`) en producción.

---

## Historial Global de Entregas

| Versión Backend | Versión Frontend | Fecha | Hito Principal | Detalle |
| :--- | :--- | :--- | :--- | :--- |
| **0.6.1** | **0.6.1** | 2026-11-16 | **Semana 4 (Release Final)**: GeoSalud en Docker, Detección por Ubicación, Confirmación HITL y Evaluación 20/20 Hit@5 | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#061---2026-11-16) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#061---2026-11-16) |
| **0.6.0** | **0.6.0** | 2026-11-16 | **Semana 4**: Centros de Salud con Enlaces a Google Maps, Avisos de Emergencia y Simulador de Defensa | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#060---2026-11-16) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#060---2026-11-16) |
| **0.5.2** | **0.5.2** | 2026-11-10 | **Semana 4**: Triaje por Temporalidad, Anonimización PII (LOPDP), Cloud Run 2 vCPU/2 GiB y 16 Smoke Tests | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#052---2026-11-10) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#052---2026-11-10) |
| **0.5.1** | **0.5.1** | 2026-11-08 | **Semana 4**: Enmascaramiento de Datos Personales en Historial SQLite | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#051---2026-11-08) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#051---2026-11-08) |
| **0.4.0** | **0.4.0** | 2026-11-07 | **Semana 4**: Despliegue Continuo en Google Cloud Run, 119 Pruebas Automatizadas y Endurecimiento OWASP | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#040---2026-11-07) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#040---2026-11-07) |
| **0.3.2** | **0.3.2** | 2026-11-07 | **Semana 4**: Automatización CI/CD Unificada (`ci.yml`, `release.yml`, `deploy.yml`) | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#032---2026-11-07) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#032---2026-11-07) |
| **0.2.0-SNAPSHOT-RC2** | **0.2.0-SNAPSHOT-RC2** | 2026-10-31 | **Semana 3**: Estabilización de Razonamiento Gemini, Resiliencia CORS y Versiones Simétricas | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#020-snapshot-rc2---2026-10-31) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#020-snapshot-rc2---2026-10-31) |
| **0.2.0-SNAPSHOT-RC1** | **0.2.0-SNAPSHOT-RC1** | 2026-10-31 | **Semana 3**: Agente Clínico v2, RAG ChromaDB, HITL y GeoSalud | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#020-snapshot-rc1---2026-10-31-semana-3) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#020-snapshot-rc1---2026-10-31-semana-3) |
| **0.1.1** | **0.1.1** | 2026-10-24 | **Semana 2**: Cliente LLM Resiliente, Failover, Memoria y Chat React | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#011---2026-10-24-semana-2) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#011---2026-10-24-semana-2) |
| **0.1.0** | **0.1.0** | 2026-10-17 | **Semana 1**: Inicialización de API FastAPI, Maquetación y SemVer CI | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#010---2026-10-17-semana-1) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#010---2026-10-17-semana-1) |
