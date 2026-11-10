# Matriz de riesgos · Grupo 5 · Orientación sobre dengue

Referencias: OWASP Top 10 for LLM Applications 2026 y OWASP Top 10 for Agentic Applications.

| Riesgo | OWASP | Probabilidad | Impacto | Mitigación | Dónde se ve | Responsable |
|---|---|---|---|---|---|---|
| Inyección de prompt para forzar al asistente a recetar fármacos contraindicados (ej. ibuprofeno/aspirina) o dar diagnósticos definitivos. | LLM01 | Media | Alto | Delimitación de entradas con etiquetas <consulta_usuario>, instrucciones de rol inmutable en system prompt y rechazo de directivas de anulación. | app/services/seguridad.py, tests/test_dengue.py | Rafael Minaya |
| Fuga inadvertida de datos personales de salud (síntomas vinculados a usuarios) en trazas de error o respuestas de depuración. | LLM02 | Media | Alto | Arquitectura con Minimización de Datos (LOPDP) sin registro de datos identificables, enmascaramiento irreversible de PII, manejo de errores estándar RFC 9457 sin stacktrace y UUIDs efímeros de sesión. | app/main.py, tests/test_dengue.py | Rafael Minaya |
| Ejecución descontrolada de acciones o llamadas repetitivas y no autorizadas a herramientas externas por parte del agente. | LLM03 | Baja | Alto | Lista cerrada de herramientas permitidas, tope estricto de 6 vueltas en el bucle del agente y confirmación humana requerida (HITL) para notificaciones de emergencia. | app/services/agent.py | Wilson Salinas |
| Agotamiento de cuotas y denegación de servicio por envío masivo o ráfagas automatizadas de consultas hacia los proveedores Gemini y Groq. | LLM06 | Alta | Medio | Limitador de tasa con algoritmo de ventana deslizante en memoria (10 solicitudes/minuto por idSesion) que retorna código HTTP 429 con cabecera Retry-After. | app/services/seguridad.py, tests/test_dengue.py | Wilson Salinas |
| Alucinación médica o desinformación al evaluar signos de alarma de dengue grave, induciendo a no buscar atención hospitalaria oportuna. | LLM07 | Media | Alto | Triaje determinista por reglas de código para signos de alarma sin delegar el cálculo al LLM, y fundamentación estricta de respuestas en guías del MSP mediante RAG. | app/tools/evaluar_signos_alarma.py | Luis Caguana |
