"""Pruebas unitarias para la herramienta consultar_guia_msp."""
import pytest
from pydantic import ValidationError
from unittest.mock import MagicMock

from app.schemas import Fuente
from app.services.retriever import ResultadoBusqueda
from app.tools.consultar_guia_msp import consultar_guia_msp, ConsultarGuiaMspIn


def test_valida_esquema_pydantic_longitud_minima():
    with pytest.raises(ValidationError):
        ConsultarGuiaMspIn(texto="ab")  # Menos de 3 caracteres


def test_ejecucion_con_mock_buscador():
    mock_buscador = MagicMock()
    mock_buscador.buscar.return_value = [
        ResultadoBusqueda(
            id="f1",
            texto="Los signos de alarma del dengue incluyen dolor abdominal y vómitos.",
            documento="Guia_Clinica_Dengue_MSP.pdf",
            seccion="4.1 Signos de alarma",
            distancia=0.15,
            metadata={"vigente": True},
        )
    ]
    datos = ConsultarGuiaMspIn(texto="signos de alarma de dengue")
    res = consultar_guia_msp(datos, buscador=mock_buscador)

    assert res["encontrado"] is True
    assert len(res["fragmentos"]) == 1
    assert res["fuentes"][0]["documento"] == "Guia_Clinica_Dengue_MSP.pdf"
    assert res["fuentes"][0]["seccion"] == "4.1 Signos de alarma"


def test_es_determinista():
    mock_buscador = MagicMock()
    mock_buscador.buscar.return_value = [
        ResultadoBusqueda(
            id="f2",
            texto="Hidratación oral con sales de rehidratación oral.",
            documento="Protocolo_MSP.pdf",
            seccion="Tratamiento grupo A",
            distancia=0.2,
            metadata={"vigente": True},
        )
    ]
    datos = ConsultarGuiaMspIn(texto="como hidratar al paciente con dengue")
    res1 = consultar_guia_msp(datos, buscador=mock_buscador)
    res2 = consultar_guia_msp(datos, buscador=mock_buscador)
    assert res1 == res2
