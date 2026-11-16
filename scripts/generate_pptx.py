import pptx
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os

TEMPLATE_PATH = r'docs/Plantilla_Presentacion_Grado.pptx'
OUTPUT_PATH = r'docs/evidencias/semana-4/defensa/Presentacion_GuiaVital_Grupo5.pptx'
OUTPUT_PATH_ALT = r'docs/evidencias/semana-4/defensa/Presentación.pptx'
ASSETS_DIR = r'docs/evidencias/semana-4/defensa/assets'

IMG_FONDO_CONTENIDO = os.path.join(ASSETS_DIR, 'image4.png')
IMG_LOGO = os.path.join(ASSETS_DIR, 'image3.png')

# Colores de la paleta oficial
GOLD = RGBColor(0xFF, 0xC5, 0x01)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xE2, 0xE8, 0xF0)
MUTED_GRAY = RGBColor(0x94, 0xA3, 0xB8)
DARK_BLUE = RGBColor(0x0A, 0x20, 0x48)
CARD_BG = RGBColor(0x0D, 0x1B, 0x38)
CARD_BORDER = RGBColor(0x2A, 0x3E, 0x66)
TEAL = RGBColor(0x5E, 0xEA, 0xD4)
EMERALD = RGBColor(0x34, 0xD3, 0x99)
CRIMSON = RGBColor(0xFB, 0x71, 0x85)

prs = pptx.Presentation(TEMPLATE_PATH)
slide_w = prs.slide_width
slide_h = prs.slide_height

# -------------------------------------------------------------
# 1. ACTUALIZAR SLIDE 1 (PORTADA)
# -------------------------------------------------------------
slide0 = prs.slides[0]

# Shape 2: Título del tema
shape2 = slide0.shapes[2]
shape2.text_frame.clear()
p2 = shape2.text_frame.paragraphs[0]
p2.text = 'GUÍAVITAL: ASISTENTE DE ORIENTACIÓN EN SALUD PÚBLICA SOBRE DENGUE Y ARBOVIROSIS EN ECUADOR'
p2.font.name = 'Arial'
p2.font.size = Pt(20)
p2.font.bold = True
p2.font.color.rgb = GOLD

p2_sub = shape2.text_frame.add_paragraph()
p2_sub.text = 'Caso 05 · Proceso de Titulación Complexivo UNIANDES · v0.6.1'
p2_sub.font.name = 'Arial'
p2_sub.font.size = Pt(14)
p2_sub.font.color.rgb = LIGHT_GRAY

# Shape 6: Integrantes
shape6 = slide0.shapes[6]
shape6.text_frame.clear()
members = [
    'Luis Caguana (Tech Lead)',
    'Wilson Salinas (Builder)',
    'Rafael Minaya (QA / Seguridad)'
]
for i, m in enumerate(members):
    p = shape6.text_frame.paragraphs[0] if i == 0 else shape6.text_frame.add_paragraph()
    p.text = m
    p.font.name = 'Arial'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = GOLD

# Shape 7: Grupo N°
shape7 = slide0.shapes[7]
shape7.text_frame.clear()
p7 = shape7.text_frame.paragraphs[0]
p7.text = 'GRUPO N° 5'
p7.font.name = 'Arial'
p7.font.size = Pt(30)
p7.font.bold = True
p7.font.color.rgb = WHITE

# Barra inferior de accesos directos sobre franja blanca (alto contraste azul oscuro)
tb_cover_links = slide0.shapes.add_textbox(Emu(820000), Emu(6400000), Emu(7000000), Emu(380000))
tf_links = tb_cover_links.text_frame
tf_links.word_wrap = True
p_links = tf_links.paragraphs[0]
p_links.text = 'CLOUD RUN (v0.6.1):  App Frontend ↗  ·  /manage/health ↗  ·  API Docs ↗  ·  GitHub ↗'
p_links.font.name = 'Consolas'
p_links.font.size = Pt(10.5)
p_links.font.bold = True
p_links.font.color.rgb = RGBColor(0x07, 0x15, 0x2B)

