"""
Módulo principal del Backend: Asistente de Orientación en Salud Pública sobre Dengue (GuíaVital).

Expone los endpoints operativos /manage/health y /manage/info cumpliendo con
los principios SOLID (Responsabilidad Única) y los endpoints del asistente de IA.
"""
from __future__ import annotations

import logging
import os
import re
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.repositorio.historial import RepositorioHistorial
from app.schemas import (
    ProblemaRFC9457,
    RespuestaAsistente,
    RespuestaChat,
    Solicitud,
)
from app.services.llm import ClienteLLM, ProveedorNoDisponible, SalidaInvalida, cargar_prompt
from app.services.seguridad import LimiteExcedido, LimitadorTasa, delimitar_consulta

APP_NAME = "GuíaVital"
APP_VERSION = "0.1.0"
SEMVER_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

PROMPT = "system_v4"

log_app = logging.getLogger("app")

app = FastAPI(
    title="GuíaVital - Asistente de Orientación en Salud Pública sobre Dengue",
    description="API Backend para orientación preventiva y triaje de signos de alarma en dengue.",
    version=APP_VERSION,
)

# CORS cerrado: solo los orígenes declarados en CORS_ORIGINS (nunca "*").
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in (os.getenv("CORS_ORIGINS", "").strip() or "http://localhost:8501,http://localhost:5173").split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    expose_headers=["Retry-After"],
)


def _problema(status: int, titulo: str, detalle: str, request: Request, headers: Optional[dict] = None) -> JSONResponse:
    """Error en formato RFC 9457 (Problem Details), sin detalles internos."""
    cuerpo = ProblemaRFC9457(type=f"/errores/{status}", title=titulo, status=status,
                             detail=detalle, instance=str(request.url.path))
    return JSONResponse(cuerpo.model_dump(), status_code=status, headers=headers,
                        media_type="application/problem+json")


@lru_cache
def obtener_llm() -> ClienteLLM:
    return ClienteLLM()


@lru_cache
def obtener_repositorio() -> RepositorioHistorial:
    return RepositorioHistorial()


@lru_cache
def obtener_limitador() -> LimitadorTasa:
    maximo = int(os.getenv("RATE_LIMIT_PER_MINUTE", "").strip() or "10")
    return LimitadorTasa(maximo, 60)


@app.exception_handler(RequestValidationError)
async def _manejar_422(request: Request, exc: RequestValidationError):
    return _problema(422, "Solicitud inválida", "Revisa idSesion y texto (5 a 2000 caracteres).", request)


@app.exception_handler(LimiteExcedido)
async def _manejar_429(request: Request, exc: LimiteExcedido):
    return _problema(429, "Demasiadas solicitudes", "Espera un momento antes de volver a consultar.",
                     request, {"Retry-After": str(exc.retry_after)})


@app.exception_handler(ProveedorNoDisponible)
async def _manejar_503(request: Request, exc: ProveedorNoDisponible):
    return _problema(503, "Servicio no disponible", exc.mensaje_usuario, request, {"Retry-After": "30"})


@app.exception_handler(Exception)
async def _manejar_500(request: Request, exc: Exception):
    log_app.exception("error no controlado")  # el detalle queda solo en el log interno
    return _problema(500, "Error interno", "Ocurrió un error inesperado.", request)


@app.post("/api/v1/chat", response_model=RespuestaChat, tags=["Asistente"],
          responses={422: {"model": ProblemaRFC9457}, 429: {"model": ProblemaRFC9457},
                     503: {"model": ProblemaRFC9457}})
def chat(solicitud: Solicitud,
         llm: ClienteLLM = Depends(obtener_llm),
         repo: RepositorioHistorial = Depends(obtener_repositorio),
         limitador: LimitadorTasa = Depends(obtener_limitador)):
    limitador.verificar(solicitud.idSesion)
    historial = [{"role": t.rol, "content": t.contenido} for t in repo.ultimos_turnos(solicitud.idSesion)]
    try:
        r = llm.generar_json(cargar_prompt(PROMPT), delimitar_consulta(solicitud.texto),
                             RespuestaAsistente, historial)
        datos = r.datos
        repo.guardar(solicitud.idSesion, "user", solicitud.texto)
        repo.guardar(solicitud.idSesion, "assistant", datos.respuesta)
        return RespuestaChat(
            respuesta=datos.respuesta,
            se_abstiene=datos.se_abstiene,
            derivar_a=datos.derivar_a,
            fuentes=datos.fuentes,
            proveedor=r.proveedor,
        )
    except SalidaInvalida:
        return RespuestaChat(
            respuesta="No pudimos procesar la respuesta automáticamente. Por favor acuda al centro de salud más cercano ante cualquier síntoma de alarma o sospecha.",
            se_abstiene=True,
            derivar_a="Centro de Salud MSP",
            fuentes=[],
            proveedor=None,
        )


def check_health(readiness_probes: Optional[List[Callable[[], bool]]] = None) -> Tuple[Dict[str, Any], int]:
    """
    Evalúa el estado de salud de la aplicación (Liveness y Readiness).

    - Liveness: 'UP' si el proceso de la aplicación está activo y respondiendo.
    - Readiness: 'UP' si todas las sondas de preparación pasan con éxito; 'DOWN' si alguna falla.

    Retorna:
        Tuple[Dict[str, Any], int]: Estructura con el detalle del diagnóstico y código de estado HTTP (200 o 503).
    """
    liveness_status = "UP"

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
