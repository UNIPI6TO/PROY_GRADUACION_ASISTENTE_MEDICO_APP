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
