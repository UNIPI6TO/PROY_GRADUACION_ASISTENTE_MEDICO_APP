# 01. Propuesta de Solución: Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis

## 1. Problema Real y Justificación
El dengue es una enfermedad viral aguda transmitida por el mosquito *Aedes aegypti*, endémica en las regiones de la Costa y la Amazonía ecuatorianas. Durante los picos epidemiológicos y brotes estacionales, la demanda espontánea colapsa y satura las salas de emergencia y los centros de salud del primer nivel de atención.

El factor crítico que determina la morbilidad grave y la mortalidad es la **consulta médica tardía**. La población con frecuencia no reconoce la fase crítica de la enfermedad (cuando desaparece la fiebre pero emergen los signos de alarma), confunde el dengue con cuadros gripales comunes, o recurre a la automedicación peligrosa (como el uso de AINEs que incrementan el riesgo hemorrágico).

Aunque el Ministerio de Salud Pública del Ecuador (MSP) y la Organización Panamericana de la Salud (OPS) disponen de guías clínicas completas y materiales educativos, la ciudadanía enfrenta barreras de accesibilidad, lenguaje técnico y sobreabundancia de desinformación en línea. Se requiere un canal digital directo, validado y accesible que guíe oportunamente al ciudadano hacia la prevención y la búsqueda inmediata de atención médica cuando existan signos de peligro.

---

## 2. Usuarios Objetivo
1. **Población en zonas endémicas o de brote:** Ciudadanos de la Costa y Amazonía que presentan fiebre o malestar general, o conviven con personas en riesgo, requiriendo claridad sobre cuidados y síntomas de alarma.
2. **Cuidadores de grupos vulnerables:** Padres, familiares y cuidadores de niños menores de 5 años, adultos mayores, mujeres embarazadas y personas con enfermedade concurrentes (diabetes, hipertensión, nefropatías).
3. **Comunidad en general:** Personas interesadas en erradicar criaderos domiciliarios y adoptar medidas preventivas comunitarias e individuales.

---

## 3. Alcance del Sistema

### 3.1 Lo que el sistema HACE (Alcance Positivo)
- **Orientación informativa contextualizada:** Responde preguntas sobre medidas preventivas, ciclo de vida del vector, fases de la enfermedad y síntomas habituales, basándose de forma estricta y exclusiva en la documentación oficial del MSP y OPS.
- **Trazabilidad y citación documental:** Cada respuesta generada incluye de forma obligatoria la fuente oficial, el documento y la sección o página de referencia.
- **Lista de verificación (Checklist) determinista de signos de alarma:** Aplica un triaje algorítmico guiado en código Python para evaluar la presencia de signos de alarma (dolor abdominal intenso y continuo, vómitos persistentes, sangrado de mucosas, letargo/irritabilidad, hipotensión postural, acumulación de líquidos).
- **Derivación inmediata:** Si el checklist detecta al menos un signo de alarma, el sistema interrumpe la orientación informativa y genera instrucciones claras de traslado urgente al establecimiento de salud más cercano o llamar al ECU-911.
- **Ubicación de establecimientos de salud:** Consulta mediante herramientas deterministas el directorio oficial de establecimientos (GeoSalud / MSP) por localidad o ciudad.

### 3.2 Lo que el sistema NUNCA HARÁ (Alcance Negativo Estricto)
- **NUNCA emitirá diagnósticos médicos:** No validará ni afirmará que un usuario "tiene dengue", "dengue con signos de alarma" o "dengue grave".
- **NUNCA prescribirá ni recomendará medicamentos:** Prohibición absoluta de sugerir fármacos, dosis, antibióticos, analgésicos o remedios caseros (incluyendo advertencia explícita contra aspirina, ibuprofeno y otros AINEs).
- **NUNCA reemplazará la consulta clínica presencial:** No sustituye el criterio médico profesional ni exámenes de laboratorio (hematocrito, recuento plaquetario).
- **NUNCA calculará riesgos mediante el LLM en texto libre:** La evaluación de signos de alarma se ejecuta en código determinista con reglas booleanas rígidas, jamás en el razonamiento probabilístico del modelo de lenguaje.

---

## 4. Riesgos Éticos y de Seguridad del Paciente

| Riesgo Identificado | Severidad | Mitigación Técnica y Operativa |
| :--- | :--- | :--- |
| **Falsa tranquilidad por alucinación del LLM** (el modelo descarta un síntoma grave). | **Crítica** | Cero inferencia diagnóstica en LLM. Checklist de signos de alarma ejecutado en Python determinista. Todo síntoma de peligro deriva de inmediato a urgencias. |
| **Automedicación facilitada** (usuario pregunta qué tomar para el dolor o fiebre). | **Crítica** | Bloqueo determinista vía expresiones y guardrails en backend; respuesta estándar indicando abstenerse de AINEs y acudir a consulta profesional. |
| **Retraso en la atención de emergencia** | **Alta** | Interfaz con botón persistente de emergencia "Llamar al 911" y aviso visible constante de acudir al centro de salud ante vómitos, dolor abdominal o sangrado. |
| **Filtración de Datos Personales de Salud (PII)** | **Alta** | El asistente opera en modalidad completamente anónima. No almacena nombres, números de cédula, direcciones exactas ni teléfonos en base de datos. |
| **Alucinación de fuentes inexistentes** | **Media** | Restricción RAG con prompt de rechazo estricto: si la respuesta no se encuentra en los fragmentos de ChromaDB, el sistema declara explícitamente desconocer la información y orienta a canales oficiales del MSP. |

---

## 5. Selección y Justificación del Modelo Generativo

Para el componente generativo de RAG se selecciona: **Google Gemini (Gemini 1.5 Flash / Groq Llama-3-70b como respaldo)**.

### Criterios de Selección:
1. **Alineación con directivas y fidelidad a contexto (Grounding):** Alta precisión en seguir instrucciones de sistema restrictivas ("system instructions"), respetando la prohibición estricta de salirse del contexto suministrado y citando metadatos.
2. **Latencia y Eficiencia (Time-to-First-Token):** Gemini Flash ofrece tiempos de respuesta inferiores a 1.2 segundos para generación de síntesis, indispensable para usuarios en conexiones móviles 3G/4G en regiones costeras y amazónicas.
3. **Compatibilidad nativa con Tool Calling / Function Calling:** Permite invocar las herramientas deterministas de Python (`evaluar_signos_alarma`, `ubicar_establecimiento`) bajo esquemas JSON estructurados y validados por Pydantic.
4. **Costo y Viabilidad en Sector Público:** Nivel de uso gratuito o de muy bajo costo por token, garantizando viabilidad técnica y presupuestaria para despliegues de salud comunitaria.
