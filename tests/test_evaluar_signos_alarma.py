"""Pruebas unitarias para la herramienta evaluar_signos_alarma."""
import pytest
from app.tools.evaluar_signos_alarma import evaluar_signos_alarma, EvaluarSignosAlarmaIn


def test_sin_signos_de_alarma():
    datos = EvaluarSignosAlarmaIn(sintomas=["dolor de cabeza leve", "malestar general", "fiebre moderada"])
    res = evaluar_signos_alarma(datos)
    assert res["tiene_signos_alarma"] is False
    assert res["gravedad"] == "observacion_ambulatoria"
    assert len(res["signos_detectados"]) == 0


def test_con_signos_de_alarma_criticos():
    datos = EvaluarSignosAlarmaIn(sintomas=["tengo dolor abdominal intenso y continuo", "vomitos persistentes"])
    res = evaluar_signos_alarma(datos)
    assert res["tiene_signos_alarma"] is True
    assert res["gravedad"] == "urgente"
    assert "dolor abdominal intenso y continuo" in res["signos_detectados"]
    assert "vomitos persistentes" in res["signos_detectados"]


def test_es_determinista():
    datos = EvaluarSignosAlarmaIn(sintomas=["sangrado de mucosas"])
    assert evaluar_signos_alarma(datos) == evaluar_signos_alarma(datos)


def test_sinonimo_coloquial_me_sangran_las_encias():
    """Verifica que el sinónimo coloquial «me sangran las encías» active sangrado de mucosas sin UnboundLocalError."""
    datos = EvaluarSignosAlarmaIn(sintomas=["tengo fiebre y me sangran las encias"])
    res = evaluar_signos_alarma(datos)
    assert res["tiene_signos_alarma"] is True
    assert res["gravedad"] == "urgente"
    assert "sangrado de mucosas" in res["signos_detectados"]


def test_sinonimos_coloquiales_multiples():
    """Verifica que expresiones populares activen las categorías oficiales del MSP."""
    datos = EvaluarSignosAlarmaIn(sintomas=["dolor de barriga fuerte", "no paro de vomitar", "me falta el aire"])
    res = evaluar_signos_alarma(datos)
    assert res["tiene_signos_alarma"] is True
    assert "dolor abdominal intenso y continuo" in res["signos_detectados"]
    assert "vomitos persistentes" in res["signos_detectados"]
    assert "dificultad respiratoria" in res["signos_detectados"]
