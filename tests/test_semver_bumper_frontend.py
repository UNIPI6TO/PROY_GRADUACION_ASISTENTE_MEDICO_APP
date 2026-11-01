"""Pruebas unitarias para scripts/semver_bumper_frontend.py."""
import json
import pytest
from scripts.semver_bumper_frontend import (
    validate_semver,
    determine_increment,
    calculate_next_release,
    calculate_next_snapshot,
    update_package_json,
    update_package_lock_json,
    TAG_PREFIX,
)


def test_incremento_release_frontend():
    base = "0.2.0"
    assert calculate_next_release(base, determine_increment(["feat(ui): nuevo diseño de chat"])) == "0.3.0"
    assert calculate_next_release(base, determine_increment(["fix(ui): corrige overflow de mensaje"])) == "0.2.1"
    assert calculate_next_release(base, determine_increment(["feat!: rediseño con breaking change"])) == "1.0.0"


def test_snapshot_progression_frontend():
    base = "0.2.0"
    tags_vacio = []
    assert calculate_next_snapshot(base, tags_vacio) == "0.2.0-SNAPSHOT-RC1"

    tags_con_rc1 = ["frontend-v0.2.0-SNAPSHOT-RC1", "v0.2.0-SNAPSHOT-RC5"]
    assert calculate_next_snapshot(base, tags_con_rc1) == "0.2.0-SNAPSHOT-RC2"


def test_actualizacion_package_json_y_lock(tmp_path):
    pkg_file = tmp_path / "package.json"
    pkg_file.write_text(json.dumps({"name": "test", "version": "0.1.0"}), encoding="utf-8")

    lock_file = tmp_path / "package-lock.json"
    lock_file.write_text(
        json.dumps({"name": "test", "version": "0.1.0", "packages": {"": {"version": "0.1.0"}}}),
        encoding="utf-8",
    )

    update_package_json(pkg_file, "0.2.0-SNAPSHOT-RC1")
    update_package_lock_json(lock_file, "0.2.0-SNAPSHOT-RC1")

    assert json.loads(pkg_file.read_text(encoding="utf-8"))["version"] == "0.2.0-SNAPSHOT-RC1"
    assert json.loads(lock_file.read_text(encoding="utf-8"))["packages"][""]["version"] == "0.2.0-SNAPSHOT-RC1"