# -------------------------------------------------------------
# HELPER: Configurar título en Slide
# -------------------------------------------------------------
def setup_slide_header(slide, eyebrow_text, title_text, is_new=False):
    if is_new:
        # Fondo oficial y Logo oficial
        slide.shapes.add_picture(IMG_FONDO_CONTENIDO, 0, 0, slide_w, slide_h)
        slide.shapes.add_picture(IMG_LOGO, 10523188, 6126113, 1527672, 547750)
        tb = slide.shapes.add_textbox(Emu(670558), Emu(600000), Emu(10500000), Emu(1100000))
    else:
        # Encontrar el shape de Título
        tb = None
        for s in slide.shapes:
            if s.name == 'Título 1' and s.has_text_frame:
                tb = s
                break
        if tb is None:
            tb = slide.shapes.add_textbox(Emu(670558), Emu(600000), Emu(10500000), Emu(1100000))

    tf = tb.text_frame
    tf.clear()
    tf.word_wrap = True

    # Eyebrow
    p_eye = tf.paragraphs[0]
    p_eye.text = eyebrow_text.upper()
    p_eye.font.name = 'Arial'
    p_eye.font.size = Pt(12)
    p_eye.font.bold = True
    p_eye.font.color.rgb = GOLD

    # H2 Title
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.name = 'Arial'
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = WHITE
    return tb

def add_card(slide, left, top, width, height, title, body_bullets, accent_color=GOLD):
    # Shape rectángulo
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    rect.fill.solid()
    rect.fill.fore_color.rgb = CARD_BG
    rect.line.color.rgb = CARD_BORDER
    rect.line.width = Pt(1)

    tf = rect.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.2)
    tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    tf.margin_bottom = Inches(0.2)
    tf.clear()

    if title:
        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.name = 'Arial'
        p_title.font.size = Pt(14)
        p_title.font.bold = True
        p_title.font.color.rgb = accent_color

    first = True if not title else False
    for bullet in body_bullets:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = f"• {bullet}"
        p.font.name = 'Arial'
        p.font.size = Pt(12)
        p.font.color.rgb = LIGHT_GRAY

# -------------------------------------------------------------
# SLIDE 2: 01 · Contexto Epidemiológico y Usuario
# -------------------------------------------------------------
slide1 = prs.slides[1]
setup_slide_header(slide1, "01 · Contexto Epidemiológico y Usuario", "¿Qué problema de salud pública resolvemos en Ecuador?")
add_card(slide1, Emu(800000), Emu(1900000), Emu(5100000), Emu(4200000), "3 BARRERAS CRÍTICAS IDENTIFICADAS", [
    "01 / Brotes Invernales y Saturación: Endemia crítica en Costa y Amazonía (Guayaquil, Manta, Machala). Saturación de salas de urgencia por consultas leves sin signos de alarma.",
    "02 / Peligro de Automedicación (AINEs): Uso letal de ibuprofeno, aspirina o diclofenaco que induce hemorragias en la fase crítica cuando la fiebre desciende.",
    "03 / Derivación Tardía en Grupos Vulnerables: Retraso en atención para gestantes, menores de 5 años y adultos mayores por falta de reconocimiento de señales de alarma."
], CRIMSON)

add_card(slide1, Emu(6100000), Emu(1900000), Emu(5100000), Emu(4200000), "MANDATO DE INGENIERÍA Y USUARIOS", [
    "Población Objetivo: Ciudadanos residentes en cantones de alta transmisibilidad vectorial y cuidadores de grupos prioritarios en Ecuador.",
    "Orientación Preventiva 24/7: Educación sobre eliminación de criaderos de mosquitos Aedes aegypti sin automedicación.",
    "Triaje Determinista Inmediato: Identificación estricta de las 6 señales de alarma basadas en la Guía de Práctica Clínica MSP.",
    "Derivación de Emergencia Segura: Protocolo asistido con confirmación humana (HITL) para enlace telefónico o WhatsApp de auxilio."
], TEAL)

# -------------------------------------------------------------
# SLIDE 3: 02 · Alcance y Objetivos de Ingeniería
# -------------------------------------------------------------
slide2 = prs.slides[2]
setup_slide_header(slide2, "02 · Alcance y Objetivos de Ingeniería", "Objetivo general del Caso 05 y ejecución en 4 fases")
add_card(slide2, Emu(800000), Emu(1900000), Emu(10400000), Emu(1300000), "OBJETIVO GENERAL DEL CASO 05", [
    "Construir un asistente y agente de orientación en salud pública sobre dengue y arbovirosis, fundamentado en guías oficiales MSP/OPS, con recuperación vectorial auditada, triaje determinista de signos de alarma, privacidad estricta LOPDP y despliegue continuo en la nube."
], GOLD)

