# GuíaVital · Guion Oficial de Sustentación Técnica
**Proyecto de Titulación Complexivo · Ingeniería de Software con IA Generativa**  
**Caso N.º 05 – Grupo 5 · Versión del Software:** `v0.5.2` (Tag oficial Git)  
**Institución:** Universidad Regional Autónoma de Los Andes (UNIANDES)  
**Tiempo Total de Defensa:** 12 minutos exactos (720 segundos)  
**Velocidad de Dicción Calibrada:** 115 – 120 palabras por minuto (tono sereno, confiado y asertivo)

---

## 1. Distribución de Roles y Cronograma por Expositor

| Bloque | Expositor | Rol Principal | Diapositivas | Tiempo Asignado | Reloj Acumulado |
|---|---|---|---|---|---|
| **Bloque 1** | **Luis Caguana** | Tech Lead | **Diapositivas 01 a 03**<br>Contexto, Problema Clínico y Objetivos | **3 min 00 s** (180 s) | `00:00 – 03:00` |
| **Bloque 2** | **Rafael Minaya** | QA / Seguridad | **Diapositiva 04**<br>Demostración en Vivo en Google Cloud Run | **3 min 00 s** (180 s) | `03:00 – 06:00` |
| **Bloque 3** | **Wilson Salinas** | Builder | **Diapositivas 05 a 12**<br>Arquitectura, ADRs, Pruebas, CI/CD, Seguridad y Cierre | **6 min 00 s** (360 s) | `06:00 – 12:00` |

---

## 2. Recomendaciones de Lenguaje Corporal y Pacing

1. **Postura de Dominio Técnico:** No mirar fijamente a las diapositivas. Las láminas son de diseño minimalista suizo para servir de ancla visual al tribunal; el presentador debe mirar a los evaluadores.
2. **Respiración y Pausas Estratégicas:** Tras enunciar un dato clave (ej. *"cero falsos negativos"*, *"distancia coseno menor o igual a 0.155"*), hacer una pausa de 1.5 a 2 segundos para permitir que la cifra se asiente.
3. **Manejo de Transiciones:** Al entregar la palabra al compañero, nombrarlo con su rol técnico para reforzar la cohesión del equipo ante el tribunal.
4. **Respaldo en Vivo:** Mientras Luis expone el Bloque 1, Rafael ya debe tener abierta en una pestaña la URL pública `https://guiavital-448060764458.us-central1.run.app` con el backend activo en `/manage/health`.

---

## 3. Guion Detallado Diapositiva por Diapositiva

```
========================================================================================
BLOQUE 1: LUIS CAGUANA (TECH LEAD) · 00:00 A 03:00 (3 MINUTOS)
========================================================================================
```

### Diapositiva 01 · Portada del Proyecto
- **Tiempo asignado:** 55 segundos (`00:00 – 00:55`)
- **Objetivo:** Captar autoridad inmediata, ubicar el caso de estudio y presentar al equipo.
- **Acotación:** *Mirada frontal al tribunal, tono firme y pausado. No apresurarse.*

> **Luis Caguana:**  
> «Buenos días, miembros del Tribunal Evaluador. Somos el Grupo 5 y hoy les presentamos **GuíaVital**, nuestra solución integral para el Caso de Estudio número 5: un asistente inteligente de orientación ciudadana en salud pública sobre dengue y arbovirosis.
>
> *(Pausa de 2 segundos)*
>
> Cuando se aplica inteligencia artificial generativa a la salud, el mayor riesgo es otorgar autonomía diagnóstica a un modelo de lenguaje. Por esa razón, construimos GuíaVital sobre tres principios no negociables:
> 1. Recuperación aumentada (RAG) respaldada exclusivamente por literatura oficial del Ministerio de Salud Pública y la OPS.
> 2. Un triaje de signos de alarma gobernado por reglas clínicas deterministas, garantizando cero falsos negativos.
> 3. Y estricta minimización de datos personales bajo la LOPDP ecuatoriana con confirmación humana supervisada.
>
> El equipo de ingeniería está conformado por mi persona, Luis Caguana como Tech Lead; Rafael Minaya a cargo del Aseguramiento de Calidad y Seguridad; y Wilson Salinas como Builder responsable del Pipeline RAG, Frontend e infraestructura Cloud.»

---

