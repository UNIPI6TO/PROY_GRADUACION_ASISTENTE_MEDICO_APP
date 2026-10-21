# 05. Especificación de CI/CD: Automatización de Versionado SemVer del Backend

**Rol:** Site Reliability Engineer (SRE)  
**Proyecto:** Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis (Backend)

---

## 1. Reglas y Convenciones de Versionado SemVer

### 1.1. Convención de Commits y Reglas de Incremento
El pipeline de GitHub Actions analiza los mensajes de commit (*Conventional Commits*) para determinar el incremento SemVer:
- **`feat:`** Nuevas funcionalidades o endpoints (FastAPI, servicios, herramientas del agente) $\rightarrow$ Incremento **MINOR** (ej. `0.1.0` $\rightarrow$ `0.2.0`).
- **`fix:`** Corrección de errores o bugs $\rightarrow$ Incremento **PATCH** (ej. `0.1.0` $\rightarrow$ `0.1.1`).
- **`refactor:`** Reestructuración de código sin alterar funcionalidad externa $\rightarrow$ Incremento **PATCH**.
- **`chore:`** Tareas de mantenimiento, dependencias, configuración $\rightarrow$ Incremento **PATCH**.
- **`test:`** Pruebas unitarias o de integración $\rightarrow$ Incremento **PATCH**.
- **`docs:`** Cambios en documentación técnica y especificaciones (`docs/` o README). Si solo afecta `docs/`, se omite la ejecución por filtro de rutas; si se incluye con cambios en `app/`, aplica **PATCH**.
- **`BREAKING CHANGE:` o sufijo `!` (ej. `feat!:`, `fix!:`):** Cambios incompatibles con versiones previas $\rightarrow$ Incremento **MAJOR** (ej. `0.1.0` $\rightarrow$ `1.0.0`).

### 1.2. Estrategia por Ramas
- **Rama `main` (Releases):**
  - Genera versiones oficiales de producción con formato SemVer estricto: `X.Y.Z`.
  - Actualiza la variable `APP_VERSION` en `app/main.py`.
  - Crea un Git Tag formal (ej. `vX.Y.Z`).
- **Rama `develop` (Snapshots):**
  - Genera versiones pre-release con nomenclatura `X.Y.Z-SNAPSHOT-RC#`.
  - El correlativo `RC#` incrementa secuencialmente en cada Pull Request integrado hacia `develop` (ej. `0.1.0-SNAPSHOT-RC1`, `0.1.0-SNAPSHOT-RC2`).
  - Actualiza la variable `APP_VERSION` en `app/main.py`.
  - Crea el Git Tag respectivo (ej. `v0.1.0-SNAPSHOT-RC1`).

### 1.3. Expresión Regular Oficial SemVer
Toda versión generada o manual debe validar contra:
```regex
r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
```

### 1.4. Manejo de Modificaciones Manuales de Versión
Si el desarrollador ya modificó manualmente la variable `APP_VERSION` en `app/main.py` dentro del commit, el pipeline respeta dicha versión (validando que cumpla el patrón SemVer) y evita sobreescribirla, procediendo a generar el Git Tag correspondiente.

---

## 2. Historia de Usuario

### HU-CICD-01: Automatización de Versionado SemVer y Generación de Tags en GitHub Actions

- **Historia:**
  Como **Site Reliability Engineer (SRE)**,  
  quiero implementar un workflow de GitHub Actions que se dispare ante cambios en la ruta `app/` para actualizar la variable `APP_VERSION` en `app/main.py` bajo reglas SemVer (Release en `main` y `SNAPSHOT-RC#` en `develop`) y generar el Git Tag respectivo respetando posibles cambios manuales,  
  para estandarizar la entrega continua del Backend, asegurar trazabilidad de despliegues y eliminar errores operativos manuales.

- **Estimación:** 2 días (implementación y pruebas completas en menos de 3 días).