add_card(slide2, Emu(800000), Emu(3400000), Emu(5100000), Emu(2700000), "FASES 1 Y 2 · RAG Y AGENTE CLÍNICO", [
    "Fase 1 (RAG Normativo): Ingesta reproducible de guías MSP/OPS, fragmentación semántica en 161 chunks, embeddings multilingual-e5-small y umbral coseno dist ≤ 0.155.",
    "Fase 2 (Agente Determinista): Herramientas deterministas en Python (triaje_signos_alarma con 0 falsos negativos, calculo_dosis_paracetamol por kg y centro_salud_cercano)."
], TEAL)

add_card(slide2, Emu(6100000), Emu(3400000), Emu(5100000), Emu(2700000), "FASES 3 Y 4 · FRONTEND Y NUBE", [
    "Fase 3 (Frontend Seguro y LOPDP): SPA en React 19 + TypeScript + Vite, máquina de 7 estados clínicos, confirmación HITL de emergencia y anonimización de teléfonos en BD.",
    "Fase 4 (Despliegue y Calidad CI/CD): Despliegue en Google Cloud Run bajo contenedores Docker, suite de 135 pruebas automatizadas y certificación con 16 casos smoke en vivo."
], EMERALD)

# -------------------------------------------------------------
# SLIDE 4: 03 · Demostración en Vivo
# -------------------------------------------------------------
slide3 = prs.slides[3]
setup_slide_header(slide3, "03 · Demostración en Vivo", "3 comportamientos verificables en Google Cloud Run")
add_card(slide3, Emu(800000), Emu(1900000), Emu(3300000), Emu(4200000), "CASO A · PREVENTIVO", [
    "Escenario: Usuario consulta cómo evitar mosquitos en tanques de agua en su domicilio.",
    "RAG Activado: Recupera fragmentos de control larvario físico y biológico MSP.",
    "Cita Normativa: Cita explícita de Guía Oficial MSP Ecuador.",
    "Resultado Clínico: Orientación clara sin generar derivación hospitalaria innecesaria."
], TEAL)

add_card(slide3, Emu(4350000), Emu(1900000), Emu(3300000), Emu(4200000), "CASO B · AUTOMEDICACIÓN", [
    "Escenario: Usuario con fiebre pide tomar ibuprofeno o aspirina.",
    "Bloqueo Categórico: Regla clínica inquebrantable que prohíbe AINEs por riesgo de hemorragia.",
    "Educación Farmacológica: Alerta del peligro de sangrado y recomendación de hidratación oral abundante.",
    "Resultado Clínico: Cálculo seguro de paracetamol según peso/edad si aplica."
], CRIMSON)

add_card(slide3, Emu(7900000), Emu(1900000), Emu(3300000), Emu(4200000), "CASO C · ALARMA Y HITL", [
    "Escenario: Usuario reporta dolor abdominal intenso continuo y vómitos persistentes.",
    "Triaje Determinista: Detección inmediata de Signos de Alarma Grado B2/C.",
    "Derivación Urgente: Indicación perentoria de traslado a centro Tipo C u hospital.",
    "Confirmación HITL: Solicitud interactiva al usuario antes de enviar alerta WhatsApp SOS."
], GOLD)

# -------------------------------------------------------------
# Función para crear diapositivas adicionales
# -------------------------------------------------------------
blank_layout = prs.slide_layouts[6]

# SLIDE 5: 04 · Diseño de Sistemas y Trazabilidad
slide4 = prs.slides.add_slide(blank_layout)
setup_slide_header(slide4, "04 · Diseño de Sistemas y Trazabilidad", "Arquitectura desacoplada en 4 capas de seguridad", is_new=True)
add_card(slide4, Emu(800000), Emu(1900000), Emu(5100000), Emu(2000000), "CAPA 1 · CLIENTE WEB (REACT 19 + TS)", [
    "Máquina determinista de 7 estados clínicos (reposo, evaluando, alarma, HITL).",
    "Consentimiento informado de privacidad LOPDP previo a la interacción.",
    "Interfaz responsiva con renderizado accesible y confirmación interactiva HITL."
], TEAL)

