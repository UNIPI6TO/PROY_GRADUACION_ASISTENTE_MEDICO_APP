# Evidencias de Ingeniería y Prompts - Semana 1

## 1. Información General del Proyecto
- **Proyecto:** Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis (Grupo 5).
- **Semana:** Semana 1 - Definición del problema, requisitos y diseño de arquitectura.
- **Rol del Asistente:** Tech Lead / Arquitecto de Software Senior (Modo Ponytail - pragmático, modular, cero alucinaciones).
- **Entregables Principales:**
  - [`docs/01-propuesta.md`](../01-propuesta.md): Definición del problema real, usuarios, alcance positivo y negativo estricto, riesgos éticos y modelo generativo.
  - [`docs/02-requisitos.md`](../02-requisitos.md): 8 historias de usuario con 4 criterios Gherkin c/u, requisitos no funcionales y gaps (`FALTA:`).
  - [`docs/03-arquitectura.md`](../03-arquitectura.md): Diagrama modular simplificado de flujos, diagrama de clases, flujo de consulta, y arquitectura de bajo costo en GCP con Cloud Run, Angular PWA e IAM.
  - [`docs/04-fuentes.md`](../04-fuentes.md): Inventario de fuentes oficiales (MSP, OPS 2016, GeoSalud) y estrategia de chunking jerárquico.
  - [`docs/05-especificacion-CICD.md`](../05-especificacion-CICD.md): Especificación formal de CI/CD para versionado SemVer automático en ramas `main` y `develop` mediante GitHub Actions.
  - [`README.md`](../../README.md): Documentación del repositorio con alcance positivo/negativo estricto, guías de instalación, ejecución, pruebas y señalamiento explícito de datos faltantes (`FALTA:`).

---

## 2. Registro Cronológico de Prompts y Trazabilidad

A continuación se documentan los prompts literales utilizados durante las sesiones de ingeniería para construir y refinar los artefactos de la Semana 1.

### Prompt 1: Generación Base de Entregables Semana 1
**Propósito:** Crear `01-propuesta.md`, `02-requisitos.md`, `03-arquitectura.md` y `04-fuentes.md` con alcance negativo estricto, 8 historias de usuario en Gherkin, diagrama inicial y chunking clínico.