### Diapositiva 02 · Problema Clínico, Contexto y Usuario
- **Tiempo asignado:** 65 segundos (`00:55 – 02:00`)
- **Objetivo:** Justificar la pertinencia epidemiológica en Ecuador y el marco de privacidad.
- **Acotación:** *Cambiar a Diapositiva 02. Señalar con seguridad las tarjetas de la izquierda y luego la derecha.*

> **Luis Caguana:**  
> «¿Qué problema de salud pública resolvemos en nuestro país? En las provincias del litoral y la Amazonía ecuatoriana, los inviernos provocan brotes endémicos que colapsan los servicios de emergencia. Pero la mortalidad evitable ocurre principalmente por dos factores críticos en el hogar:
>
> El primero es la **automedicación peligrosa con AINEs**: cuando un paciente con fiebre toma ibuprofeno, aspirina o naproxeno sin saber que cursa dengue, estos fármacos inhiben las plaquetas y multiplican el riesgo de hemorragia grave y choque. El segundo es la **detección tardía de los signos de alarma**, sobre todo entre el tercer y séptimo día de enfermedad, cuando cae la fiebre y se inicia la fase crítica con dolor abdominal continuo o vómitos persistentes.
>
> *(Pausa breve señalando el panel derecho)*
>
> GuíaVital fue diseñado para familias en zonas de riesgo, cuidadores de niños pequeños o gestantes, y promotores de salud comunitaria. Nuestra frontera clínica es categórica: **orientamos y derivamos oportunamente, pero jamás emitimos diagnósticos ni recetamos medicamentos**.
>
> Además, cumplimos estrictamente los artículos 10 y 11 de la LOPDP: no recolectamos cédulas ni identificadores innecesarios; y los números de contacto de emergencia se procesan en memoria volátil y se enmascaran de forma irreversible con nuestra función `anonimizar_pii()` antes de persistir en base de datos.»

---

### Diapositiva 03 · Objetivos del Caso 05 y Alcance en 4 Fases
- **Tiempo asignado:** 60 segundos (`02:00 – 03:00`)
- **Objetivo:** Explicar el mandato formal del caso y las 4 fases de ingeniería.
- **Acotación:** *Cambiar a Diapositiva 03. Mantener el hilo conductor con calma y dar paso a Rafael.*

> **Luis Caguana:**  
> «El mandato del Caso 05 fue muy claro: construir un asistente web que explique medidas de prevención y síntomas citando material oficial, e incorporar un agente con triaje determinista de signos de alarma que derive al ECU-911 o centros de salud, sin recetar jamás.
>
> Para lograrlo de forma reproducible, estructuramos el proyecto en **cuatro fases de ingeniería**:
> - En la **Fase 1 de Diseño**, definimos el alcance negativo estricto y curamos las guías clínicas de la OPS 2016 y los manuales SIVE-Alerta del MSP.
> - En la **Fase 2 de MVP**, desarrollamos el backend en FastAPI y frontend en React 19, implementando prompts con salvaguardas y tolerancia a fallos entre Gemini Flash y Groq.
> - En la **Fase 3 de Inteligencia**, construimos la base vectorial con 161 fragmentos en ChromaDB bajo un umbral de asertividad menor o igual a `0.155`, junto a las herramientas clínicas deterministas y la pausa de confirmación humana.
> - Y en la **Fase 4 de Producción**, desplegamos en Google Cloud Run certificando el sistema mediante una suite de 135 pruebas automatizadas.
>
> A continuación, le cedo la palabra a **Rafael Minaya**, quien ejecutará la demostración técnica en vivo sobre nuestra plataforma en producción.»

---

```
========================================================================================
BLOQUE 2: RAFAEL MINAYA (QA & SEGURIDAD) · 03:00 A 06:00 (3 MINUTOS)
========================================================================================
```

### Diapositiva 04 · Demostración en Vivo en Google Cloud Run
- **Tiempo asignado:** 3 minutos exactos (`03:00 – 06:00`)
- **Objetivo:** Demostrar en vivo los 3 comportamientos clave en la URL pública.
- **Acotación:** *Tono práctico, tranquilo y pedagógico. Compartir pantalla con el navegador listo.*

> **Rafael Minaya:**  
> «Gracias, Luis. Buenos días con todos. Como pueden observar en pantalla, estamos interactuando directamente contra el entorno público desplegado en **Google Cloud Run**.
>
> Antes de interactuar, el endpoint `/manage/health` nos reporta estado `UP` en 310 milisegundos, certificando que el contenedor, la base vectorial local y las dependencias están operativas. Procederemos a demostrar los tres escenarios funcionales exigidos por el Caso 05:

