"""Esquemas (Pydantic) de lo que ENTRA al sistema y de lo que el MODELO debe devolver.

Reglas para que el esquema funcione con el modo estricto de Gemini y Groq:
  - extra="forbid" en cada modelo (no se aceptan campos inventados).
  - Todos los campos son obligatorios; si algo puede faltar, use `tipo | None`.
  - Nada de límites raros en el esquema (minLength, pattern…): esas reglas van en
    validadores de Python. El esquema GUÍA al modelo; la validación la hace su código.
"""
from __future__ import annotations

import re
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Estricto(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ======================================================================
# ENTRADA
# ======================================================================
class Solicitud(BaseModel):
    """Lo que envía el usuario. Límite de tamaño = defensa contra consumo excesivo (OWASP LLM10)."""
    idSesion: str = Field(description="ID de la sesión del usuario (letras, números, '-' o '_', máx. 64)")
    texto: str = Field(min_length=5, max_length=2000, description="Consulta del usuario")

    @field_validator("idSesion")
    @classmethod
    def id_sesion_seguro(cls, v: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", v):
            raise ValueError("idSesion inválido")
        return v


# ======================================================================
# SOPORTE DE PRUEBAS DEL CLIENTE LLM
# ======================================================================
class Clasificacion(Estricto):
    """Esquema de ejemplo que SOLO usa tests/test_llm.py para probar ClienteLLM.
    No forma parte del dominio de GuíaVital."""
    es_soporte_tecnologico: bool = Field(description="false si la solicitud no es de soporte TI")
    categoria: Literal["hardware", "software", "red", "accesos", "otro"]
    impacto: Literal["bajo", "medio", "alto"] = Field(description="A cuántas personas o procesos afecta")
    urgencia: Literal["baja", "media", "alta"] = Field(description="Qué tan pronto hay que resolverlo")
    resumen: str = Field(description="Una sola oración, sin datos personales")
    datos_faltantes: list[str] = Field(description="Qué habría que preguntarle al usuario; lista vacía si nada")

    @field_validator("resumen")
    @classmethod
    def resumen_corto(cls, v: str) -> str:
        if len(v) > 300:
            raise ValueError("el resumen debe tener máximo 300 caracteres")
        return v


# ======================================================================
# SALIDA DEL MODELO Y RESPUESTA AL CLIENTE
# ======================================================================
class Fuente(Estricto):
    documento: str
    seccion: str | None


class RespuestaAsistente(Estricto):
    """Asistente conversacional · caso 05 Dengue.
    Respuesta estructurada para mostrar la abstención o la derivación."""
    respuesta: str
    se_abstiene: bool = Field(description="true si la información no está en sus fuentes")
    derivar_a: str | None = Field(description="Persona u oficina a la que debe acudir, si aplica")
    fuentes: list[Fuente] = Field(description="Vacía en la semana 2; con citas desde la semana 3")


class RespuestaChat(BaseModel):
    """Respuesta completa del endpoint de chat hacia el cliente/frontend."""
    respuesta: str
    se_abstiene: bool
    derivar_a: str | None = None
    fuentes: list[Fuente] = Field(default_factory=list)
    proveedor: str | None = None


# ======================================================================
# HISTORIAL Y ERRORES
# ======================================================================
class TurnoHistorial(BaseModel):
    """Un mensaje guardado en SQLite."""
    id_sesion: str
    rol: Literal["user", "assistant"]
    contenido: str
    creado_en: str | None = None


class ProblemaRFC9457(BaseModel):
    """Formato de error estándar (Problem Details for HTTP APIs)."""
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None


# ======================================================================
# AGENTE DE ALCANCE CONTROLADO (SEMANA 3 / V2)
# ======================================================================
class EstadoAgente(str, Enum):
    COMPLETADO = "completado"
    REQUIERE_CONFIRMACION = "requiere_confirmacion"
    TOPE_ALCANZADO = "tope_alcanzado"


class AccionPendiente(BaseModel):
    tool_call_id: str
    nombre_herramienta: str
    argumentos: dict[str, Any]
    advertencia: str = "Esta acción requiere autorización humana explícita antes de ejecutarse."


class RespuestaChatV2(BaseModel):
    idSesion: str
    estado: EstadoAgente
    respuesta: str | None = None
    accion_pendiente: AccionPendiente | None = None
    fuentes: list[Fuente] = Field(default_factory=list)
    vueltas_usadas: int = 1


class SolicitudConfirmacion(BaseModel):
    idSesion: str
    tool_call_id: str
    aprobado: bool

