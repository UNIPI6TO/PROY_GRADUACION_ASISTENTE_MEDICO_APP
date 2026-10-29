"""Servicio de búsqueda en la base vectorial (ChromaDB + multilingual-e5-small).

Reglas de la Clase 2 (Bases Vectoriales):
  1. Usar exactamente el mismo cartero ('intfloat/multilingual-e5-small') que en ingest.py.
  2. Anteponer 'query: ' a la pregunta del usuario antes de codificar.
  3. Filtrar por etiqueta antes de buscar (where={'vigente': True}).
  4. Soportar búsqueda híbrida por palabra/código exacto (where_document={'$contains': ...}).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from app.schemas import Fuente
from scripts.ingest import MODELO_EMBEDDINGS, NOMBRE_COLECCION, RUTA_CHROMA_DEFAULT


@dataclass(frozen=True)
class ResultadoBusqueda:
    id: str
    texto: str
    documento: str
    seccion: str
    distancia: float
    metadata: dict[str, Any]

    def como_fuente(self) -> Fuente:
        """Convierte el resultado al esquema Pydantic Fuente de app/schemas.py."""
        return Fuente(documento=self.documento, seccion=self.seccion)


@lru_cache(maxsize=1)
def _cargar_cartero_default() -> Any:
    from sentence_transformers import SentenceTransformer
    try:
        return SentenceTransformer(MODELO_EMBEDDINGS, local_files_only=True)
    except Exception:
        return SentenceTransformer(MODELO_EMBEDDINGS)


class BuscadorVectorial:
    """Consulta los vecinos más cercanos en la colección de ChromaDB."""

    def __init__(
        self,
        ruta_db: Path | str = RUTA_CHROMA_DEFAULT,
        nombre_coleccion: str = NOMBRE_COLECCION,
        cartero: Any | None = None,
        coleccion: Any | None = None,
    ) -> None:
        self._cartero = cartero
        if coleccion is not None:
            self._col = coleccion
        else:
            cliente = chromadb.PersistentClient(
                path=str(ruta_db),
                settings=Settings(anonymized_telemetry=False),
            )
            self._col = cliente.get_collection(name=nombre_coleccion)

    @property
    def cartero(self) -> Any:
        if self._cartero is None:
            self._cartero = _cargar_cartero_default()
        return self._cartero

    def buscar(
        self,
        pregunta: str,
        k: int = 5,
        solo_vigentes: bool = True,
        origen: str | None = None,
        palabra_exacta: str | None = None,
    ) -> list[ResultadoBusqueda]:
        """Devuelve los top-k fragmentos más cercanos ordenados por menor distancia coseno."""
        pregunta_limpia = pregunta.strip()
        if not pregunta_limpia:
            return []

        q = self.cartero.encode(["query: " + pregunta_limpia], normalize_embeddings=True)
        if hasattr(q, "tolist"):
            q = q.tolist()

        # Filtro por etiquetas (Límite 3: vigencia / origen)
        condiciones: list[dict[str, Any]] = []
        if solo_vigentes:
            condiciones.append({"vigente": True})
        if origen:
            condiciones.append({"origen": origen})

        where_filter: dict[str, Any] | None = None
        if len(condiciones) == 1:
            where_filter = condiciones[0]
        elif len(condiciones) > 1:
            where_filter = {"$and": condiciones}

        # Filtro por código o término exacto (Límite 2: búsqueda híbrida)
        where_doc: dict[str, str] | None = None
        if palabra_exacta and palabra_exacta.strip():
            where_doc = {"$contains": palabra_exacta.strip()}

        kwargs_query: dict[str, Any] = {
            "query_embeddings": q,
            "n_results": k,
        }
        if where_filter is not None:
            kwargs_query["where"] = where_filter
        if where_doc is not None:
            kwargs_query["where_document"] = where_doc

        r = self._col.query(**kwargs_query)

        ids = (r.get("ids") or [[]])[0]
        docs = (r.get("documents") or [[]])[0]
        metas = (r.get("metadatas") or [[]])[0]
        dists = (r.get("distances") or [[]])[0]

        resultados: list[ResultadoBusqueda] = []
        for frag_id, doc, meta, dist in zip(ids, docs, metas, dists):
            meta_dict = meta or {}
            resultados.append(
                ResultadoBusqueda(
                    id=str(frag_id),
                    texto=str(doc),
                    documento=str(meta_dict.get("documento", "")),
                    seccion=str(meta_dict.get("seccion", "")),
                    distancia=float(dist),
                    metadata=meta_dict,
                )
            )
        return resultados