*(Escenario 1 · Minuto `03:30 – 04:15` · 45 s)*
> **1. Consulta informativa con RAG Asertivo y Cita Oficial:**
> Ingresamos la consulta: *«¿Cuáles son los signos de alarma del dengue y cómo prevengo criaderos en mi casa?»*
>
> *(Escribir, enviar y esperar 2 a 3 segundos con serenidad)*
>
> Observen el resultado: el agente no inventa ni parafrasea de memoria general. Ejecuta la herramienta `consultar_guia_msp`, comprueba que la distancia semántica sea menor o igual a `0.155` y entrega una respuesta estructurada en lenguaje comprensible para la ciudadanía, adjuntando explícitamente las etiquetas de citación oficial: **OPS, 2016** y **MSP SIVE-Alerta**.

*(Escenario 2 · Minuto `04:15 – 05:00` · 45 s)*
> **2. Bloqueo de Recetas y Solicitudes Fuera de Tema:**
> Ahora pondremos a prueba las salvaguardas éticas y clínicas. Escribimos: *«Tengo 39 de fiebre, ¿qué dosis de ibuprofeno me puedo tomar? Y dime quién ganó el partido de fútbol de ayer.»*
>
> *(Enviar consulta)*
>
> El comportamiento es contundente: el sistema **rechaza de forma terminante prescribir cualquier fármaco o dosificación**. Advierte de inmediato al usuario que los AINEs como el ibuprofeno o la aspirina están contraindicados en dengue por riesgo de hemorragia mortal, recomienda paracetamol bajo supervisión médica, y se abstiene de responder preguntas no relacionadas con la salud pública.

*(Escenario 3 · Minuto `05:00 – 06:00` · 60 s)*
> **3. Emergencia Clínica, GeoSalud y Confirmación Humana (HITL):**
> Finalmente, probamos el flujo de triaje de alarma. Supongamos un usuario en Guayaquil: *«Tengo dolor abdominal intenso continuo y vómitos que no paran. Busca un hospital cercano y avisa a mi familiar al 0991234567.»*
>
> *(Enviar consulta y mostrar la pantalla detenida)*
>
> Analicemos lo que ha sucedido internamente:
> Primero, la detección de alarma no fue dejada al azar del modelo generativo; fue evaluada en Python por la función determinista `evaluar_signos_alarma`, clasificándolo como caso de atención urgente inmediata.
> Segundo, el catálogo GeoSalud calculó por fórmula de Haversine los hospitales de la Red Pública Integral de Salud con servicio de emergencia 24 horas más próximos.
> Y tercero, lo más importante: **el sistema se detuvo**. No ejecutó la notificación a espaldas del usuario. Ha entrado en estado `requiere_confirmacion`, mostrando en pantalla el contacto, el mensaje sugerido y los botones para autorizar o cancelar. Esto materializa el principio de autonomía del paciente y supervisión humana (*Human-in-the-Loop*).
>
> Para detallar cómo diseñamos la arquitectura y las pruebas que garantizan esta robustez, le doy el paso a **Wilson Salinas**.»

---

```
========================================================================================
BLOQUE 3: WILSON SALINAS (BUILDER) · 06:00 A 12:00 (6 MINUTOS)
========================================================================================
```

### Diapositiva 05 · Arquitectura del Sistema en 4 Capas
- **Tiempo asignado:** 55 segundos (`06:00 – 06:55`)
- **Objetivo:** Explicar el desacoplamiento de capas y el diseño técnico.
- **Acotación:** *Cambiar a Diapositiva 05. Tono técnico, seguro y pausado.*

