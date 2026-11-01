"""
Módulo para automatización de versionado SemVer del Frontend.
Cumple con el principio de Responsabilidad Única (SOLID).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

SEMVER_REGEX = (
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

TAG_PREFIX = "v"


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
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


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

        if "BREAKING CHANGE:" in cleaned or re.search(r"^[a-zA-Z]+(\([^\)]+\))?!:", cleaned):
            has_major = True
            break

        if re.search(r"^feat(\([^\)]+\))?:", cleaned):
            has_minor = True
            continue

        if re.search(r"^(fix|refactor|chore|test|docs)(\([^\)]+\))?:", cleaned):
            has_patch = True
            continue

        has_patch = True

    if has_major:
        return "MAJOR"
    if has_minor:
        return "MINOR"
    return "PATCH"


def calculate_next_release(base_version: str, increment: str) -> str:
    """Calcula la siguiente versión limpia X.Y.Z para la rama 'main'."""
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


def calculate_next_snapshot(
    base_version: str,
    existing_tags: List[str],
    prefix: str = TAG_PREFIX,
    increment: Optional[str] = None,
) -> str:
    """
    Calcula la versión Snapshot para la rama 'develop' con nomenclatura X.Y.Z-SNAPSHOT-RC#.
    Busca los tags existentes y la versión actual para incrementar el correlativo RC#.
    """
    major, minor, patch = parse_semver_core(base_version)

    if increment and not "-SNAPSHOT" in base_version:
        inc = increment.upper()
        if inc == "MAJOR":
            major += 1
            minor = 0
            patch = 0
        elif inc == "MINOR":
            minor += 1
            patch = 0
        elif inc == "PATCH":
            patch += 1

    base_core = f"{major}.{minor}.{patch}"

    tag_pattern = re.compile(rf"^{re.escape(prefix)}{re.escape(base_core)}-SNAPSHOT-RC([1-9]\d*)$")
    highest_rc = 0

    for tag in existing_tags:
        match = tag_pattern.match(tag.strip())
        if match:
            rc_num = int(match.group(1))
            if rc_num > highest_rc:
                highest_rc = rc_num

    # Considerar también el RC de la versión actual si pertenece al mismo core
    current_rc_match = re.search(rf"^{re.escape(base_core)}-SNAPSHOT-RC([1-9]\d*)$", base_version)
    if current_rc_match:
        current_rc = int(current_rc_match.group(1))
        if current_rc > highest_rc:
            highest_rc = current_rc

    next_rc = highest_rc + 1
    new_snapshot = f"{base_core}-SNAPSHOT-RC{next_rc}"

    if not validate_semver(new_snapshot):
        raise ValueError(f"La versión snapshot generada no cumple con SemVer: {new_snapshot}")

    return new_snapshot


def update_package_json(package_path: Path, new_version: str) -> None:
    """Actualiza la clave 'version' en package.json de forma limpia."""
    if not validate_semver(new_version):
        raise ValueError(f"Versión inválida para package.json: {new_version}")

    data = json.loads(package_path.read_text(encoding="utf-8"))
    data["version"] = new_version
    package_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_package_lock_json(lock_path: Path, new_version: str) -> None:
    """Actualiza la clave 'version' en package-lock.json si existe."""
    if not lock_path.exists() or not validate_semver(new_version):
        return

    data = json.loads(lock_path.read_text(encoding="utf-8"))
    data["version"] = new_version
    if "packages" in data and "" in data["packages"]:
        data["packages"][""]["version"] = new_version
    lock_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_git_tags() -> List[str]:
    """Obtiene la lista de tags existentes en Git."""
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


def get_git_commit_messages_frontend(base_ref: Optional[str] = None) -> List[str]:
    """Obtiene los mensajes de commit recientes que afectan al frontend/."""
    if not base_ref:
        cmd = ["git", "log", "-n", "20", "--pretty=format:%s", "--", "frontend/"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [line.strip() for line in res.stdout.splitlines() if line.strip()]
        except Exception:
            return []

    clean_base = base_ref.replace("refs/heads/", "").strip()
    candidates = [
        ["git", "log", f"origin/{clean_base}..HEAD", "--pretty=format:%s", "--", "frontend/"],
        ["git", "log", f"{clean_base}..HEAD", "--pretty=format:%s", "--", "frontend/"],
        ["git", "log", "-n", "20", "--pretty=format:%s", "--", "frontend/"],
    ]
    for cmd in candidates:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            commits = [line.strip() for line in res.stdout.splitlines() if line.strip()]
            if commits:
                return commits
        except Exception:
            continue
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Automatización de versionado SemVer para Frontend.")
    parser.add_argument(
        "--branch",
        type=str,
        default=os.getenv("GITHUB_BASE_REF") or os.getenv("GITHUB_REF_NAME", "develop"),
        help="Rama objetivo: 'main' para release o 'develop' para snapshot.",
    )
    parser.add_argument(
        "--package-json",
        type=str,
        default="frontend/package.json",
        help="Ruta a frontend/package.json.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula el cálculo sin escribir en el archivo.",
    )
    args = parser.parse_args()

    pkg_path = Path(args.package_json)
    if not pkg_path.exists():
        print(f"Error: no existe {pkg_path}", file=sys.stderr)
        return 1

    pkg_data = json.loads(pkg_path.read_text(encoding="utf-8"))
    current_version = pkg_data.get("version", "0.1.0")

    branch_name = args.branch.lower().replace("refs/heads/", "")
    commits = get_git_commit_messages_frontend(base_ref=args.branch)
    increment = determine_increment(commits)

    if "main" in branch_name:
        new_version = calculate_next_release(current_version, increment)
    else:
        tags = get_git_tags()
        new_version = calculate_next_snapshot(current_version, tags, prefix=TAG_PREFIX, increment=increment)

    tag_name = f"{TAG_PREFIX}{new_version}"
    print(f"Nueva versión de Frontend calculada: {new_version} (tag: {tag_name})")

    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"version={new_version}\n")
            f.write(f"tag={tag_name}\n")

    if not args.dry_run:
        update_package_json(pkg_path, new_version)
        lock_path = pkg_path.parent / "package-lock.json"
        update_package_lock_json(lock_path, new_version)
        print(f"Archivos package.json y package-lock.json actualizados a versión '{new_version}'.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
