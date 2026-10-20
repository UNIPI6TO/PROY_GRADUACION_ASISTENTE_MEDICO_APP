"""
Módulo para automatización de versionado SemVer del Backend.
Cumple con el principio de Responsabilidad Única (SOLID).
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SEMVER_REGEX = (
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def validate_semver(version: str) -> bool:
    """Verifica si una cadena cumple estrictamente con el patrón oficial SemVer."""
    if not isinstance(version, str):
        return False
    return re.match(SEMVER_REGEX, version.strip()) is not None


def parse_semver_core(version: str) -> Tuple[int, int, int]:
    """Extrae los componentes numéricos principales (MAJOR, MINOR, PATCH)."""
    match = re.match(SEMVER_REGEX, version.strip())
    if not match:
        raise ValueError(f"Versión no válida bajo SemVer: {version}")
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    return major, minor, patch


def determine_increment(commit_messages: List[str]) -> str:
    """
    Analiza una lista de mensajes de commit siguiendo Conventional Commits y
    retorna el incremento SemVer de mayor precedencia: 'MAJOR', 'MINOR' o 'PATCH'.
    """
    has_major = False
    has_minor = False
    has_patch = False

    for msg in commit_messages:
        cleaned = msg.strip()
        if not cleaned:
            continue

        # 1. Detección de cambios de ruptura (MAJOR)
        if "BREAKING CHANGE:" in cleaned or re.search(r"^[a-zA-Z]+(\([^\)]+\))?!:", cleaned):
            has_major = True
            break

        # 2. Detección de nuevas funcionalidades (MINOR)
        if re.search(r"^feat(\([^\)]+\))?:", cleaned):
            has_minor = True
            continue

        # 3. Detección de correcciones, refactors, docs, tests, chores (PATCH)
        if re.search(r"^(fix|refactor|chore|test|docs)(\([^\)]+\))?:", cleaned):
            has_patch = True
            continue

        # Cualquier otro commit que afecte la ruta app/ aplica PATCH por defecto
        has_patch = True

    if has_major:
        return "MAJOR"
    if has_minor:
        return "MINOR"
    if has_patch:
        return "PATCH"
    return "PATCH"


def calculate_next_release(base_version: str, increment: str) -> str:
    """
    Calcula la siguiente versión limpia X.Y.Z para la rama 'main',
    eliminando cualquier sufijo previo de pre-release o snapshot.
    """
    major, minor, patch = parse_semver_core(base_version)
    inc = increment.upper()

    if inc == "MAJOR":
        new_version = f"{major + 1}.0.0"
    elif inc == "MINOR":
        new_version = f"{major}.{minor + 1}.0"
    elif inc == "PATCH":
        new_version = f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Incremento desconocido: {increment}. Debe ser MAJOR, MINOR o PATCH.")

    if not validate_semver(new_version):
        raise ValueError(f"La versión calculada no cumple con SemVer: {new_version}")

    return new_version


def calculate_next_snapshot(base_version: str, existing_tags: List[str]) -> str:
    """
    Calcula la versión Snapshot para la rama 'develop' con nomenclatura X.Y.Z-SNAPSHOT-RC#.
    Busca los tags existentes para incrementar el correlativo RC# iniciando en RC1.
    """
    major, minor, patch = parse_semver_core(base_version)
    base_core = f"{major}.{minor}.{patch}"

    tag_pattern = re.compile(rf"^v?{re.escape(base_core)}-SNAPSHOT-RC([1-9]\d*)$")
    highest_rc = 0

    for tag in existing_tags:
        match = tag_pattern.match(tag.strip())
        if match:
            rc_num = int(match.group(1))
            if rc_num > highest_rc:
                highest_rc = rc_num

    next_rc = highest_rc + 1
    new_snapshot = f"{base_core}-SNAPSHOT-RC{next_rc}"

    if not validate_semver(new_snapshot):
        raise ValueError(f"La versión snapshot generada no cumple con SemVer: {new_snapshot}")

    return new_snapshot


def detect_manual_version_change(diff_text: str) -> Optional[str]:
    """
    Inspecciona un diff de git para determinar si el usuario actualizó manualmente
    la variable APP_VERSION en app/main.py.

    - Si fue modificada y es válida según SemVer, retorna dicha versión.
    - Si fue modificada pero NO cumple con SemVer, lanza ValueError.
    - Si no fue modificada manualmente, retorna None.
    """
    pattern = re.compile(r'^\+\s*APP_VERSION\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)
    matches = pattern.findall(diff_text)
    if not matches:
        return None

    manual_version = matches[-1].strip()
    if not validate_semver(manual_version):
        raise ValueError(f"La versión manual '{manual_version}' no cumple con el regex de SemVer.")

    return manual_version


def update_app_version_in_file(file_path: Path, new_version: str) -> None:
    """Sustituye la asignación APP_VERSION = \"...\" en el archivo destino."""
    if not validate_semver(new_version):
        raise ValueError(f"No se puede actualizar el archivo. Versión inválida: {new_version}")

    content = file_path.read_text(encoding="utf-8")
    version_line_pattern = re.compile(r'APP_VERSION\s*=\s*["\'][^"\']+["\']')

    if not version_line_pattern.search(content):
        raise ValueError(f"No se encontró la variable APP_VERSION en {file_path}")

    updated_content = version_line_pattern.sub(f'APP_VERSION = "{new_version}"', content, count=1)
    file_path.write_text(updated_content, encoding="utf-8")


