"""
Pruebas unitarias para el script de versionado SemVer (Paso 1 del plan).
No modifica ninguna prueba existente en el proyecto.
"""

import pytest
from scripts.semver_bumper import (
    validate_semver,
    determine_increment,
    calculate_next_release,
    calculate_next_snapshot,
    detect_manual_version_change,
    update_app_version_in_file,
)


def test_release_increment_and_calculation_main():
    """
    Prueba 1 del plan:
    Verifica las reglas de incremento según Conventional Commits y el cálculo
    de versiones Release para la rama 'main', validando el cumplimiento estricto de SemVer.
    """
    base_version = "0.1.0"

    # 1. Caso MINOR: commit con prefijo feat:
    commits_minor = ["feat: implementa endpoint de triaje y orientación"]
    inc_minor = determine_increment(commits_minor)
    next_minor = calculate_next_release(base_version, inc_minor)
    assert inc_minor == "MINOR"
    assert next_minor == "0.2.0"
    assert validate_semver(next_minor) is True

    # 2. Caso PATCH: commit con prefijo fix:
    commits_patch = ["fix: corrige timeout en sondas de disponibilidad"]
    inc_patch = determine_increment(commits_patch)
    next_patch = calculate_next_release(base_version, inc_patch)
    assert inc_patch == "PATCH"
    assert next_patch == "0.1.1"
    assert validate_semver(next_patch) is True

    # 3. Caso PATCH para tareas de mantenimiento y documentación
    commits_chore_docs = [
        "chore: actualiza dependencias del backend",
        "docs: documenta especificación de arquitectura",
    ]
    inc_chore = determine_increment(commits_chore_docs)
    next_chore = calculate_next_release(base_version, inc_chore)
    assert inc_chore == "PATCH"
    assert next_chore == "0.1.1"
    assert validate_semver(next_chore) is True

    # 4. Caso MAJOR: commit con BREAKING CHANGE:
    commits_major_footer = [
        "fix: ajusta respuesta en endpoint de síntomas",
        "BREAKING CHANGE: se modifica la estructura del contrato JSON",
    ]
    inc_major_1 = determine_increment(commits_major_footer)
    next_major_1 = calculate_next_release(base_version, inc_major_1)
    assert inc_major_1 == "MAJOR"
    assert next_major_1 == "1.0.0"
    assert validate_semver(next_major_1) is True

    # 5. Caso MAJOR: commit con prefijo feat!: o fix!:
    commits_major_bang = ["feat!: elimina endpoint legacy de compatibilidad"]
    inc_major_2 = determine_increment(commits_major_bang)
    next_major_2 = calculate_next_release(base_version, inc_major_2)
    assert inc_major_2 == "MAJOR"
    assert next_major_2 == "1.0.0"
    assert validate_semver(next_major_2) is True

    # 6. Precedencia: Si hay feat y fix juntos, prevalece MINOR sobre PATCH
    commits_mixed = [
        "fix: soluciona detalle de logging",
        "feat: añade nueva herramienta de recuperación",
    ]
    inc_mixed = determine_increment(commits_mixed)
    next_mixed = calculate_next_release(base_version, inc_mixed)
    assert inc_mixed == "MINOR"
    assert next_mixed == "0.2.0"
    assert validate_semver(next_mixed) is True


