# 05. Especificación de CI/CD: Automatización de Versionado SemVer y Despliegue Continuo (Backend y Frontend)

**Rol:** Site Reliability Engineer (SRE)  
**Proyecto:** GuíaVital · Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis  

---

## 1. Reglas y Convenciones de Versionado SemVer

### 1.1. Convención de Commits y Reglas de Incremento
Los pipelines de GitHub Actions analizan los mensajes de commit (*Conventional Commits*) para determinar el incremento SemVer:
- **`feat:`** Nuevas funcionalidades o endpoints $\rightarrow$ Incremento **MINOR** (ej. `0.1.0` $\rightarrow$ `0.2.0`).
- **`fix:`** Corrección de errores o bugs $\rightarrow$ Incremento **PATCH** (ej. `0.1.0` $\rightarrow$ `0.1.1`).
- **`refactor:`** Reestructuración de código sin alterar funcionalidad externa $\rightarrow$ Incremento **PATCH**.
- **`chore:`** Tareas de mantenimiento, dependencias o configuración $\rightarrow$ Incremento **PATCH**.
- **`test:`** Pruebas unitarias o de integración $\rightarrow$ Incremento **PATCH**.
- **`docs:`** Cambios en documentación técnica y especificaciones $\rightarrow$ Incremento **PATCH** (si acompaña cambios en código).
- **`BREAKING CHANGE:` o sufijo `!` (ej. `feat!:`, `fix!:`):** Cambios incompatibles con versiones previas $\rightarrow$ Incremento **MAJOR** (ej. `0.1.0` $\rightarrow$ `1.0.0`).

### 1.2. Estrategia por Ramas (Releases vs Snapshots)
- **Rama `main` (Releases de Producción):**
  - Genera versiones oficiales definitivas con formato SemVer estricto: `X.Y.Z` (sin sufijos pre-release).
  - Tags Git: `vX.Y.Z` (Backend) y `frontend-vX.Y.Z` (Frontend).
- **Rama `develop` (Snapshots de Pre-producción):**
  - Genera versiones con nomenclatura `X.Y.Z-SNAPSHOT-RC#`.
  - El correlativo `RC#` incrementa secuencialmente en cada entrega hacia `develop` (ej. `0.2.0-SNAPSHOT-RC1`, `0.2.0-SNAPSHOT-RC2`).
  - Tags Git: `vX.Y.Z-SNAPSHOT-RC#` (Backend) y `frontend-vX.Y.Z-SNAPSHOT-RC#` (Frontend).

### 1.3. Expresión Regular Oficial SemVer 2.0
Toda versión generada o manual valida estrictamente contra:
```regex
r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
```

### 1.4. Manejo de Modificaciones Manuales de Versión
Si el desarrollador ya modificó manualmente `APP_VERSION` en `app/main.py` o `version` en `frontend/package.json`, el pipeline valida el formato SemVer y respeta dicho valor sin sobreescribirlo.

---

## 2. Arquitectura de Ciclo de Vida en Dos Fases

Para evitar tags huérfanos o modificaciones prematuras en `CHANGELOG.md` por Pull Requests cancelados o rechazados, el versionado opera en dos fases desacopladas:

```mermaid
flowchart TD
    subgraph FASE_1["FASE 1: Pull Request (Rama Entrante)"]
        A["PR abierto / actualizado"] --> B{"Ruta modificada"}
        B -->|app/**| C[".github/workflows/semver.yml"]
        B -->|frontend/**| D[".github/workflows/semver-frontend.yml"]
        C --> E["Quality Gate (pytest) + Bump app/main.py"]
        D --> F["Quality Gate (npm test) + Bump package.json"]
        E --> G["Commit y Push a la rama del PR [skip ci]"]
        F --> G
    end

    subgraph FASE_2["FASE 2: Post-Merge (develop / main)"]
        H["PR aprobado y fusionado (Merge)"] --> I{"Rama destino"}
        I -->|Push app/**| J[".github/workflows/tag-backend.yml"]
        I -->|Push frontend/**| K[".github/workflows/tag-frontend.yml"]
        J --> L["develop: SNAPSHOT-RC# | main: Release X.Y.Z"]
        K --> L
        L --> M["Crea y publica Git Tag (v... / frontend-v...)"]
        M --> N["Actualiza CHANGELOG.md (actualizar_changelog.py)"]
        N --> O["Commit y Push directo a la rama base [skip ci]"]
    end

    subgraph FASE_3["FASE 3: Despliegue Paralelo a Cloud Run"]
        O -.->|Automático por workflow_run| P[".github/workflows/deploy-backend.yml"]
        O -.->|Automático por workflow_run| Q[".github/workflows/deploy-frontend.yml"]
        R["Disparo Manual (workflow_dispatch)"] --> P
        R --> Q
        P --> S["Build Docker CPU (450 MB) + Cloud Run Backend"]
        Q --> T["Build Docker Nginx + Cloud Run Frontend"]
        S --> U["Sondas SRE /manage/health y /manage/info"]
        T --> V["Sonda SRE /healthz"]
    end

    FASE_1 --> FASE_2
    FASE_2 --> FASE_3
```

