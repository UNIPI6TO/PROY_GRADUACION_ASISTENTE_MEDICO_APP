# eval/evaluar.py · Grupo 5 · corre en CI: python eval/evaluar.py
import json
import sys
from pathlib import Path

# Garantizar imports desde la raíz
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.flujo import procesar

METAS = {
    "rag_acierto_top3": 0.85,
    "rag_con_cita": 0.85,
    "rag_silencio": 1.00,
    "agente_tareas": 0.01,
    "flujo_max_revision": 0.30,
    "flujo_errores_silenciosos": 0,
}


def leer(ruta):
    p = Path(ruta)
    if not p.exists():
        return []
    return [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]

def evaluar_rag(preguntas, k=3):
    from app.tools.consultar_guia_msp import consultar_guia_msp, ConsultarGuiaMspIn
    aciertos = callados = con_citas = 0
    con, sin = [p for p in preguntas if p.get("fuente")], [p for p in preguntas if not p.get("fuente")]
    for p in con:
        r = consultar_guia_msp(ConsultarGuiaMspIn(texto=p["pregunta"]))
        texto = " ".join(r["fragmentos"]).lower()
        aciertos += r["encontrado"] and any(kw.lower() in texto for kw in p["keywords"])
        tiene_citas_validas = (
            r["encontrado"]
            and len(r.get("fuentes", [])) > 0
            and all(bool(f.get("documento")) and f.get("seccion") is not None for f in r["fuentes"])
        )
        con_citas += tiene_citas_validas
    for p in sin:
        callados += not consultar_guia_msp(ConsultarGuiaMspIn(texto=p["pregunta"]))["encontrado"]
    return aciertos / len(con), callados / len(sin), con_citas / len(con)       # si Chroma no carga, que el script falle

def evaluar_flujo(casos):
    auto = rev = silenciosos = 0
    for c in casos:
        r = procesar(c)
        if r["destino"] == "revision":
            rev += 1
        else:
            auto += 1
            if r["resultado"] != c["esperado"]["resultado"]:
                silenciosos += 1  # Salió automático pero con acción equivocada
    return {"revision": rev / max(1, len(casos)), "silenciosos": silenciosos}


if __name__ == "__main__":
    casos = leer("eval/casos_flujo.jsonl")
    flujo = evaluar_flujo(casos)
    
    preguntas = leer("eval/preguntas_rag.jsonl")
    rag_acierto, rag_silencio, rag_con_cita = evaluar_rag(preguntas)

    print(f"RAG acierto top-3: {rag_acierto:.0%}  ·  Con cita: {rag_con_cita:.0%}  ·  Silencio: {rag_silencio:.0%}  ·  Flujo a revisión: {flujo['revision']:.0%}  ·  Errores silenciosos: {flujo['silenciosos']}")

    ok = (
        (rag_acierto >= METAS["rag_acierto_top3"])
        and (rag_con_cita >= METAS["rag_con_cita"])
        and (rag_silencio >= METAS["rag_silencio"])
        and (flujo["silenciosos"] == METAS["flujo_errores_silenciosos"])
        and (flujo["revision"] <= METAS["flujo_max_revision"])
    )

    if ok:
        print("[EXITO] Todas las metas del Plan de Calidad de la Semana 3 se han cumplido.")
    else:
        print("[FALLO] Una o mas metas del Plan de Calidad no se cumplieron.")

    sys.exit(0 if ok else 1)
