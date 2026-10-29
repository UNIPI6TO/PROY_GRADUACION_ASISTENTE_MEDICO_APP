"""Script de evaluación de recuperación vectorial (eval/run_eval.py).

Lee eval/preguntas.csv, consulta los 5 vecinos más cercanos en ChromaDB
e imprime en qué puesto (1..5) aparece el fragmento esperado y su distancia.
"""
from __future__ import annotations

import csv
from pathlib import Path

from app.services.retriever import BuscadorVectorial

RUTA_PREGUNTAS = Path(__file__).resolve().parent / "preguntas.csv"


def evaluar_recuperacion(k: int = 5) -> dict[str, int | float]:
    buscador = BuscadorVectorial()
    encontradas = 0
    en_top_1 = 0
    total = 0

    print("=" * 95)
    print(f"EVALUACIÓN DE BASE VECTORIAL GUÍAVITAL (Top-{k} vecinos más cercanos · Distancia Coseno)")
    print("=" * 95)

    with open(RUTA_PREGUNTAS, mode="r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            total += 1
            pregunta = fila["pregunta"]
            palabra_clave = fila["palabra_esperada"].lower()
            resultados = buscador.buscar(pregunta, k=k)

            puesto = None
            for idx, r in enumerate(resultados, start=1):
                if palabra_clave in r.texto.lower() or palabra_clave in r.seccion.lower():
                    puesto = idx
                    encontradas += 1
                    if puesto == 1:
                        en_top_1 += 1
                    print(
                        f"[{fila['id']}] Puesto #{puesto} (dist={r.distancia:.4f}) | "
                        f"Fuente: {r.metadata.get('origen')} -> {r.seccion}"
                    )
                    break
            if puesto is None:
                mejor = resultados[0] if resultados else None
                detalle = f"salió '{mejor.seccion[:50]}' (dist={mejor.distancia:.4f})" if mejor else "sin resultados"
                print(f"[{fila['id']}] NO ENCONTRÓ '{palabra_clave}' en top-{k} | {detalle}")

    porcentaje_k = (encontradas / max(total, 1)) * 100
    porcentaje_1 = (en_top_1 / max(total, 1)) * 100
    print("-" * 95)
    print(
        f"Resumen: Hit@1 = {en_top_1}/{total} ({porcentaje_1:.1f}%) | "
        f"Hit@{k} = {encontradas}/{total} ({porcentaje_k:.1f}%)"
    )
    print("=" * 95)
    return {"total": total, "encontradas": encontradas, "en_top_1": en_top_1, "hit_at_k": porcentaje_k}


if __name__ == "__main__":
    evaluar_recuperacion()
