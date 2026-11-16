"""Bucle del Agente de Alcance Controlado (Grupo 5: GuíaVital Dengue).

Implementa las tres decisiones en código (no en el prompt):
  1. Lista cerrada (PERMITIDAS): el modelo solo puede pedir funciones autorizadas.
  2. Tope de vueltas (MAX_ITER = 6): previene bucles infinitos y costos no controlados.
  3. Confirmación humana (REQUIEREN_OK): pausa el ciclo ante acciones que salen del sistema.
"""
from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Callable

from app.config import cargar_parametros
from app.schemas import Fuente
from app.services.llm import ClienteLLM
from app.tools.buscar_centro_salud import (
    ESQUEMA as ESQ_CENTROS,
    RUTA_GEOSALUD,
    BuscarCentroSaludIn,
    buscar_centro_salud,
)
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

_PATRON_SOLICITUD_CENTROS = re.compile(
    r"\b("
    r"centro\s+de\s+salud|centros\s+de\s+salud|"
    r"centro\s+medico|centros\s+medicos|"
    r"hospital|hospitales|clinica|subcentro|dispensario|establecimiento|establecimientos|"
    r"donde\s+(?:puedo\s+|debo\s+|podria\s+)?(?:acudir|ir|atenderme)|"
    r"a\s+donde\s+(?:puedo\s+|debo\s+|podria\s+)?(?:acudir|ir|atenderme)|"
    r"donde\s+voy|(?:puedo|debo)\s+(?:ir|acudir)|"
    r"me\s+atiend\w*|ser\s+atendid\w*|atencion\s+medica|"
    r"cercano|cercanos|cercana|cercanas|cerca\s+de|"
    r"ubicacion|direccion|direcciones|horario|horarios|servicio|servicios|"
    r"como\s+llegar|mapa|maps"
    r")\b"
)

_PATRON_SOLICITUD_NOTIF = re.compile(
    r"\b(notifica\w*|avisa\w*|alerta\w*|comunica\w*|envia\w*\s+un?\s*mensaje)\b.*"
    r"\b(contacto|familiar|hermano|hermana|mama|madre|papa|padre|esposo|esposa|emergencia|\d{7,15})\b",
    re.DOTALL,
)
_PATRON_DESTINATARIO = re.compile(r"(?:\+?593[\s.-]?|0)?9\d(?:[\s.-]?\d){7,8}\b|\b\d{7,15}\b")


