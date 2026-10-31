"""Pruebas unitarias para la herramienta buscar_centro_salud (GeoSalud Ecuador)."""
import pytest
from app.tools.buscar_centro_salud import buscar_centro_salud, BuscarCentroSaludIn


def test_buscar_por_ciudad():
    datos = BuscarCentroSaludIn(ciudad="Guayaquil", solo_emergencia_24h=True)
    res = buscar_centro_salud(datos)
    assert res["total_encontrados"] >= 1
    assert any("Guayaquil" in c["ciudad"] for c in res["centros_cercanos"])
    assert all(c["emergencia_24h"] is True for c in res["centros_cercanos"])


def test_buscar_por_coordenadas_gps_ordena_por_distancia():
    # Coordenadas aproximadas del centro de Guayaquil (-2.19, -79.89)
    datos = BuscarCentroSaludIn(latitud=-2.19, longitud=-79.89, solo_emergencia_24h=True)
    res = buscar_centro_salud(datos)
    assert len(res["centros_cercanos"]) > 0
    centros = res["centros_cercanos"]
    # Verifica que estén ordenados por distancia ascendente
    distancias = [c["distancia_km"] for c in centros if c["distancia_km"] is not None]
    assert distancias == sorted(distancias)
    assert distancias[0] < 30.0  # El más cercano a Guayaquil está a menos de 30 km


def test_es_determinista():
    datos = BuscarCentroSaludIn(ciudad="Machala")
    assert buscar_centro_salud(datos) == buscar_centro_salud(datos)
