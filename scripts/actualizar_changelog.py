"""
Módulo para actualizar CHANGELOG.md tras el tageo SemVer en el pipeline de CI/CD.
Cumple con el principio de Responsabilidad Única (SOLID).
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys


def obtener_commits_recientes(carpeta: str | None = None) -> list[str]:
    """Obtiene los últimos commits para registrar cambios si [Unreleased] estaba vacío."""
    try:
        cmd = ["git", "log", "-n", "10", "--pretty=format:%s"]
        if carpeta:
            cmd.extend(["--", carpeta])
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        commits: list[str] = []
        for linea in res.stdout.splitlines():
            linea = linea.strip()
            if linea and "[skip ci]" not in linea and not linea.startswith("Merge "):
                commits.append(linea)
        return commits[:5]
    except Exception:
        return []


def actualizar_changelog(ruta_changelog: Path, version: str, fecha: str | None = None) -> bool:
    """Promociona la sección [Unreleased] a la nueva versión o crea la entrada en CHANGELOG.md."""
    if not ruta_changelog.exists():
        print(f"Advertencia: No existe el archivo {ruta_changelog}. Creando plantilla base.", file=sys.stderr)
        ruta_changelog.parent.mkdir(parents=True, exist_ok=True)
        ruta_changelog.write_text("# Changelog\n\n## [Unreleased]\n\n", encoding="utf-8")

    contenido = ruta_changelog.read_text(encoding="utf-8")
    version_limpia = re.sub(r"^(frontend-v|v)", "", version).strip()

    if not version_limpia:
        print("Error: Versión vacía o inválida.", file=sys.stderr)
        return False

    # Evitar duplicar la sección si ya existe
    if f"[{version_limpia}]" in contenido:
        print(f"La versión [{version_limpia}] ya existe en {ruta_changelog.name}.")
        return False

    fecha_str = fecha or datetime.now().strftime("%Y-%m-%d")

    patron_unreleased = re.compile(r"##\s*\[Unreleased\]", re.IGNORECASE)
    match_unreleased = patron_unreleased.search(contenido)

    if not match_unreleased:
        print(f"No se encontró la cabecera '## [Unreleased]' en {ruta_changelog.name}.", file=sys.stderr)
        return False

    idx_inicio = match_unreleased.end()

    # Buscar la siguiente versión documentada (ej. ## [0.2.0...)
    patron_siguiente = re.compile(r"\n##\s*\[")
    match_siguiente = patron_siguiente.search(contenido, pos=idx_inicio)

    if match_siguiente:
        idx_fin = match_siguiente.start()
        bloque_unreleased = contenido[idx_inicio:idx_fin].strip()
        resto = contenido[idx_fin:]
    else:
        bloque_unreleased = contenido[idx_inicio:].strip()
        resto = ""

    # Si hay notas en Unreleased, transferirlas a la nueva versión
    if bloque_unreleased:
        seccion_nueva = (
            f"## [Unreleased]\n\n"
            f"## [{version_limpia}] - {fecha_str}\n\n"
            f"{bloque_unreleased}\n"
        )
    else:
        # Si estaba vacío, buscar commits específicos de la carpeta
        carpeta_nombre = ruta_changelog.parent.name if ruta_changelog.parent.name in ("app", "frontend") else None
        commits = obtener_commits_recientes(carpeta_nombre)
        lineas_commits = "\n".join(f"- {c}" for c in commits) if commits else "- No hubo cambios."
        seccion_nueva = (
            f"## [Unreleased]\n\n"
            f"## [{version_limpia}] - {fecha_str}\n\n"
            f"{lineas_commits}\n\n"
        )

    nuevo_contenido = contenido[:match_unreleased.start()] + seccion_nueva + resto.lstrip("\n")
    ruta_changelog.write_text(nuevo_contenido, encoding="utf-8")
    print(f"{ruta_changelog.name} actualizado con éxito para [{version_limpia}] ({fecha_str}).")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Actualizar CHANGELOG.md tras publicación de versión.")
    parser.add_argument("--version", type=str, required=True, help="Versión o tag generado (ej: 0.2.0-SNAPSHOT-RC2).")
    parser.add_argument("--file", type=str, default="CHANGELOG.md", help="Ruta al archivo CHANGELOG.md.")
    parser.add_argument("--fecha", type=str, default=None, help="Fecha en formato YYYY-MM-DD.")
    args = parser.parse_args()

    try:
        actualizar_changelog(Path(args.file), args.version, args.fecha)
        return 0
    except Exception as e:
        print(f"Advertencia: Error al actualizar {args.file}: {e}", file=sys.stderr)
        return 0  # Garantizar que el workflow de CI/CD nunca falle por el changelog


if __name__ == "__main__":
    sys.exit(main())