add_card(slide4, Emu(6100000), Emu(1900000), Emu(5100000), Emu(2000000), "CAPA 2 · GATEWAY Y API (FASTAPI)", [
    "Endpoints desacoplados v1 (RAG simple) y v2 (Agente con herramientas).",
    "Validación estricta de esquemas mediante Pydantic v2 y sanitización de entrada.",
    "Limitador de tasa (Rate Limiting) y middlewares de seguridad HTTPS."
], GOLD)

add_card(slide4, Emu(800000), Emu(4100000), Emu(5100000), Emu(2000000), "CAPA 3 · AGENTE Y HERRAMIENTAS", [
    "Loop autónomo controlado con tope estricto de 6 iteraciones (evita bucles infinitos).",
    "Llamadas deterministas a funciones Python de triaje y dosificación MSP.",
    "Resiliencia con conmutación automática de Gemini 3.8 Flash a Groq Llama-3.3."
], EMERALD)

add_card(slide4, Emu(6100000), Emu(4100000), Emu(5100000), Emu(2000000), "CAPA 4 · BASE VECTORIAL Y CORPUS", [
    "ChromaDB persistente con embeddings normativos multilingual-e5-small.",
    "161 chunks indexados a partir de guías oficiales MSP Ecuador y OPS/OMS.",
    "Filtro estricto por distancia coseno (dist ≤ 0.155) para evitar alucinaciones."
], TEAL)

# -------------------------------------------------------------
# SLIDE 6: 05 · Registro de Decisiones de Arquitectura (ADR)
# -------------------------------------------------------------
slide5 = prs.slides.add_slide(blank_layout)
setup_slide_header(slide5, "05 · Registro de Decisiones de Arquitectura (ADR)", "¿Por qué diseñamos así y qué alternativas descartamos?", is_new=True)

# Crear tabla de ADRs
rows = 6
cols = 4
top = Emu(1900000)
left = Emu(800000)
width = Emu(10400000)
height = Emu(4200000)

table_shape = slide5.shapes.add_table(rows, cols, left, top, width, height)
tbl = table_shape.table
tbl.columns[0].width = Emu(2200000)
tbl.columns[1].width = Emu(2800000)
tbl.columns[2].width = Emu(2800000)
tbl.columns[3].width = Emu(2600000)

headers = ["DECISIÓN (ADR)", "ARQUITECTURA ELEGIDA", "ALTERNATIVA DESCARTADA", "JUSTIFICACIÓN TÉCNICA"]
for col_idx, h in enumerate(headers):
    cell = tbl.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = DARK_BLUE
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.name = 'Arial'
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOLD

adrs = [
    ("ADR-01: Proveedor LLM", "Gemini 3.8 Flash + fallback Groq Llama-3.3", "LLM local (Ollama / Llama-cpp)", "Latencia sub-2s y 0 consumo excesivo de RAM en contenedor"),
    ("ADR-02: Base Vectorial", "ChromaDB + multilingual-e5-small", "FAISS en memoria efímera", "Persistencia robusta y soporte de metadatos de fuentes oficiales"),
    ("ADR-03: Triaje de Alarma", "Herramienta determinista en Python", "Dejar el triaje al prompt libre del LLM", "0% margen de error en detección de signos de riesgo vital"),
    ("ADR-04: Cliente Frontend", "React 19 + TypeScript + Vite", "Streamlit / Gradio", "Control estricto de máquina de estados, LOPDP y UX móvil"),
    ("ADR-05: Protocolo HITL", "Confirmación obligatoria previa a SOS", "Envío automático desatendido", "Evita pánico y falsas alarmas sin autorización del paciente")
]

for row_idx, data in enumerate(adrs, start=1):
    for col_idx, text in enumerate(data):
        cell = tbl.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG
        p = cell.text_frame.paragraphs[0]
        p.text = text
        p.font.name = 'Arial'
        p.font.size = Pt(10)
        p.font.color.rgb = WHITE if col_idx == 0 else LIGHT_GRAY

# -------------------------------------------------------------
# SLIDE 7: 06 · Evidencias Funcionales y Suite de Pruebas
# -------------------------------------------------------------
slide6 = prs.slides.add_slide(blank_layout)
setup_slide_header(slide6, "06 · Evidencias Funcionales y Suite de Pruebas", "135 pruebas automatizadas y 16 casos en vivo en Cloud Run", is_new=True)

