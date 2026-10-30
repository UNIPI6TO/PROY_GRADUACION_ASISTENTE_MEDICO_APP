"""Herramienta Libre: Evaluación determinista de signos de alarma de dengue."""
from __future__ import annotations

import unicodedata
from typing import Any
from pydantic import BaseModel, Field

from app.config import cargar_parametros


class EvaluarSignosAlarmaIn(BaseModel):
    sintomas: list[str] = Field(description="Lista de síntomas reportados por el paciente")


def _normalizar(texto: str) -> str:
    """Elimina tildes, caracteres especiales y convierte a minúsculas."""
    return "".join(
        c for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )


def evaluar_signos_alarma(datos: EvaluarSignosAlarmaIn) -> dict[str, Any]:
    """Compara deterministamente los síntomas del paciente contra los signos de alarma oficiales."""
    params = cargar_parametros().get("signos_alarma", {})
    lista_oficial = [_normalizar(s) for s in params.get("lista_oficial", [])]

    detectados: list[str] = []
    for sintoma in datos.sintomas:
        s_norm = _normalizar(sintoma)
        for oficial in lista_oficial:
            # Coincidencia si el síntoma contiene el signo o el signo contiene el síntoma relevante
            if oficial in s_norm or (len(s_norm) > 4 and s_norm in oficial):
                detectados.append(oficial)
                break

    detectados_unicos = sorted(list(set(detectados)))
    tiene_alarma = len(detectados_unicos) > 0

    return {
        "tiene_signos_alarma": tiene_alarma,
        "signos_detectados": detectados_unicos,
        "gravedad": "urgente" if tiene_alarma else "observacion_ambulatoria",
        "accion_recomendada": (
            "Acudir de inmediato al centro de salud u hospital más cercano sin automedicarse."
            if tiene_alarma
            else "Mantener hidratación oral continua y vigilar la aparición de nuevos signos de alarma."
        ),
    }


class EvaluarSignosAlarmaHttpIn(BaseModel):
    dias_fiebre: int = Field(ge=0, le=30, description="Días con fiebre")
    dolor_abdominal: bool = Field(description="Dolor abdominal intenso y continuo")
    vomitos_persistentes: bool = Field(description="Vómitos persistentes")
    sangrado: bool = Field(description="Sangrado de mucosas")
    edad: int = Field(ge=0, le=120, description="Edad en años")


class EvaluarSignosAlarmaHttpOut(BaseModel):
    signos_presentes: int
    nivel: str
    recomendacion: str
    fuente: str


def evaluar_signos_alarma_clinica(d: EvaluarSignosAlarmaHttpIn) -> EvaluarSignosAlarmaHttpOut:
    """Evaluación clínica determinista según la Guía de Dengue del MSP para el endpoint HTTP."""
    params = cargar_parametros()
    umbral_dias = params.get("umbral_dias_fiebre", params.get("signos_alarma", {}).get("umbral_dias", 3))
    fuente = params.get("signos_alarma", {}).get("fuente", "Guía de dengue del MSP, sección signos de alarma")

    signos = sum([d.dolor_abdominal, d.vomitos_persistentes, d.sangrado])
    if signos >= 1:
        nivel, rec = "alarma", "Acudir hoy al centro de salud más cercano"
    elif d.dias_fiebre >= umbral_dias:
        nivel, rec = "vigilancia", "Control médico en 24 horas e hidratación"
    else:
        nivel, rec = "sin_alarma", "Hidratación y control de la fiebre; volver si aparece un signo"

    return EvaluarSignosAlarmaHttpOut(
        signos_presentes=signos,
        nivel=nivel,
        recomendacion=rec,
        fuente=fuente,
    )


ESQUEMA = {
    "type": "function",
    "function": {
        "name": "evaluar_signos_alarma",
        "description": "Compara deterministamente los síntomas del paciente contra la lista oficial de signos de alarma de dengue del MSP.",
        "parameters": EvaluarSignosAlarmaIn.model_json_schema(),
    },
}