def get_git_tags() -> List[str]:
    """Obtiene la lista de tags existentes en Git."""
    import subprocess

    try:
        res = subprocess.run(
            ["git", "tag", "-l"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [tag.strip() for tag in res.stdout.splitlines() if tag.strip()]
    except Exception:
        return []


def get_git_commit_messages(base_ref: Optional[str] = None) -> List[str]:
    """Obtiene los mensajes de commit recientes."""
    import subprocess

    try:
        cmd = ["git", "log", "-n", "20", "--pretty=format:%s"]
        if base_ref:
            cmd = ["git", "log", f"{base_ref}..HEAD", "--pretty=format:%s"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def get_git_diff_app() -> str:
    """Obtiene el diff reciente sobre el directorio app/."""
    import subprocess

    try:
        res = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD", "--", "app/main.py"],
            capture_output=True,
            text=True,
        )
        return res.stdout
    except Exception:
        return ""


def main() -> int:
    """Punto de entrada CLI para GitHub Actions y ejecución local."""
    parser = argparse.ArgumentParser(description="Automatización de versionado SemVer.")
    parser.add_argument(
        "--branch",
        type=str,
        default=os.getenv("GITHUB_BASE_REF") or os.getenv("GITHUB_REF_NAME", "develop"),
        help="Rama de ejecución u objetivo: 'main' para release o 'develop' para snapshot.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default="app/main.py",
        help="Ruta al archivo que define APP_VERSION.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula el cálculo sin escribir en el archivo.",
    )
    args = parser.parse_args()

    target_file = Path(args.file)
    if not target_file.exists():
        print(f"Error: no existe el archivo objetivo {target_file}", file=sys.stderr)
        return 1

    content = target_file.read_text(encoding="utf-8")
    current_match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', content)
    current_version = current_match.group(1) if current_match else "0.1.0"

    # 1. Comprobar si hubo modificación manual de versión
    diff_text = get_git_diff_app()
    manual_version = detect_manual_version_change(diff_text)
    if manual_version:
        print(f"Versión manual detectada y respetada: {manual_version}")
        new_version = manual_version
    else:
        branch_name = args.branch.lower().replace("refs/heads/", "")
        if "main" in branch_name:
            commits = get_git_commit_messages()
            increment = determine_increment(commits)
            new_version = calculate_next_release(current_version, increment)
        else:
            tags = get_git_tags()
            new_version = calculate_next_snapshot(current_version, tags)

    print(f"Nueva versión calculada: {new_version}")

    # Emitir output para GitHub Actions si existe GITHUB_OUTPUT
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"version={new_version}\n")
            f.write(f"tag=v{new_version}\n")

    if not args.dry_run and not manual_version:
        update_app_version_in_file(target_file, new_version)
        print(f"Archivo {target_file} actualizado con APP_VERSION = \"{new_version}\"")

    return 0


if __name__ == "__main__":
    sys.exit(main())
