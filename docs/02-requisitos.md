# 02. Especificación de Requisitos de Software: Asistente de Orientación en Salud Pública

> **Nota de Requisitos y Levantamiento de Información:**  
> FALTA: Archivo anexo con la transcripción literal de preguntas ciudadanas de campo (se derivaron las 8 historias de usuario directamente del núcleo de necesidad oficial, síntomas del MSP y catálogo de signos de alarma de la OPS 2016).  
> FALTA: Endpoint o API REST pública en tiempo real de GeoSalud; se asume para el MVP una ingesta estructurada o dataset estático en `data/geosalud_ecuador.json`.

---

## 1. Historias de Usuario (MVP - Sprint 1)

### HU-01: Consulta de Medidas de Prevención y Eliminación de Criaderos
- **Historia:** Como ciudadano en una zona endémica, quiero consultar medidas para prevenir la picadura del mosquito y eliminar criaderos en mi hogar, para reducir el riesgo de transmisión del dengue en mi familia y comunidad.
- **Estimación:** 1.5 días.
- **Criterios de Aceptación (Gherkin):**
  - **Criterio 1.1:**
    - *Dado* que el usuario escribe "¿Cómo elimino los criaderos de mosquitos en mi patio?",
    - *Cuando* el sistema procesa la consulta contra la base vectorial del MSP,
    - *Entonces* devuelve recomendaciones directas (lavado, cepillado y tapado de recipientes, desecho de llantas y recipientes en desuso) citando la guía de prevención comunitaria del MSP.
  - **Criterio 1.2:**
    - *Dado* que el usuario consulta sobre el uso de repelentes o mosquiteros,
    - *Cuando* el RAG recupera los fragmentos oficiales,
    - *Entonces* detalla las medidas de protección personal (ropa manga larga, mosquiteros tratados) sin recomendar marcas comerciales.
  - **Criterio 1.3:**
    - *Dado* que el usuario realiza una pregunta sobre métodos preventivos no avalados científicamente (ej. plantas mágicas o sahumerios),
    - *Cuando* la información no consta en la base de conocimiento oficial,
    - *Entonces* el sistema declara que dicha práctica no consta en las guías oficiales y reitera las medidas de control físico del vector aprobadas por el MSP.
  - **Criterio 1.4:**
    - *Dado* que se genera la respuesta preventiva,
    - *Cuando* se visualiza en la interfaz,
    - *Entonces* se incluye al pie de la tarjeta la cita formal con documento y acápite oficial correspondiente.

---

### HU-02: Consulta Informativa sobre Síntomas Generales y Fases de la Enfermedad
- **Historia:** Como usuario con sospecha de malestar, quiero consultar cuáles son los síntomas habituales y las fases del dengue según la OPS/MSP, para comprender la evolución de la enfermedad sin recibir un diagnóstico clínico.
- **Estimación:** 2 días.
- **Criterios de Aceptación (Gherkin):**
  - **Criterio 2.1:**
    - *Dado* que el usuario pregunta "¿Cuáles son los síntomas típicos del dengue?",
    - *Cuando* el sistema genera la orientación basada en las guías clínicas de la OPS 2016,
    - *Entonces* lista la fiebre alta repentina, cefalea intensa, dolor retroocular, mialgias y artralgias, acompañada de una advertencia de que estos síntomas exigen evaluación médica.
  - **Criterio 2.2:**
    - *Dado* que el usuario consulta por qué se siente peor cuando baja la fiebre,
    - *Cuando* el sistema recupera la sección de curso clínico,
    - *Entonces* explica la fase crítica (entre el 3er y 7mo día de evolución) donde cae la fiebre pero pueden aparecer complicaciones.
  - **Criterio 2.3:**
    - *Dado* que el usuario pregunta "Tengo fiebre y dolor de ojos, ¿tengo dengue?",
    - *Cuando* el backend evalúa el prompt del usuario,
    - *Entonces* el sistema se abstiene de diagnosticar y responde: "No puedo emitir un diagnóstico. Estos síntomas coinciden con el cuadro clínico inicial del dengue según el MSP, por lo que debe acudir a un centro de salud para evaluación médica y exámenes de laboratorio."
  - **Criterio 2.4:**
    - *Dado* que la consulta requiere orientación general de síntomas,
    - *Cuando* el sistema emite la respuesta,
    - *Entonces* el tiempo total de respuesta es menor a 2.5 segundos e incluye la cita exacta de la Guía de Práctica Clínica del MSP.

