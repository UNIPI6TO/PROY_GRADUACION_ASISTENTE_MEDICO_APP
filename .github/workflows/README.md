# Pipelines de CI/CD · GuíaVital

Este directorio contiene los flujos de trabajo (*workflows*) automatizados de **GitHub Actions** para el asistente médico **GuíaVital**. La arquitectura sigue las mejores prácticas de **Site Reliability Engineering (SRE)** y principios **SOLID (Responsabilidad Única)**, desacoplando el Backend y el Frontend en ciclos de vida independientes.

---

## 🗺️ Mapa de Flujos de Trabajo

```mermaid
flowchart TD
    subgraph FASE1["1. Fase de Pull Request (Bump)"]
        PR["Apertura / Sincronización de PR"] --> CHECK_PATH{"Ruta de cambios"}
        CHECK_PATH -->|app/**| WF_PR_BE["semver.yml<br/>(Backend PR)"]
        CHECK_PATH -->|frontend/**| WF_PR_FE["semver-frontend.yml<br/>(Frontend PR)"]
        WF_PR_BE --> TEST_BE["Quality Gate: pytest<br/>Bump: app/main.py"]
        WF_PR_FE --> TEST_FE["Quality Gate: Vitest + Secrets<br/>Bump: package.json"]
    end

    subgraph FASE2["2. Fase Post-Merge (Tageo & Changelog Unificado)"]
        MERGE["Merge de Pull Request a develop o main"] --> WF_REL["release.yml<br/>(Tageo Simétrico & Changelogs)"]
        WF_REL --> TAG_BE["Tag: vX.Y.Z[-RC#]<br/>Update app/CHANGELOG.md & frontend/CHANGELOG.md"]
    end

    subgraph FASE3["3. Fase de Despliegue (Cloud Run en Paralelo)"]
        TAG_BE -.->|workflow_run<br/>(continúa si hay fallos)| WF_DEP_BE["deploy-backend.yml<br/>(Deploy Backend)"]
        TAG_BE -.->|workflow_run<br/>(continúa si hay fallos)| WF_DEP_FE["deploy-frontend.yml<br/>(Deploy Frontend)"]
        MANUAL["workflow_dispatch (Manual)"] --> WF_DEP_BE
        MANUAL --> WF_DEP_FE
        WF_DEP_BE --> DEPLOY_BE["Build Docker CPU (~450 MB)<br/>Deploy guiavital-backend"]
        WF_DEP_FE --> DEPLOY_FE["Build Docker Nginx<br/>Deploy guiavital"]
    end

    FASE1 --> FASE2
    FASE2 --> FASE3
```

---

## 📋 Catálogo de Workflows

### 1. Versionado en Pull Request (Fase 1)
| Workflow | Archivo | Disparador | Acción Principal |
| :--- | :--- | :--- | :--- |
| **SemVer Backend (PR Bump)** | [`semver.yml`](semver.yml) | `pull_request` (`app/**`) hacia `main`/`develop` (excluye changelogs) | Ejecuta `pytest`, calcula la versión SemVer y actualiza `APP_VERSION` en `app/main.py` de la rama **compare** (`head_ref`). |
| **SemVer Frontend (PR Bump)** | [`semver-frontend.yml`](semver-frontend.yml) | `pull_request` (`frontend/**`) hacia `main`/`develop` (excluye changelogs) | Ejecuta `verify:secrets` y `npm test`, calcula la versión e incrementa `package.json` en la rama **compare** (`head_ref`). |

> [!NOTE]
> - **Actualización exclusiva de la rama compare:** El commit de bump se empuja únicamente a la rama del PR (`HEAD:${{ github.head_ref }}`), **nunca** a la rama base (`develop`/`main`).
> - **Exclusión de Changelogs:** Modificar `app/CHANGELOG.md`, `frontend/CHANGELOG.md` o `CHANGELOG.md` **no** activa los pipelines de SemVer, evitando ejecuciones redundantes.

---

### 2. Publicación de Tags y Changelog Post-Merge (Fase 2)
| Workflow | Archivo | Disparador | Acción Principal |
| :--- | :--- | :--- | :--- |
| **Release & Tag Unificado** | [`release.yml`](release.yml) | `pull_request: closed` (merged) hacia `main`/`develop` | Genera el tag simétrico (`v...`), actualiza `app/CHANGELOG.md` y `frontend/CHANGELOG.md` de forma resiliente (`continue-on-error: true`). Si falla, la instalación continúa de todos modos. |

