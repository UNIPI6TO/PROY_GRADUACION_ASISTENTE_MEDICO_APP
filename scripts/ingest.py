"""Ingesta reproducible de los documentos oficiales de GuíaVital en ChromaDB.

Documentos procesados:
  1. data/raw/Guia-dengue-OPS-2016.pdf (Guía completa OPS 2016: Preliminares clave,
     Capítulos 1-8 y Anexos clínicos D-U; excluye bibliografía págs. 107-127).
  2. data/raw/manual_de_procedimientos_sive-alerta.pdf (Páginas 95-100:
     Sección 8.2.3.2 DENGUE del MSP Ecuador).

Uso:
    python -m scripts.ingest
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import shutil
from typing import Any

import chromadb
from chromadb.config import Settings
import pymupdf

MODELO_EMBEDDINGS = "intfloat/multilingual-e5-small"
NOMBRE_COLECCION = "guia_vital_dengue"

RUTA_BASE = Path(__file__).resolve().parent.parent
RUTA_OPS_PDF = RUTA_BASE / "data" / "raw" / "Guia-dengue-OPS-2016.pdf"
RUTA_SIVE_PDF = RUTA_BASE / "data" / "raw" / "manual_de_procedimientos_sive-alerta.pdf"
RUTA_PROCESSED_DIR = RUTA_BASE / "data" / "processed"
RUTA_CHROMA_DEFAULT = RUTA_BASE / "chroma_db"

DOC_OPS_NOMBRE = "Dengue: Guías para la atención de enfermos en la Región de las Américas (OPS, 2016)"
DOC_SIVE_NOMBRE = "Manual de procedimientos del Subsistema Alerta Acción SIVE-Alerta (MSP, 2013)"


@dataclass(frozen=True)
class Fragmento:
    id: str
    texto: str
    metadata: dict[str, Any]


def _limpiar_texto(texto: str) -> str:
    """Elimina marcas de agua ('Documento final'), números de página sueltos, cabeceras repetidas y espacios múltiples."""
    texto = re.sub(r"(?m)^\s*Documento\s+final\s*$", "", texto, flags=re.IGNORECASE)
    texto = re.sub(
        r"(?m)^\s*Dengue:\s*guías\s+para\s+la\s+atención\s+de\s+enfermos\s+en\s+la\s+Región\s+de\s+las\s+Américas\s*$",
        "",
        texto,
    )
    # Quitar números de página sueltos en su propia línea (1 a 3 dígitos)
    texto = re.sub(r"(?m)^\s*\d{1,3}\s*$", "", texto)
    texto = re.sub(r"\r\n", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def _subdividir_si_excede(texto: str, encabezado: str, max_chars: int = 1600) -> list[str]:
    """Si una sección supera max_chars, la divide por párrafos conservando el encabezado clínico."""
    texto = texto.strip()
    if len(texto) <= max_chars:
        return [f"[{encabezado}]\n{texto}"]

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    bloques_crudos: list[str] = []
    actual: list[str] = []
    longitud_actual = 0

    for p in parrafos:
        if actual and (longitud_actual + len(p) > max_chars):
            bloques_crudos.append("\n\n".join(actual))
            actual = [p]
            longitud_actual = len(p)
        else:
            actual.append(p)
            longitud_actual += len(p) + 2

    if actual:
        ultimo = "\n\n".join(actual)
        # Evitar fragmentos huérfanos muy cortos al final (< 150 chars): unirlos al bloque anterior
        if len(ultimo) < 150 and bloques_crudos:
            bloques_crudos[-1] = bloques_crudos[-1] + "\n\n" + ultimo
        else:
            bloques_crudos.append(ultimo)

    return [f"[{encabezado}]\n{b}" for b in bloques_crudos]


def extraer_fragmentos_sive(
    ruta_pdf: Path = RUTA_SIVE_PDF,
    pag_inicio: int = 95,
    pag_fin: int = 100,
) -> list[Fragmento]:
    """Extrae y corta por secciones la ficha 8.2.3.2 DENGUE (págs. 95-100) del manual SIVE-Alerta."""
    pdf = pymupdf.open(str(ruta_pdf))
    try:
        paginas_texto: list[str] = []
        for num_pag in range(pag_inicio, pag_fin + 1):
            raw = pdf[num_pag - 1].get_text()
            raw = re.sub(rf"(?m)^\s*{num_pag}\s*$", "", raw)
            paginas_texto.append(_limpiar_texto(raw))
        texto_completo = "\n\n".join(paginas_texto)
    finally:
        pdf.close()

    # Recortar exactamente desde "8.2.3.2 DENGUE" (pág. 95) hasta antes de "8.2.3.3 FIEBRE AMARILLA" (pág. 100)
    inicio_match = re.search(r"8\.2\.3\.2\s+DENGUE", texto_completo)
    if inicio_match:
        texto_completo = texto_completo[inicio_match.start():]
    fin_match = re.search(r"8\.2\.3\.3\s+FIEBRE\s+AMARILLA", texto_completo)
    if fin_match:
        texto_completo = texto_completo[:fin_match.start()]

    # Patrón de corte por los bloques normativos oficiales del MSP en las págs. 95-100
    patron_secciones = re.compile(
        r"(?m)^(?="
        r"8\.2\.3\.2\s+DENGUE|"
        r"MODALIDAD\s+DE\s+VIGILANCIA|"
        r"CADENA\s+EPIDEMIOLÓGICA|"
        r"DENGUE\s+SIN\s+SIGNOS\s+DE\s+ALARMA\s*\nCaso\s+confirmado|"
        r"DENGUE\s+CON\s+SIGNOS\s+DE\s+ALARMA\s*\nCaso\s+sospechoso|"
        r"DENGUE\s+GRAVE:|"
        r"PROCESO\s+DE\s+INVESTIGACIÓN|"
        r"INVESTIGACIÓN\s+DE\s+CAMPO|"
        r"MEDIDAS\s+DE\s+CONTROL"
        r")"
    )

    partes = [p.strip() for p in patron_secciones.split(texto_completo) if p.strip()]
    fragmentos: list[Fragmento] = []

    for idx, parte in enumerate(partes, start=1):
        primera_linea = parte.splitlines()[0].strip().rstrip(":")
        seccion = f"8.2.3.2 Dengue · {primera_linea} (págs. {pag_inicio}-{pag_fin})"
        encabezado = f"MSP SIVE-Alerta 2013 · {seccion}"

        for sub_idx, bloque in enumerate(_subdividir_si_excede(parte, encabezado), start=1):
            frag_id = f"sive-dengue-{idx:02d}-{sub_idx:02d}"
            fragmentos.append(
                Fragmento(
                    id=frag_id,
                    texto=bloque,
                    metadata={
                        "documento": DOC_SIVE_NOMBRE,
                        "origen": "MSP Ecuador",
                        "seccion": seccion,
                        "pagina_inicio": pag_inicio,
                        "pagina_fin": pag_fin,
                        "anio": 2013,
                        "vigente": True,
                        "codigo_cie10": "A90, A91",
                    },
                )
            )
    return fragmentos


def extraer_fragmentos_ops(ruta_pdf: Path = RUTA_OPS_PDF) -> list[Fragmento]:
    """Extrae y corta estructuradamente la Guía de Dengue OPS 2016 completa (sin bibliografía)."""
    pdf = pymupdf.open(str(ruta_pdf))
    fragmentos: list[Fragmento] = []
    try:
        # 1. Preliminares útiles: Pág. PDF 2 (Prevención) y Págs. PDF 16-17 (Abreviaturas)
        texto_prev = _limpiar_texto(pdf[1].get_text())
        fragmentos.append(
            Fragmento(
                id="ops-prelim-prevencion",
                texto=f"[OPS 2016 · Prevención vectorial en instituciones y hogares]\n{texto_prev}",
                metadata={
                    "documento": DOC_OPS_NOMBRE,
                    "origen": "OPS/OMS",
                    "seccion": "Preliminar · ¡Sin mosquitos no hay dengue! (pág. ii)",
                    "pagina_inicio": 2,
                    "pagina_fin": 2,
                    "anio": 2016,
                    "vigente": True,
                    "codigo_cie10": "A90, A91",
                },
            )
        )

        texto_abrev = _limpiar_texto(pdf[15].get_text() + "\n" + pdf[16].get_text())
        fragmentos.append(
            Fragmento(
                id="ops-prelim-abreviaturas",
                texto=f"[OPS 2016 · Abreviaturas y Siglas Clínicas]\n{texto_abrev}",
                metadata={
                    "documento": DOC_OPS_NOMBRE,
                    "origen": "OPS/OMS",
                    "seccion": "Abreviaturas y Siglas (págs. xiv-xv)",
                    "pagina_inicio": 16,
                    "pagina_fin": 17,
                    "anio": 2016,
                    "vigente": True,
                    "codigo_cie10": "A90, A91",
                },
            )
        )

        # 2. Cuerpo Clínico Principal: Págs. PDF 19 a 105 (Introducción y Capítulos 1 al 8)
        paginas_cuerpo: list[str] = []
        for idx_pag in range(18, 105):  # 0-indexed: páginas PDF 19 a 105
            raw = _limpiar_texto(pdf[idx_pag].get_text())
            if raw:
                paginas_cuerpo.append(raw)
        texto_cuerpo = "\n\n".join(paginas_cuerpo)

        patron_cuerpo = re.compile(
            r"(?m)^(?="
            r"INTRODUCCIÓN|"
            r"\d+\.\d+(?:\.\d+)?\.?\s+[A-ZÁÉÍÓÚÑ¿¡]|"
            r"Cuadro\s+\d+\.|"
            r"Figura\s+2\.\s+Clasificación|"
            r"Categoría\s+de\s+intervención\s+(?:A|B1|B2|C)"
            r")"
        )
        secciones_cuerpo = [s.strip() for s in patron_cuerpo.split(texto_cuerpo) if len(s.strip()) > 60]

        for idx, sec in enumerate(secciones_cuerpo, start=1):
            primera_linea = sec.splitlines()[0].strip()
            seccion_limpia = re.sub(r"\s+", " ", primera_linea)[:120]
            encabezado = f"OPS 2016 · {seccion_limpia}"
            for sub_idx, bloque in enumerate(_subdividir_si_excede(sec, encabezado), start=1):
                fragmentos.append(
                    Fragmento(
                        id=f"ops-cap-{idx:03d}-{sub_idx:02d}",
                        texto=bloque,
                        metadata={
                            "documento": DOC_OPS_NOMBRE,
                            "origen": "OPS/OMS",
                            "seccion": seccion_limpia,
                            "pagina_inicio": 19,
                            "pagina_fin": 105,
                            "anio": 2016,
                            "vigente": True,
                            "codigo_cie10": "A90, A91",
                        },
                    )
                )

        # 3. Anexos Clínicos: Págs. PDF 128 a 141 (Anexo D al Anexo U)
        # Se excluyen págs. PDF 107-127 (Bibliografía y Anexos metodológicos A-C)
        paginas_anexos: list[str] = []
        for idx_pag in range(127, 141):  # 0-indexed: páginas PDF 128 a 141
            raw = _limpiar_texto(pdf[idx_pag].get_text())
            if raw:
                paginas_anexos.append(raw)
        texto_anexos = "\n\n".join(paginas_anexos)

        patron_anexos = re.compile(r"(?m)^(?=Anexo\s+[D-U]\.)")
        secciones_anexos = [a.strip() for a in patron_anexos.split(texto_anexos) if len(a.strip()) > 60]

        for idx, anexo in enumerate(secciones_anexos, start=1):
            primera_linea = anexo.splitlines()[0].strip()
            seccion_limpia = re.sub(r"\s+", " ", primera_linea)[:120]
            encabezado = f"OPS 2016 · {seccion_limpia}"
            for sub_idx, bloque in enumerate(_subdividir_si_excede(anexo, encabezado), start=1):
                fragmentos.append(
                    Fragmento(
                        id=f"ops-anexo-{idx:02d}-{sub_idx:02d}",
                        texto=bloque,
                        metadata={
                            "documento": DOC_OPS_NOMBRE,
                            "origen": "OPS/OMS",
                            "seccion": seccion_limpia,
                            "pagina_inicio": 128,
                            "pagina_fin": 141,
                            "anio": 2016,
                            "vigente": True,
                            "codigo_cie10": "A90, A91",
                        },
                    )
                )
    finally:
        pdf.close()

    return fragmentos


def exportar_fragmentos(
    fragmentos: list[Fragmento],
    directorio: Path = RUTA_PROCESSED_DIR,
) -> tuple[Path, Path]:
    """Exporta los fragmentos cortados a data/processed/ en formato JSON y Markdown legible."""
    directorio.mkdir(parents=True, exist_ok=True)
    ruta_json = directorio / "fragmentos.json"
    ruta_md = directorio / "fragmentos.md"

    with open(ruta_json, "w", encoding="utf-8") as f_json:
        json.dump([asdict(f) for f in fragmentos], f_json, ensure_ascii=False, indent=2)

    lineas_md = [
        "# Fragmentos Procesados de la Base Vectorial (GuíaVital)",
        "",
        f"- **Total de fragmentos:** {len(fragmentos)}",
        "",
        "---",
        "",
    ]
    for idx, f in enumerate(fragmentos, start=1):
        lineas_md.append(f"## {idx}. `{f.id}` — {f.metadata.get('seccion')}")
        lineas_md.append(
            f"- **Documento:** {f.metadata.get('documento')}\n"
            f"- **Origen:** `{f.metadata.get('origen')}` | **Vigencia:** `{f.metadata.get('vigente')}` | "
            f"**Longitud:** `{len(f.texto)} caracteres`"
        )
        lineas_md.append("")
        lineas_md.append("```text")
        lineas_md.append(f.texto)
        lineas_md.append("```")
        lineas_md.append("")

    with open(ruta_md, "w", encoding="utf-8") as f_md:
        f_md.write("\n".join(lineas_md))

    return ruta_json, ruta_md


def ingestar_documentos(
    ruta_db: Path = RUTA_CHROMA_DEFAULT,
    cartero: Any | None = None,
    reiniciar: bool = True,
    exportar: bool = True,
) -> dict[str, int]:
    """Ejecuta los Pasos 1 y 2 de la clase: corta ambos PDFs, vectoriza con 'passage: ' y guarda en ChromaDB."""
    frag_ops = extraer_fragmentos_ops(RUTA_OPS_PDF)
    frag_sive = extraer_fragmentos_sive(RUTA_SIVE_PDF, pag_inicio=95, pag_fin=100)
    todos = frag_ops + frag_sive

    if exportar:
        exportar_fragmentos(todos)

    if reiniciar and ruta_db.exists():
        shutil.rmtree(ruta_db)

    if cartero is None:
        from sentence_transformers import SentenceTransformer
        try:
            modelo = SentenceTransformer(MODELO_EMBEDDINGS, local_files_only=True)
        except Exception:
            modelo = SentenceTransformer(MODELO_EMBEDDINGS)
    else:
        modelo = cartero
    db = chromadb.PersistentClient(
        path=str(ruta_db),
        settings=Settings(anonymized_telemetry=False),
    )

    existentes = [c.name for c in db.list_collections()]
    if NOMBRE_COLECCION in existentes:
        db.delete_collection(NOMBRE_COLECCION)

    col = db.create_collection(
        name=NOMBRE_COLECCION,
        configuration={"hnsw": {"space": "cosine"}},
    )

    textos_passage = ["passage: " + f.texto for f in todos]
    vectores = modelo.encode(textos_passage, normalize_embeddings=True)
    if hasattr(vectores, "tolist"):
        vectores = vectores.tolist()

    col.add(
        ids=[f.id for f in todos],
        documents=[f.texto for f in todos],
        metadatas=[f.metadata for f in todos],
        embeddings=vectores,
    )

    resumen = {
        "ops_2016": len(frag_ops),
        "sive_alerta_95_100": len(frag_sive),
        "total": col.count(),
    }
    print(
        f"Ingesta completada en '{ruta_db}': "
        f"{resumen['ops_2016']} fragmentos OPS 2016 + "
        f"{resumen['sive_alerta_95_100']} fragmentos SIVE-Alerta (págs. 95-100) = "
        f"{resumen['total']} fragmentos totales."
    )
    return resumen


if __name__ == "__main__":
    ingestar_documentos()
