import re

HTML_PATH = r'docs/evidencias/semana-4/Presentación PowerPoint.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# ---------------------------------------------------------------------------
# 1. ACTUALIZAR ESTILOS CSS EN <style>
# ---------------------------------------------------------------------------
# Nueva paleta en :root y estilos adaptados a la plantilla PPTX
new_css = """
:root {
  --bg-stage: #050b14;
  --bg-slide: #0a2048;
  --surface: rgba(13, 27, 56, 0.88);
  --surface-alt: rgba(19, 38, 77, 0.92);
  --ink: #ffffff;
  --ink-secondary: #e2e8f0;
  --ink-muted: #94a3b8;
  --line: rgba(255, 255, 255, 0.12);
  --line-strong: rgba(255, 255, 255, 0.22);
  --accent: #FFC501;
  --accent-gold: #FFC501;
  --accent-dark: #d9a300;
  --accent-soft: rgba(255, 197, 1, 0.14);
  --navy: #07152b;
  --crimson: #fb7185;
  --crimson-soft: rgba(244, 63, 94, 0.16);
  --emerald: #34d399;
  --emerald-soft: rgba(16, 185, 129, 0.16);
  --teal: #5eead4;
  --font-display: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Consolas, monospace;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: var(--font-sans);
  background: var(--bg-stage);
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.deck {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.slide {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  width: min(1280px, 96vw);
  height: 720px;
  min-height: 720px;
  max-height: 720px;
  background-color: var(--bg-slide);
  background-image: url("assets/fondo_contenido.png");
  background-size: 100% 100%;
  background-position: center;
  background-repeat: no-repeat;
  border-radius: 4px;
  padding: 28px 48px 18px;
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.75);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--ink);
}

.slide.active {
  display: flex;
  flex-direction: column;
}

/* PORTADA OFICIAL DE LA PLANTILLA PPTX */
.slide.cover {
  background-color: #07152b;
  background-image: url("assets/fondo_portada.png");
  background-size: 100% 100%;
  background-position: center;
  background-repeat: no-repeat;
  color: #f8fafc;
  justify-content: space-between;
  padding: 32px 50px 20px;
}

.cover-layout {
  display: grid;
  grid-template-columns: 1fr 1.15fr;
  gap: 40px;
  height: calc(100% - 48px);
  align-items: center;
  padding: 8px 16px;
}

.cover-left {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  padding-bottom: 8px;
}

.cover-logo-main {
  width: 320px;
  max-width: 100%;
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.6));
}

.cover-block {
  margin: 12px 0;
}

.cover-label {
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.cover-label-lg {
  font-family: var(--font-sans);
  font-size: 32px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 1.5px;
  margin-bottom: 12px;
}

.cover-team {
  font-size: 17px;
  font-weight: 700;
  color: var(--accent);
  line-height: 1.6;
}

.cover-team .role {
  font-size: 13.5px;
  color: #cbd5e1;
  font-weight: 500;
}

.cover-group {
  font-size: 32px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 1px;
}

.cover-right {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-left: 24px;
  border-left: 1px solid rgba(255, 255, 255, 0.15);
}

.cover-topic {
  font-size: 24px;
  font-weight: 800;
  color: var(--accent);
  line-height: 1.35;
  margin-bottom: 12px;
  letter-spacing: -0.01em;
}

.cover-subtopic {
  font-size: 15px;
  font-weight: 600;
  color: #cbd5e1;
  margin-bottom: 22px;
  letter-spacing: 0.5px;
}

.cover-meta-badges {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.cover-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  padding-top: 10px;
  padding-right: 140px;
  font-family: var(--font-mono);
  font-size: 12.5px;
  color: var(--ink-muted);
}

.cover-links a {
  color: var(--teal);
  text-decoration: none;
  transition: color 0.2s;
}

.cover-links a:hover {
  text-decoration: underline;
  color: #ffffff;
}

/* LOGO INSTITUCIONAL DE ESQUINA INFERIOR DERECHA */
.slide-logo {
  position: absolute;
  bottom: 12px;
  right: 28px;
  height: 38px;
  width: auto;
  object-fit: contain;
  z-index: 10;
  pointer-events: none;
  filter: drop-shadow(0 2px 5px rgba(0,0,0,0.6));
}

/* CABECERA EDITORIAL DE DIAPOSITIVA */
.slide-head {
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  padding-bottom: 8px;
  margin-bottom: 14px;
  flex-shrink: 0;
}

.eyebrow {
  font-family: var(--font-mono);
  color: var(--accent);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1.6px;
  text-transform: uppercase;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.eyebrow::before {
  content: "";
  display: inline-block;
  width: 18px;
  height: 2px;
  background: var(--accent);
}

h1 {
  font-family: var(--font-display);
  font-size: 74px;
  line-height: 0.98;
  margin: 0 0 14px;
  color: #ffffff;
  font-weight: 800;
  letter-spacing: -0.04em;
}

h2 {
  font-family: var(--font-display);
  color: #ffffff;
  font-size: 24px;
  line-height: 1.15;
  margin: 0;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.cover h2 {
  font-family: var(--font-sans);
  color: #94a3b8;
  font-size: 24px;
  font-weight: 400;
  max-width: 820px;
  line-height: 1.4;
  letter-spacing: -0.01em;
}

p {
  font-size: 15.5px;
  line-height: 1.5;
  margin: 0 0 8px;
  color: var(--ink-secondary);
}

a {
  color: var(--teal);
  font-weight: 600;
  text-decoration: none;
  border-bottom: 1px solid rgba(94, 234, 212, 0.4);
  transition: color 0.15s ease, border-color 0.15s ease;
}

a:hover {
  color: #ffffff;
  border-bottom-color: #ffffff;
}

code {
  font-family: var(--font-mono);
  background: var(--surface-alt);
  color: var(--teal);
  padding: 2px 6px;
  border-radius: 2px;
  font-size: 13.5px;
  font-weight: 600;
  border: 1px solid var(--line);
}

/* ETIQUETAS TÉCNICAS */
.tag {
  font-family: var(--font-mono);
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 2px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.4px;
  text-transform: uppercase;
  white-space: nowrap;
}
.tag-teal { background: rgba(94, 234, 212, 0.15); color: #5eead4; border: 1px solid rgba(94, 234, 212, 0.4); }
.tag-dark { background: rgba(7, 21, 43, 0.9); color: #f8fafc; border: 1px solid rgba(255, 255, 255, 0.15); }
.tag-crimson { background: var(--crimson-soft); color: var(--crimson); border: 1px solid rgba(251, 113, 133, 0.4); }
.tag-emerald { background: var(--emerald-soft); color: var(--emerald); border: 1px solid rgba(52, 211, 153, 0.4); }
.tag-outline { background: rgba(255, 255, 255, 0.04); color: #cbd5e1; border: 1px solid rgba(255, 255, 255, 0.2); }

/* ÍNDICE NUMÉRICO */
.idx {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.5px;
}
.idx-crimson { color: var(--crimson); }
.idx-navy { color: var(--ink-muted); }

/* GRIDS ARQUITECTÓNICOS */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

/* PANELES MINIMALISTAS */
.panel {
  background: var(--surface);
  backdrop-filter: blur(8px);
  border: 1px solid var(--line);
  border-top: 2px solid var(--accent);
  border-radius: 2px;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  color: var(--ink-secondary);
}

.panel-teal { border-top-color: var(--teal); }
.panel-crimson { border-top-color: var(--crimson); }
.panel-emerald { border-top-color: var(--emerald); }
.panel-subtle { border-top: 1px solid var(--line); background: var(--surface); }

.panel-dark {
  background: rgba(7, 18, 40, 0.92);
  backdrop-filter: blur(8px);
  color: #f8fafc;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-top: 2px solid var(--accent);
  border-radius: 2px;
  padding: 16px 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  min-height: 26px;
}

.panel-title {
  font-family: var(--font-display);
  font-size: 17.5px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.02em;
  line-height: 1.2;
  white-space: nowrap;
}

.panel-dark .panel-title {
  color: #ffffff;
}

.panel-body {
  font-size: 15px;
  line-height: 1.45;
  color: var(--ink-secondary);
  flex: 1;
}

.panel-body strong {
  color: #ffffff;
}

.panel-dark .panel-body {
  color: #cbd5e1;
}

.panel-foot {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid var(--line);
  font-family: var(--font-mono);
  font-size: 12.5px;
  color: var(--ink-muted);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* MÉTRICAS */
.stat-cell {
  background: var(--surface);
  backdrop-filter: blur(8px);
  border: 1px solid var(--line);
  border-top: 2px solid var(--accent);
  border-radius: 2px;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-val {
  font-family: var(--font-display);
  font-size: 38px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.0;
  letter-spacing: -0.04em;
}

.stat-lbl {
  font-size: 15px;
  font-weight: 700;
  color: #f1f5f9;
  margin-top: 6px;
  letter-spacing: -0.01em;
}

.stat-sub {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--ink-muted);
  margin-top: 3px;
}

/* FRANJA DE ESTADO */
.status-bar {
  background: var(--surface);
  backdrop-filter: blur(8px);
  border: 1px solid var(--line);
  border-left: 3px solid var(--emerald);
  border-radius: 2px;
  padding: 10px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  font-size: 15px;
  color: var(--ink-secondary);
}

.status-bar strong {
  color: #ffffff;
}

/* LISTA NUMERADA */
.row-list {
  display: flex;
  flex-direction: column;
  border-top: 1px solid var(--line);
}

.row-item {
  display: grid;
  grid-template-columns: 32px 1fr;
  align-items: baseline;
  padding: 8px 0;
  border-bottom: 1px solid var(--line);
  font-size: 15px;
  line-height: 1.38;
  color: var(--ink-secondary);
}

.row-item strong {
  color: #ffffff;
}

/* TABLA EDITORIAL LIMPIA */
table.swiss-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--surface);
  border-top: 2px solid var(--accent);
  border-bottom: 1px solid var(--line-strong);
  font-size: 15px;
}

table.swiss-table th {
  font-family: var(--font-mono);
  background: var(--surface-alt);
  color: #ffffff;
  padding: 10px 14px;
  font-weight: 700;
  text-align: left;
  font-size: 12.5px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  border-bottom: 1px solid var(--line-strong);
}

table.swiss-table td {
  padding: 11px 14px;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
  line-height: 1.4;
  color: var(--ink-secondary);
}

table.swiss-table td strong {
  color: #ffffff;
}

/* PIE DE PÁGINA */
.footer {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--ink-muted);
  font-family: var(--font-mono);
  font-size: 12px;
  border-top: 1px solid var(--line);
  padding-top: 8px;
  padding-right: 140px;
  flex-shrink: 0;
}

/* BARRA DE NAVEGACIÓN */
.nav {
  position: fixed;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(7, 21, 43, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 6px 14px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  z-index: 1000;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
}

.nav button {
  background: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.15);
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border-radius: 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.nav button:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: #07152b;
}

.nav button.btn-pptx {
  background: rgba(255, 197, 1, 0.18);
  color: var(--accent);
  border-color: var(--accent);
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  padding: 0 12px;
  gap: 4px;
}

.nav button.btn-pptx:hover {
  background: var(--accent);
  color: #07152b;
}

.nav span {
  font-family: var(--font-mono);
  font-size: 12.5px;
  font-weight: 600;
  min-width: 58px;
  text-align: center;
  color: #94a3b8;
}

.progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: var(--accent);
  z-index: 200;
  transition: width 0.2s ease;
}

/* IMPRESIÓN Y EXPORTACIÓN PDF 16:9 */
@page {
  size: 338.67mm 190.5mm;
  margin: 0;
}

@media print {
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  html, body {
    margin: 0 !important;
    padding: 0 !important;
    background: var(--bg-slide) !important;
    width: 338.67mm !important;
  }

  .deck {
    display: block !important;
    padding: 0 !important;
    margin: 0 !important;
    min-height: 0 !important;
  }

  .slide,
  .slide.active {
    display: flex !important;
    flex-direction: column !important;
    width: 338.67mm !important;
    height: 190.5mm !important;
    min-height: 190.5mm !important;
    max-height: 190.5mm !important;
    padding: 30px 48px 24px !important;
    margin: 0 !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    page-break-after: always !important;
    break-after: page !important;
    page-break-inside: avoid !important;
    break-inside: avoid !important;
    overflow: hidden !important;
  }

  .slide.cover {
    justify-content: space-between !important;
    padding: 36px 50px 24px !important;
  }

  .slide:last-child {
    page-break-after: auto !important;
    break-after: auto !important;
  }

  .nav,
  .progress {
    display: none !important;
  }
}
"""