---

## 3. Matriz de Workflows de GitHub Actions

| Archivo de Workflow | Disparador (Trigger) | Evento / Alcance | Responsabilidad (SOLID) |
| :--- | :--- | :--- | :--- |
| **`semver.yml`** | `pull_request` (`app/**`) | En rama del PR | **Fase 1 Backend**: Tests backend + Bump de `APP_VERSION` en `app/main.py`. |
| **`tag-backend.yml`** | `push` (`app/**`) en `main`/`develop` | Post-Merge | **Fase 2 Backend**: Tag Git (`v...`) + Actualización de `CHANGELOG.md`. |
| **`semver-frontend.yml`** | `pull_request` (`frontend/**`) | En rama del PR | **Fase 1 Frontend**: Tests frontend + Bump en `package.json` y `package-lock.json`. |
| **`tag-frontend.yml`** | `push` (`frontend/**`) en `main`/`develop` | Post-Merge | **Fase 2 Frontend**: Tag Git (`frontend-v...`) + Actualización de `CHANGELOG.md`. |
| **`deploy-backend.yml`** | `workflow_dispatch` o `workflow_run` de `tag-backend` | Despliegue | **Instalación Backend**: Build Docker CPU + Despliegue `guiavital-backend` a Cloud Run. |
| **`deploy-frontend.yml`** | `workflow_dispatch` o `workflow_run` de `tag-frontend` | Despliegue | **Instalación Frontend**: Inyección URL API + Despliegue `guiavital` a Cloud Run. |

---

## 4. Historias de Usuario SRE

### HU-CICD-01: Versionado SemVer y Bump en Pull Request (Fase 1)
- **Historia:** Como SRE, quiero que al abrir o sincronizar un Pull Request hacia `develop` o `main`, el pipeline ejecute los tests automatizados e incremente la versión en el código de la rama entrante (`app/main.py` o `frontend/package.json`), para asegurar trazabilidad antes de la integración sin crear tags prematuros.
- **Criterios de Aceptación:**
  1. Si el PR modifica `app/**`, ejecuta `pytest` y actualiza `APP_VERSION` vía `scripts/semver_bumper.py`.
  2. Si el PR modifica `frontend/**`, ejecuta `npm test` y actualiza `package.json` vía `scripts/semver_bumper_frontend.py`.
  3. Realiza commit con `[skip ci]` hacia `HEAD:${{ github.head_ref }}`.
  4. **No** crea tags Git ni modifica `CHANGELOG.md` en esta fase.

### HU-CICD-02: Publicación de Tag y Actualización de Changelog Post-Merge (Fase 2)
- **Historia:** Como SRE, quiero que cuando un PR se fusione en `develop` o `main`, se genere el tag formal de Git y se actualice automáticamente `CHANGELOG.md`, para garantizar que el historial solo refleje código efectivamente integrado.
- **Criterios de Aceptación:**
  1. En `develop`, genera tags con formato `vX.Y.Z-SNAPSHOT-RC#` o `frontend-vX.Y.Z-SNAPSHOT-RC#`.
  2. En `main`, genera tags de release oficial `vX.Y.Z` o `frontend-vX.Y.Z`.
  3. Ejecuta `scripts/actualizar_changelog.py --version "$TAG"`, promocionando la sección `[Unreleased]` y organizándola por componentes (Backend / Frontend).
  4. Realiza commit y push directo a la rama base con `[skip ci]`.

### HU-CICD-03: Despliegue Continuo en Paralelo y Manual a GCP Cloud Run (Fase 3)
- **Historia:** Como SRE, quiero contar con workflows de instalación y despliegue desacoplados que puedan ejecutarse automáticamente tras el merge en paralelo o dispararse manualmente por demanda, para minimizar el tiempo de entrega y permitir el mantenimiento independiente de cada servicio.
- **Criterios de Aceptación:**
  1. `deploy-backend.yml` y `deploy-frontend.yml` pueden ejecutarse manualmente en cualquier momento mediante `workflow_dispatch`.
  2. Al completarse exitosamente el post-merge (`tag-backend.yml` o `tag-frontend.yml`), el workflow de despliegue correspondiente se activa automáticamente vía `workflow_run`.
  3. Si ambos servicios se fusionan simultáneamente, ambos despliegues se ejecutan **en paralelo** sin bloquearse entre sí.
  4. `deploy-backend.yml` utiliza la imagen optimizada con PyTorch CPU (`~450 MB`) e inyecta secretos desde GCP Secret Manager.
  5. `deploy-frontend.yml` resuelve dinámicamente la URL del backend mediante `gcloud run services describe`, compila los estáticos con Nginx y verifica `/healthz`.