> **Wilson Salinas:**  
> «Muchas gracias, Rafael. Buenos días, señores miembros del Tribunal. Para que una solución médica sea mantenible y segura en producción, debe tener límites de responsabilidad bien definidos. Por ello, diseñamos una **arquitectura desacoplada en cuatro capas de seguridad**:
>
> - En la **Capa 01 (Cliente Web)**, el frontend en React 19 y TypeScript está gobernado por una máquina determinista de 7 estados en `estados.ts`, evitando estados intermedios inconsistentes y coordinando la interfaz reactiva del checklist del MSP.
> - En la **Capa 02 (API Gateway)**, FastAPI maneja un esquema de CORS restringido únicamente al dominio de producción, junto a un limitador de tasa deslizante de 10 peticiones por minuto para mitigar abusos OWASP LLM06, y respuestas estandarizadas bajo **RFC 9457** que aíslan las trazas del servidor.
> - En la **Capa 03 (Núcleo Clínico)**, el agente opera en un bucle ReAct cerrado con solo 4 herramientas registradas y un tope forzado de 6 iteraciones, complementado por nuestra cinta de confianza con umbral `0.85`.
> - Y en la **Capa 04 (Datos e Inteligencia)**, implementamos **ChromaDB embebido en disco local** con 161 fragmentos vectorizados con el modelo `multilingual-e5-small`, conmutación dual de modelos LLM y la base geoespacial GeoSalud Ecuador.»

---

### Diapositiva 06 · Decisiones Técnicas de Arquitectura (ADRs)
- **Tiempo asignado:** 60 segundos (`06:55 – 07:55`)
- **Objetivo:** Justificar las 5 decisiones más críticas y sus alternativas descartadas.
- **Acotación:** *Cambiar a Diapositiva 06. Señalar la tabla comparativa con aplomo.*

> **Wilson Salinas:**  
> «En ingeniería de software, cada decisión técnica debe sustentarse con métricas. En la Diapositiva 6 exponemos nuestros registros de decisiones de arquitectura (ADRs):
>
> 1. **ADR-001 (Proveedor IA y Fallback):** Seleccionamos **Gemini Flash** como principal y **Groq** como respaldo en caliente. Descartamos a Groq como principal porque su cuota gratuita de 6 mil a 12 mil tokens por minuto colapsaba con apenas dos consultas con contexto RAG; Gemini nos brinda un millón de tokens por minuto.
> 2. **ADR-002 y 004 (Triaje por Reglas):** Evaluamos los 8 signos de alarma y sinónimos coloquiales con **código determinista en Python**. Descartamos delegar el triaje al LLM porque el riesgo de falsos negativos por alucinación es clínicamente inadmisible.
> 3. **ADR-005 (RAG Asertivo ChromaDB + E5):** En el pipeline RAG que configuramos, aplicamos un **umbral de distancia coseno menor o igual a `0.155`**, equivalente a una **similitud semántica mínima del 84.5%**. Al ser un asistente de salud, si un fragmento no alcanza esta proximidad estricta con las guías de OPS o MSP, se descarta y el asistente se abstiene, logrando cero citas irrelevantes o desinformación.
> 4. **ADR de Flujo:** Con nuestro clasificador de confianza logramos 70% de atención automatizada, 30% de desvío a supervisión humana y **cero errores silenciosos** en el conjunto dorado.
> 5. **ADR-0006 (Despliegue Cloud Run):** Empaquetamos en Google Cloud Run asignando **2 vCPU y 2 GiB de RAM** con `min-instances=0` para costo cero en reposo. Descartamos AWS Lambda o Vercel Serverless por su restricción de paquete de 250 MB, incapaz de alojar PyTorch CPU y los pesos del modelo E5.»

---

### Diapositiva 07 · Evidencias I: Suite de 135 Pruebas y Smoke Tests
- **Tiempo asignado:** 50 segundos (`07:55 – 08:45`)
- **Objetivo:** Demostrar la cobertura integral de pruebas y validación en la nube.
- **Acotación:** *Cambiar a Diapositiva 07. Resaltar las 4 cifras de la franja superior.*

> **Wilson Salinas:**  
> «La confiabilidad de este sistema está demostrada con datos: contamos con una **suite total de 135 pruebas automatizadas pasando al 100%**:
> - **92 pruebas de backend** con Pytest, que cubren desde los contratos Pydantic hasta el limitador de tasa y la resiliencia del cliente LLM.
> - **27 pruebas de frontend** con Vitest y MSW, testeando la máquina de 7 estados y el renderizado seguro de componentes.
> - Y **16 pruebas de humo en vivo** ejecutadas contra la URL pública de Cloud Run mediante `tests/smoke.py`.
>
> Como se aprecia en los cuatro cuadrantes, estas 16 pruebas en producción certifican una latencia promedio de **2.73 segundos** y un percentil 95 de **6.31 segundos**, validando la salud del servicio en 250 milisegundos, el bloqueo de recetas, la geolocalización Haversine, la neutralización de ataques de inyección LLM01 y la respuesta HTTP 429 con cabecera `Retry-After`.»

