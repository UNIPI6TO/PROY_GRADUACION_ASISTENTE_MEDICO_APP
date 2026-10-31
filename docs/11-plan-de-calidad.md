## Plan de calidad y evaluación

*Grupo 5 · Orientación sobre dengue · taller de la Clase 4, 29 de octubre de 2026*

### 1. Evaluación básica del RAG
| Métrica | Cómo se mide | Meta |
|---|---|---|
| Acierto de recuperación | La fuente correcta aparece en los primeros 3 resultados, sobre 20 preguntas del conjunto del lunes | 85 % |
| Respuestas con cita | Respuestas que citan su fuente | 85 % |
| Silencio correcto | 5 preguntas cuya respuesta no está en los documentos: el sistema debe decir que no sabe | 100 % |

### 2. Evaluación básica del agente
- Escenarios: A · Camino feliz; B · Fuera de alcance; C · El tope; D · Inyección en un documento.
- Meta de tareas cumplidas: 1 %. Rechazos correctos en fuera de alcance e inyección: 100 %.

### 3. Evaluación del flujo automatizado
- Conjunto dorado: 20 casos en `eval/casos_flujo.jsonl`, con el resultado esperado escrito antes de correr.
- Errores silenciosos: **0**. Máximo a revisión humana: 30 %. Umbral actual: 0.85.

### 4. Calidad del software
| Práctica | Se aplica |
|---|---|
| Pruebas unitarias con pytest (cada función de cálculo y cada herramienta) | Sí |
| Medición de cobertura (pytest-cov) | Sí |
| Linter y formato (ruff, eslint o similar) | Sí |
| Integración continua (GitHub Actions) que corre todo en cada push | Sí |
| La evaluación del RAG, el agente y el flujo también corre en CI | Sí |

- Meta de cobertura: 85 %.
- Quién y cuándo: Git Actions cuando ocurre el un pull request a la rama develop

### Evidencia para la Revisión 3 y la Entrega 3
- Salida de `python eval/evaluar.py` y de `pytest` en `docs/evidencias/semana-3/`.
