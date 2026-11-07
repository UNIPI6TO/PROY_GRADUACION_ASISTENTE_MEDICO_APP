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


def test_chat_v2_respuesta_con_citas_validadas(monkeypatch):
    """Verifica que el endpoint /api/v2/chat retorne las fuentes validadas en el esquema HTTP."""
    from app.schemas import Fuente
    from app.services import agent

    repo = RepositorioHistorial(":memory:")
    limitador = LimitadorTasa(maximo=10, ventana_s=60)

    def fake_consultar_guia_msp(_datos):
        return {
            "encontrado": True,
            "fragmentos": [{"texto": "La fase febril suele durar entre 2 y 7 días."}],
            "fuentes": [
                {
                    "documento": "Dengue: Guías para la atención de enfermos en la Región de las Américas (OPS, 2016)",
                    "seccion": "2.1 Fase febril",
                }
            ],
        }

    monkeypatch.setitem(agent.PERMITIDAS, "consultar_guia_msp", fake_consultar_guia_msp)

    tc_rag = NS(
        id="call_rag_99",
        function=NS(
            name="consultar_guia_msp",
            arguments='{"texto": "fase febril del dengue"}'
        ),
    )
    msg_rag = NS(content="", tool_calls=[tc_rag])
    msg_final = NS(content="La fase febril suele durar entre 2 y 7 días.", tool_calls=[])

    llm = LLMAgenteFalso([msg_rag, msg_final])
    solicitud = Solicitud(idSesion="sesion-cita-v2", texto="¿Cuánto dura la fiebre?")
    res = chat_v2(solicitud, llm=llm, repo=repo, limitador=limitador)

    assert res.estado == EstadoAgente.COMPLETADO
    assert len(res.fuentes) > 0
    assert all(isinstance(f, Fuente) for f in res.fuentes)
    assert res.fuentes[0].documento != ""
