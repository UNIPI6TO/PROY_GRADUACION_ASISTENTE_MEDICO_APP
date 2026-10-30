"""Pruebas unitarias para el bucle del Agente de Alcance Controlado (app/services/agent.py)."""
from unittest.mock import MagicMock
import pytest

from app.services.agent import ejecutar_bucle_agente, reanudar_agente


class MensajeMock:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class ToolCallMock:
    def __init__(self, call_id, nombre, arguments):
        self.id = call_id
        self.function = MagicMock()
        self.function.name = nombre
        self.function.arguments = arguments


def test_camino_feliz_sin_herramientas():
    mock_llm = MagicMock()
    mock_llm.completar_con_herramientas.return_value = (
        MensajeMock(content="Recomiendo reposo e hidratación abundante."),
        "simulado",
        "modelo-1",
    )
    mensajes = [{"role": "user", "content": "Tengo fiebre hace 2 días."}]
    res = ejecutar_bucle_agente(mensajes, cliente_llm=mock_llm)

    assert res["estado"] == "completado"
    assert "reposo e hidratación" in res["respuesta"]
    assert res["vueltas"] == 1


def test_lista_cerrada_rechaza_herramienta_no_permitida():
    mock_llm = MagicMock()
    # Vuelta 1: pide 'diagnosticar' (herramienta fuera de la lista)
    # Vuelta 2: responde con texto tras recibir el error
    tc_prohibida = ToolCallMock("call_1", "diagnosticar", '{"enfermedad": "dengue hemorragico"}')
    mock_llm.completar_con_herramientas.side_effect = [
        (MensajeMock(content="", tool_calls=[tc_prohibida]), "simulado", "modelo-1"),
        (MensajeMock(content="Solo puedo orientar sobre signos de alarma, no diagnosticar."), "simulado", "modelo-1"),
    ]

    mensajes = [{"role": "user", "content": "Dime exactamente si tengo dengue grave."}]
    res = ejecutar_bucle_agente(mensajes, cliente_llm=mock_llm)

    assert res["estado"] == "completado"
    # Verificar que en los mensajes de tool se incluyó el error de herramienta no permitida
    assert any("no permitida" in m.get("content", "") for m in mensajes if m.get("role") == "tool")
    assert res["vueltas"] == 2


def test_tope_de_vueltas_alcanzado():
    mock_llm = MagicMock()
    # Simula un modelo que insiste en llamar a una herramienta que falla en cada vuelta
    tc = ToolCallMock("call_loop", "evaluar_signos_alarma", '{"sintomas": ["fiebre"]}')
    mock_llm.completar_con_herramientas.return_value = (
        MensajeMock(content="", tool_calls=[tc]),
        "simulado",
        "modelo-1",
    )

    mensajes = [{"role": "user", "content": "Evalúa mis síntomas en bucle."}]
    res = ejecutar_bucle_agente(mensajes, cliente_llm=mock_llm)

    assert res["estado"] == "tope_alcanzado"
    assert res["vueltas"] == 6
    assert "No puedo resolver la consulta completamente" in res["respuesta"]


def test_confirmacion_humana_pausa_y_reanuda():
    mock_llm = MagicMock()
    tc_notif = ToolCallMock(
        "call_notif",
        "notificar_contacto_emergencia",
        '{"destinatario": "0991234567", "mensaje": "Paciente con sangrado"}'
    )
    mock_llm.completar_con_herramientas.return_value = (
        MensajeMock(content="", tool_calls=[tc_notif]),
        "simulado",
        "modelo-1",
    )

    mensajes = [{"role": "user", "content": "Avisa a mi familiar."}]
    res_pausa = ejecutar_bucle_agente(mensajes, cliente_llm=mock_llm)

    assert res_pausa["estado"] == "requiere_confirmacion"
    assert res_pausa["nombre_herramienta"] == "notificar_contacto_emergencia"
    assert res_pausa["tool_call_id"] == "call_notif"

    # Ahora el humano aprueba la acción
    mock_llm.completar_con_herramientas.return_value = (
        MensajeMock(content="Se ha notificado a su contacto de emergencia con éxito."),
        "simulado",
        "modelo-1",
    )
    res_final = reanudar_agente(
        mensajes=res_pausa["mensajes"],
        tool_call_id="call_notif",
        aprobado=True,
        accion_nombre="notificar_contacto_emergencia",
        argumentos={"destinatario": "0991234567", "mensaje": "Paciente con sangrado"},
        cliente_llm=mock_llm,
        vuelta_actual=res_pausa["vueltas"],
    )

    assert res_final["estado"] == "completado"
    assert "notificado a su contacto" in res_final["respuesta"]
