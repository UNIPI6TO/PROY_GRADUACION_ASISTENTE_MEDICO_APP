"""Herramienta Libre: Localiza centros de salud cercanos y verifica su disponibilidad operativa."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

RUTA_GEOSALUD = Path(__file__).resolve().parent.parent.parent / "data" / "geosalud_ecuador.json"


class BuscarCentroSaludIn(BaseModel):
    ciudad: str | None = Field(default=None, description="Nombre de la ciudad o cantón (ej. Guayaquil, Machala, Portoviejo, Tena)")
    latitud: float | None = Field(default=None, ge=-5.0, le=2.5, description="Latitud GPS del usuario")
    longitud: float | None = Field(default=None, ge=-92.0, le=-75.0, description="Longitud GPS del usuario")
    solo_emergencia_24h: bool = Field(default=True, description="Si es True, prioriza centros con servicio de emergencia 24 horas.")


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia ortodrómica en kilómetros entre dos coordenadas geográficas."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def buscar_centro_salud(datos: BuscarCentroSaludIn) -> dict[str, Any]:
    """Busca establecimientos de salud del MSP ordenando por distancia y disponibilidad."""
    if not RUTA_GEOSALUD.exists():
        return {"error": "Base de datos GeoSalud no disponible"}

    with open(RUTA_GEOSALUD, "r", encoding="utf-8") as f:
        centros = json.load(f)

    candidatos = []
    for c in centros:
        # Filtro de ciudad (si fue provisto)
        if datos.ciudad and datos.ciudad.strip():
            ciudad_buscada = datos.ciudad.strip().lower()
            if ciudad_buscada not in c.get("ciudad", "").lower() and ciudad_buscada not in c.get("provincia", "").lower():
                continue

        es_24h = any(h.get("es_24_horas", False) for h in c.get("horarios", []))
        if datos.solo_emergencia_24h and not es_24h:
            continue

        distancia = None
        if datos.latitud is not None and datos.longitud is not None:
            distancia = round(_haversine_km(datos.latitud, datos.longitud, c["latitud"], c["longitud"]), 2)

        candidatos.append({
            "nombre": c.get("nombre", ""),
            "provincia": c.get("provincia", ""),
            "ciudad": c.get("ciudad", ""),
            "direccion": c.get("direccion", ""),
            "distancia_km": distancia,
            "emergencia_24h": es_24h,
            "telefonos": [t.get("telefono", "") for t in c.get("telefonos", [])],
        })

    # Ordenar por proximidad si hay coordenadas
    if datos.latitud is not None and datos.longitud is not None:
        candidatos.sort(key=lambda x: (x["distancia_km"] is None, x["distancia_km"]))

    # Tomar los 3 más cercanos o relevantes
    seleccionados = candidatos[:3]

    return {
        "total_encontrados": len(candidatos),
        "centros_cercanos": seleccionados,
    }


ESQUEMA = {
    "type": "function",
    "function": {
        "name": "buscar_centro_salud",
        "description": "Busca hospitales y centros de salud del MSP cercanos al usuario y verifica si tienen servicio de emergencia 24 horas activo.",
        "parameters": BuscarCentroSaludIn.model_json_schema(),
    },
}
