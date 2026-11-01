"""Pruebas automatizadas de fragmentación (chunking) y base vectorial ChromaDB."""
from __future__ import annotations

import chromadb
import pytest

from app.schemas import Fuente
from app.services.retriever import BuscadorVectorial
from scripts.ingest import (
    DOC_OPS_NOMBRE,
    DOC_SIVE_NOMBRE,
    extraer_fragmentos_ops,
    extraer_fragmentos_sive,
    ingestar_documentos,
)


class CarteroDeterminista:
    """Doble de SentenceTransformer para pruebas rápidas sin red ni descarga de 470 MB.
    Registra los textos recibidos (para verificar prefijos 'passage: ' y 'query: ')
    y genera vectores semánticos deterministas por conceptos clave del dominio.
    """

    CONCEPTOS = [
        ("alarma", "barriga", "abdominal", "vomito", "vómito", "sangrado", "mucosas", "letargo"),
        ("tanques", "criaderos", "llantas", "cepillar", "mosquitero", "repelente", "vector"),
        ("ibuprofeno", "aspirina", "diclofenaco", "naproxeno", "aine", "automedicarse", "paracetamol"),
        ("embarazo", "embarazada", "gestante", "parto", "fetal", "recién nacido"),
        ("ns1", "igg", "igm", "pcr", "laboratorio", "suero", "muestra"),
        ("a 90", "a90", "a 91", "a91", "cie-10"),
    ]

    def __init__(self) -> None:
        self.Historial_encode: list[list[str]] = []

    def encode(self, textos: list[str], normalize_embeddings: bool = True) -> list[list[float]]:
        self.Historial_encode.append(list(textos))
        vectores: list[list[float]] = []
        for t in textos:
            t_low = t.lower()
            vec = [0.01] * len(self.CONCEPTOS)
            for idx, palabras in enumerate(self.CONCEPTOS):
                coincidencias = sum(1 for p in palabras if p in t_low)
                if coincidencias:
                    vec[idx] = float(coincidencias)
            norma = sum(x * x for x in vec) ** 0.5
            vec = [x / norma for x in vec]
            vectores.append(vec)
        return vectores


def test_extraccion_sive_alerta_paginas_95_a_100():
    """Verifica que solo se extraiga 8.2.3.2 DENGUE de las págs. 95-100 sin Chagas ni Fiebre Amarilla."""
    fragmentos = extraer_fragmentos_sive()
    assert len(fragmentos) >= 6

    texto_unido = "\n".join(f.texto for f in fragmentos)
    assert "8.2.3.2 DENGUE" in texto_unido
    assert "CIE-10" in texto_unido and "A 91" in texto_unido
    assert "Lavar y cepillar bien las paredes internas de los tanques" in texto_unido
    assert "ibuprofeno" in texto_unido.lower() and "aspirina" in texto_unido.lower()

    assert "Documento final" not in texto_unido
    assert "8.2.3.3 FIEBRE AMARILLA" not in texto_unido
    assert "triatominos" not in texto_unido.lower()

    for f in fragmentos:
        assert f.metadata["documento"] == DOC_SIVE_NOMBRE
        assert f.metadata["vigente"] is True
        assert f.metadata["pagina_inicio"] == 95 and f.metadata["pagina_fin"] == 100


def test_extraccion_guia_ops_2016_sin_bibliografia():
    """Verifica que la Guía OPS 2016 incluya capítulos y anexos clínicos D-U pero excluya bibliografía."""
    fragmentos = extraer_fragmentos_ops()
    assert len(fragmentos) >= 40

    secciones = [f.metadata["seccion"] for f in fragmentos]
    assert any("2.2" in s or "signos de alarma" in s.lower() for s in secciones)
    assert any("Anexo D" in s for s in secciones)
    assert any("Anexo G" in s for s in secciones)

    texto_unido = "\n".join(f.texto for f in fragmentos)
    assert "Pregnan* OR abortion OR pre-natal" not in texto_unido

    for f in fragmentos:
        assert f.metadata["documento"] == DOC_OPS_NOMBRE
        assert f.metadata["vigente"] is True


@pytest.fixture(scope="module")
def base_vectorial_pruebas(tmp_path_factory):
    """Fixture de módulo: genera la base vectorial de prueba una sola vez para toda la suite."""
    cartero = CarteroDeterminista()
    ruta_db = tmp_path_factory.mktemp("chroma_suite")
    resumen = ingestar_documentos(ruta_db=ruta_db, cartero=cartero, reiniciar=True, exportar=False)
    buscador = BuscadorVectorial(ruta_db=ruta_db, cartero=cartero)
    return {
        "ruta_db": ruta_db,
        "cartero": cartero,
        "resumen": resumen,
        "buscador": buscador,
    }


def test_ingesta_y_busqueda_semantica_con_prefijos_e5(base_vectorial_pruebas):
    """Verifica el flujo completo C-E-B-F-G-A: ingesta con 'passage: ' y búsqueda con 'query: '."""
    cartero = base_vectorial_pruebas["cartero"]
    resumen = base_vectorial_pruebas["resumen"]
    buscador = base_vectorial_pruebas["buscador"]

    assert resumen["total"] == resumen["ops_2016"] + resumen["sive_alerta_95_100"]

    assert len(cartero.Historial_encode) >= 1
    assert all(t.startswith("passage: ") for t in cartero.Historial_encode[0])

    resultados = buscador.buscar(
        "¿Cómo limpio los tanques de agua en mi patio para eliminar criaderos?",
        k=5,
    )

    assert cartero.Historial_encode[-1][0].startswith("query: ")
    assert len(resultados) == 5
    distancias = [r.distancia for r in resultados]
    assert distancias == sorted(distancias)
    assert any("tanques" in r.texto.lower() or "criaderos" in r.texto.lower() for r in resultados)
    assert isinstance(resultados[0].como_fuente(), Fuente)


def test_busqueda_hibrida_por_codigo_exacto(base_vectorial_pruebas):
    """Límite 2 de la clase: where_document={'$contains': ...} para códigos exactos."""
    buscador = base_vectorial_pruebas["buscador"]
    resultados = buscador.buscar(
        "¿Cuál es el código CIE-10 del dengue grave?",
        k=5,
        palabra_exacta="A 91",
    )
    assert len(resultados) >= 1
    assert all("A 91" in r.texto for r in resultados)


def test_filtro_por_etiqueta_vigente():
    """Límite 3 de la clase: el buscador filtra por where={'vigente': True} antes de buscar."""
    cartero = CarteroDeterminista()
    cliente = chromadb.EphemeralClient()
    col = cliente.create_collection(
        name="test_vigencia",
        configuration={"hnsw": {"space": "cosine"}},
    )

    textos = [
        "Protocolo antiguo derogado sobre dolor abdominal y signos de alarma.",
        "Protocolo vigente sobre dolor abdominal intenso y signos de alarma.",
    ]
    vectores = cartero.encode(["passage: " + t for t in textos])
    col.add(
        ids=["doc-antiguo", "doc-vigente"],
        documents=textos,
        metadatas=[
            {"documento": "Guía 2010", "seccion": "Signos", "vigente": False},
            {"documento": "Guía OPS 2016", "seccion": "Signos", "vigente": True},
        ],
        embeddings=vectores,
    )

    buscador = BuscadorVectorial(cartero=cartero, coleccion=col)
    resultados = buscador.buscar("Me duele fuerte la barriga, ¿es signo de alarma?", k=5, solo_vigentes=True)
    assert [r.id for r in resultados] == ["doc-vigente"]