# 4 Stat Cards
stats = [
    ("135 / 135", "Suite Total", "100% PRUEBAS PASANDO", EMERALD),
    ("92", "Backend Pytest", "RAG, AGENTE, API & TOOLS", TEAL),
    ("27", "Frontend Vitest", "COMPONENTES & ESTADOS", GOLD),
    ("16", "Smoke Tests Nube", "CASOS VIVOS CLOUD RUN", WHITE)
]
card_w = Emu(2450000)
card_h = Emu(1300000)
for idx, (val, lbl, sub, col) in enumerate(stats):
    pos_x = Emu(800000 + idx * 2650000)
    add_card(slide6, pos_x, Emu(1900000), card_w, card_h, "", [f"{val}\n{lbl} ({sub})"], col)

add_card(slide6, Emu(800000), Emu(3400000), Emu(5100000), Emu(2700000), "COBERTURA DE SEGURIDAD CLÍNICA", [
    "Pruebas de Triaje de Alarma: 18 casos unitarios verifican que ninguna combinación de dolor abdominal, sangrado o vómitos sea omitida (0 falsos negativos).",
    "Pruebas Anti-Automedicación: 12 casos verifican el bloqueo estricto de AINEs (ibuprofeno, aspirina, diclofenaco, naproxeno).",
    "Pruebas de Grupos Prioritarios: Verificación obligatoria de derivación para gestantes, neonatos y adultos mayores."
], CRIMSON)

add_card(slide6, Emu(6100000), Emu(3400000), Emu(5100000), Emu(2700000), "VERIFICACIÓN EN PRODUCCIÓN CLOUD RUN", [
    "16 Pruebas End-to-End Ejecutadas: El script smoke.py ejecuta 16 consultas contra el contenedor activo en Google Cloud Run.",
    "Latencia y Rendimiento: Respuestas del agente completadas en una media de 1.8 segundos.",
    "Health Checks Activos: Endpoint /manage/health reporta estado en verde para ChromaDB, modelo LLM y caché de memoria."
], EMERALD)

# -------------------------------------------------------------
# SLIDE 8: 07 · Métricas Clínicas y Despliegue Continuo
# -------------------------------------------------------------
slide7 = prs.slides.add_slide(blank_layout)
setup_slide_header(slide7, "07 · Métricas Clínicas y Despliegue Continuo", "Evaluación cuantitativa y pipeline CI/CD en verde", is_new=True)

add_card(slide7, Emu(800000), Emu(1900000), Emu(5100000), Emu(4200000), "MÉTRICAS CUANTITATIVAS DEL MODELO", [
    "86.7% Acierto RAG Top-3 (evaluar.py): 13 de 15 preguntas clínicas recuperaron los fragmentos exactos del MSP (Meta: ≥ 85%).",
    "100% Hit@5 y 90.0% Hit@1 (run_eval.py): 20 de 20 preguntas clínicas doradas en Top-5 (18/20 en Puesto #1).",
    "Distancia Coseno Media ≤ 0.155: Similitud semántica del 84.5% entre la consulta del usuario y el corpus normativo.",
    "100% Citas Oficiales y 100% Abstención: Referencia documental OPS/MSP en el 100% de respuestas y 5/5 silencio fuera de dominio.",
    "0 Errores Silenciosos: 100% sensibilidad en alarma y 30% de desvío seguro a revisión médica humana."
], TEAL)

add_card(slide7, Emu(6100000), Emu(1900000), Emu(5100000), Emu(4200000), "PIPELINE CI/CD Y GOBERNANZA CLOUD RUN (v0.6.1)", [
    "Integración Continua (CI): GitHub Actions ejecuta automáticamente gitleaks, pytest (92 tests), vitest (27 tests) y evaluar.py.",
    "Release Simétrico (release.yml): Bump automático a v0.6.1, actualización de changelogs y publicación de tag en Git.",
    "Despliegue Continuo (CD): Despliegue automático a Google Cloud Run (2 vCPU, 2 GiB) con GeoSalud y enlaces a Google Maps.",
    "Certificación en Producción: 16 pruebas de humo (smoke.py) ejecutadas en vivo contra el Agente v2."
], GOLD)

# -------------------------------------------------------------
# SLIDE 9: 08 · Seguridad Operativa y Tolerancia a Fallos
# -------------------------------------------------------------
slide8 = prs.slides.add_slide(blank_layout)
setup_slide_header(slide8, "08 · Seguridad Operativa y Tolerancia a Fallos", "¿Dónde viven las claves y qué pasa cuando la IA falla?", is_new=True)