# Reemplazar el bloque <style>...</style>
html = re.sub(r'<style>.*?</style>', f'<style>{new_css}</style>', html, flags=re.DOTALL)

# ---------------------------------------------------------------------------
# 2. REEMPLAZAR SLIDE 1 (PORTADA)
# ---------------------------------------------------------------------------
new_slide1 = """<section class="slide cover active" id="slide-1">
  <div class="cover-layout">
    <!-- COLUMNA IZQUIERDA: LOGO UNIANDES, INTEGRANTES Y GRUPO -->
    <div class="cover-left">
      <img src="assets/logo_uniandes.png" alt="UNIANDES" class="cover-logo-main">
      
      <div class="cover-block">
        <div class="cover-label">INTEGRANTES:</div>
        <div class="cover-team">
          <div>Luis Caguana <span class="role">(Tech Lead)</span></div>
          <div>Wilson Salinas <span class="role">(Builder)</span></div>
          <div>Rafael Minaya <span class="role">(QA / Seguridad)</span></div>
        </div>
      </div>

      <div class="cover-group">GRUPO N° 5</div>
    </div>

    <!-- COLUMNA DERECHA: TEMA, TÍTULO Y BADGES -->
    <div class="cover-right">
      <div class="cover-block">
        <div class="cover-label-lg">TEMA:</div>
        <div class="cover-topic">
          GUÍAVITAL: ASISTENTE DE ORIENTACIÓN EN SALUD PÚBLICA SOBRE DENGUE Y ARBOVIROSIS EN ECUADOR
        </div>
        <div class="cover-subtopic">
          CASO 05 · PROCESO DE TITULACIÓN COMPLEXIVO UNIANDES
        </div>
        <div class="cover-meta-badges">
          <span class="tag tag-outline">RAG Oficial OPS/MSP · dist ≤ 0.155</span>
          <span class="tag tag-outline">Triaje Determinista · 0 Falsos Negativos</span>
          <span class="tag tag-outline">Minimización LOPDP & HITL</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Barra de accesos directos inferior -->
  <div class="cover-footer">
    <div class="cover-links">
      <span style="color:var(--accent);font-weight:700">CLOUD RUN:</span>
      <a href="https://guiavital-448060764458.us-central1.run.app" target="_blank" rel="noopener" style="margin-left:8px">App Frontend ↗</a> ·
      <a href="https://guiavital-backend-448060764458.us-central1.run.app/manage/health" target="_blank" rel="noopener">/manage/health ↗</a> ·
      <a href="https://guiavital-backend-448060764458.us-central1.run.app/docs" target="_blank" rel="noopener">API Docs ↗</a> ·
      <a href="https://github.com/UNIPI6TO/PROY_GRADUACION_ASISTENTE_MEDICO_APP" target="_blank" rel="noopener">GitHub ↗</a>
    </div>
    <div>01 / 12</div>
  </div>

  <!-- Logo esquina inferior derecha oficial -->
  <img src="assets/logo_uniandes.png" alt="UNIANDES" class="slide-logo">
</section>"""

