"""Persistencia del historial de chat en SQLite. Única responsabilidad: guardar/leer turnos."""
from __future__ import annotations

import os
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

from app.schemas import TurnoHistorial

_DDL = """
CREATE TABLE IF NOT EXISTS historial_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sesion TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('user', 'assistant')),
    contenido TEXT NOT NULL,
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_historial_sesion ON historial_chat (id_sesion, id);
"""


class RepositorioHistorial:
    def __init__(self, ruta: str | None = None):
        self.ruta = ruta or os.getenv("HISTORIAL_DB", "").strip() or "data/historial.db"
        if self.ruta != ":memory:":
            Path(self.ruta).parent.mkdir(parents=True, exist_ok=True)
        # En memoria hay que conservar la misma conexión; si no, la base desaparece.
        self._conservada = sqlite3.connect(self.ruta, check_same_thread=False) if self.ruta == ":memory:" else None
        with self._conexion() as c, c:
            c.executescript(_DDL)

    @contextmanager
    def _conexion(self):
        """Entrega una conexión; solo cierra las que abre ella (no la compartida de :memory:)."""
        if self._conservada is not None:
            yield self._conservada
        else:
            with closing(sqlite3.connect(self.ruta)) as c:
                yield c

    def guardar(self, id_sesion: str, rol: str, contenido: str) -> None:
        with self._conexion() as c, c:
            c.execute("INSERT INTO historial_chat (id_sesion, rol, contenido) VALUES (?, ?, ?)",
                      (id_sesion, rol, contenido))

    def ultimos_turnos(self, id_sesion: str, limite: int = 6) -> list[TurnoHistorial]:
        """Solo turnos de ESA sesión (consulta parametrizada), en orden cronológico."""
        with self._conexion() as c:
            filas = c.execute(
                "SELECT id_sesion, rol, contenido, creado_en FROM historial_chat "
                "WHERE id_sesion = ? ORDER BY id DESC LIMIT ?", (id_sesion, limite)).fetchall()
        return [TurnoHistorial(id_sesion=f[0], rol=f[1], contenido=f[2], creado_en=f[3]) for f in reversed(filas)]

    def limpiar_sesion(self, id_sesion: str) -> None:
        with self._conexion() as c, c:
            c.execute("DELETE FROM historial_chat WHERE id_sesion = ?", (id_sesion,))
