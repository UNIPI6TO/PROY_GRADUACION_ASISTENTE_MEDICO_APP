## ADR · Flujo automatizado con IA

*Taller de la Clase 4 · 29 de octubre de 2026 · Grupo 5 · Orientación sobre dengue*
*Integrantes: Wilson Salinas, Rafael Minaya, Luis Caguana*

### Contexto
En el producto se repite un proceso que hoy hace una persona a mano: Consulta de inquietudes por síntomas sospechosos, Consulta de información y signos de alarma. (1500 por día). Queremos automatizarlo sin que la IA tome decisiones exactas ni riesgosas.

### Decisión
- **Disparador:** Formulario web
- **Acción final:** Muestra información de establecimientos cercanos y solicita al ciudadano que llame al 911
- **Flujo fijo y no agente porque:** los pasos son siempre los mismos; hay que poder auditar cada decisión; el volumen es alto y repetitivo; un error tiene consecuencias de dinero o legales; en realidad conviene un agente: los pasos cambian según el caso. Enviar la consulta en el chat, Buscar Centros médicos cercanos.

| Estación | Qué hace | Decide | Qué sale |
|---|---|---|---|
| Disparador | Llega: síntomas reportados por la persona o un familiar (formulario web) | Sistema | Evento en la cola |
| Clasificar | Decidir el tipo (síntomas, consulta u otro) con un número de confianza | IA | JSON {tipo, confianza} |
| Umbral | Si la confianza es baja, desviar a revisión | Código | Sigue o va a revisión |
| Extraer | Sacar los campos: días con fiebre, signos presentes, edad, ubicación | IA | Datos validados con Pydantic |
| Reglas | Comparar con la lista oficial de signos de alarma | Código | Resultado exacto con su fuente |
| Revisión | Un profesional de salud revisa si hay signos de alarma | Persona | Aprobado o corregido |
| Actuar | Registrar el caso y mostrar el centro de salud más cercano | Sistema | Registro con auditoría |

- **Umbral de confianza: 0.85** (en `config/parametros.yaml`). Con los 10 casos de práctica: 7 automáticos, 3 a revisión (30 %), 0 errores silenciosos. Motivo: Con 0.85 no hay errores silenciosos
- **La persona que revisa recibe:** La derivación al centro medico para su atención cercana, recomendaciones de no automedicarse y si no puede moverse el ciudadano el sistema solicita aprobación para llamar al 911

### Seguridad
- Todo lo que entra por el disparador es texto no confiable.
- La IA solo produce campos de un esquema validado; nunca ejecuta acciones.
- Ninguna estación automática mueve dinero ni envía a terceros sin una persona.
- Las acciones que escriben son idempotentes (no se duplican si se reintentan).

### Consecuencias
- El umbral se recalibra con el conjunto dorado (eval/casos_flujo.jsonl) cada vez que cambian el prompt o el modelo.
- Todo documento termina en un estado: procesado, en revisión o rechazado con motivo. Nunca se descarta en silencio.
- Pendiente para la Entrega 3: implementar app/flujo.py, completar los casos reales del conjunto dorado y correr eval/evaluar.py.