# Reemplazar la primera slide
html = re.sub(r'<section class=\"slide cover active\">.*?</section>', new_slide1, html, count=1, flags=re.DOTALL)

# ---------------------------------------------------------------------------
# 3. AGREGAR LOGO INSTITUCIONAL A TODAS LAS DIAPOSITIVAS (SLIDES 2 A 12)
# ---------------------------------------------------------------------------
# Encontrar cada </section> de las diapositivas 2 a 12 y asegurarse de que tengan el logo oficial
slide_matches = list(re.finditer(r'<section class=\"slide[^\"]*\">(.*?)</section>', html, re.DOTALL))
print(f'Total slides matched: {len(slide_matches)}')

# Reemplazar en cada slide que no sea slide 1
def add_logo_to_slide(match):
    content = match.group(0)
    if 'id="slide-1"' in content:
        return content # ya tiene el logo
    if 'class="slide-logo"' not in content:
        # Insertar antes del cierre de </section>
        content = content[:-10] + '\n  <img src="assets/logo_uniandes.png" alt="UNIANDES" class="slide-logo">\n</section>'
    return content

html = re.sub(r'<section class=\"slide[^\"]*\".*?</section>', add_logo_to_slide, html, flags=re.DOTALL)

# ---------------------------------------------------------------------------
# 4. AGREGAR BOTÓN DE DESCARGA PPTX EN LA BARRA DE NAVEGACIÓN
# ---------------------------------------------------------------------------
old_nav = """<div class="nav">
  <button onclick="previousSlide()" title="Diapositiva anterior (Flecha izquierda)">‹</button>
  <span id="counter">1 / 12</span>
  <button onclick="nextSlide()" title="Siguiente diapositiva (Flecha derecha)">›</button>
  <button onclick="fullscreen()" title="Pantalla completa">⛶</button>
  <button onclick="exportarPDF()" title="Exportar PDF (Tecla P)">⎙</button>
</div>"""