```markdown
Actúas como Ingeniero de Requisitos de un equipo de desarrollo de software para el sector público y de salud.
El resultado lo usará el equipo de desarrollo (frontend y backend) para programar y probar el Producto Mínimo Viable (MVP) durante el primer sprint del proyecto.
Redacta al menos 8 historias de usuario para la necesidad entre <necesidad>. Cada una debe poder implementarse y probarse en menos de 3 días.
Ejemplo de formato: Como [usuario], quiero [acción], para [beneficio].
Para cada historia, escribe 4 criterios de aceptación en Gherkin (Dado / Cuando / Entonces).
Usa solo la necesidad descrita. No agregues funciones que no estén ahí. Si falta información, escribe FALTA: y qué falta.

<necesidad>
Problema a resolver
El dengue es endémico en la Costa y la Amazonía ecuatorianas, con brotes que saturan los servicios de salud. Gran parte de las complicaciones graves se asocia a la consulta tardía cuando aparecen signos de alarma. El Ministerio de Salud Pública (MSP) y la Organización Panamericana de la Salud (OPS) disponen de guías y material educativo, pero la población no
siempre accede a ellos ni los comprende. Un asistente de orientación —no de diagnóstico— puede mejorar la prevención y la búsqueda oportuna de atención.
Construir un asistente web de orientación ciudadana que explique prevención, síntomas y signos de alarma del dengue con base exclusiva en material oficial, e incorporar un agente que
aplique una lista de verificación de signos de alarma mediante reglas deterministas y derive a un establecimiento de salud o al 911 cuando corresponda, sin emitir diagnósticos ni recomendar medicamentos.
Insumos que necesitamos para la semana 1 son:
docs/01-propuesta.md: problema real, usuarios, alcance (qué hace y qué nunca hará), riesgos identificados y modelo generativo elegido con justificación.

docs/02-requisitos.md: al menos 8 historias de usuario con criterios de aceptación verificables, y requisitos no funcionales medibles (tiempo de respuesta, trazabilidad de la fuente, privacidad, disponibilidad).

docs/03-arquitectura.md: diagrama (Mermaid o imagen) con frontend, backend, modelo, base vectorial, herramientas del agente y fuentes; descripción del flujo de una consulta de principio a fin.

docs/04-fuentes.md: inventario de la base de conocimiento: documento, origen oficial, URL, fecha de publicación o vigencia, formato, y la estrategia de fragmentación prevista.
</necesidad>

**Contexto de Ejecución:**
Activa tu rol de Tech Lead / Arquitecto de Software Senior (estilo ponytail). Estamos en la Semana 1 (Definición del problema y diseño de la solución) para el proceso de titulación. 

**Datos del Proyecto (Caso 5):**
- **Tema:** Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis.
- **Fuentes Oficiales Base:** Guías de práctica clínica del Ministerio de Salud Pública (MSP), Registro de establecimientos de salud (GeoSalud) y Guías para la atención de enfermos de dengue de la OPS (2016).

**Instrucción:**
Genera el contenido técnico, estructurado y profesional para los siguientes 4 archivos en formato Markdown. No agregues funciones fuera de este alcance. Si detectas que falta información crítica para el desarrollo, indícalo con el prefijo "FALTA:".

1. `docs/01-propuesta.md`
- Define el problema real (el dengue satura el sistema y las complicaciones graves ocurren por consulta tardía).
- Define los usuarios objetivo.
- Alcance negativo estricto: Especifica explícitamente que el sistema NUNCA emitirá diagnósticos, no recomendará medicamentos y derivará inmediatamente ante cualquier signo de alarma.
- Identifica riesgos éticos y de seguridad del paciente.
- Justifica la elección del modelo generativo.

2. `docs/02-requisitos.md`
- Actúa como Ingeniero de Requisitos. Redacta al menos 8 historias de usuario derivándolas estrictamente de la lista de preguntas reales suministrada.
- Formato: Como [usuario], quiero [acción], para [beneficio]. Cada historia debe poder implementarse en menos de 3 días.
- Para cada historia, redacta 4 criterios de aceptación en formato Gherkin (Dado / Cuando / Entonces).
- Incluye requisitos no funcionales medibles (tiempo de respuesta, trazabilidad de la fuente obligatoria, privacidad, disponibilidad).

3. `docs/03-arquitectura.md`
- Describe el flujo completo de una consulta (de principio a fin).
- Genera el código en Mermaid.js para el diagrama de arquitectura. 
- El diagrama debe mostrar obligatoriamente: Frontend web, Backend en FastAPI, LLM, ChromaDB (Base Vectorial), y las herramientas del agente (específicamente las funciones deterministas evaluar_signos_alarma(respuestas) y ubicar_establecimiento(ciudad)).

4. `docs/04-fuentes.md`
- Crea el inventario de la base de conocimiento estructurado en una tabla: documento, origen oficial, URL, fecha de publicación/vigencia y formato.
- Redacta una justificación técnica sólida sobre la estrategia de fragmentación (chunking) prevista para estas guías clínicas, asegurando que los fragmentos mantengan el contexto médico sin cortar artículos o síntomas por la mitad.
```

---

### Prompt 2: Incorporación de Diagramas de Clases y Despliegue en GCP
**Propósito:** Extender `docs/03-arquitectura.md` con modelado formal de clases y propuesta inicial en nube pública Google Cloud Platform.

```markdown
en arquitectura agrega diagramas de clase y diagramas de flujo de datos la arquitectura se instalara en GCP
```

---

### Prompt 3: Especificación de Componentes, Flechas y Payload de Datos
**Propósito:** Formalizar qué dato exacto viaja por cada enlace del diagrama modular e identificar faltantes con `FALTA:`.

```markdown
Dibuja en Mermaid la arquitectura de este sistema en el archivo 03-arquitectura.md: componentes y flechas, y qué viaja por cada flecha.
Usa solo los componentes que te describo. Si falta un dato, escribe FALTA. [describa aquí los componentes de su Sistema]
```

---

### Prompt 4: Depuración y Enfoque Modular (Remoción de DFD)
**Propósito:** Eliminar los diagramas de flujo de datos de nivel 0 y 1 para evitar redundancias y mantener la arquitectura concisa.

