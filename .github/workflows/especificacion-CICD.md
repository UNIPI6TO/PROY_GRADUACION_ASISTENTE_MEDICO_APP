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

Para evitar ejecuciones redundantes o tags huérfanos por Pull Requests cancelados, el ciclo de vida opera en tres etapas encadenadas donde `release.yml` envía explícitamente el `version_tag` y la rama destino a `deploy.yml`:

```mermaid
flowchart TD
    subgraph FASE_1["FASE 1: Pull Request (ci.yml · Solo en PR)"]
        A["Se crea o actualiza PR<br/>(opened, synchronize, reopened)<br/>hacia develop o main"] --> B["secret-scan:<br/>Auditoría de Secretos (Gitleaks)"]
        A --> C["backend-quality-gate:<br/>Test Calidad del Backend (Pytest y Evaluador RAG/Flujo)"]
        A --> D["frontend-quality-gate:<br/>Test Calidad del Frontend (Vitest)"]
    end

    subgraph FASE_2["FASE 2: Post-Merge (release.yml · Al completar Merge)"]
        E["PR Fusionado (merged == true)<br/>en develop o main"] --> F["release-and-tag:<br/>Versionado SemVer, Bitácoras y Publicación de Git Tag"]
        F --> G["Commit consolidado de versión + Push Git Tag ($TAG)"]
        G --> H["gh workflow run deploy.yml<br/>--ref $BRANCH -f version_tag=$TAG"]
    end

    subgraph FASE_3["FASE 3: Despliegue desde el Tag (deploy.yml)"]
        H ==> I["secret-scan:<br/>Test de Secretos (Gitleaks) sobre version_tag"]
        H ==> J["quality-gate-backend:<br/>Pruebas del Backend (Pytest + Evaluador RAG/Flujo)"]
        H ==> K["quality-gate-frontend:<br/>Pruebas del Frontend (Vitest)"]
        I & J & K ==>|100% aprobados (needs)| L["deploy-backend:<br/>Construcción y Despliegue del Backend en Cloud Run<br/>+ Sondas SRE + tests/smoke.py (6/6)"]
        L ==>|Backend y Smoke OK (needs)| M["deploy-frontend:<br/>Construcción y Despliegue del Frontend en Cloud Run<br/>+ Sonda /manage/health"]
    end

    FASE_1 -->|PR Aprobado y Merged| FASE_2
```

---

## 3. Matriz Definitiva de Workflows y Jobs de GitHub Actions

| Archivo de Workflow | Disparador (Trigger) | Jobs Configurados (`id`: `name`) | Responsabilidad (SOLID) |
| :--- | :--- | :--- | :--- |
| **`ci.yml`**<br/>*Integración Continua (Compuertas de Calidad y Pruebas)* | Automático: `pull_request` (`opened`, `synchronize`, `reopened`) hacia `main` y `develop`<br/>Manual: `workflow_dispatch` | - `secret-scan`: **Auditoría de Secretos (Gitleaks)**<br/>- `backend-quality-gate`: **Test Calidad del Backend (Pytest y Evaluador RAG/Flujo)**<br/>- `frontend-quality-gate`: **Test Calidad del Frontend (Vitest)** | **Fase 1 · Compuertas de PR**: Valida secretos (`secretos.yml`), 92 pruebas de backend (`pytest -q`), `eval/evaluar.py`, `verify:secrets` y 27 pruebas de frontend (`npm test`). |
| **`release.yml`**<br/>*Publicación y Tageo de Versiones (Post-Merge)* | Automático: `pull_request` (`closed` con `merged == true`) hacia `main` y `develop`<br/>Manual: `workflow_dispatch` | - `release-and-tag`: **Versionado SemVer, Bitácoras y Publicación de Git Tag** | **Fase 2 · Versionado, Tag y Disparo**: Ejecuta `scripts/semver_bumper.py`, actualiza bitácoras (`scripts/actualizar_changelog.py`), publica el Git Tag (`$TAG`) y dispara `deploy.yml` enviando `--ref "$BRANCH" -f version_tag="$TAG"`. |
| **`deploy.yml`**<br/>*Pipeline de Despliegue Continuo a GCP Cloud Run* | Automático desde `release.yml` o manual: `workflow_dispatch` (`inputs.version_tag`) | - `secret-scan`: **Test de Secretos (Gitleaks) sobre `${{ inputs.version_tag }}`**<br/>- `quality-gate-backend`: **Pruebas del Backend (Pytest + Evaluador RAG/Flujo)**<br/>- `quality-gate-frontend`: **Pruebas del Frontend (Vitest)**<br/>- `deploy-backend`: **Construcción y Despliegue del Backend en Cloud Run**<br/>- `deploy-frontend`: **Construcción y Despliegue del Frontend en Cloud Run** | **Fase 3 · Compuertas sobre el Tag + Docker + Cloud Run**: Descarga el código desde `inputs.version_tag`, ejecuta los 3 jobs bloqueantes de secretos y pruebas, y solo si aprueban construye las imágenes Docker, despliega en Cloud Run y ejecuta `tests/smoke.py` (6/6). |
| **`secretos.yml`**<br/>*Auditoría y Detección de Secretos* | Automático: `push` (`branches-ignore: [main, develop]`)<br/>Reusable: `workflow_call`<br/>Manual: `workflow_dispatch` | - `gitleaks`: **Escaneo de secretos con Gitleaks** | Valida en cada `push` a ramas de trabajo (`feature/*`, `fix/*`, etc., excluyendo `main` y `develop`) y como flujo reusable en PR (`ci.yml`) y Despliegue (`deploy.yml`) mediante `gitleaks/gitleaks-action@v3`. |
| **`infra-gcp.yml`** | Manual: `workflow_dispatch` | Aprovisionamiento GCP | Creación idempotente de Artifact Registry, cuentas de servicio IAM y secretos en Secret Manager. |

