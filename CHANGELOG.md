# Changelog · GuíaVital

Todas las modificaciones notables de este proyecto se documentan de forma independiente para cada aplicación:

- 🖥️ **Backend (FastAPI, RAG, Agente Clínico, Base Vectorial)**: [app/CHANGELOG.md](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md)
- 🌐 **Frontend (React, Vite, TypeScript, Componentes)**: [frontend/CHANGELOG.md](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md)

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

### DevOps e Infraestructura
- **Changelogs Desacoplados por Aplicación**: Separación de bitácoras de cambios en `app/CHANGELOG.md` y `frontend/CHANGELOG.md`, actualizadas automáticamente en post-merge por sus respectivos flujos de CI/CD.
- **Optimización de Contenedor Docker Backend**: Configuración de PyTorch CPU (`--index-url https://download.pytorch.org/whl/cpu`) en `app/Dockerfile`, disminuyendo el peso de la imagen de ~3.2 GB a ~450 MB.
- **Reglas de Contexto Docker**: Actualización de `.dockerignore` para excluir fuentes crudas (`data/raw/`, `data/processed/`) y permitir el empaquetado de la base vectorial indexada (`!chroma_db/**`).
- **Pipeline CI/CD en 2 Fases**:
  - Fase 1 (PR): Cálculo y bump SemVer (`semver.yml` y `semver-frontend.yml`).
  - Fase 2 (Post-Merge): Tageo Git y promoción de Changelog (`tag-backend.yml` y `tag-frontend.yml`).

---

## Historial Global de Entregas

| Versión Backend | Versión Frontend | Fecha | Hito Principal | Detalle |
| :--- | :--- | :--- | :--- | :--- |
| **0.2.0-SNAPSHOT-RC2** | **0.2.0-SNAPSHOT-RC2** | 2026-10-31 | **Semana 3**: Estabilización de Razonamiento Gemini, Resiliencia CORS y Versiones Simétricas | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#020-snapshot-rc2---2026-10-31) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#020-snapshot-rc2---2026-10-31) |
| **0.2.0-SNAPSHOT-RC1** | **0.2.0-SNAPSHOT-RC1** | 2026-10-31 | **Semana 3**: Agente Clínico v2, RAG ChromaDB, HITL y GeoSalud | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#020-snapshot-rc1---2026-10-31-semana-3) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#020-snapshot-rc1---2026-10-31-semana-3) |
| **0.1.1** | **0.1.1** | 2026-10-24 | **Semana 2**: Cliente LLM Resiliente, Failover, Memoria y Chat React | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#011---2026-10-24-semana-2) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#011---2026-10-24-semana-2) |
| **0.1.0** | **0.1.0** | 2026-10-17 | **Semana 1**: Inicialización de API FastAPI, Maquetación y SemVer CI | [Backend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/app/CHANGELOG.md#010---2026-10-17-semana-1) · [Frontend](file:///d:/UNIANDES/Seminario%20de%20Graduaci%C3%B3n/PROY_GRADUACION_ASISTENTE_MEDICO_APP/frontend/CHANGELOG.md#010---2026-10-17-semana-1) |