add_card(slide8, Emu(800000), Emu(1900000), Emu(3300000), Emu(4200000), "0 CLAVES EN CÓDIGO NI GIT", [
    "Gestión de Secretos: Ninguna API Key reside en el repositorio git ni en imágenes Docker.",
    "Variables de Entorno: Inyección segura mediante variables de entorno y Secret Manager en Cloud Run.",
    "Escaneo Pre-Commit: Auditoría automatizada con detect-secrets para evitar filtraciones accidentales."
], TEAL)

add_card(slide8, Emu(4350000), Emu(1900000), Emu(3300000), Emu(4200000), "RESILIENCIA MULTIPROVEEDOR", [
    "Fallback Automático: Si Gemini 3.8 Flash agota cuota (429) o sufre degradación (503), el sistema conmuta a Groq (Llama-3.3-70b).",
    "Transparencia al Usuario: La conmutación ocurre en menos de 400ms sin interrumpir la sesión del ciudadano.",
    "Circuit Breaker: Detección rápida de fallos en proveedores externos para evitar cuelgues del servidor."
], GOLD)

add_card(slide8, Emu(7900000), Emu(1900000), Emu(3300000), Emu(4200000), "MODO SEGURO Y PRIVACIDAD", [
    "Fallback Determinista: Si ambos proveedores LLM colapsan, se activa un modo seguro que entrega la guía directa del RAG.",
    "Anonimización LOPDP: Los números telefónicos para alertas SOS son enmascarados irreversiblemente (ej. 099***67) en la BD.",
    "Defensa OWASP LLM: Filtros anti prompt-injection y bloqueo de temas no relacionados con salud pública."
], EMERALD)

# -------------------------------------------------------------
# SLIDE 10: 09 · Transparencia Técnica y Equipo
# -------------------------------------------------------------
slide9 = prs.slides.add_slide(blank_layout)
setup_slide_header(slide9, "09 · Transparencia Técnica y Equipo", "Fronteras del sistema, auditoría de IA y roles verificados", is_new=True)

add_card(slide9, Emu(800000), Emu(1900000), Emu(5100000), Emu(4200000), "LIMITACIONES Y FRONTERAS DEL SISTEMA", [
    "01 / No es Diagnóstico Médico: GuíaVital no reemplaza la consulta profesional ni prescribe tratamientos farmacológicos.",
    "02 / Triaje Basado en Guías: Opera bajo un árbol de decisión determinista alineado a la clasificación clínica del MSP (Grupos A, B1, B2, C).",
    "03 / Ámbito Geográfico: Calibrado para la epidemiología de arbovirosis en Ecuador y centros de salud del MSP.",
    "04 / Exclusión de Farmacoterapia Compleja: Prohíbe sugerir corticoides, antibióticos o AINEs."
], CRIMSON)

add_card(slide9, Emu(6100000), Emu(1900000), Emu(5100000), Emu(4200000), "ROLES Y RESPONSABILIDADES DEL EQUIPO", [
    "Luis Caguana (Tech Lead): Arquitectura de software, pipeline RAG, herramientas deterministas Python, ingeniería de prompts y evaluador CI.",
    "Wilson Salinas (Builder): Desarrollo frontend en React 19 + TypeScript, máquina de 7 estados clínicos, contenedor Docker y CI/CD en Google Cloud Run.",
    "Rafael Minaya (QA / Seguridad): Estrategia de calidad integral, suite de 135 pruebas automatizadas, auditoría OWASP Top 10 for LLM y cumplimiento LOPDP."
], GOLD)

# -------------------------------------------------------------
# SLIDE 11: 10 · Conclusiones y Cierre de Sustentación
# -------------------------------------------------------------
slide10 = prs.slides.add_slide(blank_layout)
setup_slide_header(slide10, "10 · Conclusiones y Cierre de Sustentación", "100% de objetivos e indicadores clínicos cumplidos", is_new=True)

# Tabla de Cumplimiento de Indicadores
tbl_shape = slide10.shapes.add_table(6, 4, Emu(800000), Emu(1900000), Emu(10400000), Emu(4200000))
t = tbl_shape.table
t.columns[0].width = Emu(3000000)
t.columns[1].width = Emu(2000000)
t.columns[2].width = Emu(2600000)
t.columns[3].width = Emu(2800000)

