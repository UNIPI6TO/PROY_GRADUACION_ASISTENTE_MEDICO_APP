"""Esquemas (Pydantic) de lo que ENTRA al sistema y de lo que el MODELO debe devolver.

Reglas para que el esquema funcione con el modo estricto de Gemini y Groq:
  - extra="forbid" en cada modelo (no se aceptan campos inventados).
  - Todos los campos son obligatorios; si algo puede faltar, use `tipo | None`.
  - Nada de límites raros en el esquema (minLength, pattern…): esas reglas van en
    validadores de Python. El esquema GUÍA al modelo; la validación la hace su código.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Estricto(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ======================================================================
# EJEMPLO TRABAJADO · Caso 03 · Triaje de soporte (familia: automatización)
# ======================================================================
class Solicitud(BaseModel):
    """Lo que envía el usuario. Límite de tamaño = defensa contra consumo excesivo (OWASP LLM10)."""
    idSesion: str = Field(description="ID de la sesión del usuario")
    texto: str = Field(min_length=5, max_length=2000, description="Descripción del problema")


class Clasificacion(Estricto):
    """Lo que el MODELO debe devolver."""
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


PRIORIDAD = {  # decisión DETERMINISTA: la toma el código, no el modelo
    ("alto", "alta"): "P1", ("alto", "media"): "P2", ("medio", "alta"): "P2",
    ("alto", "baja"): "P3", ("medio", "media"): "P3", ("bajo", "alta"): "P3",
}


def calcular_prioridad(c: Clasificacion) -> str:
    return PRIORIDAD.get((c.impacto, c.urgencia), "P4")


class RespuestaClasificar(BaseModel):
    clasificacion: Clasificacion | None
    prioridad: str | None
    requiere_revision_humana: bool
    mensaje: str
    proveedor: str | None = None


# ======================================================================
# PUNTOS DE PARTIDA para las otras familias de casos (adáptelos a su caso)
# ======================================================================
class Fuente(Estricto):
    documento: str
    seccion: str | None


class RespuestaAsistente(Estricto):
    """Asistentes conversacionales · casos 01 Titulación, 05 Dengue, 09 Cacao.
    (En el chat normal use generar_stream; este esquema sirve si necesita la
    respuesta estructurada, por ejemplo para mostrar la abstención o la derivación.)"""
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


class Hallazgo(Estricto):
    titulo: str
    detalle: str
    gravedad: Literal["baja", "media", "alta"]


class AnalisisDocumento(Estricto):
    """Procesadores de documentos · casos 02 Reclamos, 06 Pliegos, 10 Código seguro."""
    resumen: str
    hallazgos: list[Hallazgo]
    datos_faltantes: list[str]
    advertencia: str | None = Field(description="Límites del análisis; no reemplaza a un profesional")


class Actividad(Estricto):
    hora: str = Field(description="HH:MM")
    lugar: str
    descripcion: str


class Dia(Estricto):
    numero: int
    actividades: list[Actividad]


class Plan(Estricto):
    """Planificadores · caso 04 Turismo.
    (07 Liquidaciones y 11 RIMPE: el modelo EXTRAE los datos; los CÁLCULOS van en código.)"""
    titulo: str
    dias: list[Dia]
    supuestos: list[str] = Field(description="Lo que el sistema asumió y el usuario debe confirmar")


class Opcion(Estricto):
    texto: str
    es_correcta: bool
    explicacion: str = Field(description="Por qué es correcta o incorrecta")


class Escenario(Estricto):
    """Simuladores · caso 08 Situaciones viales. La norma exacta (artículo y sanción)
    se consulta en las fuentes desde la semana 3; el modelo no debe inventarla."""
    situacion: str
    pregunta: str
    opciones: list[Opcion]
    advertencia: str | None = Field(description="Recordatorio de que es material educativo")
