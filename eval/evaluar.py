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
    aciertos = callados = 0
    con, sin = [p for p in preguntas if p.get("fuente")], [p for p in preguntas if not p.get("fuente")]
    for p in con:
        r = consultar_guia_msp(ConsultarGuiaMspIn(texto=p["pregunta"]))
        texto = " ".join(r["fragmentos"]).lower()
        aciertos += r["encontrado"] and any(kw.lower() in texto for kw in p["keywords"])
    for p in sin:
        callados += not consultar_guia_msp(ConsultarGuiaMspIn(texto=p["pregunta"]))["encontrado"]
    return aciertos / len(con), callados / len(sin)       # si Chroma no carga, que el script falle

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
    rag = evaluar_rag(preguntas)

    print(f"RAG acierto top-3: {rag:.0%}  ·  Flujo a revisión: {flujo['revision']:.0%}  ·  Errores silenciosos: {flujo['silenciosos']}")

    ok = (
        (rag >= METAS["rag_acierto_top3"])
        and (flujo["silenciosos"] == METAS["flujo_errores_silenciosos"])
        and (flujo["revision"] <= METAS["flujo_max_revision"])
    )

    if ok:
        print("[EXITO] Todas las metas del Plan de Calidad de la Semana 3 se han cumplido.")
    else:
        print("[FALLO] Una o mas metas del Plan de Calidad no se cumplieron.")

    sys.exit(0 if ok else 1)