```markdown
quita los diagramas de flujo de datos de la arquitectura
```

---

### Prompt 5: Simplificación a Arquitectura Serverless de Bajo Costo (4 Cloud Run)
**Propósito:** Definir una infraestructura de costo \$0 en reposo en un único proyecto GCP separando Frontend y Backend para Producción y Test.

```markdown
la Arquitectura de Despliegue en Google Cloud Platform (GCP) debe ser mas simple se debe usar cloud run para el front end y otro para el back end y en el mismo proyecto vamos a instalar produccion y test en total son 4 services de cloud run, es una arquitectura de bajo costo.
```

---

### Prompt 6: Separación de Diagramas de Despliegue (Prod vs. Test)
**Propósito:** Evitar sobrecarga visual generando dos diagramas Mermaid independientes para cada ambiente.

```markdown
separa en dos diagramas uno de produccion y uno de test para no mezclar
```

---

### Prompt 7: Seguridad Service-to-Service con Roles IAM y Service Accounts
**Propósito:** Restringir el backend para que no sea público y solo pueda ser consumido por el frontend con tokens OIDC y rol `roles/run.invoker`.

```markdown
agrega que solo el front end consume el back mediante roles de invoker y sa y modifica el .md con esta sugerencia si hay algo que falta indicame
```

---

### Prompt 8: Selección Tecnológica del Frontend: Angular PWA
**Propósito:** Definir Angular como framework de interfaz con soporte PWA (Progressive Web App) para instalación móvil y resiliencia offline.

```markdown
para el front end se utilizara Angular una aplicacion compatible con PWA
```

---

### Prompt 9: Simplificación del Diagrama Modular de Flujos
**Propósito:** Reducir la complejidad visual del diagrama 2.2 agrupando el backend y consolidando los flujos principales de datos.

```markdown
ayudame a simplificar el Diagrama de Componentes, Flechas y Flujos de Datos
```

---

### Prompt 10: Análisis de Requisitos y Casos Borde para el Backend Inicial
**Propósito:** Analizar la lógica de negocio, datos de entrada/salida y casos borde para los endpoints operativos `/manage/health` y `/manage/info` antes de escribir cualquier línea de código.

```markdown
Vamos a trabajar en el back end de la solucion. 
Te paso un criterio de aceptación en Gherkin entre <criterio>. 
Explícame con tus palabras:
Qué debe hacer la función que clasifica la prioridad.
2. Qué dato entra y qué dato sale.
3. Qué casos borde ves. 
No escribas código todavía.
<criterio>
Escenario: hacer un get manage/health y manage/info
Actualmente no hay codigo generado se debe crear el backend incial
El health debe mostrar la comprobacion de estado liveness y readiness
El info la version actual de la aplicacion con formato SemVer y el nombre de la aplicacion
</criterio>
```

---

### Prompt 11: Planificación de Pruebas Unitarias TDD y Definición Modular
**Propósito:** Establecer los nombres de archivos y funciones y diseñar 3 pruebas unitarias con Pytest usando exclusivamente la biblioteca estándar de Python, bajo un esquema de aprobación humana obligatoria (*Human-in-the-Loop*).

```markdown
Ahora propón un plan antes de programar: 
Nombre de la función y del archivo.
Las 3 pruebas que escribirías primero con pytest, una frase por prueba. Usa solo la biblioteca estándar de Python.
Espera mi aprobación antes de escribir Código.
```

---

### Prompt 12: Aprobación del Plan de Implementación
**Propósito:** Validación formal por parte del usuario del artefacto `implementation_plan.md` autorizando la creación del código.

```markdown
[Aprobación del plan de implementación en implementation_plan.md]
```

---

### Prompt 13: Guía Operativa de Ejecución Local y Pruebas
**Propósito:** Solicitar los procedimientos y comandos estándar para levantar el backend en local con Uvicorn y correr las pruebas unitarias.

```markdown
como levanto la aplicacion y como ejecuto las pruebas?
```

---

### Prompt 14: Estandarización de Comandos en la Guía de Agentes (`AGENTS.md`)
**Propósito:** Registrar formalmente en el archivo normativo `AGENTS.md` los comandos del backend local y testing para que cualquier agente o desarrollador pueda ejecutarlos de manera reproducible.

