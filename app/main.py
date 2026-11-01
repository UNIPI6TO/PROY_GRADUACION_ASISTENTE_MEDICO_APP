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
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.repositorio.historial import RepositorioHistorial
from app.schemas import (
    AccionPendiente,
    EstadoAgente,
    ProblemaRFC9457,
    RespuestaAsistente,
    RespuestaChat,
    RespuestaChatV2,
    Solicitud,
    SolicitudConfirmacion,
)
from app.services.agent import ejecutar_bucle_agente, reanudar_agente
from app.services.llm import ClienteLLM, ProveedorNoDisponible, SalidaInvalida, cargar_prompt
from app.services.seguridad import LimiteExcedido, LimitadorTasa, delimitar_consulta
from app.tools.evaluar_signos_alarma import (
    EvaluarSignosAlarmaHttpIn,
    EvaluarSignosAlarmaHttpOut,
    evaluar_signos_alarma_clinica,
)

APP_NAME = "GuíaVital"
APP_VERSION = "0.2.0-SNAPSHOT-RC1"
SEMVER_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

PROMPT = "system_v4"

log_app = logging.getLogger("app")

app = FastAPI(
    title="GuíaVital - Asistente de Orientación en Salud Pública sobre Dengue",
    description="API Backend para orientación preventiva y triaje de signos de alarma en dengue.",
    version=APP_VERSION,
)

# CORS: permitir orígenes locales de desarrollo y los declarados en CORS_ORIGINS
ORIGENES_LOCALES = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:8501",
]
origenes_env = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
origenes_permitidos = list(dict.fromkeys(ORIGENES_LOCALES + origenes_env))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
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
    # Para los endpoints de herramientas (Semana 3), devolver el formato estándar de Pydantic (loc, type, msg, input)
    if request.url.path.startswith("/herramientas"):
        return await request_validation_exception_handler(request, exc)

    # Para los endpoints de chat (/api/...), mantener el formato RFC 9457 con mensajes amigables en español
    mensajes_amigables: list[str] = []
    for err in exc.errors():
        campo = ".".join(str(l) for l in err.get("loc", [])[1:])
        tipo = err.get("type", "")
        if campo == "texto":
            if "too_short" in tipo:
                mensajes_amigables.append(
                    "Tu consulta es muy breve. Por favor, escribe al menos 5 caracteres describiendo tu duda o los síntomas que deseas consultar."
                )
            elif "too_long" in tipo:
                mensajes_amigables.append(
                    "Tu consulta supera el límite máximo de 2000 caracteres. Por favor, resúmela para poder orientarte mejor."
                )
            else:
                mensajes_amigables.append(
                    "Por favor, ingresa un texto de consulta válido (entre 5 y 2000 caracteres)."
                )
        elif campo == "idSesion":
            mensajes_amigables.append(
                "No se pudo validar la sesión actual. Por favor, inicia una 'Nueva consulta' o recarga la página."
            )
        else:
            mensajes_amigables.append(f"{campo}: {err.get('msg', 'Valor inválido')}")

    detalle_final = " ".join(mensajes_amigables) if mensajes_amigables else "Por favor, verifica el texto de tu consulta antes de enviarla."
    return _problema(422, "Solicitud inválida", detalle_final, request)


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


# Almacén en memoria de turnos pausados para confirmación humana (por idSesion)
_ACCIONES_PENDIENTES: dict[str, dict[str, Any]] = {}


@app.post("/api/v2/chat", response_model=RespuestaChatV2, tags=["Asistente v2 (Agente)"],
          responses={422: {"model": ProblemaRFC9457}, 429: {"model": ProblemaRFC9457},
                     503: {"model": ProblemaRFC9457}})
