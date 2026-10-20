# 04. Inventario de Fuentes de la Base de Conocimiento, Catálogo GeoSalud y Estrategia de Fragmentación (Chunking)

---

## 1. Inventario de la Base de Conocimiento Oficial

La base de conocimiento del asistente se alimenta de manera estricta y exclusiva de publicaciones normativas, epidemiológicas y clínicas aprobadas por las autoridades oficiales de salud pública: la **Organización Panamericana de la Salud / Organización Mundial de la Salud (OPS/OMS)** y el **Ministerio de Salud Pública del Ecuador (MSP)**.

Se han incorporado fuentes canónicas de referencia y sus actualizaciones emitidas en los últimos 4 a 5 años:

| ID | Documento Oficial | Origen Institucional | URL Oficial / Permalink de Verificación | Fecha Publicación / Vigencia | Formato Original | Estado / Destino Local |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DOC-01** | *Dengue: Guías para el diagnóstico, tratamiento, prevención y control (Nueva ed.)* | Organización Mundial de la Salud (OMS / OPS) | [who.int/publications/i/item/9789241547871](https://www.who.int/publications/i/item/9789241547871) | 2009 (Referencia canónica regional y global) | PDF Digital (160 págs.) | Insumo Base (`data/raw/ops_guia_diagnostico_prevencion_2009_esp.pdf`) |
| **DOC-02** | *Dengue: Guías para la atención de enfermos en la Región de las Américas (2.ª ed.)* | Organización Panamericana de la Salud (OPS/OMS) | [iris.paho.org/handle/10665.2/31207](https://iris.paho.org/handle/10665.2/31207) *(Respaldo: [handle/10665.2/28232](https://iris.paho.org/handle/10665.2/28232))* | 2016 (Marco canónico regional) | PDF Digital (114 págs.) | Insumo Base (`data/raw/ops_guia_dengue_2016.pdf`) |
| **DOC-03** | *Directrices para el diagnóstico clínico y el tratamiento del dengue, el chikunguña y el zika* | Organización Panamericana de la Salud (OPS/OMS) | [iris.paho.org/handle/10665.2/55125](https://iris.paho.org/handle/10665.2/55125) *(Descarga: [Directrices OPS 2022 PDF](https://iris.paho.org/bitstream/handle/10665.2/55125/9789275324196_spa.pdf))* | 2022 (Actualización clínica y triaje) | PDF Digital (140 págs.) | Insumo Complementario (`data/raw/ops_directrices_arbovirosis_2022.pdf`) |
| **DOC-04** | *Plan de Contingencia Nacional frente a Época Lluviosa y Enfermedades Transmitidas por Vectores* | Subsecretaría de Vigilancia, Prevención y Control - MSP | [Plan de Contingencia MSP Oficial](https://www.salud.gob.ec/wp-content/uploads/2026/06/PLAN_DE_CONTINGENCIA_NACIONAL_FRENTE_A_LA_EPOCA_LLUVIOSA_Y_FENOMENO_DE_EL_NINO_2026-signed-1-signed.pdf) | 2024 – 2026 | PDF Oficial Gubernamental | Insumo Complementario (`data/raw/msp_plan_contingencia_2026.pdf`) |
| **DOC-05** | *Catálogo Nacional de Establecimientos de Salud (GeoSalud / RUES)* | MSP / Dirección Nacional de Vigilancia Epidemiológica | [geosalud.msp.gob.ec/geovisualizador](https://geosalud.msp.gob.ec/geovisualizador/) *(Datos Abiertos: [datosabiertos.gob.ec/dataset](https://www.datosabiertos.gob.ec/dataset/?organization=ministerio-de-salud-publica))* | 2024 – 2026 | CSV / JSON Estructurado | Base Georreferenciada (`data/geosalud_ecuador.json`) |
| **DOC-06** | *Estudio de Validación Ciudadana y Banco de Preguntas en Escala Likert sobre Dengue* | Levantamiento empírico de campo UNIANDES | [Formulario Google Forms](https://docs.google.com/forms/d/e/1FAIpQLScFV0KYkgELnUVlBiKz0pveYl05AgWShOHoK-BO9g9k7JP-sQ/viewform) | 2026 | PDF / Excel / TXT Estructurado | Insumos Empíricos (`data/raw/ANALISIS DE PREGUNTAS.pdf`, `RESPUESTAS.xlsx`, `preguntas`) |

---

## 2. Referencias Bibliográficas Oficiales (Norma APA 7.ª Edición)

1. **Ministerio de Salud Pública del Ecuador.** (2024). *Plan de contingencia nacional para la respuesta frente a la época lluviosa y enfermedades transmitidas por vectores*. Subsecretaría de Vigilancia, Prevención y Control de la Salud. https://www.salud.gob.ec
2. **Ministerio de Salud Pública del Ecuador.** (2024). *Registro Único de Establecimientos de Salud (GeoSalud - RUES)*. Dirección Nacional de Vigilancia Epidemiológica. Recuperado el 12 de octubre de 2026, de https://geosalud.msp.gob.ec/geovisualizador/
3. **Ministerio de Salud Pública del Ecuador.** (s. f.). *Guías de práctica clínica, lineamientos y material educativo sobre dengue y arbovirosis*. Recuperado el 12 de octubre de 2026, de https://www.salud.gob.ec
4. **Organización Panamericana de la Salud.** (2016). *Dengue: Guías para la atención de enfermos en la Región de las Américas* (2.ª ed.). OPS. https://iris.paho.org/handle/10665.2/31207
5. **Organización Panamericana de la Salud.** (2022). *Directrices para el diagnóstico clínico y el tratamiento del dengue, el chikunguña y el zika* (Ed. corregida). OPS. https://iris.paho.org/handle/10665.2/55125
6. **World Health Organization.** (2009). *Dengue: Guidelines for diagnosis, treatment, prevention and control* (New ed.). WHO. https://www.who.int/publications/i/item/9789241547871

---

## 3. Catálogo de Establecimientos de Salud de Referencia en Zonas Endémicas de Ecuador

El dengue en el Ecuador afecta prioritariamente a las provincias tropicales y subtropicales de la **Costa** y la **Amazonía** (bajo los 1.500 m.s.n.m.), donde existen condiciones de temperatura, humedad y presencia del vector *Aedes aegypti*.

Ante la presencia de sospecha de dengue con signos de alarma, comorbilidades (diabetes, hipertensión, nefropatías) o grupos vulnerables (niños menores de 5 años, gestantes y adultos mayores), el protocolo clínico exige valoración presencial por personal médico, especialistas (Medicina Interna, Infectología, Pediatría) y toma de laboratorio urgente (hematocrito y plaquetas).

A continuación se detalla la red pública de referencia según tipología de establecimiento:
* **Centro de Salud Tipo C (Primer Nivel de Atención Especializado):** Dispone de atención de emergencia médica 24/7, laboratorio clínico para biometría hemática de urgencia, farmacia y camas de observación y rehidratación rápida.
* **Hospital Básico / General (Segundo Nivel):** Cuenta con servicio de internación hospitalaria, especialistas de guardia (Medicina Interna, Pediatría), terapia de fluidos intravenosos continua y banco de sangre.
* **Hospital de Especialidades / Infectología (Tercer Nivel):** Manejo de dengue grave, choque por extravasación de plasma, hemorragias severas y Unidad de Cuidados Intensivos (UCI).

### Directorio Focalizado por Provincias Endémicas de Mayor Incidencia:

| Provincia | Cantón / Ciudad | Nombre del Establecimiento | Nivel / Tipo | Especialidades y Capacidad Resolutiva | Servicio de Emergencia |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Guayas** | Guayaquil | **Hospital de Infectología Dr. José Daniel Rodríguez Maridueña** | Tercer Nivel (Especializado) | Infectología, Terapia Intensiva, Medicina Tropical, Laboratorio Viral | 24 Horas |
| **Guayas** | Guayaquil | **Hospital General Monte Sinaí** | Segundo Nivel (General) | Medicina Interna, Pediatría, Gineco-Obstetricia, Cuidados Intermedios | 24 Horas |
| **Guayas** | Guayaquil | **Hospital del Niño Dr. Roberto Gilbert Elizalde** | Tercer Nivel (Pediátrico) | Infectología Pediátrica, Cuidados Intensivos Pediátricos (UCIP) | 24 Horas |
| **Guayas** | Guayaquil | **Centro de Salud Tipo C Bastión Popular** | Primer Nivel (Tipo C) | Triaje de urgencias, Hidratación oral/IV rápida, Laboratorio de plaquetas | 24 Horas |
| **Guayas** | Durán | **Hospital General Dr. Enrique Ortega Moreira** | Segundo Nivel (General) | Medicina Interna, Pediatría, Emergencias 24h, Laboratorio | 24 Horas |
| **Manabí** | Portoviejo | **Hospital General de Especialidades Portoviejo** | Tercer Nivel (Especialidades) | Medicina Interna, Infectología, UCI Adultos y Pediátrica | 24 Horas |
| **Manabí** | Manta | **Hospital General Dr. Rodríguez Zambrano** | Segundo Nivel (General) | Medicina Interna, Pediatría, Observación de Urgencias | 24 Horas |
| **Manabí** | Chone | **Hospital General Dr. Napoleón Dávila Córdova** | Segundo Nivel (General) | Cuidados Críticos, Medicina Interna, Laboratorio Clínico | 24 Horas |
| **Manabí** | Manta | **Centro de Salud Tipo C Manta** | Primer Nivel (Tipo C) | Emergencias, Rehidratación, Toma de muestras de urgencia | 24 Horas |
| **Esmeraldas** | Esmeraldas | **Hospital General Delfina Torres de Concha** | Segundo Nivel (General) | Medicina Interna, Pediatría, Cuidados Críticos, Banco de Sangre | 24 Horas |
| **Esmeraldas** | Quinindé | **Hospital Básico Padre Alberto Buffoni** | Segundo Nivel (Básico) | Medicina General, Pediatría básica, Estabilización de shock | 24 Horas |
| **Esmeraldas** | San Lorenzo | **Hospital Básico Divina Providencia** | Segundo Nivel (Básico) | Emergencias 24h, Triage para zonas fronterizas | 24 Horas |
| **Los Ríos** | Babahoyo | **Hospital General Martín Icaza** | Segundo Nivel (General) | Medicina Interna, Pediatría, Rehidratación supervisada | 24 Horas |
| **Los Ríos** | Quevedo | **Hospital General Sagrado Corazón de Jesús** | Segundo Nivel (General) | Medicina Interna, Pediatría, Laboratorio de hematocrito | 24 Horas |
| **El Oro** | Machala | **Hospital General Teófilo Dávila** | Segundo Nivel (General) | Infectología, Medicina Interna, Cuidados Intensivos (UCI) | 24 Horas |
| **El Oro** | Santa Rosa | **Hospital Básico Santa Teresita** | Segundo Nivel (Básico) | Atención médica de urgencia, Hidratación endovenosa | 24 Horas |
| **Santo Domingo** | Santo Domingo | **Hospital General Dr. Gustavo Domínguez Zambrano** | Segundo Nivel (General) | Medicina Interna, Cuidados Intensivos, Pediatría, Laboratorio | 24 Horas |
| **Santo Domingo** | Santo Domingo | **Centro de Salud Tipo C Los Rosales** | Primer Nivel (Tipo C) | Emergencias 24h, Observación corta estancia, Biometría | 24 Horas |
| **Sucumbíos** | Lago Agrio (Nueva Loja) | **Hospital General Marco Vinicio Iza** | Segundo Nivel (General) | Medicina Interna, Pediatría, Cuidados Intermedios amazónicos | 24 Horas |
| **Orellana** | Francisco de Orellana (Coca)| **Hospital General Francisco de Orellana** | Segundo Nivel (General) | Emergencias, Laboratorio clínico, Medicina Interna | 24 Horas |
| **Pastaza** | Puyo | **Hospital General Puyo** | Segundo Nivel (General) | Atención a comunidades amazónicas, Pediatría, Medicina Interna | 24 Horas |
| **Napo** | Tena | **Hospital General José María Velasco Ibarra** | Segundo Nivel (General) | Emergencias 24h, Medicina Interna, Hospitalización | 24 Horas |
| **Morona Santiago**| Macas | **Hospital General de Macas** | Segundo Nivel (General) | Medicina Interna, Pediatría, Traslado asistido de emergencia | 24 Horas |

> **Manejo Estructurado del Catálogo en el Sistema:**  
> Este catálogo se extrae del portal de GeoSalud y se compila en el archivo estructurado **`data/geosalud_ecuador.json`**.  
> La herramienta del agente `ubicar_establecimiento(ciudad)` consume directamente este JSON en forma determinista, garantizando que el usuario reciba datos verificados de contacto, nivel de atención y dirección física sin depender de generación probabilística.

---

## 4. Justificación Técnica de la Estrategia de Fragmentación (Chunking)

### 4.1 El Problema del Chunking Ingenuo en Guías Médicas
El fraccionamiento por longitud fija de caracteres o tokens (ej. cortes ciegos cada 500 caracteres) es **inaceptable en el dominio clínico**:
1. **Corte de listas de signos de alarma:** Si un fragmento se corta a la mitad de una enumeración de signos de peligro, el sistema puede omitir un síntoma crítico (ej. "sangrado de mucosas") en la recuperación, induciendo una falsa sensación de seguridad en el usuario.
2. **Pérdida de contexto condicional:** En medicina, las advertencias dependen del contexto previo (ej. *"En caso de dengue sin signos de alarma... sin embargo, si aparece vómito continuo..."*). Separar la condición del síntoma altera el significado clínico.
3. **Pérdida de trazabilidad jerárquica:** El fragmento pierde el capítulo o sección al que pertenece (ej. si corresponde a cuidados en el hogar o criterios de ingreso a UCI).

---

### 4.2 Estrategia Seleccionada: Fragmentación Semántica Jerárquica Guiada por Encabezados (Markdown-Aware Chunking)

Para preservar la integridad clínica, el pipeline de ingesta (`scripts/ingest.py`) implementará una estrategia basada en la estructura del documento:

#### A. Preprocesamiento Estructurado
* Conversión de los PDFs oficiales a texto estructurado en Markdown (`.md`), respetando rigurosamente títulos `#`, subtítulos `##`, `###` y listas de viñetas `-`.
* Las tablas clínicas (clasificación del dengue según gravedad: Dengue sin signos, Dengue con signos, Dengue grave) se convierten a tablas Markdown compactas para no dispersar filas entre fragmentos.

#### B. Separadores Jerárquicos
Se configuran divisores semánticos en orden de prioridad:
```python
separators = [
    "\n## ",     # Secciones principales (ej. "Signos de Alarma", "Fase Crítica")
    "\n### ",    # Subsecciones clínicas específicas
    "\n\n",      # Párrafos completos y tablas
    "\n",        # Saltos de línea en listas de verificación
    ". "         # Oraciones completas (último recurso)
]