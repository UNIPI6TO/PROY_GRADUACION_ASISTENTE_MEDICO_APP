# Evidencia técnica · Semana 3

Caso 05 · GuíaVital · Asistente de Orientación en Salud Pública sobre Dengue  
Revisión 3: Viernes 30 de octubre de 2026  
Integrantes: Wilson Salinas, Rafael Minaya, Luis Caguana  

---

## 1. Lista de verificación

- [x] **Herramienta determinista con modelo Pydantic:** `EvaluarSignosAlarmaHttpIn` y `EvaluarSignosAlarmaHttpOut` en `app/tools/evaluar_signos_alarma.py`.
- [x] **Endpoint HTTP formal:** `POST /herramientas/signos-alarma` en `app/main.py` con `response_model` y validación automática 422.
- [x] **Endpoints operativos preservados:** `GET /manage/health` y `GET /manage/info` en `app/main.py` con diagnóstico de sondas y cumplimiento SemVer.
- [x] **Cinta de flujo automatizado (7 estaciones):** Implementada en `app/flujo.py` con umbral de confianza 0.85.
- [x] **Conjunto dorado de evaluación:** 20 casos clínicos reales en `eval/casos_flujo.jsonl` (70% automáticos, 30% a revisión médica, 0 errores silenciosos).
- [x] **Plan de calidad y script de evaluación CI:** `docs/11-plan-de-calidad.md` y `eval/evaluar.py` cumpliendo todas las metas (RAG top-3 $\ge 85\%$, errores silenciosos $= 0$, revisión $\le 30\%$).
- [x] **ADR de automatización:** `docs/10-automatizacion.md` documentando las decisiones de diseño del flujo fijo vs agente.
- [x] **Colección de pruebas manuales Bruno:** Ubicada en `bruno/GuiaVital/` (excluida en `.gitignore`), con selector de entornos `Local` (`http://127.0.0.1:8000`) y `Nube`.
- [x] **Pruebas automatizadas con `pytest`:** Pruebas unitarias y de integración con `TestClient` pasando al 100%.

---

## 2. Ejecución del Plan de Calidad (`python eval/evaluar.py`)

```text
Loading weights: 100%|##########| 199/199 [00:00<00:00, 3993.66it/s]
RAG acierto top-3: 87%  ·  Flujo a revisión: 30%  ·  Errores silenciosos: 0
[EXITO] Todas las metas del Plan de Calidad de la Semana 3 se han cumplido.
```

* **RAG acierto top-3:** $87\%$ (Meta: $\ge 85\%$).
* **Casos derivados a revisión humana:** $30\%$ (Meta: $\le 30\%$).
* **Errores silenciosos:** $0$ (Meta: estricta $= 0$, crítico en salud pública).

---

## 3. Pruebas Automatizadas de la Confianza y la Cinta (`pytest tests/test_flujo.py -v -s`)

```text
tests/test_flujo.py::test_alta_confianza_en_reporte_clinico_claro 
  [TEST 1: Reporte Clinico Claro]
  Entrada:             "Presento 4 dias de fiebre alta, dolor abdominal intenso y continuo"
  Tipo detectado:      reporte_sintomas
  Confianza obtenida:  0.95 (Umbral: 0.85)
  Supera el umbral:    True -> Decision: Flujo Automatico
PASSED

tests/test_flujo.py::test_baja_confianza_en_sintomas_vagos 
  [TEST 2: Sintomas Vagos sin Contexto]
  Entrada:             "Tengo malestar general"
  Tipo detectado:      reporte_sintomas
  Confianza obtenida:  0.70 (Umbral: 0.85)
  Supera el umbral:    False -> Decision: Desvia a REVISION MEDICA
PASSED

tests/test_flujo.py::test_baja_confianza_ante_intenciones_mezcladas 
  [TEST 3: Intenciones Mezcladas (Picadura + Consulta Administrativa)]
  Entrada:             "Me pico un mosquito pero tambien quiero saber el horario de atencion del centro de salud"
  Tipo detectado:      reporte_sintomas
  Confianza obtenida:  0.75 (Umbral: 0.85)
  Supera el umbral:    False -> Decision: Desvia a REVISION MEDICA
PASSED

tests/test_flujo.py::test_evaluacion_conjunto_dorado_cumple_plan_calidad 
  [TEST 8: Calibracion sobre Conjunto Dorado (20 casos)]
  Total casos:           20
  Casos a revision:      6 (30%)  [Meta: <= 30%]
  Errores silenciosos:   0  [Meta: = 0]
PASSED
```

## 4. Pruebas Generales del Backend (`pytest -q`)

```text
...................................                                      [100%]
35 passed in 5.12s
```

* Cobertura de endpoints de gestión: `/manage/health`, `/manage/info`.
* Cobertura de herramienta determinista: `/herramientas/signos-alarma` (códigos 200 y 422).
* Cobertura del bucle del agente y RAG.

---

## 4. Guía de Uso de la Colección Bruno

La colección reside en `bruno/GuiaVital/` e incluye las siguientes peticiones preconfiguradas:

1. **`01 - Health Check` (`GET {{baseUrl}}/manage/health`)**: Verifica el estado Liveness y Readiness del backend.
2. **`02 - App Info` (`GET {{baseUrl}}/manage/info`)**: Retorna metadatos de versión SemVer.
3. **`03 - Evaluar Signos Alarma (200 OK)` (`POST {{baseUrl}}/herramientas/signos-alarma`)**: Envía síntomas válidos y retorna el triaje con fuente oficial del MSP.
4. **`04 - Evaluar Signos Alarma (422 Error)` (`POST {{baseUrl}}/herramientas/signos-alarma`)**: Prueba la frontera de Pydantic enviando valores fuera de rango (ej. edad o días de fiebre inválidos).
5. **`05 - Chat V2 (Agente)` (`POST {{baseUrl}}/api/v2/chat`)**: Prueba la interacción multimodal con el agente inteligente y Function Calling.

**Para alternar entre Local y Nube en Bruno:**
* Seleccionar el entorno en la esquina superior derecha: `Local` o `Nube`.
