"""Bucle del Agente de Alcance Controlado (Grupo 5: GuíaVital Dengue).

Implementa las tres decisiones en código (no en el prompt):
  1. Lista cerrada (PERMITIDAS): el modelo solo puede pedir funciones autorizadas.
  2. Tope de vueltas (MAX_ITER = 6): previene bucles infinitos y costos no controlados.
  3. Confirmación humana (REQUIEREN_OK): pausa el ciclo ante acciones que salen del sistema.
"""
from __future__ import annotations

import json
import re
from typing import Any, Callable

from app.config import cargar_parametros
from app.schemas import Fuente
from app.services.llm import ClienteLLM
from app.tools.buscar_centro_salud import ESQUEMA as ESQ_CENTROS, BuscarCentroSaludIn, buscar_centro_salud
from app.tools.consultar_guia_msp import ESQUEMA as ESQ_MSP, ConsultarGuiaMspIn, consultar_guia_msp
from app.tools.evaluar_signos_alarma import ESQUEMA as ESQ_ALARMA, EvaluarSignosAlarmaIn, evaluar_signos_alarma
from app.tools.notificar_contacto_emergencia import (
    ESQUEMA as ESQ_NOTIF,
    NotificarContactoEmergenciaIn,
    notificar_contacto_emergencia,
)

# 1. Lista cerrada
PERMITIDAS: dict[str, Callable[[Any], dict[str, Any]]] = {
    "consultar_guia_msp": consultar_guia_msp,
    "evaluar_signos_alarma": evaluar_signos_alarma,
    "buscar_centro_salud": buscar_centro_salud,
    "notificar_contacto_emergencia": notificar_contacto_emergencia,
}

MODELOS_IN = {
    "consultar_guia_msp": ConsultarGuiaMspIn,
    "evaluar_signos_alarma": EvaluarSignosAlarmaIn,
    "buscar_centro_salud": BuscarCentroSaludIn,
    "notificar_contacto_emergencia": NotificarContactoEmergenciaIn,
}

ESQUEMAS = [ESQ_MSP, ESQ_ALARMA, ESQ_CENTROS, ESQ_NOTIF]

# 2. Confirmación humana requerida
REQUIEREN_OK = {"notificar_contacto_emergencia"}


def _desempacar_respuesta(texto: str) -> str:
    """Extrae texto conversacional limpio si el modelo envolvió la salida en JSON."""
    t = (texto or "").strip()
    if t.startswith("```"):
        m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, re.DOTALL)
        if m:
            t = m.group(1).strip()
    if t.startswith("{") and t.endswith("}"):
        try:
            datos = json.loads(t)
            if isinstance(datos, dict) and "respuesta" in datos:
                return str(datos["respuesta"]).strip()
        except Exception:
            pass
    return t


def ejecutar_bucle_agente(
    mensajes: list[dict[str, Any]],
    cliente_llm: ClienteLLM | None = None,
    vuelta_inicial: int = 1,
) -> dict[str, Any]:
    """Ejecuta el ciclo de razonamiento y acción del agente con límites estrictos."""
    params = cargar_parametros().get("agente", {})
    max_iter = params.get("max_iter", 6)
    mensaje_tope = params.get(
        "mensaje_tope",
        "No puedo resolver la consulta completamente. Por favor acuda al centro de salud más cercano o llame al 911.",
    )

    cliente = cliente_llm or ClienteLLM()
    fuentes_detectadas: list[Fuente] = []

    for vuelta in range(vuelta_inicial, max_iter + 1):
        msg, proveedor, modelo = cliente.completar_con_herramientas(mensajes, tools=ESQUEMAS)

        # Si el modelo respondió con texto y sin llamadas a herramientas -> meta cumplida
        tool_calls = getattr(msg, "tool_calls", None)
        if not tool_calls:
            return {
                "estado": "completado",
                "respuesta": _desempacar_respuesta(msg.content or ""),
                "vueltas": vuelta,
                "mensajes": mensajes,
                "fuentes": fuentes_detectadas,
                "proveedor": proveedor,
            }

        # Serializar mensaje del asistente con las llamadas preservando metadatos (ej. extra_content / thought_signature)
        tool_calls_dict = []
        for tc in tool_calls:
            if hasattr(tc, "model_dump"):
                tc_dict = tc.model_dump(exclude_none=True)
            elif isinstance(tc, dict):
                tc_dict = dict(tc)
            else:
                tc_dict = {
                    "id": getattr(tc, "id", None),
                    "type": getattr(tc, "type", "function"),
                    "function": {
                        "name": getattr(tc.function, "name", ""),
                        "arguments": getattr(tc.function, "arguments", ""),
                    },
                }
            tool_calls_dict.append(tc_dict)

        mensajes.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": tool_calls_dict,
        })

        for tc in tool_calls:
            nombre = tc.function.name
            try:
                args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
            except Exception:
                args = {}

            # Validación de lista cerrada
            if nombre not in PERMITIDAS:
                mensajes.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps({"error": f"Herramienta '{nombre}' no permitida"}),
                })
                continue

            # Verificación de confirmación humana
            if nombre in REQUIEREN_OK:
                return {
                    "estado": "requiere_confirmacion",
                    "tool_call_id": tc.id,
                    "nombre_herramienta": nombre,
                    "argumentos": args,
                    "vueltas": vuelta,
                    "mensajes": mensajes,
                    "fuentes": fuentes_detectadas,
                }

            # Ejecución determinista de herramienta libre
            try:
                datos_validados = MODELOS_IN[nombre](**args)
                resultado = PERMITIDAS[nombre](datos_validados)
                # Acumular fuentes si vienen de consultar_guia_msp
                if isinstance(resultado, dict) and "fuentes" in resultado:
                    for f in resultado["fuentes"]:
                        fuentes_detectadas.append(
                            Fuente(documento=f.get("documento", ""), seccion=f.get("seccion"))
                        )
            except Exception as e:
                resultado = {"error": f"Error validando argumentos: {str(e)}"}

            mensajes.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(resultado, default=str),
            })

    # Si se superó el número de iteraciones
    return {
        "estado": "tope_alcanzado",
        "respuesta": mensaje_tope,
        "vueltas": max_iter,
        "mensajes": mensajes,
        "fuentes": fuentes_detectadas,
    }


def reanudar_agente(
    mensajes: list[dict[str, Any]],
    tool_call_id: str,
    aprobado: bool,
    accion_nombre: str,
    argumentos: dict[str, Any],
    cliente_llm: ClienteLLM | None = None,
    vuelta_actual: int = 1,
) -> dict[str, Any]:
    """Reanuda el agente tras la decisión humana de aprobar o rechazar la acción."""
    if not aprobado:
        mensajes.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps({"rechazado_por_el_usuario": True}),
        })
    else:
        try:
            datos_validados = MODELOS_IN[accion_nombre](**argumentos)
            res = PERMITIDAS[accion_nombre](datos_validados)
        except Exception as e:
            res = {"error": f"Error al ejecutar acción aprobada: {str(e)}"}

        mensajes.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(res, default=str),
        })

    # Continúa el bucle desde la siguiente vuelta
    return ejecutar_bucle_agente(mensajes, cliente_llm=cliente_llm, vuelta_inicial=vuelta_actual + 1)