#### Regla de Ramas:
* **Rama `develop`:** Genera versiones **Snapshot** de pre-producción simétricas (`v0.2.0-SNAPSHOT-RC1`, `v0.2.0-SNAPSHOT-RC2`).
* **Rama `main`:** Genera versiones oficiales definitivas **Release** simétricas (`v0.2.0`).

---

### 3. Instalación y Despliegue en GCP Cloud Run (Fase 3)
| Workflow | Archivo | Disparador | Acción Principal |
| :--- | :--- | :--- | :--- |
| **Deploy Backend to Cloud Run** | [`deploy-backend.yml`](deploy-backend.yml) | `workflow_run` (post-tag backend) o Manual (`workflow_dispatch`) | Compila la imagen Docker optimizada con PyTorch CPU (`app/Dockerfile`, ~450 MB), la publica en Artifact Registry y despliega `guiavital-backend`. |
| **Deploy Frontend to Cloud Run** | [`deploy-frontend.yml`](deploy-frontend.yml) | `workflow_run` (post-tag frontend) o Manual (`workflow_dispatch`) | Resuelve dinámicamente la URL del backend, compila `frontend/Dockerfile` con Nginx y despliega el servicio `guiavital`. |

> [!TIP]
> Ambos despliegues se ejecutan **en paralelo**. Si un cambio solo afecta al Frontend, el Backend no se re-despliega, optimizando tiempos de build y cuotas de cómputo en GCP.

---

### 4. Infraestructura Base
| Workflow | Archivo | Disparador | Acción Principal |
| :--- | :--- | :--- | :--- |
| **Provision GCP Infrastructure (SRE)** | [`infra-gcp.yml`](infra-gcp.yml) | `workflow_dispatch` | Crea y valida de forma idempotente las Service Accounts de mínimo privilegio, el repositorio en Artifact Registry y los contenedores de Secret Manager. |

---

## 🔐 Secretos y Variables Requeridas

Para el correcto funcionamiento de los workflows en GitHub Actions, deben configurarse los siguientes secretos en el repositorio (`Settings` -> `Secrets and variables` -> `Actions`):

| Nombre del Secreto / Variable | Tipo | Requerido por | Descripción |
| :--- | :--- | :--- | :--- |
| **`BUMP_TOKEN`** | Secret | `semver*.yml`, `tag*.yml` | Personal Access Token (PAT) con permisos de `repo` para autorizar commits y tags en ramas con reglas de protección. *(Si no se define, se usa `GITHUB_TOKEN`)*. |
| **`GCP_JSON_KEY`** | Secret | `deploy*.yml`, `infra*.yml` | Credencial JSON de la Service Account desplegadora con permisos en Cloud Run y Artifact Registry. |
| **`GCP_PROJECT_ID`** | Variable | `deploy*.yml`, `infra*.yml` | ID del proyecto en Google Cloud Platform (ej. `project-3e1faa58-1e7d-4e8d-933`). |
| **`GCP_REGION`** | Variable | `deploy*.yml` | Región geográfica de despliegue en GCP (predeterminado: `us-central1`). |
| **`GAR_REPOSITORY`** | Variable | `deploy*.yml` | Nombre del repositorio de imágenes en Artifact Registry (ej. `guiavital-repo`). |

---

## 🚀 Guía de Operación Rápida

### ¿Cómo entregar una nueva funcionalidad?
1. Crea una rama desde `develop`: `git checkout -b feature/nueva-herramienta develop`.
2. Realiza tus cambios siguiendo *Conventional Commits* (ej. `feat: agregar búsqueda de síntomas`).
3. Abre un **Pull Request** hacia `develop`.
4. El workflow de PR correspondiente (`semver.yml` o `semver-frontend.yml`) ejecutará las pruebas y subirá automáticamente un commit bump con `[skip ci]`.
5. Una vez aprobado el PR, haz **Merge**:
   * Se dispara el workflow de tageo (`tag-backend.yml` o `tag-frontend.yml`), generando el tag `SNAPSHOT-RC#` y actualizando `CHANGELOG.md`.
   * Automáticamente se activa el despliegue paralelo a Google Cloud Run (`deploy-backend.yml` / `deploy-frontend.yml`).

### ¿Cómo forzar un despliegue manual a producción?
1. Ve a la pestaña **Actions** en GitHub.
2. Selecciona **Deploy Backend to Cloud Run** o **Deploy Frontend to Cloud Run**.
3. Haz clic en **Run workflow**, selecciona la rama deseada (`main` o `develop`) y confirma.