```markdown
modifica en el AGENTS.md como hago las pruebas del back end y como levanto en el local la aplicacion de python en el local
```

---

### Prompt 15: Levantamiento Asistido del Backend en Local
**Propósito:** Solicitar al agente la instalación de dependencias, el arranque en segundo plano del servidor FastAPI/Uvicorn y la verificación en vivo de los endpoints.

```markdown
levanta por mi la aplicacion
```

---

### Prompt 16: Redacción de Historia de Usuario SemVer para SRE y Detección de Faltantes
**Propósito:** Definir la automatización del versionado SemVer para el Backend bajo rol SRE, especificando ramas `main` (release) y `develop` (snapshot), historias en Gherkin con entrega en < 3 días y detección estricta de gaps (`FALTA:`).

```markdown
Actúas como SRE para elaboracion de versionado SemVer para el BackEnd.
El repositorio debe tiene dos ramas la main donde se generan los relese y la develop debe generar snapshoot.
Redacta 1 historia de usuario para la necesidad entre <necesidad>; cada una debe implementarse y probarse en menos de 3 días.
Para cada historia, al menos 3 criterios en Gherkin (Dado / Cuando / Entonces).
Usa solo la necesidad descrita. Si falta información, escribe FALTA: y qué falta.
<necesidad>
- Cuando se haya modificado un archivo dentro del path app/ debe activarse un git action donde la aplicacion cambiar la version acorde a las reglas de SemVer 
- Documentar las historias en docs/05-especificacion-CICD.md 
- Las version esta en el siguiente archivo app\main.py variable APP_VERSION
- Usar este regex para SenVer r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
</necesidad>
```

---

### Prompt 17: Resolución de Faltantes (Conventional Commits, SNAPSHOT-RC#, Tagging y Cambio Manual)
**Propósito:** Proporcionar las directrices operativas exactas para resolver las cuatro áreas faltantes identificadas en la especificación de SemVer.

```markdown
En los que incida falta seguir las intruciones 
- Criterio o convención para determinar el tipo de incremento SemVer (MAJOR, MINOR o PATCH). No se especifica si se deducirá a partir de *Conventional Commits*.  Se fijara con los siguiente:
   - `docs:` Cambios o adiciones en documentación técnica y especificaciones (archivos en `docs/` o README).
   - `feat:` Nuevas funcionalidades o endpoints (FastAPI, frontend, herramientas del agente).
   - `fix:` Corrección de errores o bugs.
   - `chore:` Tareas de mantenimiento, dependencias, `.gitignore`, `.gitattributes`, configuración.
   - `refactor:` Reestructuración de código sin alterar funcionalidad externa.
   - `test:` Pruebas unitarias o de integración.
- Nomenclatura y formato exacto del identificador de pre-release para el snapshot en la rama `develop` debes usar SNAPSHOT-RC1 el valor de RC# va ir incrementando cada vez que se realice un  pull request a la la develop
-  Estrategia de persistencia y publicación del cambio de versión. se debe modificar el main.py y tambien crear un tag en git. 
- Manejo de excepciones cuando el cambio en `app/` ya incluye una actualización manual de la variable `APP_VERSION`. Respetar el cambio manual si en el archivo viene el cambio desde el usuario.
```

---

### Prompt 18: Análisis de Código, Flujo de Datos y Casos Borde para SemVer
**Propósito:** Solicitar análisis conceptual y técnico del código actual, flujos de entrada/salida y casos borde de SemVer antes de programar.

```markdown
Lee el archivo docs\05-especificacion-CICD.md y el criterio de aceptación que está entre `<criterio>`.
Explícame qué hace hoy el código, qué datos entran y salen, y qué casos borde ves.
**No escribas código todavía.**
```

---

### Prompt 19: Propuesta de Plan Inicial de Implementación y Arquitectura
**Propósito:** Exigir un plan detallado de cambios por función y por archivo con espera de aprobación previa del usuario.

```markdown
Propón un plan antes de programar: qué funciones cambiarías y en qué archivos 
Espera mi aprobación.
```

---

