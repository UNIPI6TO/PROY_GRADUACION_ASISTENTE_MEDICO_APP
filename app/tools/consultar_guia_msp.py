"""Herramienta Libre: Busca información en la guía del MSP mediante ChromaDB."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from app.services.retriever import BuscadorVectorial

from app.config import cargar_parametros

class ConsultarGuiaMspIn(BaseModel):
    texto: str = Field(min_length=3, max_length=1000, description="Consulta o síntomas a buscar en las guías oficiales del MSP.")


def consultar_guia_msp(datos: ConsultarGuiaMspIn, buscador: BuscadorVectorial | None = None) -> dict[str, Any]:
    """Busca en la guía clínica del MSP a través de la base vectorial."""
    b = buscador or BuscadorVectorial()
    params = cargar_parametros().get("retriever", {})
    tope = float(params.get("distancia_max", 0.155))
    top_k = int(params.get("top_k", 3))
    solo_vigentes = bool(params.get("solo_vigentes", True))

    resultados = [r for r in b.buscar(datos.texto, k=top_k, solo_vigentes=solo_vigentes) if r.distancia <= tope]
    if not resultados:
        return {"encontrado": False, "fragmentos": [], "fuentes": [],
                "mensaje": "La guía del MSP no trata este tema. No respondas con conocimiento propio."}

    return {
        "encontrado": True,
        "fragmentos": [r.texto for r in resultados],
        "fuentes": [{"documento": r.documento, "seccion": r.seccion} for r in resultados],
    }


ESQUEMA = {
    "type": "function",
    "function": {
        "name": "consultar_guia_msp",
        "description": "Busca protocolos y guías oficiales del MSP/OPS sobre dengue, arbovirosis (zika, chikungunya, fiebre amarilla) y signos de alarma en la base documental.",
        "parameters": ConsultarGuiaMspIn.model_json_schema(),
    },
}
