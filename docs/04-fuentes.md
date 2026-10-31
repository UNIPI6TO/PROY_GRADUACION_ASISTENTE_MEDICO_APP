# 04. Inventario de Fuentes de la Base de Conocimiento, Catálogo GeoSalud y Estrategia de Fragmentación (Chunking)

---

## 1. Inventario de la Base de Conocimiento Oficial

La base de conocimiento del asistente se alimenta de manera estricta y exclusiva de publicaciones normativas, epidemiológicas y clínicas aprobadas por las autoridades oficiales de salud pública: la **Organización Panamericana de la Salud / Organización Mundial de la Salud (OPS/OMS)** y el **Ministerio de Salud Pública del Ecuador (MSP)**.

Se han incorporado fuentes canónicas de referencia y sus actualizaciones emitidas en los últimos 4 a 5 años:

| ID | Documento Oficial | Origen Institucional | URL Oficial / Permalink de Verificación | Fecha Publicación / Vigencia | Formato Original | Estado / Destino Local |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DOC-01** | *Dengue: Guías para la atención de enfermos en la Región de las Américas (2.ª ed.)* | Organización Panamericana de la Salud (OPS/OMS) | [iris.paho.org/handle/10665.2/31207](https://iris.paho.org/handle/10665.2/31207) *(Respaldo: [handle/10665.2/28232](https://iris.paho.org/server/api/core/bitstreams/73bbb097-bcdd-41c2-ad5d-444cd71a387a/content))* | 2016 (Marco canónico regional) | PDF Digital (114 págs.) | Insumo Base (`data/raw/ops_guia_dengue_2016.pdf`) |
| **DOC-02** | *Sistema Integrado de Vigilancia Epidemiologica* | Ministerio de Salud Publica | [Guias-atencion-enfermos-Americas-2010-dengue.pdf](https://www.salud.gob.ec/manuales/) *(Respaldo: [www.salud.gob.ec/manuales/](https://aplicaciones.msp.gob.ec/salud/archivosdigitales/documentosDirecciones/dnn/archivos/manual_de_procedimientos_sive-alerta.pdf?utm_source=chatgpt.com))*  | 2013 | PDF Digital (235 págs.) | Insumo Base (`data/raw/manual_de_procedimientos_sive-alerta.pdf`) |
| **DOC-03** | *Catálogo Nacional de Establecimientos de Salud (GeoSalud / RUES)* | MSP / Dirección Nacional de Vigilancia Epidemiológica | [geosalud.msp.gob.ec/geovisualizador](https://geosalud.msp.gob.ec/geovisualizador/) *(Datos Abiertos: [datosabiertos.gob.ec/dataset](https://www.datosabiertos.gob.ec/dataset/?organization=ministerio-de-salud-publica))* | 2024 – 2026 | CSV / JSON Estructurado | Base Georreferenciada (`data/geosalud_ecuador.json`) |
| **DOC-04** | *Estudio de Validación Ciudadana y Banco de Preguntas en Escala Likert sobre Dengue* | Levantamiento empírico de campo UNIANDES | [Formulario Google Forms](https://docs.google.com/forms/d/e/1FAIpQLScFV0KYkgELnUVlBiKz0pveYl05AgWShOHoK-BO9g9k7JP-sQ/viewform) | 2026 | PDF / Excel / TXT Estructurado | Insumos Empíricos (`data/raw/ANALISIS DE PREGUNTAS.pdf`, `RESPUESTAS.xlsx`, `preguntas`) |

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

### 4.2 Estrategia Implementada: Fragmentación Semántica Jerárquica Guiada por Encabezados y Delimitación Normativa

Para preservar la integridad clínica, el pipeline de ingesta (`scripts/ingest.py`) implementa una estrategia basada en la estructura jerárquica del documento con delimitación estricta y limpieza de ruido:

#### A. Delimitación y Limpieza del Manual SIVE-Alerta (MSP Ecuador, Págs. 95–100)
* **Delimitación exacta por regex:** En la página 95 del PDF concluye el protocolo de *Enfermedad de Chagas* y en la página 100 inicia *Fiebre Amarilla*. El script acota la extracción exactamente entre el encabezado `8.2.3.2 DENGUE` y `8.2.3.3 FIEBRE AMARILLA`.
* **Eliminación de artefactos:** Se depura mediante expresiones regulares la marca de agua transversal `"Documento final"` presente en cada página, junto con pies de página y numeraciones flotantes.
* **Resultado:** 12 fragmentos semánticos que cubren: casos sospechosos con/sin alarma y grave, criterios de confirmación por laboratorio (NS1, RT-PCR, IgM), descarte, flujo de notificación inmediata en 24h y medidas de control vectorial.

#### B. Extracción y Filtrado Clínico de la Guía OPS/OMS 2016
* **Preliminares de impacto comunitario:** Se extrae la página 2 (medidas intradomiciliarias: *"¡Sin mosquitos no hay dengue!"*) y páginas 16–17 (tabla de abreviaturas clínicas). Se descartan dedicatorias e índices generales.
* **Núcleo Clínico (Capítulos 1 al 8):** Segmentación por capítulos numerados (`1.1`, `2.3`, `3.2`), cuadros clínicos (`Cuadro 1: Curso de la enfermedad`, `Cuadro 3: Signos de alarma`, `Cuadro 6: Categorías de intervención`) y categorías de manejo (A, B1, B2, C).
* **Anexos Clínicos (D al U):** Conservación de tablas de hematocrito, líquidos de mantenimiento (Holliday-Segar), tablas de goteo y hoja de monitoreo.
* **Exclusión intencional del Capítulo 9 (Referencias bibliográficas / PubMed):** Páginas 107 a 127 excluidas para evitar contaminación vectorial (impedir que búsquedas por "shock" o "embarazo" recuperen cadenas de búsqueda en inglés o nombres de autores en vez del protocolo asistencial).

#### C. Inyección de Contexto en Sub-fragmentos
Cuando una sección clínica supera los 1.600 caracteres, se subdivide por párrafos conservando siempre en el encabezado del fragmento el contexto padre:
```text
[OPS 2016 · 3.4 Categoría de intervención B2: Pacientes con signos de alarma] (Parte 2/3)
Contenido de la administración de solución salina isotónica...
```

#### D. Métricas Finales de la Base de Conocimiento Indexada
* **Total de fragmentos en ChromaDB:** **161 fragmentos** (149 de OPS 2016 + 12 de SIVE-Alerta).
* **Formato de persistencia de respaldo:** Exportados de forma transparente a [`data/processed/fragmentos.md`](../data/processed/fragmentos.md) y [`data/processed/fragmentos.json`](../data/processed/fragmentos.json).
* **Modelo de embeddings:** `intfloat/multilingual-e5-small` (384 dimensiones) con prefijo obligatorio `"passage: "`.
* **Colección en ChromaDB:** `guia_vital_dengue` con espacio métrico `cosine`.