---

### HU-03: Identificación Explicativa de Signos de Alarma
- **Historia:** Como familiar o cuidador de un paciente con fiebre, quiero conocer cuáles son los signos de alarma del dengue, para saber identificar a tiempo una complicación grave y buscar ayuda médica de inmediato.
- **Estimación:** 1.5 días.
- **Criterios de Aceptación (Gherkin):**
  - **Criterio 3.1:**
    - *Dado* que el usuario consulta "¿Cuáles son las señales de peligro o alarma en el dengue?",
    - *Cuando* el sistema consulta la base documental oficial de la OPS/MSP,
    - *Entonces* enumera explícitamente los 7 signos clínicos de alarma: dolor abdominal intenso y continuo, vómitos persistentes, acumulación de líquidos, sangrado de mucosas, decaimiento extremo/irritabilidad, mareo al ponerse de pie (hipotensión postural) y hepatomegalia.
  - **Criterio 3.2:**
    - *Dado* que se despliega la lista de signos de alarma,
    - *Cuando* el usuario lee la información en la pantalla,
    - *Entonces* el sistema resalta en color de alerta alta que la presencia de CUALQUIERA de estos signos requiere traslado inmediato a un hospital.
  - **Criterio 3.3:**
    - *Dado* que el usuario pregunta si el sangrado de encías o nariz es normal en el dengue,
    - *Cuando* el sistema procesa el síntoma,
    - *Entonces* clasifica el sangrado de mucosas como un signo de alarma formal según la OPS (2016) e instruye no esperar la cita regular y acudir a urgencias.
  - **Criterio 3.4:**
    - *Dado* que el usuario revisa los signos de alarma,
    - *Cuando* finaliza la lectura,
    - *Entonces* la interfaz le ofrece un botón directo y accesible para iniciar la lista interactiva de verificación de signos de alarma.

---

### HU-04: Lista Interactiva de Verificación (Checklist) de Signos de Alarma
- **Historia:** Como usuario o cuidador, quiero responder una lista de verificación interactiva de signos de alarma mediante preguntas sí/no, para determinar de forma objetiva y determinista si debo trasladar al paciente a urgencias.
- **Estimación:** 2.5 días.
- **Criterios de Aceptación (Gherkin):**
  - **Criterio 4.1:**
    - *Dado* que el usuario pulsa "Evaluar signos de alarma",
    - *Cuando* la interfaz despliega el checklist determinista,
    - *Entonces* presenta los campos estructurados correspondientes a los signos de alarma oficiales (dolor abdominal persistente, vómitos reiterados, sangrado, mareos graves, somnolencia extrema).
  - **Criterio 4.2:**
    - *Dado* que el usuario marca una o más casillas afirmativas ("SÍ"),
    - *Cuando* se envían las respuestas al backend a la función `evaluar_signos_alarma(respuestas)`,
    - *Entonces* la función en Python ejecuta la evaluación lógica determinista retornando `alerta: TRUE` y el listado de signos detectados en menos de 300 ms sin consultar al LLM.
  - **Criterio 4.3:**
    - *Dado* que el usuario marca "NO" a todos los signos de alarma pero reporta fiebre,
    - *Cuando* el backend procesa el checklist,
    - *Entonces* retorna `alerta: FALSE` con instrucciones de vigilancia estricta de 48 horas, hidratación oral abundante y consulta médica ordinaria en su centro de salud.
  - **Criterio 4.4:**
    - *Dado* que el usuario envía el checklist sin contestar todos los campos obligatorios,
    - *Cuando* la validación de Pydantic intercepta la petición,
    - *Entonces* la API responde con un error HTTP 422 indicando con precisión los campos faltantes sin procesar un resultado ambiguo.

---

