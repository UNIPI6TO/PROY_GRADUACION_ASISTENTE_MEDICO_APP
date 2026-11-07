# 05. Especificación de CI/CD: Automatización de Versionado SemVer y Despliegue Continuo (Backend y Frontend)

**Rol:** Site Reliability Engineer (SRE)  
**Proyecto:** GuíaVital · Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis  

---

## 1. Reglas y Convenciones de Versionado SemVer

### 1.1. Convención de Commits y Reglas de Incremento
Los pipelines de GitHub Actions analizan los mensajes de commit (*Conventional Commits*) mediante `scripts/semver_bumper.py` para determinar el incremento SemVer:
- **`feat:`** Nuevas funcionalidades o endpoints $\rightarrow$ Incremento **MINOR** (ej. `0.1.0` $\rightarrow$ `0.2.0`).
- **`fix:`** Corrección de errores o bugs $\rightarrow$ Incremento **PATCH** (ej. `0.1.0` $\rightarrow$ `0.1.1`).
- **`refactor:`** Reestructuración de código sin alterar funcionalidad externa $\rightarrow$ Incremento **PATCH**.
- **`chore:`** Tareas de mantenimiento, dependencias o configuración $\rightarrow$ Incremento **PATCH**.
- **`test:`** Pruebas unitarias o de integración $\rightarrow$ Incremento **PATCH**.
- **`docs:`** Cambios en documentación técnica y especificaciones $\rightarrow$ Incremento **PATCH** (si acompaña cambios en código).
- **`BREAKING CHANGE:` o sufijo `!` (ej. `feat!:`, `fix!:`):** Cambios incompatibles con versiones previas $\rightarrow$ Incremento **MAJOR** (ej. `0.1.0` $\rightarrow$ `1.0.0`).

### 1.2. Estrategia por Ramas (Releases vs Snapshots con Simetría Backend/Frontend)
- **Simetría de Versiones y Tags:** Backend (`app/main.py`), Frontend (`frontend/package.json` y `package-lock.json`) y `README.md` comparten exactamente la misma versión SemVer y el mismo formato de tag Git (`vX.Y.Z` o `vX.Y.Z-SNAPSHOT-RC#`), garantizando paridad de entrega.
- **Rama `main` (Releases de Producción):**
  - Genera versiones oficiales definitivas con formato SemVer estricto: `X.Y.Z` (sin sufijos pre-release).
  - Tags Git simétricos: `vX.Y.Z`.
- **Rama `develop` (Snapshots de Pre-producción):**
  - Genera versiones con nomenclatura `X.Y.Z-SNAPSHOT-RC#`.
  - El correlativo `RC#` incrementa secuencialmente en cada entrega hacia `develop` (ej. `0.2.0-SNAPSHOT-RC1`, `0.2.0-SNAPSHOT-RC2`).
  - Tags Git simétricos: `vX.Y.Z-SNAPSHOT-RC#`.

### 1.3. Expresión Regular Oficial SemVer 2.0
Toda versión generada o manual valida estrictamente contra:
```regex
r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
```

### 1.4. Manejo de Modificaciones Manuales de Versión
Si el desarrollador ya modificó manualmente `APP_VERSION` en `app/main.py` o `version` en `frontend/package.json`, el pipeline valida el formato SemVer y respeta dicho valor sin sobreescribirlo.

---

## 2. Arquitectura del Ciclo de Vida en Tres Etapas (`ci.yml` $\rightarrow$ `release.yml` $\rightarrow$ `deploy.yml`)

Para evitar ejecuciones redundantes o tags huérfanos por Pull Requests cancelados, el ciclo de vida opera en tres etapas encadenadas y estrictas:

```mermaid
flowchart TD
    subgraph FASE_1["FASE 1: Pull Request (ci.yml · Solo en PR)"]
        A["Se crea o actualiza PR<br/>(opened, synchronize, reopened)<br/>hacia develop o main"] --> B["secret-scan (Gitleaks)"]
        A --> C["backend-quality-gate<br/>pytest -q (92 tests) + eval/evaluar.py"]
        A --> D["frontend-quality-gate<br/>npm run verify:secrets + npm test (27 tests)"]
    end

    subgraph FASE_2["FASE 2: Post-Merge (release.yml · Al completar Merge)"]
        E["PR Fusionado (merged == true)<br/>en develop o main"] --> F["scripts/semver_bumper.py<br/>Bump simétrico en app/main.py, package.json y README.md"]
        F --> G["scripts/actualizar_changelog.py<br/>Actualiza app/CHANGELOG.md y frontend/CHANGELOG.md"]
        G --> H["Commit consolidado [skip ci] + Push Git Tag (vX.Y.Z / SNAPSHOT-RC#)"]
    end

    subgraph FASE_3["FASE 3: Despliegue con Compuertas Bloqueantes (deploy.yml)"]
        H ==>|workflow_run: completed & success| I["Job 1: secret-scan (Gitleaks)"]
        H ==> J["Job 2: quality-gate-backend (pytest 92 + eval)"]
        H ==> K["Job 3: quality-gate-frontend (verify:secrets + Vitest 27)"]
        I & J & K ==>|100% aprobados (needs)| L["Job 4: deploy-backend<br/>Docker Build Backend + Deploy Cloud Run<br/>+ Sondas SRE + tests/smoke.py (6/6)"]
        L ==>|Backend y Smoke OK (needs)| M["Job 5: deploy-frontend<br/>Docker Build Frontend + Deploy Cloud Run<br/>+ Sonda /manage/health"]
    end

    FASE_1 -->|PR Aprobado y Merged| FASE_2
    FASE_2 --> FASE_3
```