indicadores_headers = ["INDICADOR EXIGIDO (CASO 05)", "META", "RESULTADO LOGRADO", "EVIDENCIA TÉCNICA"]
for col_idx, h in enumerate(indicadores_headers):
    c = t.cell(0, col_idx)
    c.fill.solid()
    c.fill.fore_color.rgb = DARK_BLUE
    p = c.text_frame.paragraphs[0]
    p.text = h
    p.font.name = 'Arial'
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOLD

matriz = [
    ("1. Corpus Normativo Oficial MSP", "100% fuentes oficiales", "100% OPS / MSP Ecuador", "161 chunks indexados en ChromaDB"),
    ("2. Precisión RAG (Top-3 / Hit@5)", "≥ 85% acierto semántico", "86.7% Top-3 · 100% Hit@5 (20/20)", "Evaluación en eval/evaluar.py y run_eval.py"),
    ("3. Triaje Determinista de Alarma", "0 falsos negativos", "0 omisiones críticas (100%)", "18 pruebas unitarias en test_tools.py"),
    ("4. Bloqueo de Automedicación AINEs", "100% prohibición", "0 prescripciones erróneas", "Regla inquebrantable en prompt y código"),
    ("5. Despliegue en Producción", "Nube pública verificable", "Google Cloud Run activo (v0.6.1)", "16 smoke tests aprobados en vivo")
]

for row_idx, row in enumerate(matriz, start=1):
    for col_idx, val in enumerate(row):
        c = t.cell(row_idx, col_idx)
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_BG
        p = c.text_frame.paragraphs[0]
        p.text = val
        p.font.name = 'Arial'
        p.font.size = Pt(10)
        p.font.color.rgb = WHITE if col_idx == 0 else (EMERALD if col_idx == 2 else LIGHT_GRAY)

# -------------------------------------------------------------
# SLIDE 12: 11 · Cierre y Ronda de Preguntas del Tribunal
# -------------------------------------------------------------
slide11 = prs.slides.add_slide(blank_layout)
setup_slide_header(slide11, "11 · Cierre y Ronda de Preguntas del Tribunal", "Muchas gracias por su atención", is_new=True)

add_card(slide11, Emu(800000), Emu(1900000), Emu(10400000), Emu(1200000), "SUSTENTACIÓN Y DEFENSA COMPLEXIVA · CASO 05", [
    "El equipo de desarrollo queda a entera disposición del Honorable Tribunal de Grado para responder preguntas técnicas y clínicas o realizar demostraciones en vivo sobre el entorno activo en Google Cloud Run."
], GOLD)

# 4 Stat Cards resumen
c_w = Emu(2450000)
c_h = Emu(1300000)
resumen_stats = [
    ("135 / 135", "Pruebas Pasando", "100% EXITOSO", EMERALD),
    ("≤ 0.155", "Distancia Coseno RAG", "CORPUS OFICIAL MSP", TEAL),
    ("0 Errores", "Triaje Determinista", "0 FALSOS NEGATIVOS", GOLD),
    ("LOPDP", "Privacidad y HITL", "ART. 10 Y 11 CUMPLIDOS", WHITE)
]
for idx, (val, lbl, sub, col) in enumerate(resumen_stats):
    pos_x = Emu(800000 + idx * 2650000)
    add_card(slide11, pos_x, Emu(3300000), c_w, c_h, "", [f"{val}\n{lbl} ({sub})"], col)

add_card(slide11, Emu(800000), Emu(4800000), Emu(10400000), Emu(1300000), "ENLACES Y ACCESOS EN VIVO", [
    "Frontend en Cloud Run: https://guiavital-448060764458.us-central1.run.app  |  Health Check: /manage/health",
    "Repositorio de Código: https://github.com/UNIPI6TO/PROY_GRADUACION_ASISTENTE_MEDICO_APP",
    "Equipo Grupo 5: Luis Caguana (Tech Lead) · Wilson Salinas (Builder) · Rafael Minaya (QA / Seguridad)"
], TEAL)

# Guardar la presentación completa
prs.save(OUTPUT_PATH)
prs.save(OUTPUT_PATH_ALT)
print(f"Presentation successfully created with {len(prs.slides)} slides at: {OUTPUT_PATH} and {OUTPUT_PATH_ALT}")