def test_snapshot_rc_progression_develop():
    """
    Prueba 2 del plan:
    Verifica la generación e incremento correlativo de versiones Snapshot para la
    rama 'develop' con nomenclatura X.Y.Z-SNAPSHOT-RC#, validando el cumplimiento
    estricto del patrón regex de SemVer.
    """
    base_version = "0.1.0"

    # 1. Sin tags previos de snapshot para la versión: inicia en RC1
    tags_vacios = []
    snapshot_1 = calculate_next_snapshot(base_version, tags_vacios)
    assert snapshot_1 == "0.1.0-SNAPSHOT-RC1"
    assert validate_semver(snapshot_1) is True

    # 2. Con un tag previo de snapshot RC1: incrementa a RC2
    tags_con_rc1 = ["v0.1.0-SNAPSHOT-RC1", "v0.0.9"]
    snapshot_2 = calculate_next_snapshot(base_version, tags_con_rc1)
    assert snapshot_2 == "0.1.0-SNAPSHOT-RC2"
    assert validate_semver(snapshot_2) is True

    # 3. Con tags existentes hasta RC2: incrementa a RC3
    tags_con_rc2 = ["v0.1.0-SNAPSHOT-RC1", "v0.1.0-SNAPSHOT-RC2", "v0.0.1"]
    snapshot_3 = calculate_next_snapshot(base_version, tags_con_rc2)
    assert snapshot_3 == "0.1.0-SNAPSHOT-RC3"
    assert validate_semver(snapshot_3) is True

    # 4. Cuando la versión base proviene de develop y ya contiene un sufijo snapshot anterior
    base_con_sufijo = "0.1.0-SNAPSHOT-RC2"
    tags_existentes = ["v0.1.0-SNAPSHOT-RC1", "v0.1.0-SNAPSHOT-RC2"]
    snapshot_4 = calculate_next_snapshot(base_con_sufijo, tags_existentes)
    assert snapshot_4 == "0.1.0-SNAPSHOT-RC3"
    assert validate_semver(snapshot_4) is True


def test_manual_version_change_and_file_update(tmp_path):
    """
    Prueba 3 del plan:
    Verifica que se detecten y respeten modificaciones manuales válidas de versión
    en el diff, que se rechacen formatos inválidos, y que la actualización en archivo
    sea segura y atómica.
    """
    # 1. Diff con versión manual válida: debe ser respetada
    diff_valido = """
--- a/app/main.py
+++ b/app/main.py
@@ -11,4 +11,4 @@
-APP_VERSION = "0.1.0"
+APP_VERSION = "0.5.0"
"""
    manual_ver = detect_manual_version_change(diff_valido)
    assert manual_ver == "0.5.0"
    assert validate_semver(manual_ver) is True

    # 2. Diff sin modificaciones en APP_VERSION: retorna None
    diff_sin_version = """
--- a/app/main.py
+++ b/app/main.py
@@ -20,2 +20,3 @@
+    # Comentario añadido
"""
    assert detect_manual_version_change(diff_sin_version) is None

    # 3. Diff con versión manual inválida (ej. con prefijo 'v' o incompleta): debe lanzar ValueError
    diff_invalido = """
--- a/app/main.py
+++ b/app/main.py
@@ -11,4 +11,4 @@
-APP_VERSION = "0.1.0"
+APP_VERSION = "v0.5.0"
"""
    with pytest.raises(ValueError, match="no cumple con el regex de SemVer"):
        detect_manual_version_change(diff_invalido)

    # 4. Actualización segura en archivo sin alterar constantes adyacentes
    dummy_file = tmp_path / "main.py"
    dummy_file.write_text(
        'APP_NAME = "test-app"\nAPP_VERSION = "0.1.0"\nSEMVER_REGEX = r"^..."\n',
        encoding="utf-8",
    )
    update_app_version_in_file(dummy_file, "0.5.0")
    nuevo_contenido = dummy_file.read_text(encoding="utf-8")
    assert 'APP_VERSION = "0.5.0"' in nuevo_contenido
    assert 'APP_NAME = "test-app"' in nuevo_contenido
    assert 'SEMVER_REGEX = r"^..."' in nuevo_contenido


def test_actualizacion_simetrica_frontend(tmp_path):
    import json
    from scripts.semver_bumper import update_frontend_versions

    pkg = tmp_path / "package.json"
    lock = tmp_path / "package-lock.json"

    pkg.write_text(json.dumps({"name": "front", "version": "0.1.0"}), encoding="utf-8")
    lock.write_text(json.dumps({"name": "front", "version": "0.1.0", "packages": {"": {"version": "0.1.0"}}}), encoding="utf-8")

    update_frontend_versions("0.2.0-SNAPSHOT-RC2", pkg_path=pkg, lock_path=lock)

    assert json.loads(pkg.read_text(encoding="utf-8"))["version"] == "0.2.0-SNAPSHOT-RC2"
    assert json.loads(lock.read_text(encoding="utf-8"))["version"] == "0.2.0-SNAPSHOT-RC2"