def chat_v2(solicitud: Solicitud,
            llm: ClienteLLM = Depends(obtener_llm),
            repo: RepositorioHistorial = Depends(obtener_repositorio),
            limitador: LimitadorTasa = Depends(obtener_limitador)):
    """Endpoint v2: Agente de alcance controlado con Function Calling, RAG y límites estrictos."""
    limitador.verificar(solicitud.idSesion)

    mensajes: list[dict[str, Any]] = [
        {"role": "system", "content": cargar_prompt("system_agente")}
    ]
    for t in repo.ultimos_turnos(solicitud.idSesion):
        mensajes.append({"role": t.rol, "content": t.contenido})
    mensajes.append({"role": "user", "content": delimitar_consulta(solicitud.texto)})

    res = ejecutar_bucle_agente(mensajes, cliente_llm=llm)

    if res["estado"] == "requiere_confirmacion":
        _ACCIONES_PENDIENTES[solicitud.idSesion] = {
            "mensajes": res["mensajes"],
            "tool_call_id": res["tool_call_id"],
            "nombre_herramienta": res["nombre_herramienta"],
            "argumentos": res["argumentos"],
            "vueltas": res["vueltas"],
            "texto_usuario": solicitud.texto,
        }
        return RespuestaChatV2(
            idSesion=solicitud.idSesion,
            estado=EstadoAgente.REQUIERE_CONFIRMACION,
            accion_pendiente=AccionPendiente(
                tool_call_id=res["tool_call_id"],
                nombre_herramienta=res["nombre_herramienta"],
                argumentos=res["argumentos"],
            ),
            fuentes=res.get("fuentes", []),
            vueltas_usadas=res["vueltas"],
        )

    # El ciclo concluyó (completado o tope alcanzado)
    _ACCIONES_PENDIENTES.pop(solicitud.idSesion, None)
    repo.guardar(solicitud.idSesion, "user", solicitud.texto)
    repo.guardar(solicitud.idSesion, "assistant", res["respuesta"])

    estado_final = EstadoAgente.COMPLETADO if res["estado"] == "completado" else EstadoAgente.TOPE_ALCANZADO
    return RespuestaChatV2(
        idSesion=solicitud.idSesion,
        estado=estado_final,
        respuesta=res["respuesta"],
        fuentes=res.get("fuentes", []),
        vueltas_usadas=res["vueltas"],
    )


@app.post("/api/v2/chat/confirmar", response_model=RespuestaChatV2, tags=["Asistente v2 (Agente)"],
          responses={422: {"model": ProblemaRFC9457}, 429: {"model": ProblemaRFC9457},
                     503: {"model": ProblemaRFC9457}})
def confirmar_accion_v2(confirmacion: SolicitudConfirmacion,
                        llm: ClienteLLM = Depends(obtener_llm),
                        repo: RepositorioHistorial = Depends(obtener_repositorio)):
    """Reanuda la ejecución del agente tras la decisión humana (Aprobar / Rechazar)."""
    pendiente = _ACCIONES_PENDIENTES.pop(confirmacion.idSesion, None)
    if not pendiente or pendiente["tool_call_id"] != confirmacion.tool_call_id:
        return _problema(422, "Acción no encontrada", "No hay una acción pendiente de confirmación con ese identificador.", Request({"type": "http", "path": "/api/v2/chat/confirmar"}))

    res = reanudar_agente(
        mensajes=pendiente["mensajes"],
        tool_call_id=confirmacion.tool_call_id,
        aprobado=confirmacion.aprobado,
        accion_nombre=pendiente["nombre_herramienta"],
        argumentos=pendiente["argumentos"],
        cliente_llm=llm,
        vuelta_actual=pendiente["vueltas"],
    )

    if res["estado"] == "requiere_confirmacion":
        _ACCIONES_PENDIENTES[confirmacion.idSesion] = {
            "mensajes": res["mensajes"],
            "tool_call_id": res["tool_call_id"],
            "nombre_herramienta": res["nombre_herramienta"],
            "argumentos": res["argumentos"],
            "vueltas": res["vueltas"],
            "texto_usuario": pendiente.get("texto_usuario", ""),
        }
        return RespuestaChatV2(
            idSesion=confirmacion.idSesion,
            estado=EstadoAgente.REQUIERE_CONFIRMACION,
            accion_pendiente=AccionPendiente(
                tool_call_id=res["tool_call_id"],
                nombre_herramienta=res["nombre_herramienta"],
                argumentos=res["argumentos"],
            ),
            fuentes=res.get("fuentes", []),
            vueltas_usadas=res["vueltas"],
        )

    # Finalizado
    texto_orig = pendiente.get("texto_usuario", "")
    if texto_orig:
        repo.guardar(confirmacion.idSesion, "user", texto_orig)
    repo.guardar(confirmacion.idSesion, "assistant", res["respuesta"])

    estado_final = EstadoAgente.COMPLETADO if res["estado"] == "completado" else EstadoAgente.TOPE_ALCANZADO
    return RespuestaChatV2(
        idSesion=confirmacion.idSesion,
        estado=estado_final,
        respuesta=res["respuesta"],
        fuentes=res.get("fuentes", []),
        vueltas_usadas=res["vueltas"],
    )


@app.post(
    "/herramientas/signos-alarma",
    response_model=EvaluarSignosAlarmaHttpOut,
    tags=["Herramientas Deterministas"],
    status_code=200,
)
def endpoint_signos_alarma(datos: EvaluarSignosAlarmaHttpIn) -> EvaluarSignosAlarmaHttpOut:
    """Endpoint oficial Semana 3: Evaluación determinista de signos de alarma con parámetros del MSP."""
    return evaluar_signos_alarma_clinica(datos)


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
