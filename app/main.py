"""
Módulo principal del Backend: Asistente de Orientación en Salud Pública sobre Dengue.

Expone los endpoints operativos /manage/health y /manage/info cumpliendo con
los principios SOLID (Responsabilidad Única) y permitiendo su ejecución y prueba
tanto de forma modular como mediante FastAPI.
"""

import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

APP_NAME = "asistente-orientacion-salud-dengue"
APP_VERSION = "0.1.0"
SEMVER_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"


def check_health(readiness_probes: Optional[List[Callable[[], bool]]] = None) -> Tuple[Dict[str, Any], int]:
    """
    Evalúa el estado de salud de la aplicación (Liveness y Readiness).

    - Liveness: 'UP' si el proceso de la aplicación está activo y respondiendo.
    - Readiness: 'UP' si todas las sondas de preparación pasan con éxito; 'DOWN' si alguna falla.

    Retorna:
        Tuple[Dict[str, Any], int]: Estructura con el detalle del diagnóstico y código de estado HTTP (200 o 503).
    """
    liveness_status = "UP"

    # Evaluación de sondas de disponibilidad (readiness)
    readiness_status = "UP"
    if readiness_probes:
        for probe in readiness_probes:
            try:
                if not probe():
                    readiness_status = "DOWN"
                    break
            except Exception:
                readiness_status = "DOWN"
                break

    is_healthy = (liveness_status == "UP") and (readiness_status == "UP")
    http_status = 200 if is_healthy else 503

    payload = {
        "status": "UP" if is_healthy else "DOWN",
        "checks": {
            "liveness": {"status": liveness_status},
            "readiness": {"status": readiness_status},
        },
    }

    return payload, http_status


def get_info() -> Tuple[Dict[str, str], int]:
    """
    Retorna la información y metadatos de versión de la aplicación.
    Garantiza el cumplimiento del formato semántico SemVer.

    Retorna:
        Tuple[Dict[str, str], int]: Diccionario con nombre y versión SemVer, junto con el código 200 OK.
    """
    app_name = os.getenv("APP_NAME", APP_NAME)
    version = os.getenv("APP_VERSION", APP_VERSION)

    if not re.match(SEMVER_REGEX, version):
        raise ValueError(f"Versión inválida bajo SemVer: {version}")

    payload = {
        "name": app_name,
        "version": version,
    }

    return payload, 200


# Integración opcional / declarativa con FastAPI si el paquete está presente
try:
    from fastapi import FastAPI, Response

    app = FastAPI(
        title="Asistente de Orientación en Salud Pública - Dengue",
        description="API Backend para orientación preventiva y triaje de signos de alarma en dengue.",
        version=APP_VERSION,
    )

    @app.get("/manage/health", tags=["Management"])
    def manage_health_endpoint(response: Response) -> Dict[str, Any]:
        data, status_code = check_health()
        response.status_code = status_code
        return data

    @app.get("/manage/info", tags=["Management"])
    def manage_info_endpoint(response: Response) -> Dict[str, str]:
        data, status_code = get_info()
        response.status_code = status_code
        return data

except ImportError:
    app = None