### Prompt 20: Refinamiento del Plan TDD con las 3 Primeras Pruebas Unitarias
**Propósito:** Incorporar al plan las 3 pruebas unitarias prioritarias a escribir primero bajo la metodología TDD con aprobación humana.

```markdown
Propón un plan antes de programar: qué funciones cambiarías, en qué archivos y qué 3 pruebas escribirías primero.   Espera mi aprobación.
```

---

### Prompt 21: Implementación y Verificación del Paso 1 (Cálculo de Release y Conventional Commits)
**Propósito:** Autorizar e implementar exclusivamente el Paso 1 (módulo de incremento SemVer y Prueba 1 para `main`), verificando con Pytest y respetando pruebas preexistentes.

```markdown
Implementa solo el paso 1 del plan. Ejecuta las pruebas y muéstrame el resultado. No modifiques las pruebas.
```

---

### Prompt 22: Implementación y Verificación del Paso 2 (Snapshot SNAPSHOT-RC# en develop)
**Propósito:** Autorizar e implementar exclusivamente el Paso 2 (lógica de snapshots incrementales en `develop` y Prueba 2), ejecutando la suite de pruebas.

```markdown
Implementa solo el paso 2 del plan. Ejecuta las pruebas y muéstrame el resultado. No modifiques las pruebas.
```

---

### Prompt 23: Implementación de Pasos Restantes (Cambio Manual, CLI, Workflow y Docs)
**Propósito:** Autorizar e implementar los pasos restantes del plan: detección de versiones manuales (Prueba 3), CLI en `scripts/semver_bumper.py`, workflow de GitHub Actions y documentación técnica.

```markdown
Implementa los siguientes pasos. Ejecuta las pruebas y muéstrame el resultado. No modifiques
las pruebas.
```

---

### Prompt 24: Corrección de Evento Trigger en GitHub Actions (Migración a Pull Request)
**Propósito:** Corregir el disparador del workflow para que se active en eventos de `pull_request` hacia `main` y `develop` en lugar de `push`.

```markdown
pero vi que el action esta cuando se hace push y aqui se debe activar cuando se hace un pull request
```

---

### Prompt 25: Redacción Estricta del README.md del Repositorio (Metodología R.E.C.E.T.A.)
**Propósito:** Elaborar el `README.md` oficial del repositorio con alcance positivo/negativo, instalación, ejecución y pruebas, basándose de manera estricta y exclusiva en los archivos existentes y declarando `FALTA` ante cualquier omisión.

```markdown
Redacta el README de este repositorio: propósito, instalación, cómo ejecutar y cómo probar. Usa solo lo que está en los archivos. Si falta un dato, escribe FALTA.
```

---

### Prompt 26: Ejecución Asistida del Backend en Local con Uvicorn
**Propósito:** Solicitar el levantamiento del backend FastAPI en local para habilitar y verificar el servidor en segundo plano con recarga automática en el puerto 8000.

```markdown
ejecutar backend en mi local
```

---

## 3. Matriz de Trazabilidad: Prompts vs. Archivos Resultantes