---

### Diapositiva 08 · Evidencias II: Métricas Clínicas y Pipeline CI/CD
- **Tiempo asignado:** 50 segundos (`08:45 – 09:35`)
- **Objetivo:** Explicar el progreso frente a Semana 3 y el ciclo de vida continuo.
- **Acotación:** *Cambiar a Diapositiva 08. Mirar al tribunal al enunciar las métricas.*

> **Wilson Salinas:**  
> «En la evaluación cuantitativa de calidad superamos todas las metas exigidas:
> - **86.7% de acierto RAG en Top-3**, superando la meta del 85%.
> - **100% de respuestas con cita oficial** verificada bajo la distancia `0.155`.
> - **100% de abstención** ante preguntas no médicas.
> - **95.2% de Hit@5 vectorial** sobre las 21 consultas de referencia.
> - **30% de desvío a revisión humana** con **cero errores silenciosos**.
>
> Esta calidad se preserva mediante nuestro **pipeline CI/CD automatizado en GitHub Actions**:
> 1. En cada Pull Request, `ci.yml` ejecuta Gitleaks, los 92 tests de Pytest, los 27 tests de Vitest y el evaluador clínico, sumando 119 pruebas bloqueantes.
> 2. Al fusionar en la rama principal, `release.yml` realiza el bump automático a la versión `v0.5.2` y sincroniza el changelog.
> 3. Finalmente, `deploy.yml` compila las imágenes sin privilegios root, despliega en Cloud Run con 2 vCPU y 2 GiB de RAM y ejecuta las 16 pruebas de humo en vivo.»

---

### Diapositiva 09 · Seguridad Operativa y Resiliencia ante Fallos
- **Tiempo asignado:** 50 segundos (`09:35 – 10:25`)
- **Objetivo:** Explicar el manejo de secretos en GCP y el circuito de tolerancia a fallos.
- **Acotación:** *Cambiar a Diapositiva 09. Transmitir total seguridad operativa.*

> **Wilson Salinas:**  
> «En cuanto a la seguridad de la información: **cero credenciales en código ni en el historial de Git**. En el repositorio solo existe el archivo `.env.example`. Todas las claves de API residen en **Google Cloud Secret Manager** y se inyectan en tiempo de ejecución en el contenedor, auditadas en cada commit por Gitleaks y por nuestro script `verificar-secretos.mjs`.
>
> *(Pausa breve señalando el panel derecho)*
>
> Y cuando el modelo generativo falla o tiene intermitencia, nuestro módulo `llm.py` implementa un **circuito de resiliencia en cinco capas**:
> 1. Timeout estricto a los 30 segundos y límite de 2048 tokens.
> 2. Hasta 3 reintentos con backoff exponencial y jitter ante errores 429 o caídas 5xx.
> 3. Un reintento de autocorrección enviando los errores de validación Pydantic al modelo si el JSON llega mal estructurado.
> 4. Conmutación transparente e inmediata a Groq Llama 3 si Gemini sufre una indisponibilidad.
> 5. Y si ambos proveedores cayeran a nivel global, el sistema se degrada grácilmente retornando HTTP 503 bajo RFC 9457 sin filtrar trazas internas.»

---

### Diapositiva 10 · Limitaciones Conocidas y Transparencia en el Uso de IA
- **Tiempo asignado:** 45 segundos (`10:25 – 11:10`)
- **Objetivo:** Declarar con madurez técnica las fronteras del sistema y la autoría del equipo.
- **Acotación:** *Cambiar a Diapositiva 10. Tono transparente y profesional.*

> **Wilson Salinas:**  
> «Por rigor científico declaramos con transparencia cinco limitaciones del sistema:
> 1. Es una herramienta de orientación preventiva; **no constituye un acto médico presencial**.
> 2. Al escalar a cero instancias para mantener costo $0, el primer arranque en frío tarda entre 6 y 10 segundos mientras carga los pesos del modelo E5 en memoria.
> 3. Si ocurre una caída global de APIs externas, el chat muestra indisponibilidad controlada, pero el endpoint determinista de signos de alarma continúa operando.
> 4. GeoSalud focaliza su catálogo en hospitales y centros Tipo C con emergencia 24 horas.
> 5. Y la interacción es exclusivamente textual y por checklist; no analiza imágenes de piel.
>
> Asimismo, declaramos que los asistentes de IA generativa se utilizaron como aceleradores para el código base inicial y plantillas de pruebas. Sin embargo, el 100% de la lógica clínica, la calibración del RAG, los sinónimos regionales y la suite de 135 pruebas fueron programados, auditados y validados manualmente por Luis, Rafael y mi persona.»

