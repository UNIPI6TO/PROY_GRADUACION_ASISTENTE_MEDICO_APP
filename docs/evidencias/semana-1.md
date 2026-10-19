# Evidencia de Ingeniería de Prompts y Desarrollo - Semana 1

**Proyecto:** Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis (Grupo 5)  
**Módulo:** Backend Inicial - Endpoints de Gestión Operativa e Infraestructura (`/manage/health` y `/manage/info`)  
**Fecha:** Octubre 2026  

---

## 1. Contexto y Criterio de Aceptación (Gherkin)

Se inició el desarrollo del backend a partir del siguiente criterio de aceptación en lenguaje Gherkin:

```gherkin
Escenario: hacer un get manage/health y manage/info
Actualmente no hay codigo generado se debe crear el backend incial
El health debe mostrar la comprobacion de estado liveness y readiness
El info la version actual de la aplicacion con formato SemVer y el nombre de la aplicacion
```

---

## 2. Registro y Análisis de Prompts de la Sesión

### Prompt 1: Análisis Funcional y Casos Borde (Previo a Codificar)
> **Texto del Prompt:**  
> *"Vamos a trabajar en el back end de la solucion. Te paso un criterio de aceptación en Gherkin entre `<criterio>`. Explícame con tus palabras: 1. Qué debe hacer la función que clasifica la prioridad. 2. Qué dato entra y qué dato sale. 3. Qué casos borde ves. No escribas código todavía. `<criterio> ... </criterio>`"*

* **Técnica de Prompting:**  
  * **Role Prompting / Guardrails:** Prohibición explícita de escribir código prematuramente (*"No escribas código todavía"*).
  * **Análisis de Requerimientos:** Desglose estructurado de comportamiento, contratos de datos (I/O) y análisis de casos borde antes de la implementación.
* **Respuesta / Análisis Obtenido:**  
  * **Comportamiento:** Diferenciación entre *Liveness* (proceso vivo) y *Readiness* (servicio listo para atender tráfico). En `/manage/info`, entrega de nombre y versión SemVer (`MAJOR.MINOR.PATCH`).
  * **Entradas y Salidas:** Endpoints `GET` sin payload; salidas en JSON con códigos HTTP 200 y 503 (ante fallo de dependencias).
  * **Casos Borde Identificados:** Fallo parcial de dependencias (*zombie state*), timeouts en sondas, ausencia/corrupción de variables de entorno y cumplimiento de sintaxis SemVer.

---

### Prompt 2: Planificación de Pruebas Unitarias y TDD
> **Texto del Prompt:**  
> *"Ahora propón un plan antes de programar: Nombre de la función y del archivo. Las 3 pruebas que escribirías primero con pytest, una frase por prueba. Usa solo la biblioteca estándar de Python. Espera mi aprobación antes de escribir Código."*

* **Técnica de Prompting:**  
  * **Chain-of-Thought / Plan-First:** Forzar diseño del contrato y pruebas antes de la codificación.
  * **Restricción de Dependencias:** Uso estricto de la biblioteca estándar de Python para evitar dependencias innecesarias en pruebas iniciales.
  * **Gate de Aprobación Humana (*Human-in-the-Loop*):** Esperar confirmación explícita del usuario antes de proceder.
* **Plan Propuesto y Aprobado:**
  * **Archivo:** `app/main.py`
  * **Funciones:** `check_health()` y `get_info()`
  * **Archivo de Pruebas:** `tests/test_main.py`
  * **Pruebas Diseñadas (1 frase cada una):**
    1. `test_check_health_liveness_and_readiness_up`: Verifica que la comprobación devuelva código HTTP 200 y una estructura con liveness y readiness ambos en estado "UP".
    2. `test_check_health_readiness_down_on_failure`: Verifica que ante la simulación de un recurso dependiente no disponible, la función clasifique readiness como "DOWN" y emita estado 503.
    3. `test_get_info_semver_format_and_app_name`: Verifica que la información retorne el nombre de la aplicación y que el formato de la versión cumpla la expresión regular oficial de SemVer (`MAJOR.MINOR.PATCH`) usando el módulo estándar `re`.

---

### Prompt 3: Aprobación y Ejecución
> **Acción del Usuario:** Aprobación formal del artefacto `implementation_plan.md`.

* **Resultado Técnico:**  
  * Se implementó `app/main.py` con separación de responsabilidades y compatibilidad desacoplada con FastAPI.
  * Se implementó `tests/test_main.py` con las 3 pruebas unitarias usando únicamente `re` y `pytest`.
  * Se creó `requirements.txt` con las dependencias base (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `pytest`).

---

### Prompt 4 y 5: Documentación Operativa en `AGENTS.md`
> **Texto del Prompt:**  
> *"modifica en el AGENTS.md como hago las pruebas del back end y como levanto en el local la aplicacion de python en el local"*

* **Acción Realizada:**  
  Se actualizó `AGENTS.md` para estandarizar los comandos de ejecución del proyecto:
  ```markdown
  ## Comandos
  - Instalar Backend: `pip install -r requirements.txt`
  - Levantar Backend en Local: `uvicorn app.main:app --reload --port 8000`
  - Probar Backend: `pytest -q` (o `pytest -v` para modo detallado)
  ```

---

### Prompt 6: Despliegue y Validación en Vivo
> **Texto del Prompt:**  
> *"levanta por mi la aplicacion"*

* **Acción Realizada:**  
  * Instalación de dependencias de `requirements.txt`.
  * Ejecución de Uvicorn en segundo plano (`uvicorn app.main:app --port 8000`).
  * Comprobación exitosa contra `http://localhost:8000/manage/health` y `http://localhost:8000/manage/info`.

---

## 3. Evidencias de Ejecución

### 3.1. Ejecución de Pruebas Unitarias (`pytest -q`)
```text
...                                                                      [100%]
3 passed in 0.02s
```

### 3.2. Verificación de Endpoints HTTP
```bash
# GET /manage/health
HTTP/1.1 200 OK
Content-Type: application/json
{
  "status": "UP",
  "checks": {
    "liveness": { "status": "UP" },
    "readiness": { "status": "UP" }
  }
}

# GET /manage/info
HTTP/1.1 200 OK
Content-Type: application/json
{
  "name": "asistente-orientacion-salud-dengue",
  "version": "0.1.0"
}
```

---

## 4. Principios y Buenas Prácticas Aplicadas

| Principio / Estándar | Aplicación en la Solución |
| :--- | :--- |
| **SOLID (Single Responsibility)** | `check_health()` evalúa salud del sistema; `get_info()` gestiona metadatos; los handlers de FastAPI actúan únicamente como adaptadores HTTP. |
| **SemVer Canónico** | Validación rigurosa de versiones mediante expresión regular estándar (`MAJOR.MINOR.PATCH`). |
| **Resiliencia de Dependencias** | Chequeo de *Readiness* mediante inyección de sondas funcionales (*probes*), permitiendo clasificar fallos parciales sin colapsar el proceso principal. |
| **Pruebas con Biblioteca Estándar** | Suite de pruebas unitarias sin dependencias externas pesadas, garantizando rapidez y aislamiento (< 0.05 segundos de ejecución). |