### HU-05: Protocolo de Derivación Inmediata ante Signos de Alarma o Emergencia
- **Historia:** Como usuario con al menos un signo de alarma identificado en el checklist, quiero recibir una instrucción clara e inmediata de derivación y contacto con emergencias, para salvaguardar la vida del paciente sin demoras.
- **Estimación:** 2 días.
- **Criterios de Aceptación (Gherkin):**
  - **Criterio 5.1:**
    - *Dado* que el resultado de `evaluar_signos_alarma` arrojó `alerta: TRUE`,
    - *Cuando* se renderiza la respuesta al usuario,
    - *Entonces* la interfaz muestra un banner rojo de emergencia indicando: "ATENCIÓN MÉDICA INMEDIATA REQUERIDA. Presenta signos de alarma de dengue que pueden evolucionar a choque por extravasación."
  - **Criterio 5.2:**
    - *Dado* que se confirma la alerta de peligro,
    - *Cuando* se presenta la vista de derivación,
    - *Entonces* se proporciona un botón con enlace de llamada directa al `tel:911` (ECU-911) para dispositivos móviles.
  - **Criterio 5.3:**
    - *Dado* que el paciente debe ser trasladado a un hospital,
    - *Cuando* el usuario solicita dónde acudir,
    - *Entonces* el sistema le solicita su cantón o ciudad para desplegar los centros de salud de segundo o tercer nivel con servicio de emergencia habilitado.
  - **Criterio 5.4:**
    - *Dado* que se activa el protocolo de derivación,
    - *Cuando* el usuario intenta continuar con preguntas generales de chat,
    - *Entonces* la interfaz mantiene fijado en la parte superior el recordatorio prioritario de acudir al establecimiento de salud de inmediato.

---

### HU-06: Localización Determinista de Establecimientos de Salud (GeoSalud / MSP)
- **Historia:** Como ciudadano en situación de riesgo o consulta, quiero ingresar mi ciudad o cantón, para obtener la lista oficial de centros de salud y hospitales disponibles en mi localidad.
- **Estimación:** 2.5 días.
- **Criterios de Aceptación (Gherkin):**
  - **Criterio 6.1:**
    - *Dado* que el usuario ingresa su ciudad (ej. "Guayaquil" o "Portoviejo"),
    - *Cuando* el backend invoca la herramienta determinista `ubicar_establecimiento(ciudad="Guayaquil")`,
    - *Entonces* consulta el dataset oficial de GeoSalud y retorna una lista de hasta 5 establecimientos filtrados con nombre, tipo (Centro de Salud Tipo C / Hospital General), dirección y teléfono.
  - **Criterio 6.2:**
    - *Dado* que el usuario ingresa una ciudad con tildes, mayúsculas o caracteres especiales (ej. "guayaquil", "GUAYAQUIL", "Portoviejo"),
    - *Cuando* la herramienta determinista sanitiza el parámetro de entrada,
    - *Entonces* normaliza la cadena (lowercase, unidecode) y localiza las coincidencias exactas sin fallar.
  - **Criterio 6.3:**
    - *Dado* que el usuario ingresa una localidad que no figura en la base de datos de GeoSalud,
    - *Cuando* la función no encuentra registros,
    - *Entonces* devuelve un mensaje claro informando que no dispone de datos para esa localidad e instruye llamar directamente a la línea 171 del MSP o al 911.
  - **Criterio 6.4:**
    - *Dado* que la consulta proviene del LLM por Tool Calling,
    - *Cuando* el modelo genera el texto de salida,
    - *Entonces* presenta los datos tabulados y verificados exclusivamente de la salida JSON de la función, sin inventar nombres ni teléfonos.

---

### HU-07: Trazabilidad Obligatoria y Citas de Fuentes Oficiales
- **Historia:** Como usuario o auditor de salud pública, quiero verificar la fuente oficial de cada afirmación emitida por el asistente, para tener total certeza de que la respuesta está basada en directrices vigentes del MSP y OPS.
- **Estimación:** 2 días.
- **Criterios de Aceptación (Gherkin):**
  - **Criterio 7.1:**
    - *Dado* que el asistente genera una respuesta a partir de RAG,
    - *Cuando* el backend construye el esquema de salida `ChatResponse`,
    - *Entonces* incluye obligatoriamente una lista de objetos `fuentes` con los campos: `documento`, `origen`, `seccion_o_pagina` y `url`.
  - **Criterio 7.2:**
    - *Dado* que la información recuperada de ChromaDB tiene una distancia de similitud superior al umbral configurado (ej. score de relevancia deficiente),
    - *Cuando* no se encuentran fragmentos pertinentes en los documentos oficiales,
    - *Entonces* el sistema responde: "La información consultada no se encuentra disponible en las guías oficiales del MSP/OPS cargadas. Por favor consulte en www.salud.gob.ec o acuda a un centro de salud."
  - **Criterio 7.3:**
    - *Dado* que una respuesta utiliza fragmentos de dos guías clínicas distintas,
    - *Cuando* se compone la respuesta final,
    - *Entonces* se indexan las referencias numéricas en el texto `[1]`, `[2]` vinculadas a sus respectivas fuentes al final del mensaje.
  - **Criterio 7.4:**
    - *Dado* que el frontend recibe el payload JSON del backend,
    - *Cuando* renderiza la tarjeta de respuesta,
    - *Entonces* despliega un acordeón colapsable titulado "Fuentes Oficiales Consultadas" con enlaces verificables.