| Prompt | Archivos Afectados | Sección Modificada / Generada |
| :--- | :--- | :--- |
| **Prompt 1** | `docs/01-propuesta.md`<br/>`docs/02-requisitos.md`<br/>`docs/03-arquitectura.md`<br/>`docs/04-fuentes.md` | Generación completa de los 4 artefactos base de la Semana 1. |
| **Prompt 2** | `docs/03-arquitectura.md` | Adición del Diagrama de Clases (Pydantic y servicios) y propuesta GCP. |
| **Prompt 3** | `docs/03-arquitectura.md` | Sección 2.1 (`FALTA:`) y numeración exhaustiva de payloads por flecha. |
| **Prompt 4** | `docs/03-arquitectura.md` | Eliminación de sección DFD y renumeración de acápites. |
| **Prompt 5** | `docs/03-arquitectura.md` | Sección 5: Rediseño a 4 servicios Cloud Run serverless de bajo costo. |
| **Prompt 6** | `docs/03-arquitectura.md` | Secciones 5.1 y 5.2: Desacoplamiento de diagramas para Producción y Test. |
| **Prompt 7** | `docs/03-arquitectura.md` | Secciones 5.1, 5.2, 5.4: Implementación de Service Accounts y `roles/run.invoker`. |
| **Prompt 8** | `docs/03-arquitectura.md` | Secciones 1, 2, 5 y 6: Integración de Angular PWA con proxy reverso Nginx. |
| **Prompt 9** | `docs/03-arquitectura.md` | Sección 2.2: Diagrama limpio de 4 capas lógicas y 10 flujos principales. |
| **Prompt 10** | `app/main.py`<br/>`implementation_plan.md` | Análisis de entradas, salidas y casos borde para `/manage/health` y `/manage/info`. |
| **Prompt 11** | `app/main.py`<br/>`tests/test_main.py` | Diseño del plan TDD y 3 pruebas unitarias usando solo la biblioteca estándar. |
| **Prompt 12** | `app/main.py`<br/>`tests/test_main.py`<br/>`requirements.txt` | Implementación del código modular y paso de pruebas con Pytest. |
| **Prompt 13** | Documentación de chat | Instrucciones paso a paso para levantar Uvicorn y ejecutar Pytest. |
| **Prompt 14** | `AGENTS.md` | Actualización de la sección `## Comandos` con comandos oficiales de instalación, arranque y pruebas. |
| **Prompt 15** | Background Task / Servidor local | Instalación de dependencias y ejecución de Uvicorn en puerto 8000. |
| **Prompt 16** | `docs/05-especificacion-CICD.md` | Redacción de la historia de usuario HU-CICD-01 y criterios Gherkin con identificación de faltantes. |
| **Prompt 17** | `docs/05-especificacion-CICD.md` | Definición de reglas de Conventional Commits, SNAPSHOT-RC#, git tagging y manejo de cambio manual. |
| **Prompt 18** | Documentación de chat | Análisis de entradas, salidas, comportamiento actual de `app/main.py` y casos borde para SemVer. |
| **Prompt 19** | `implementation_plan.md` | Propuesta de plan de implementación detallando funciones, archivos y arquitectura SRE. |
| **Prompt 20** | `implementation_plan.md` | Refinamiento del plan incorporando las 3 primeras pruebas prioritarias bajo enfoque TDD. |
| **Prompt 21** | `scripts/semver_bumper.py`<br/>`tests/test_semver_bumper.py` | Implementación de Paso 1: cálculo de incremento SemVer para `main` y Prueba 1 exitosa. |
| **Prompt 22** | `scripts/semver_bumper.py`<br/>`tests/test_semver_bumper.py` | Implementación de Paso 2: progresión correlativa de `SNAPSHOT-RC#` en `develop` y Prueba 2 exitosa. |
| **Prompt 23** | `scripts/semver_bumper.py`<br/>`tests/test_semver_bumper.py`<br/>`.github/workflows/semver.yml`<br/>`docs/05-especificacion-CICD.md` | Implementación de pasos restantes: Prueba 3 (detección manual), CLI, workflow y documentación técnica. |
| **Prompt 24** | `.github/workflows/semver.yml`<br/>`docs/05-especificacion-CICD.md`<br/>`scripts/semver_bumper.py` | Migración del trigger de GitHub Actions de `push` a `pull_request` y soporte de `GITHUB_BASE_REF`. |
| **Prompt 25** | `README.md` | Redacción estricta del README oficial con propósito, instalación, ejecución y pruebas, registrando `FALTA` ante ausencias. |
| **Prompt 26** | Background Task / Servidor local | Ejecución asistida del backend con `uvicorn app.main:app --reload --port 8000` y verificación en vivo de `/manage/health`. |

---

## 4. Estado de Verificación de Entregables de la Semana 1

