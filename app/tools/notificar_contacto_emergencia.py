"""Herramienta Con Confirmación: Notifica a un contacto de emergencia (requiere confirmación humana)."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class NotificarContactoEmergenciaIn(BaseModel):
    destinatario: str = Field(min_length=5, description="Número de teléfono celular o correo electrónico del contacto de emergencia")
    mensaje: str = Field(description="Mensaje de alerta detallando los signos de alarma y el hospital al que se dirige el paciente")


def notificar_contacto_emergencia(datos: NotificarContactoEmergenciaIn) -> dict[str, Any]:
    """Acción que sale del sistema: solo se ejecuta cuando el humano dio clic en 'Aprobar'."""
    return {
        "estado": "enviado",
        "destinatario": datos.destinatario,
        "mensaje": "Alerta de signos de alarma de dengue transmitida con éxito al contacto.",
    }


ESQUEMA = {
    "type": "function",
    "function": {
        "name": "notificar_contacto_emergencia",
        "description": "Notifica a un familiar o contacto de emergencia sobre la situación de alarma de dengue del paciente. Requiere confirmación humana.",
        "parameters": NotificarContactoEmergenciaIn.model_json_schema(),
    },
}