---

## 4. Historias de Usuario SRE Cumplidas

### HU-CICD-01: Validación Exclusiva en Pull Request (`ci.yml`)
- **Criterios de Aceptación:**
  1. `ci.yml` se activa **únicamente** cuando se crea o actualiza un Pull Request (`opened`, `synchronize`, `reopened`) hacia `develop` o `main`, evitando ejecuciones duplicadas en eventos `push`.
  2. Ejecuta en paralelo los tres jobs: `Auditoría de Secretos (Gitleaks)`, `Test Calidad del Backend (Pytest y Evaluador RAG/Flujo)` y `Test Calidad del Frontend (Vitest)`.

### HU-CICD-02: Versionado Simétrico, Tageo y Disparo de Despliegue (`release.yml`)
- **Criterios de Aceptación:**
  1. Se activa automáticamente cuando el PR hacia `develop` o `main` se cierra con `merged == true`.
  2. Incrementa simétricamente la versión en `app/main.py`, `frontend/package.json`, `frontend/package-lock.json` y `README.md` (`X.Y.Z-SNAPSHOT-RC#` en `develop` y `X.Y.Z` en `main`).
  3. Promociona las bitácoras `app/CHANGELOG.md` y `frontend/CHANGELOG.md`, publica el Git Tag formal y dispara `deploy.yml` enviándole la rama donde se realizó el merge (`--ref "$BRANCH"`) y el tag (`-f version_tag="$TAG"`).

### HU-CICD-03: Despliegue Continuo desde el Tag Bloqueado por Pruebas y Secretos (`deploy.yml`)
- **Criterios de Aceptación:**
  1. Recibe `inputs.version_tag` de `release.yml` sobre la rama fusionada (`develop` o `main`) sin requerir modificaciones en `secretos.yml`.
  2. Antes de construir cualquier imagen Docker, ejecuta desde ese tag los 3 jobs bloqueantes (`Test de Secretos (Gitleaks) sobre ${{ inputs.version_tag }}`, `Pruebas del Backend (Pytest + Evaluador RAG/Flujo)` y `Pruebas del Frontend (Vitest)`). Si cualquiera falla, el pipeline se detiene y no toca Cloud Run.
  3. Si las 3 compuertas aprueban, construye y publica la imagen Docker del backend etiquetada con `inputs.version_tag` en Artifact Registry, la despliega en Cloud Run vinculando Secret Manager y ejecuta las sondas `/manage/info`, `/manage/health` y `tests/smoke.py` (6/6 casos en vivo).
  4. Solo tras aprobar los smoke tests del backend, construye la imagen Docker del frontend desde `inputs.version_tag`, la despliega en Cloud Run y verifica su endpoint `/manage/health`.