def _normalizar_consulta(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFD", (texto or "").lower())
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")


def _usuario_solicita_centros(mensajes: list[dict[str, Any]]) -> bool:
    """Verifica deterministamente si en el último mensaje del usuario se solicitó información de centros médicos."""
    for m in reversed(mensajes):
        if m.get("role") == "user":
            contenido = _normalizar_consulta(str(m.get("content", "")))
            return bool(_PATRON_SOLICITUD_CENTROS.search(contenido))
    return False


def _detectar_ciudad_en_mensajes(mensajes: list[dict[str, Any]]) -> str | None:
    """Busca en los mensajes del usuario (del más reciente al más antiguo) si mencionó una ciudad o provincia de GeoSalud."""
    if not RUTA_GEOSALUD.exists():
        return None
    try:
        with open(RUTA_GEOSALUD, "r", encoding="utf-8") as f:
            centros = json.load(f)
    except Exception:
        return None

    localidades: list[str] = []
    for c in centros:
        for campo in ("ciudad", "provincia"):
            val = (c.get(campo) or "").strip()
            if val and val not in localidades:
                localidades.append(val)

    for m in reversed(mensajes):
        if m.get("role") == "user":
            texto_norm = _normalizar_consulta(str(m.get("content", "")))
            for loc in localidades:
                loc_norm = _normalizar_consulta(loc)
                if loc_norm and re.search(rf"\b{re.escape(loc_norm)}\b", texto_norm):
                    return loc
    return None


def _ya_uso_herramienta(mensajes: list[dict[str, Any]], nombre_herramienta: str) -> bool:
    """Verifica si una herramienta ya fue invocada en el historial de mensajes del turno actual."""
    for m in mensajes:
        if m.get("role") == "assistant" and m.get("tool_calls"):
            for tc in m["tool_calls"]:
                fn = tc.get("function", {}) if isinstance(tc, dict) else getattr(tc, "function", None)
                nombre = fn.get("name", "") if isinstance(fn, dict) else getattr(fn, "name", "")
                if nombre == nombre_herramienta:
                    return True
        if m.get("role") == "system" and f"[HITL_COMPLETADO:{nombre_herramienta}]" in str(m.get("content", "")):
            return True
    return False


def _extraer_solicitud_notificacion(mensajes: list[dict[str, Any]]) -> dict[str, str] | None:
    """Detecta deterministamente si el último mensaje del usuario pide notificar a un contacto de emergencia."""
    for m in reversed(mensajes):
        if m.get("role") == "user":
            raw = str(m.get("content", ""))
            norm = _normalizar_consulta(raw)
            if _PATRON_SOLICITUD_NOTIF.search(norm):
                m_dest = _PATRON_DESTINATARIO.search(raw)
                if m_dest:
                    return {
                        "destinatario": m_dest.group(0).strip(),
                        "mensaje": "Alerta de salud (GuíaVital): El paciente presenta signos de alarma y se dirige de urgencia al hospital.",
                    }
            break
    return None


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


def _asegurar_enlaces_centros(texto: str, centros: list[dict[str, Any]]) -> str:
    """Garantiza deterministamente que los centros encontrados incluyan dirección, servicios/horarios y enlace de Google Maps."""
    if not centros or "google.com/maps" in texto:
        return texto

    lineas_extra = ["\n\n### 📍 Establecimientos de salud, servicios, horarios y ubicación:"]
    for c in centros:
        nombre = c.get("nombre", "Centro de Salud MSP")
        direccion = c.get("direccion", "")
        ciudad = c.get("ciudad", "")
        telefonos = ", ".join(c.get("telefonos", [])) or "171"
        servicios = c.get("servicios_horarios", [])
        url = c.get("google_maps_url", "")

        lineas_extra.append(f"- **{nombre}** ({ciudad})")
        if direccion:
            lineas_extra.append(f"  - **Dirección:** {direccion}")
        if servicios:
            resumen_srv = "; ".join(
                f"{s.get('servicio', '')}: {s.get('dias', '')} ({s.get('horario', '')})"
                for s in servicios
            )
            lineas_extra.append(f"  - **Servicios y horarios:** {resumen_srv}")
        lineas_extra.append(f"  - **Teléfonos:** {telefonos}")
        if url:
            lineas_extra.append(f"  - **Ubicación:** [📍 Ver ubicación y navegar en Google Maps]({url})")

    return texto.rstrip() + "\n" + "\n".join(lineas_extra)


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
    centros_detectados: list[dict[str, Any]] = []

    for vuelta in range(vuelta_inicial, max_iter + 1):
        msg, proveedor, modelo = cliente.completar_con_herramientas(mensajes, tools=ESQUEMAS)

        # Si el modelo respondió con texto y sin llamadas a herramientas -> verificar HITL pendiente o meta cumplida
        tool_calls = getattr(msg, "tool_calls", None)
        if not tool_calls:
            # Si el ciudadano solicitó explícitamente dónde acudir / centros de salud pero el LLM solo llamó a RAG,
            # ejecutar deterministamente buscar_centro_salud para su ciudad
            if not centros_detectados and _usuario_solicita_centros(mensajes):
                ciudad_ctx = _detectar_ciudad_en_mensajes(mensajes)
                if ciudad_ctx:
                    res_geo = buscar_centro_salud(
                        BuscarCentroSaludIn(ciudad=ciudad_ctx, solo_emergencia_24h=False)
                    )
                    for c in res_geo.get("centros_cercanos", []):
                        if isinstance(c, dict):
                            centros_detectados.append(c)

            respuesta_limpia = _desempacar_respuesta(msg.content or "")
            respuesta_final = _asegurar_enlaces_centros(respuesta_limpia, centros_detectados)

            notif_pendiente = _extraer_solicitud_notificacion(mensajes)
            if notif_pendiente and not _ya_uso_herramienta(mensajes, "notificar_contacto_emergencia"):
                mensajes.append({
                    "role": "system",
                    "content": f"[HITL_COMPLETADO:notificar_contacto_emergencia] BORRADOR_ASISTENTE: {respuesta_final}",
                })
                return {
                    "estado": "requiere_confirmacion",
                    "tool_call_id": "call_notif_sintetico",
                    "nombre_herramienta": "notificar_contacto_emergencia",
                    "argumentos": notif_pendiente,
                    "vueltas": vuelta,
                    "mensajes": mensajes,
                    "fuentes": fuentes_detectadas,
                }

            return {
                "estado": "completado",
                "respuesta": respuesta_final,
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

        confirmacion_pendiente: dict[str, Any] | None = None

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

            # Verificación de confirmación humana: se registra para pausar tras resolver las demás herramientas del turno
            if nombre in REQUIEREN_OK and confirmacion_pendiente is None:
                confirmacion_pendiente = {
                    "estado": "requiere_confirmacion",
                    "tool_call_id": tc.id,
                    "nombre_herramienta": nombre,
                    "argumentos": args,
                    "vueltas": vuelta,
                    "mensajes": mensajes,
                    "fuentes": fuentes_detectadas,
                }
                continue

            # Ejecución determinista de herramienta libre
            if nombre == "buscar_centro_salud" and not _usuario_solicita_centros(mensajes):
                resultado = {
                    "omitido": True,
                    "mensaje": (
                        "El ciudadano solo mencionó su localidad pero NO solicitó información de centros médicos ni preguntó a dónde acudir. "
                        "NO muestres hospitales ni centros de salud en tu respuesta; responde únicamente a su consulta y "
                        "ofrécele amablemente consultar los centros de salud cercanos si lo necesita."
                    ),
                }
            else:
                try:
                    datos_validados = MODELOS_IN[nombre](**args)
                    resultado = PERMITIDAS[nombre](datos_validados)
                    # Acumular fuentes si vienen de consultar_guia_msp
                    if isinstance(resultado, dict) and "fuentes" in resultado:
                        for f in resultado["fuentes"]:
                            fuentes_detectadas.append(
                                Fuente(documento=f.get("documento", ""), seccion=f.get("seccion"))
                            )
                    # Acumular centros si vienen de buscar_centro_salud
                    if isinstance(resultado, dict) and "centros_cercanos" in resultado:
                        for c in resultado.get("centros_cercanos", []):
                            if isinstance(c, dict):
                                centros_detectados.append(c)
                except Exception as e:
                    resultado = {"error": f"Error validando argumentos: {str(e)}"}

            mensajes.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(resultado, default=str),
            })

        if confirmacion_pendiente is not None:
            return confirmacion_pendiente

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
    # Si provino del respaldo determinista HITL (sin tool_call nativo del LLM), resolver sin romper thought_signature
    if tool_call_id == "call_notif_sintetico":
        borrador = ""
        for m in reversed(mensajes):
            if m.get("role") == "system" and "BORRADOR_ASISTENTE: " in str(m.get("content", "")):
                borrador = str(m["content"]).split("BORRADOR_ASISTENTE: ", 1)[1].strip()
                break
        if aprobado:
            try:
                datos_validados = MODELOS_IN[accion_nombre](**argumentos)
                PERMITIDAS[accion_nombre](datos_validados)
                nota_accion = (
                    f"\n\n✅ **Notificación procesada:** Se ha registrado y enviado la alerta a tu contacto "
                    f"({argumentos.get('destinatario', '')})."
                )
            except Exception as e:
                nota_accion = f"\n\n⚠️ No se pudo completar la notificación: {str(e)}"
        else:
            nota_accion = "\n\nℹ️ **Acción cancelada:** La notificación al contacto de emergencia fue rechazada por el usuario."

        return {
            "estado": "completado",
            "respuesta": (borrador + nota_accion).strip(),
            "vueltas": vuelta_actual,
            "mensajes": mensajes,
            "fuentes": [],
        }

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
