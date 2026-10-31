"""Pruebas unitarias de los endpoints v2 de app/main.py."""
from types import SimpleNamespace as NS
import pytest

from app.main import chat_v2, confirmar_accion_v2
from app.repositorio.historial import RepositorioHistorial
from app.schemas import EstadoAgente, Solicitud, SolicitudConfirmacion
from app.services.seguridad import LimitadorTasa


class LLMAgenteFalso:
    def __init__(self, respuestas):
        self.respuestas = respuestas
        self.llamadas = 0

    def completar_con_herramientas(self, mensajes, tools=None):
        resp = self.respuestas[self.llamadas]
        self.llamadas += 1
        return resp, "simulado", "simulado-1"


def test_chat_v2_respuesta_directa():
    repo = RepositorioHistorial(":memory:")
    limitador = LimitadorTasa(maximo=10, ventana_s=60)
    msg_final = NS(
        content="Orientación: manténgase hidratado y acuda a un centro de salud si presenta signos de alarma.",
        tool_calls=[],
    )
    llm = LLMAgenteFalso([msg_final])

    solicitud = Solicitud(idSesion="sesion-test-v2", texto="Hola, tengo fiebre alta desde ayer.")
    res = chat_v2(solicitud, llm=llm, repo=repo, limitador=limitador)

    assert res.idSesion == "sesion-test-v2"
    assert res.estado == EstadoAgente.COMPLETADO
    assert "hidratado" in res.respuesta
    assert res.vueltas_usadas == 1


def test_chat_v2_pausa_y_confirmacion():
    repo = RepositorioHistorial(":memory:")
    limitador = LimitadorTasa(maximo=10, ventana_s=60)

    # Vuelta 1: pide notificar_contacto_emergencia
    tc = NS(
        id="call_notif_123",
        function=NS(
            name="notificar_contacto_emergencia",
            arguments='{"destinatario": "0998765432", "mensaje": "Alerta dengue"}'
        ),
    )
    msg_con_tool = NS(content="", tool_calls=[tc])

    # Vuelta 2: tras confirmación, responde con texto
    msg_final = NS(content="Listo, he notificado a su familiar con los detalles de la alerta.", tool_calls=[])

    llm = LLMAgenteFalso([msg_con_tool, msg_final])

    # 1. Petición inicial a chat_v2
    solicitud = Solicitud(idSesion="sesion-confirmacion-1", texto="Por favor avisa a mi familiar 0998765432.")
    res1 = chat_v2(solicitud, llm=llm, repo=repo, limitador=limitador)

    assert res1.estado == EstadoAgente.REQUIERE_CONFIRMACION
    assert res1.accion_pendiente.nombre_herramienta == "notificar_contacto_emergencia"
    assert res1.accion_pendiente.tool_call_id == "call_notif_123"

    # 2. El usuario aprueba mediante confirmar_accion_v2
    confirmacion = SolicitudConfirmacion(
        idSesion="sesion-confirmacion-1",
        tool_call_id="call_notif_123",
        aprobado=True,
    )
    res2 = confirmar_accion_v2(confirmacion, llm=llm, repo=repo)

    assert res2.estado == EstadoAgente.COMPLETADO
    assert "notificado a su familiar" in res2.respuesta
