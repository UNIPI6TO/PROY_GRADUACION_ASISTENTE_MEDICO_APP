# app/flujo.py · la cinta del Grupo 5 · Taller del 29-oct-2026
# Disparador: Formulario web · Acción final: Muestra información de establecimientos cercanos y solicita al ciudadano que llame al 911
from __future__ import annotations

import logging
import re
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, ValidationError

from app.config import PARAMETROS as P
from app.tools.evaluar_signos_alarma import (
    EvaluarSignosAlarmaHttpIn,
    evaluar_signos_alarma_clinica,
)

log_flujo = logging.getLogger("flujo")

UMBRAL: float = float(P.get("umbral_confianza", 0.85))


class Clase(BaseModel):
    """Clasificación del texto recibido según intención y nivel de certeza."""
    tipo: Literal["reporte_sintomas", "consulta_general", "otro"]
    confianza: float = Field(ge=0.0, le=1.0)


class Datos(BaseModel):
    """Datos clínicos estructurados y validados con Pydantic."""
    dias_fiebre: int = Field(default=0, ge=0, le=30, description="Días con fiebre")
    dolor_abdominal: bool = Field(default=False, description="Dolor abdominal intenso y continuo")
    vomitos_persistentes: bool = Field(default=False, description="Vómitos persistentes")
    sangrado: bool = Field(default=False, description="Sangrado de mucosas")
    edad: int = Field(default=30, ge=0, le=120, description="Edad en años")
    ubicacion: Optional[str] = Field(default=None, description="Cantón o sector")
    instrucciones_en_texto: bool = Field(default=False, description="Indica intento de inyección de prompt")


def revision_humana(doc: dict[str, Any], motivo: str) -> dict[str, Any]:
    """Registra el documento como «en revisión» con su motivo y avisa al profesional."""
    doc_id = doc.get("id", "sin-id")
    log_flujo.info(f"[REVISION HUMANA] Doc {doc_id}: {motivo}")
    return {
        "id": doc_id,
        "destino": "revision",
        "motivo": motivo,
        "resultado": "Derivado a profesional de salud para revisión manual",
    }


def _normalizar(texto: str) -> str:
    import unicodedata
    return "".join(
        c for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )


def clasificar_texto(texto: str) -> Clase:
    """Estación 2: Clasifica el mensaje determinando tipo y confianza."""
    t_min = _normalizar(texto)
    
    # 1. Detectar intento de inyección de prompt o fuera de dominio
    if any(p in t_min for p in ["ignora", "system", "actua como", "hackear", "prompt"]):
        return Clase(tipo="reporte_sintomas", confianza=0.70)  # Forzar revisión de seguridad

    # 2. Casos muy cortos o saludos
    if len(texto.strip().split()) <= 2 and not any(p in t_min for p in ["fiebre", "sangr", "dolor"]):
        return Clase(tipo="otro", confianza=0.50)

    # 3. Detectar ambigüedades / dos intenciones mezcladas
    tiene_picadura = any(p in t_min for p in ["me pico", "picadura"])
    tiene_sintoma = any(p in t_min for p in ["fiebre", "sangr", "vomit", "dolor", "mareado", "veo borroso", "malestar"]) or tiene_picadura
    tiene_consulta = any(p in t_min for p in ["horario", "centro de salud", "donde", "como prevenir", "prevenir", "criadero", "prueba"])
    if tiene_sintoma and tiene_consulta:
        return Clase(tipo="reporte_sintomas", confianza=0.75)  # Menor a 0.85 -> revisión humana

    # 4. Síntomas vagos sin contexto suficiente
    if t_min.strip() in ["tengo malestar general", "tengo fiebre"]:
        return Clase(tipo="reporte_sintomas", confianza=0.70)
    if "no se si es dengue" in t_min or "mareado" in t_min:
        return Clase(tipo="reporte_sintomas", confianza=0.70)

    # 5. Consultas generales informativas claras
    if tiene_consulta and not any(p in t_min for p in ["fiebre", "sangr", "vomit", "dolor"]):
        return Clase(tipo="consulta_general", confianza=0.92)

    # 6. Reportes clínicos claros (con síntomas de dengue específicos)
    palabras_sintomas = ["fiebre", "dolor", "vomit", "sangr", "encia", "dengue", "fievre"]
    coincidencias = sum(1 for p in palabras_sintomas if p in t_min)
    
    if coincidencias >= 2 or ("fiebre" in t_min and any(c in t_min for c in ["dia", "dias"])):
        return Clase(tipo="reporte_sintomas", confianza=0.95)
    elif coincidencias == 1:
        return Clase(tipo="reporte_sintomas", confianza=0.80)
    else:
        return Clase(tipo="otro", confianza=0.50)