---

## 3. Matriz Definitiva de Workflows de GitHub Actions

| Archivo de Workflow | Disparador (Trigger) | Evento / Alcance | Responsabilidad (SOLID) |
| :--- | :--- | :--- | :--- |
| **`ci.yml`** | Automático: `pull_request` (`opened`, `synchronize`, `reopened`) hacia `main` y `develop`<br/>Manual: `workflow_dispatch` | Solo en Pull Request (sin `push`) | **Fase 1 · Compuertas de PR**: Ejecuta `secret-scan` (Gitleaks), `pytest -q` (92 pruebas), `eval/evaluar.py`, `verify:secrets` y `Vitest` (27 pruebas). |
| **`release.yml`** | Automático: `pull_request` (`closed` con `merged == true`) hacia `main` y `develop`<br/>Manual: `workflow_dispatch` | Post-Merge completado | **Fase 2 · Versionado y Tag**: Ejecuta `scripts/semver_bumper.py`, actualiza `app/CHANGELOG.md` y `frontend/CHANGELOG.md` (`scripts/actualizar_changelog.py`), hace commit `[skip ci]` y publica el Git Tag formal. |
| **`deploy.yml`** | Automático: `workflow_run` al finalizar con éxito `release.yml`<br/>Manual: `workflow_dispatch` | Post-Release hacia GCP Cloud Run | **Fase 3 · Compuertas + Docker + Cloud Run**: Ejecuta primero los jobs bloqueantes de pruebas y secretos (`secret-scan`, `quality-gate-backend`, `quality-gate-frontend`). Solo si los 3 pasan, construye los contenedores Docker, despliega en Cloud Run y ejecuta `tests/smoke.py` (6/6). |
| **`secretos.yml`** | Reusable: `workflow_call`<br/>Manual: `workflow_dispatch` | Transversal (PR y Deploy) | Escaneo de secretos en todo el historial Git con **Gitleaks**. |
| **`infra-gcp.yml`** | Manual: `workflow_dispatch` | Aprovisionamiento GCP | Creación idempotente de Artifact Registry, cuentas de servicio IAM y secretos en Secret Manager. |

---

## 4. Historias de Usuario SRE Cumplidas

### HU-CICD-01: Validación Exclusiva en Pull Request (`ci.yml`)
- **Criterios de Aceptación:**
  1. `ci.yml` se activa **únicamente** cuando se crea o actualiza un Pull Request (`opened`, `synchronize`, `reopened`) hacia `develop` o `main`, evitando ejecuciones duplicadas en eventos `push`.
  2. Verifica en paralelo: ausencia de secretos con Gitleaks, 92 pruebas unitarias de backend + evaluador de calidad RAG/Flujo, y 27 pruebas de frontend + verificación de secretos en el bundle.

### HU-CICD-02: Versionado Simétrico y Tageo al Completar el Merge (`release.yml`)
- **Criterios de Aceptación:**
  1. Se activa automáticamente cuando el PR hacia `develop` o `main` se cierra con `merged == true`.
  2. Incrementa simétricamente la versión en `app/main.py`, `frontend/package.json`, `frontend/package-lock.json` y `README.md` (`X.Y.Z-SNAPSHOT-RC#` en `develop` y `X.Y.Z` en `main`).
  3. Promociona las bitácoras `app/CHANGELOG.md` y `frontend/CHANGELOG.md` y publica el Git Tag formal.

### HU-CICD-03: Despliegue Continuo Bloqueado por Pruebas y Secretos (`deploy.yml`)
- **Criterios de Aceptación:**
  1. Al finalizar `release.yml` con éxito, se dispara automáticamente `deploy.yml` mediante `workflow_run`.
  2. Antes de construir cualquier imagen Docker, ejecuta 3 jobs bloqueantes (`secret-scan`, `quality-gate-backend`, `quality-gate-frontend`). Si cualquiera falla, el pipeline se detiene y no toca Cloud Run.
  3. Si las 3 compuertas aprueban, construye y publica la imagen Docker del backend en Artifact Registry, la despliega en Cloud Run vinculando Secret Manager y ejecuta las sondas `/manage/health`, `/manage/info` y `tests/smoke.py` (6/6 casos en vivo).
  4. Solo tras aprobar los smoke tests del backend, construye la imagen Docker del frontend con Nginx, la despliega en Cloud Run y verifica su endpoint `/manage/health`.
