"""Herramienta Libre: Localiza centros de salud cercanos y verifica su disponibilidad operativa."""
from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus
from pydantic import BaseModel, Field

RUTA_GEOSALUD = Path(__file__).resolve().parent.parent.parent / "data" / "geosalud_ecuador.json"


class BuscarCentroSaludIn(BaseModel):
    ciudad: str | None = Field(
        default=None,
        description="Nombre de la ciudad, cantón o provincia en Ecuador (ej. Manta, Guayaquil, Portoviejo, Machala, Quevedo, Esmeraldas, Tena, Puyo, Nueva Loja, El Coca)",
    )
    latitud: float | None = Field(default=None, ge=-5.0, le=2.5, description="Latitud GPS del usuario")
    longitud: float | None = Field(default=None, ge=-92.0, le=-75.0, description="Longitud GPS del usuario")
    solo_emergencia_24h: bool = Field(
        default=True,
        description=(
            "Si es True, prioriza centros con servicio de emergencia 24 horas. "
            "Envía False si el ciudadano solicita consultar todos los centros, servicios (Consulta Externa, Atención General) u horarios de atención."
        ),
    )


def _normalizar_texto(texto: str) -> str:
    """Convierte a minúsculas y elimina tildes/diacríticos para comparaciones tolerantes."""
    sin_tildes = unicodedata.normalize("NFD", (texto or "").strip().lower())
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")


def _limpiar_consulta_ciudad(texto: str) -> str:
    """Elimina prefijos descriptivos ('ciudad de Manta', 'cuidad de manta', 'cantón') para aislar la localidad."""
    norm = _normalizar_texto(texto)
    norm = re.sub(
        r"\b(la|el|los|las|en|de|del|cercano|cercana|cercanos|cerca|a|ciudad|cuidad|canton|provincia|sector|parroquia)\b",
        " ",
        norm,
    )
    norm = re.sub(r"[,.;:\-_/]+", " ", norm)
    return " ".join(norm.split())


def _coincide_localidad(busqueda_raw: str, ciudad_centro: str, provincia_centro: str) -> bool:
    """Verifica coincidencia bidireccional entre la localidad buscada y la ciudad o provincia del centro."""
    b_raw = _normalizar_texto(busqueda_raw)
    b_limpia = _limpiar_consulta_ciudad(busqueda_raw)
    c_norm = _normalizar_texto(ciudad_centro)
    p_norm = _normalizar_texto(provincia_centro)

    for candidato in (b_limpia, b_raw):
        if not candidato:
            continue
        if c_norm and (candidato in c_norm or c_norm in candidato):
            return True
        if p_norm and (candidato in p_norm or p_norm in candidato):
            return True
    return False


def _construir_google_maps_url(
    latitud: float | None,
    longitud: float | None,
    nombre: str = "",
    direccion: str = "",
    ciudad: str = "",
) -> str:
    """Construye un enlace universal de Google Maps compatible con celulares (Android/iOS) y computadoras."""
    if latitud is not None and longitud is not None:
        return f"https://www.google.com/maps/dir/?api=1&destination={latitud},{longitud}"
    consulta = ", ".join(p for p in (nombre, direccion, ciudad, "Ecuador") if p)
    return f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(consulta)}"


def _formatear_servicios_horarios(horarios_crudos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Estructura los servicios que ofrece el centro de salud junto con sus días y horarios."""
    servicios: list[dict[str, Any]] = []
    for h in horarios_crudos:
        servicio = h.get("servicio", "Atención")
        dias = h.get("dias", "")
        apertura = h.get("hora_apertura", "")
        cierre = h.get("hora_cierre", "")
        es_24h = bool(h.get("es_24_horas", False))
        rango = f"24 horas ({apertura} - {cierre})" if es_24h else f"{apertura} a {cierre}"
        servicios.append({
            "servicio": servicio,
            "dias": dias,
            "horario": rango,
            "hora_apertura": apertura,
            "hora_cierre": cierre,
            "es_24_horas": es_24h,
        })
    return servicios


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

    def _filtrar(exigir_24h: bool) -> list[dict[str, Any]]:
        lista: list[dict[str, Any]] = []
        for c in centros:
            if datos.ciudad and datos.ciudad.strip():
                if not _coincide_localidad(datos.ciudad, c.get("ciudad", ""), c.get("provincia", "")):
                    continue

            horarios_raw = c.get("horarios", [])
            es_24h = any(h.get("es_24_horas", False) for h in horarios_raw)
            if exigir_24h and not es_24h:
                continue

            lat = c.get("latitud")
            lon = c.get("longitud")
            distancia = None
            if datos.latitud is not None and datos.longitud is not None and lat is not None and lon is not None:
                distancia = round(_haversine_km(datos.latitud, datos.longitud, lat, lon), 2)

            nombre = c.get("nombre", "")
            ciudad = c.get("ciudad", "")
            direccion = c.get("direccion", "")
            servicios_horarios = _formatear_servicios_horarios(horarios_raw)

            lista.append({
                "nombre": nombre,
                "provincia": c.get("provincia", ""),
                "ciudad": ciudad,
                "direccion": direccion,
                "latitud": lat,
                "longitud": lon,
                "distancia_km": distancia,
                "emergencia_24h": es_24h,
                "servicios_horarios": servicios_horarios,
                "telefonos": [t.get("telefono", "") for t in c.get("telefonos", [])],
                "google_maps_url": _construir_google_maps_url(lat, lon, nombre, direccion, ciudad),
            })
        return lista

    candidatos = _filtrar(datos.solo_emergencia_24h)
    # Si se buscó una ciudad específica con solo_emergencia_24h=True y solo tiene centros diurnos, incluirlos como respaldo
    if not candidatos and datos.solo_emergencia_24h and datos.ciudad and datos.ciudad.strip():
        candidatos = _filtrar(False)

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
        "description": (
            "Busca hospitales y centros de salud del MSP cercanos al usuario por ciudad, cantón, provincia o coordenadas GPS, "
            "retornando dirección exacta, teléfonos, servicios ofrecidos (Emergencia, Consulta Externa, Atención General), "
            "horarios de atención y enlace directo de navegación en Google Maps."
        ),
        "parameters": BuscarCentroSaludIn.model_json_schema(),
    },
}