---

### HU-08: Bloqueo Determinista de Solicitudes de Prescripción y Advertencia contra Automedicación
- **Historia:** Como usuario que pregunta qué medicamento tomar ante síntomas de dengue, quiero recibir una advertencia contundente sobre los peligros de la automedicación, para evitar el consumo letal de fármacos contraindicados como el ácido acetilsalicílico o el ibuprofeno.
- **Estimación:** 2 días.
- **Criterios de Aceptación (Gherkin):**
  - **Criterio 8.1:**
    - *Dado* que el usuario introduce palabras clave o intenciones de medicación (ej. "¿Qué pastilla tomo para el dolor?", "¿Puedo tomar ibuprofeno o aspirina?"),
    - *Cuando* el middleware de seguridad o el prompt del agente intercepta la intención,
    - *Entonces* bloquea cualquier sugerencia de dosis o fármacos y emite el mensaje estandarizado de prohibición de automedicación.
  - **Criterio 8.2:**
    - *Dado* que se emite la advertencia contra la automedicación,
    - *Cuando* se explica el motivo clínico según la guía del MSP,
    - *Entonces* se enfatiza explícitamente que los antiinflamatorios no esteroideos (AINEs como ibuprofeno, aspirina, diclofenaco, naproxeno) aumentan drásticamente el riesgo de hemorragia grave en casos de dengue.
  - **Criterio 8.3:**
    - *Dado* que el usuario insiste en que le receten un antibiótico o jarabe,
    - *Cuando* el sistema genera su respuesta,
    - *Entonces* aclara que el dengue es una infección viral donde los antibióticos son totalmente ineficaces y perjudiciales sin prescripción médica.
  - **Criterio 8.4:**
    - *Dado* que la advertencia se dispara,
    - *Cuando* se completa la respuesta,
    - *Entonces* se provee de manera inmediata la recomendación de hidratación con suero oral y el botón para ubicar el centro de salud más cercano.

---

## 2. Requisitos No Funcionales (RNF) Medibles

| ID | Categoría | Requisito No Funcional | Métrica / Umbral Verificable |
| :--- | :--- | :--- | :--- |
| **RNF-01** | **Rendimiento / Tiempo de Respuesta** | La API de backend en FastAPI debe procesar y devolver respuestas de orientación RAG con latencia controlada. | **P95 < 2.5 segundos** en consultas de texto RAG; **P99 < 350 ms** en ejecución de herramientas deterministas (`evaluar_signos_alarma`, `ubicar_establecimiento`). |
| **RNF-02** | **Trazabilidad y Fidelidad de Fuentes** | Ninguna respuesta informativa generada por RAG podrá carecer de metadatos de origen documental oficial. | **100% de las respuestas afirmativas** deben contener metadatos estructurados (`documento`, `seccion`, `url`). Cero tolerancia a alucinación de fuentes. |
| **RNF-03** | **Privacidad y Protección de Datos (PII)** | El sistema no almacenará ni transmitirá datos de salud identificables de los ciudadanos (cumplimiento LOPDP Ecuador). | **0 bytes de datos personales (PII)** persistidos en disco o base vectorial. Registros de logging sanitizados (sin nombres, cédulas ni IPs completas). |
| **RNF-04** | **Disponibilidad y Confiabilidad** | El servicio web debe permanecer accesible durante situaciones de brote o contingencia sanitaria comunitaria. | **Disponibilidad ≥ 99.5%** en horarios hábiles de contingencia; degradación elegante ante fallo de proveedor LLM (retorno a checklist determinista estático). |
| **RNF-05** | **Codificación y Manejo de Texto** | Todos los módulos, esquemas Pydantic, scripts de ingesta y endpoints deben operar estrictamente en UTF-8. | **Codificación 100% UTF-8** en entrada y salida JSON para preservar tildes, caracteres especiales y términos médicos. |
