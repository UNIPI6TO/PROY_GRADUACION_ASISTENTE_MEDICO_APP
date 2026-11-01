"""Pruebas unitarias para scripts/actualizar_changelog.py."""
import pytest
from pathlib import Path
from scripts.actualizar_changelog import actualizar_changelog


def test_actualizar_changelog_promociona_unreleased(tmp_path):
    archivo = tmp_path / "CHANGELOG.md"
    archivo.write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Backend\n- Nuevo endpoint de salud\n\n## [0.1.0] - 2026-10-10\n",
        encoding="utf-8",
    )

    resultado = actualizar_changelog(archivo, "0.2.0", fecha="2026-10-31")
    assert resultado is True

    contenido = archivo.read_text(encoding="utf-8")
    assert "## [Unreleased]" in contenido
    assert "## [0.2.0] - 2026-10-31" in contenido
    assert "### Backend\n- Nuevo endpoint de salud" in contenido
    assert "## [0.1.0] - 2026-10-10" in contenido


def test_actualizar_changelog_es_idempotente(tmp_path):
    archivo = tmp_path / "CHANGELOG.md"
    archivo.write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [0.2.0] - 2026-10-31\n",
        encoding="utf-8",
    )

    resultado = actualizar_changelog(archivo, "0.2.0", fecha="2026-10-31")
    assert resultado is False  # Ya existía, no debe duplicar


def test_actualizar_changelog_sin_unreleased_falla_amigablemente(tmp_path):
    archivo = tmp_path / "CHANGELOG.md"
    archivo.write_text("# Changelog sin cabecera\n", encoding="utf-8")

    resultado = actualizar_changelog(archivo, "0.2.0")
    assert resultado is False


def test_actualizar_changelog_con_etiqueta_frontend(tmp_path):
    archivo = tmp_path / "CHANGELOG.md"
    archivo.write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Frontend\n- Nuevo componente de alerta\n\n## [0.1.0] - 2026-10-10\n",
        encoding="utf-8",
    )

    resultado = actualizar_changelog(archivo, "frontend-v0.2.0-SNAPSHOT-RC1", fecha="2026-10-31")
    assert resultado is True

    contenido = archivo.read_text(encoding="utf-8")
    assert "## [0.2.0-SNAPSHOT-RC1] - 2026-10-31" in contenido
    assert "### Frontend\n- Nuevo componente de alerta" in contenido


def test_actualizar_changelog_sin_commits_agrega_no_hubo_cambios(tmp_path, monkeypatch):
    archivo = tmp_path / "CHANGELOG.md"
    archivo.write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-10-10\n",
        encoding="utf-8",
    )

    # Simular que git log no devuelve commits
    monkeypatch.setattr("scripts.actualizar_changelog.obtener_commits_recientes", lambda carpeta=None: [])

    resultado = actualizar_changelog(archivo, "0.2.0-SNAPSHOT-RC2", fecha="2026-10-31")
    assert resultado is True

    contenido = archivo.read_text(encoding="utf-8")
    assert "## [0.2.0-SNAPSHOT-RC2] - 2026-10-31" in contenido
    assert "- No hubo cambios." in contenido