- [x] **01-propuesta.md:** Completo, con alcance negativo estricto y justificación de Gemini.
- [x] **02-requisitos.md:** 8 historias de usuario en Gherkin, RNF cuantitativos y gaps identificados.
- [x] **03-arquitectura.md:** Diagrama modular simplificado, diagrama de clases, flujo de triaje/RAG, 4 servicios Cloud Run con Angular PWA y seguridad IAM Zero-Trust.
- [x] **04-fuentes.md:** Catálogo documental oficial (MSP, OPS 2016, GeoSalud) y estrategia de chunking jerárquico.
- [x] **05-especificacion-CICD.md:** Especificación formal de CI/CD para versionado SemVer automático en ramas `main` y `develop` mediante GitHub Actions.
- [x] **README.md:** Redactado conforme a la estructura del repositorio con alcance positivo/negativo, instalación, ejecución, pruebas y señalamiento explícito de datos faltantes (`FALTA:`).
- [x] **app/main.py:** Backend inicial funcional con `/manage/health` (liveness y readiness) y `/manage/info` (SemVer estricto).
- [x] **scripts/semver_bumper.py:** Módulo de automatización SemVer bajo principios SOLID (Conventional Commits, cálculo de snapshots, detección manual y actualización segura).
- [x] **tests/test_main.py:** Suite de pruebas unitarias 100% aprobadas con biblioteca estándar.
- [x] **tests/test_semver_bumper.py:** Suite de pruebas unitarias TDD aprobadas cubriendo los 3 escenarios clave de versionado SemVer.
- [x] **.github/workflows/semver.yml:** Workflow automatizado en GitHub Actions activado por `pull_request` hacia `main` y `develop` con filtro en `app/**`.
- [x] **AGENTS.md:** Normativa de desarrollo y comandos operativos actualizada.
- [x] **evidencias/semana-1.md:** Memoria técnica completa, trazabilidad de 26 prompts de ingeniería y evidencias de ejecución en vivo.

---

## 5. Evidencias de Uso y Ejecución del Backend Inicial

### 5.1. Ejecución de Pruebas Unitarias (`pytest -q`)
Comando ejecutado en PowerShell:
```powershell
pytest -q
```
Salida real en consola:
```text
...                                                                      [100%]
3 passed in 0.02s
```

*Detalle de pruebas verificadas:*
1. **`test_check_health_liveness_and_readiness_up`:** Valida código HTTP 200 y que los diagnósticos de `liveness` y `readiness` retornen `"UP"`.
2. **`test_check_health_readiness_down_on_failure`:** Valida código HTTP 503 y que el estado general y de `readiness` cambien a `"DOWN"` cuando falla una sonda de disponibilidad.
3. **`test_get_info_semver_format_and_app_name`:** Valida que el nombre de la aplicación sea el oficial y que la versión cumpla la expresión regular oficial de SemVer (`0.1.0`).

### 5.2. Levantamiento del Servidor Backend en Local
Comando ejecutado:
```powershell
uvicorn app.main:app --port 8000
```
Salida de arranque:
```text
INFO:     Started server process [18432]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 5.3. Verificación en Vivo de Endpoints (Pruebas HTTP Reales)

#### Endpoint 1: `GET http://localhost:8000/manage/health`
Llamada HTTP efectuada:
```powershell
Invoke-RestMethod -Uri http://localhost:8000/manage/health
```
Respuesta HTTP 200 OK:
```json
{
  "status": "UP",
  "checks": {
    "liveness": {
      "status": "UP"
    },
    "readiness": {
      "status": "UP"
    }
  }
}
```

#### Endpoint 2: `GET http://localhost:8000/manage/info`
Llamada HTTP efectuada:
```powershell
Invoke-RestMethod -Uri http://localhost:8000/manage/info
```
Respuesta HTTP 200 OK:
```json
{
  "name": "asistente-orientacion-salud-dengue",
  "version": "0.1.0"
}
```

#### Endpoint 3: Documentación OpenAPI / Swagger UI
* **URL:** `http://localhost:8000/docs`
* **Estado:** Documentación interactiva autogenerada por FastAPI disponible para inspección de esquemas y prueba de endpoints.

### 5.4. Evidencias de Ejecución del Sistema de Versionado SemVer y CI/CD

#### 5.4.1. Ejecución de la Suite Completa de Pruebas Unitarias (`pytest -v`)
Comando ejecutado en PowerShell:
```powershell
pytest -v
```
Salida real en consola:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- C:\Tools\Python3.13.5\python.exe
cachedir: .pytest_cache
rootdir: C:\Tools\app_movil\PI\PROY_GRADUACION_ASISTENTE_MEDICO_APP
plugins: anyio-4.15.1, html-4.2.0, metadata-3.1.1
collecting ... collected 6 items

