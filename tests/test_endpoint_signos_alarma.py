"""Pruebas unitarias para el endpoint y lógica de evaluar_signos_alarma."""
import pytest
from pydantic import ValidationError

from app.main import endpoint_signos_alarma
from app.tools.evaluar_signos_alarma import (
    EvaluarSignosAlarmaHttpIn,
    EvaluarSignosAlarmaHttpOut,
    evaluar_signos_alarma_clinica,
)

VALIDO_ALARMA = {
    "dias_fiebre": 4,
    "dolor_abdominal": True,
    "vomitos_persistentes": False,
    "sangrado": False,
    "edad": 34,
}

VALIDO_VIGILANCIA = {
    "dias_fiebre": 4,
    "dolor_abdominal": False,
    "vomitos_persistentes": False,
    "sangrado": False,
    "edad": 25,
}

VALIDO_SIN_ALARMA = {
    "dias_fiebre": 2,
    "dolor_abdominal": False,
    "vomitos_persistentes": False,
    "sangrado": False,
    "edad": 30,
}


def test_endpoint_responde_con_signos_de_alarma():
    datos = EvaluarSignosAlarmaHttpIn(**VALIDO_ALARMA)
    res = endpoint_signos_alarma(datos)
    assert res.nivel == "alarma"
    assert res.signos_presentes == 1
    assert "Acudir hoy al centro de salud" in res.recomendacion
    assert "MSP" in res.fuente or "dengue" in res.fuente.lower()


def test_endpoint_responde_con_fase_vigilancia():
    datos = EvaluarSignosAlarmaHttpIn(**VALIDO_VIGILANCIA)
    res = endpoint_signos_alarma(datos)
    assert res.nivel == "vigilancia"
    assert res.signos_presentes == 0
    assert "24 horas" in res.recomendacion


def test_endpoint_responde_sin_signos_de_alarma():
    datos = EvaluarSignosAlarmaHttpIn(**VALIDO_SIN_ALARMA)
    res = endpoint_signos_alarma(datos)
    assert res.nivel == "sin_alarma"
    assert "Hidratación" in res.recomendacion


def test_pydantic_rechaza_edad_fuera_de_rango():
    with pytest.raises(ValidationError) as exc:
        EvaluarSignosAlarmaHttpIn(**{**VALIDO_ALARMA, "edad": 150})
    errores = exc.value.errors()
    assert any(e["loc"] == ("edad",) for e in errores)


def test_pydantic_rechaza_dias_fiebre_fuera_de_rango():
    with pytest.raises(ValidationError) as exc:
        EvaluarSignosAlarmaHttpIn(**{**VALIDO_ALARMA, "dias_fiebre": 35})
    errores = exc.value.errors()
    assert any(e["loc"] == ("dias_fiebre",) for e in errores)


def test_pydantic_rechaza_campo_faltante():
    incompleto = {k: v for k, v in VALIDO_ALARMA.items() if k != "dias_fiebre"}
    with pytest.raises(ValidationError) as exc:
        EvaluarSignosAlarmaHttpIn(**incompleto)
    errores = exc.value.errors()
    assert any(e["type"] == "missing" and e["loc"] == ("dias_fiebre",) for e in errores)


def test_la_evaluacion_es_determinista():
    d = EvaluarSignosAlarmaHttpIn(**VALIDO_ALARMA)
    assert evaluar_signos_alarma_clinica(d) == evaluar_signos_alarma_clinica(d)