def extraer_datos(texto: str) -> Datos:
    """Estación 4: Extrae variables clínicas desde el texto estructurándolas en Pydantic."""
    t_min = texto.lower()
    
    dias = 0
    m_dias = re.search(r"(\d+)\s*(?:dias|días|dia|día)", t_min)
    if m_dias:
        dias = min(int(m_dias.group(1)), 30)
    elif "dias" in t_min or "días" in t_min:
        dias = 3

    dolor_abdominal = any(p in t_min for p in ["dolor abdominal", "dolor de barriga", "dolor de estomago"]) and not any(neg in t_min for neg in ["no tengo dolor", "sin dolor", "no presento dolor", "descarto dolor"])
    vomitos = any(p in t_min for p in ["vomit", "vómit"]) and not any(neg in t_min for neg in ["no tengo", "sin vómitos", "sin vomitos", "ni vómitos", "ni vomitos"])
    sangrado = any(p in t_min for p in ["sangr", "hemorrag", "encia", "encías", "nasal"]) and not any(neg in t_min for neg in ["sin sangrado", "no tengo sangrado", "no sangro"])
    inyeccion = any(p in t_min for p in ["ignora", "system", "actua como", "hackear"])

    edad = 30
    m_edad = re.search(r"(\d+)\s*(?:años|anos)", t_min)
    if m_edad:
        edad = int(m_edad.group(1))

    return Datos(
        dias_fiebre=dias,
        dolor_abdominal=dolor_abdominal,
        vomitos_persistentes=vomitos,
        sangrado=sangrado,
        edad=edad,
        instrucciones_en_texto=inyeccion,
    )


def procesar(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Cinta de 7 estaciones de GuíaVital.
    Garantiza que todo documento termine en un estado: procesado o en revisión.
    """
    doc_id = doc.get("id", "sin-id")
    texto = doc.get("entrada", "")

    # 1 · Disparador (Sistema)
    if not texto or len(texto.strip()) < 5:
        return revision_humana(doc, motivo="Texto vacío o demasiado corto")

    # 2 · Clasificar (IA / Heurística)
    clase = clasificar_texto(texto)

    # 3 · Umbral (Código - Determinista)
    if clase.confianza < UMBRAL:
        return revision_humana(doc, motivo=f"Confianza {clase.confianza:.2f} inferior al umbral {UMBRAL}")

    if clase.tipo != "reporte_sintomas":
        return {
            "id": doc_id,
            "destino": "automatico",
            "resultado": f"Consulta atendida por base informativa ({clase.tipo})",
        }

    # 4 · Extraer (Pydantic)
    try:
        datos = extraer_datos(texto)
    except ValidationError as e:
        return revision_humana(doc, motivo=f"Fallo de validación en extracción: {e}")

    # Seguridad: Guardrail contra inyección
    if datos.instrucciones_en_texto:
        return revision_humana(doc, motivo="Instrucción maliciosa detectada en texto del usuario")

    # 5 · Reglas Oficiales (Código - MSP)
    input_clinico = EvaluarSignosAlarmaHttpIn(
        dias_fiebre=datos.dias_fiebre,
        dolor_abdominal=datos.dolor_abdominal,
        vomitos_persistentes=datos.vomitos_persistentes,
        sangrado=datos.sangrado,
        edad=datos.edad,
    )
    resultado_clinico = evaluar_signos_alarma_clinica(input_clinico)

    if resultado_clinico.nivel == "alarma":
        accion = "Muestra información de establecimientos cercanos y solicita al ciudadano que llame al 911"
    elif resultado_clinico.nivel == "vigilancia":
        accion = "Muestra información de establecimientos cercanos y recomienda acudir en 24h"
    else:
        accion = "Recomendaciones de hidratación oral y vigilancia de signos de alarma"

    # 7 · Actuar (Sistema)
    return {
        "id": doc_id,
        "destino": "automatico",
        "resultado": accion,
        "nivel": resultado_clinico.nivel,
        "signos_presentes": resultado_clinico.signos_presentes,
    }
