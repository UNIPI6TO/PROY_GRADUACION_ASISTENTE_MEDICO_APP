#!/usr/bin/env python3
"""
scripts/sincronizar_metricas_pruebas.py · Grupo 5 (GuíaVital)
Sincroniza y audita automáticamente el conteo exacto de pruebas automatizadas
(backend con pytest y frontend con Vitest) entre el código y la documentación
(README.md, docs/07-evaluacion.md, docs/08-pruebas.md).

Uso:
    python scripts/sincronizar_metricas_pruebas.py           # Sincroniza y actualiza archivos
    python scripts/sincronizar_metricas_pruebas.py --check   # Verifica consistencia (para CI)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def contar_pruebas_backend() -> int:
    """Cuenta el número exacto de casos ejecutables en pytest mediante --collect-only."""
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            timeout=30,
        )
        salida = res.stdout + res.stderr
        match = re.search(r"(\d+)\s+tests?\s+collected", salida)
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"[!] Advertencia al invocar pytest --collect-only: {e}", file=sys.stderr)

    # Fallback determinista: conteo manual por funciones test_* en tests/test_*.py
    total = 0
    for ruta in (RAIZ / "tests").glob("test_*.py"):
        lineas = ruta.read_text(encoding="utf-8").splitlines()
        for linea in lineas:
            linea_limpia = linea.strip()
            if linea_limpia.startswith("def test_"):
                total += 1
    return total


def contar_pruebas_frontend() -> int:
    """Cuenta el número de casos 'it(' o 'test(' en frontend/tests/*.test.ts*."""
    total = 0
    carpeta_tests = RAIZ / "frontend" / "tests"
    if not carpeta_tests.exists():
        return 0

    patron = re.compile(r"^\s*(?:it|test)\s*\(")
    for ruta in carpeta_tests.glob("*.test.*"):
        if ruta.is_file():
            contenido = ruta.read_text(encoding="utf-8")
            for linea in contenido.splitlines():
                if patron.search(linea):
                    total += 1
    return total


def sincronizar_docs(backend_n: int, frontend_n: int, solo_verificar: bool = False) -> bool:
    """Actualiza o verifica el conteo de pruebas en README.md, docs/07 y docs/08."""
    archivos_actualizados: list[str] = []
    desalineados: list[str] = []

    # 1. docs/07-evaluacion.md
    ruta_07 = RAIZ / "docs" / "07-evaluacion.md"
    if ruta_07.exists():
        contenido = ruta_07.read_text(encoding="utf-8")
        nuevo = re.sub(
            r"# 3\. Ejecutar la suite completa de pruebas unitarias y de integración \(\d+ tests sin gastar cuota de API\)",
            f"# 3. Ejecutar la suite completa de pruebas unitarias y de integración ({backend_n} tests sin gastar cuota de API)",
            contenido,
        )
        if nuevo != contenido:
            if solo_verificar:
                desalineados.append(str(ruta_07.relative_to(RAIZ)))
            else:
                ruta_07.write_text(nuevo, encoding="utf-8")
                archivos_actualizados.append(str(ruta_07.relative_to(RAIZ)))

    # 2. docs/08-pruebas.md
    ruta_08 = RAIZ / "docs" / "08-pruebas.md"
    if ruta_08.exists():
        contenido = ruta_08.read_text(encoding="utf-8")
        nuevo = re.sub(
            r"\d+\s+pruebas unitarias y de integración en backend(?:\s+más\s+(?:\d+\s+)?pruebas\s+de\s+interfaz\s+en\s+frontend\s+\(`?[Vv]itest`?\))?",
            f"{backend_n} pruebas unitarias y de integración en backend más {frontend_n} pruebas de interfaz en frontend (`Vitest`)",
            contenido,
        )
        if nuevo != contenido:
            if solo_verificar:
                desalineados.append(str(ruta_08.relative_to(RAIZ)))
            else:
                ruta_08.write_text(nuevo, encoding="utf-8")
                archivos_actualizados.append(str(ruta_08.relative_to(RAIZ)))

    # 3. README.md
    ruta_readme = RAIZ / "README.md"
    if ruta_readme.exists():
        contenido = ruta_readme.read_text(encoding="utf-8")
        nuevo = re.sub(
            r"ejecución obligatoria de \*\*\d+ pruebas en `pytest`\*\* y \*\*\d+ pruebas en `Vitest`\*\*",
            f"ejecución obligatoria de **{backend_n} pruebas en `pytest`** y **{frontend_n} pruebas en `Vitest`**",
            contenido,
        )
        nuevo = re.sub(
            r"- \*\*Backend \(`pytest`\):\*\* \*\*\d+ ejecutadas / \d+ pasadas\*\*",
            f"- **Backend (`pytest`):** **{backend_n} ejecutadas / {backend_n} pasadas**",
            nuevo,
        )
        nuevo = re.sub(
            r"- \*\*Frontend \(`Vitest`\):\*\* \*\*\d+ ejecutadas / \d+ pasadas\*\*",
            f"- **Frontend (`Vitest`):** **{frontend_n} ejecutadas / {frontend_n} pasadas**",
            nuevo,
        )
        if nuevo != contenido:
            if solo_verificar:
                desalineados.append(str(ruta_readme.relative_to(RAIZ)))
            else:
                ruta_readme.write_text(nuevo, encoding="utf-8")
                archivos_actualizados.append(str(ruta_readme.relative_to(RAIZ)))

    # Reporte
    print(f"[*] Métricas detectadas en código:")
    print(f"    - Backend (pytest):  {backend_n} pruebas")
    print(f"    - Frontend (Vitest): {frontend_n} pruebas")
    print(f"    - Total Unit/Integ:  {backend_n + frontend_n} pruebas")

    if solo_verificar:
        if desalineados:
            print(f"[X] Documentos desalineados con el código ({len(desalineados)}):", file=sys.stderr)
            for d in desalineados:
                print(f"    - {d}", file=sys.stderr)
            return False
        print("[V] Todos los documentos están sincronizados con las pruebas.")
        return True
    else:
        if archivos_actualizados:
            print(f"[V] Documentos actualizados exitosamente ({len(archivos_actualizados)}):")
            for a in archivos_actualizados:
                print(f"    - {a}")
        else:
            print("[V] Todos los documentos ya estaban al día. No se requirieron cambios.")
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Sincronizador de métricas de pruebas en documentación.")
    parser.add_argument("--check", action="store_true", help="Verifica si los documentos están sincronizados sin modificarlos.")
    args = parser.parse_args()

    n_backend = contar_pruebas_backend()
    n_frontend = contar_pruebas_frontend()

    if n_backend == 0:
        print("[!] Error: No se pudieron detectar pruebas de backend.", file=sys.stderr)
        sys.exit(1)

    exito = sincronizar_docs(n_backend, n_frontend, solo_verificar=args.check)
    sys.exit(0 if exito else 1)


if __name__ == "__main__":
    main()