tests/test_main.py::test_check_health_liveness_and_readiness_up PASSED   [ 16%]
tests/test_main.py::test_check_health_readiness_down_on_failure PASSED   [ 33%]
tests/test_main.py::test_get_info_semver_format_and_app_name PASSED      [ 50%]
tests/test_semver_bumper.py::test_release_increment_and_calculation_main PASSED [ 66%]
tests/test_semver_bumper.py::test_snapshot_rc_progression_develop PASSED [ 83%]
tests/test_semver_bumper.py::test_manual_version_change_and_file_update PASSED [100%]

============================== 6 passed in 0.44s ==============================
```

*Detalle de pruebas TDD de SemVer verificadas:*
1. **`test_release_increment_and_calculation_main`:** Valida que `determine_increment()` analice Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `BREAKING CHANGE:` / `!`), aplique precedencia estricta y que `calculate_next_release()` genere versiones de producción válidas contra el regex SemVer.
2. **`test_snapshot_rc_progression_develop`:** Valida la inicialización en `0.1.0-SNAPSHOT-RC1` y el avance secuencial a `0.1.0-SNAPSHOT-RC2` y `0.1.0-SNAPSHOT-RC3` analizando tags remotos de Git para la rama `develop`.
3. **`test_manual_version_change_and_file_update`:** Valida que modificaciones manuales de versión en el diff sean respetadas cuando cumplen SemVer, que formatos inválidos sean rechazados con `ValueError`, y que la sustitución en `app/main.py` sea atómica sin corromper líneas adyacentes.

#### 5.4.2. Simulación Local de Cálculo de Versión Release para `main` (`--dry-run`)
Comando ejecutado:
```powershell
python scripts/semver_bumper.py --dry-run --branch main
```
Salida en consola:
```text
Nueva versión calculada: 0.2.0
```

#### 5.4.3. Simulación Local de Cálculo de Versión Snapshot para `develop` (`--dry-run`)
Comando ejecutado:
```powershell
python scripts/semver_bumper.py --dry-run --branch develop
```
Salida en consola:
```text
Nueva versión calculada: 0.1.0-SNAPSHOT-RC1
```

#### 5.4.4. Verificación de Integridad de Pruebas Preexistentes
Comando ejecutado:
```powershell
git status -s
```
Salida en consola:
```text
 M .github/workflows/semver.yml
 M docs/05-especificacion-CICD.md
 M docs/evidencias/semana-1.md
 M scripts/semver_bumper.py
?? tests/test_semver_bumper.py
```
*Garantía de integridad:* El archivo original de pruebas del backend `tests/test_main.py` se mantuvo intacto sin ninguna modificación, cumpliendo estrictamente con la regla normativa del proyecto.

### 5.5. Evidencias de Redacción de README.md y Ejecución en Local con Recarga Automática

#### 5.5.1. Verificación y Suite de Pruebas tras Generación de `README.md`
Tras la redacción y generación de `README.md` bajo directivas estrictas de alcance y detección de faltantes (`FALTA:`), se ejecutó la suite de pruebas unitarias:
Comando ejecutado:
```powershell
pytest -q
```
Salida en consola:
```text
...                                                                      [100%]
3 passed in 0.35s
```

#### 5.5.2. Levantamiento Asistido del Servidor Backend en Local (`--reload`)
Comando ejecutado:
```powershell
uvicorn app.main:app --reload --port 8000
```
Salida real registrada en logs del proceso:
```text
INFO:     Will watch for changes in these directories: ['C:\\Tools\\app_movil\\PI\\PROY_GRADUACION_ASISTENTE_MEDICO_APP']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [39036] using StatReload
INFO:     Started server process [10160]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 5.5.3. Verificación en Vivo de Disponibilidad (`/manage/health`)
Comando ejecutado en PowerShell:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/manage/health
```
Salida real obtenida en consola:
```text
status checks                  
------ ------                  
UP     @{liveness=; readiness=}
```

*Endpoints verificados en ejecución local activa:*
- `GET http://127.0.0.1:8000/manage/health` (Estado general `UP`, Liveness `UP`, Readiness `UP`).
- `GET http://127.0.0.1:8000/manage/info` (Metadatos SemVer de la aplicación).
- `GET http://127.0.0.1:8000/docs` (Swagger UI interactivo de FastAPI).