- **Criterios de Aceptación (Gherkin):**

  - **Criterio 1: Generación de versión Release en rama `main` y creación de Git Tag**
    - **Dado** que se realiza un Pull Request hacia la rama `main` con cambios en archivos dentro de `app/` sin modificación manual de `APP_VERSION`,
    - **Cuando** el workflow de GitHub Actions analiza los mensajes de commit según Conventional Commits (`feat:`, `fix:`, etc.),
    - **Entonces** calcula el incremento SemVer correspondiente (MAJOR, MINOR o PATCH), valida la versión contra el regex oficial, actualiza `APP_VERSION` en `app/main.py`, persiste el cambio y crea el Git Tag con prefijo `v` (ej. `v0.2.0`).

  - **Criterio 2: Generación de versión Snapshot incremental en rama `develop`**
    - **Dado** que se realiza un Pull Request hacia la rama `develop` modificando archivos en `app/`,
    - **Cuando** se ejecuta el GitHub Action de versionado para `develop`,
    - **Entonces** el pipeline calcula la versión base y le concatena el sufijo `SNAPSHOT-RC#` (incrementando el correlativo `RC` respecto al último snapshot registrado), valida la cadena contra el regex SemVer, actualiza `APP_VERSION` en `app/main.py` y genera el tag en Git (ej. `v0.1.0-SNAPSHOT-RC2`).

  - **Criterio 3: Respeto de actualización manual de versión definida por el usuario**
    - **Dado** que un Pull Request entrante en `main` o `develop` con modificaciones en `app/` ya incluye un cambio manual sobre la variable `APP_VERSION` en `app/main.py`,
    - **Cuando** el workflow inspecciona el diff y valida que la nueva versión manual cumple con el regex de SemVer,
    - **Entonces** el sistema respeta el valor provisto por el usuario sin sobreescribirlo y procede a crear el Git Tag con dicha versión.

  - **Criterio 4: Omisión del workflow si no hay cambios dentro de `app/`**
    - **Dado** que se abre o actualiza un Pull Request a `main` o `develop` afectando únicamente archivos fuera del directorio `app/` (como `docs/`, `tests/` o configuración raíz),
    - **Cuando** GitHub Actions evalúa los filtros de rutas (`paths: ['app/**']`),
    - **Entonces** el pipeline no se activa, no se genera tag y `APP_VERSION` en `app/main.py` permanece intacto.

  - **Criterio 5: Detención y fallo de pipeline ante versión SemVer no válida**
    - **Dado** que se procesa una versión calculada o introducida manualmente en `app/main.py`,
    - **Cuando** la cadena de versión no cumple estrictamente con el regex SemVer oficial:
      `r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"`
    - **Entonces** el workflow detiene la ejecución inmediatamente con código de error, bloquea la creación de tags y reporta la falla en el resumen de GitHub Actions.

---

## 3. Arquitectura Técnica Implementada

Para asegurar la alta mantenibilidad, trazabilidad y cumplimiento del principio SOLID (Responsabilidad Única), la solución se estructura en dos capas:

1. **Núcleo de Reglas SemVer (`scripts/semver_bumper.py`):**
   - Módulo en Python 3 que contiene la lógica de negocio pura:
     - `validate_semver(version)`: Validación contra el regex oficial.
     - `determine_increment(commits)`: Jerarquía de incremento según Conventional Commits.
     - `calculate_next_release(base_version, increment)`: Cálculo de versión limpia de producción.
     - `calculate_next_snapshot(base_version, existing_tags)`: Cálculo de pre-release `SNAPSHOT-RC#`.
     - `detect_manual_version_change(diff_text)`: Detección y respeto de versiones manuales válidas.
     - `update_app_version_in_file(file_path, new_version)`: Sustitución segura en `app/main.py`.

2. **Orquestación en CI/CD (`.github/workflows/semver.yml`):**
   - Workflow de GitHub Actions que se activa ante eventos `pull_request` hacia `main` y `develop` con filtro `paths: ['app/**']`.
   - Ejecuta las pruebas unitarias automáticas con `pytest`.
   - Invoca `scripts/semver_bumper.py --branch ${{ github.base_ref }}`.
   - Realiza commit automático con bandera `[skip ci]` para prevenir loops de ejecución.
   - Genera y publica el tag Git correspondiente (`vX.Y.Z` o `vX.Y.Z-SNAPSHOT-RC#`).