new_nav = """<div class="nav">
  <button onclick="previousSlide()" title="Diapositiva anterior (Flecha izquierda)">‹</button>
  <span id="counter">1 / 12</span>
  <button onclick="nextSlide()" title="Siguiente diapositiva (Flecha derecha)">›</button>
  <button onclick="fullscreen()" title="Pantalla completa">⛶</button>
  <button onclick="exportarPDF()" title="Exportar PDF (Tecla P)">⎙ PDF</button>
  <button onclick="descargarPPTX()" title="Descargar presentación oficial en PowerPoint (.pptx)" class="btn-pptx">📥 PPTX</button>
</div>"""

if old_nav in html:
    html = html.replace(old_nav, new_nav)
else:
    # Buscar por regex
    html = re.sub(
        r'<div class=\"nav\">.*?</div>',
        new_nav,
        html,
        flags=re.DOTALL
    )

# ---------------------------------------------------------------------------
# 5. AGREGAR FUNCIÓN descargarPPTX() EN <script>
# ---------------------------------------------------------------------------
func_descargar = """function descargarPPTX() {
  const link = document.createElement("a");
  link.href = "Presentacion_GuiaVital_Grupo5.pptx";
  link.download = "Presentacion_GuiaVital_Grupo5.pptx";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
"""

if 'function descargarPPTX()' not in html:
    html = html.replace('function exportarPDF() {', func_descargar + '\nfunction exportarPDF() {')

# Guardar cambios
with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Successfully updated {HTML_PATH}")

# Mantener también en sync Presentación.html
with open(r'docs/evidencias/semana-4/Presentación.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Synchronized docs/evidencias/semana-4/Presentación.html")