---

### Diapositiva 11 · Conclusiones y Cumplimiento del Caso 05
- **Tiempo asignado:** 35 segundos (`11:10 – 11:45`)
- **Objetivo:** Confirmar el 100% de cumplimiento de las metas del proyecto.
- **Acotación:** *Cambiar a Diapositiva 11. Conclusión contundente.*

> **Wilson Salinas:**  
> «Para concluir: **el Grupo 5 ha cumplido al 100% los cuatro indicadores mandatorios del Caso 05**:
> - 100% en derivación ante signos de alarma con cero falsos negativos.
> - 100% en rechazo de solicitudes de medicamentos o dosificaciones.
> - 86.7% en recuperación RAG con 100% de citación oficial comprobada.
> - Y despliegue productivo en HTTPS con 135 pruebas certificadas y cero secretos expuestos.
>
> GuíaVital demuestra que la inteligencia artificial en salud pública es viable cuando se subordina a los principios de la bioética: **no maleficencia** al prohibir recetas que causarían hemorragias, **beneficencia** al basarse estrictamente en guías de OPS y MSP, y **autonomía** respetando la supervisión humana y la privacidad ciudadana bajo la LOPDP.»

---

### Diapositiva 12 · Despedida y Sesión de Preguntas
- **Tiempo asignado:** 15 segundos (`11:45 – 12:00`)
- **Objetivo:** Cierre formal y disposición a la ronda de preguntas.
- **Acotación:** *Cambiar a Diapositiva 12. Saludo final conjunto del equipo.*

> **Wilson Salinas:**  
> «Muchas gracias por su atención, señores miembros del Tribunal.
>
> Quedamos a su entera disposición para responder a sus inquietudes técnicas, clínicas o realizar cualquier prueba adicional sobre nuestro entorno en vivo.»

---

## 4. Guía Rápida de Contingencias Técnicas para Preguntas del Tribunal

Si el Tribunal realiza preguntas profundas en la ronda de defensa, apóyense en estas respuestas directas:

1. **¿Por qué la distancia del RAG es 0.155?**  
   *«Usamos `intfloat/multilingual-e5-small` con distancia coseno. Un umbral de 0.155 equivale a una similitud mínima de 84.5%. En pruebas empíricas (`eval/evaluar.py`), con umbrales más altos como 0.25 entraban fragmentos sobre control de vectores cuando se preguntaba por síntomas clínicos; fijar 0.155 garantiza que solo se cite el fragmento exacto o el sistema se abstenga.»*

2. **¿Por qué Cloud Run tiene 2 vCPU y 2 GiB de RAM?**  
   *«Originalmente se probó con 1 GiB, pero PyTorch CPU con el modelo E5 en memoria (~470 MB) sumado al runtime de FastAPI y ChromaDB bajo concurrencia generaba riesgo de OOM (Out Of Memory) en picos de tráfico. Con 2 vCPU y 2 GiB de RAM el tiempo de respuesta p95 bajó a 6.31 segundos y la latencia promedio a 2.73 segundos con estabilidad absoluta.»*

3. **¿Cómo garantizan que no haya PII almacenada?**  
   *«Aplicamos el principio de minimización de datos (Art. 10 y 11 LOPDP, ADR-0007). El sistema no cuenta con tabla de usuarios ni login. Si en una emergencia el usuario provee un número de contacto, este se usa en memoria volátil para generar el enlace de WhatsApp y pasa por `anonimizar_pii()`, que enmascara los dígitos centrales (ej. `099***67`) antes de cualquier persistencia en base de datos.»*

4. **¿Qué sucede si fallan las APIs de IA?**  
   *«El sistema tiene conmutación automática de Gemini Flash a Groq Llama 3. Si ambos cayeran por una falla global de infraestructura, el endpoint conversacional responde HTTP 503 bajo estándar RFC 9457 indicando indisponibilidad sin exponer el servidor, mientras que el endpoint determinista `/herramientas/signos-alarma` y el checklist continúan operando localmente al 100%.»*
