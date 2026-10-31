"""Herramienta Libre: Busca información en la guía del MSP mediante ChromaDB."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from app.services.retriever import BuscadorVectorial


class ConsultarGuiaMspIn(BaseModel):
    texto: str = Field(min_length=3, max_length=1000, description="Consulta o síntomas a buscar en las guías oficiales del MSP.")


def consultar_guia_msp(datos: ConsultarGuiaMspIn, buscador: BuscadorVectorial | None = None) -> dict[str, Any]:
    """Busca en la guía clínica del MSP a través de la base vectorial."""
    b = buscador or BuscadorVectorial()
    resultados = b.buscar(datos.texto, k=3, solo_vigentes=True)
    if not resultados:
        return {
            "encontrado": False,
            "fragmentos": [],
            "fuentes": [],
            "mensaje": "No se encontraron secciones específicas para esa consulta.",
        }

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
