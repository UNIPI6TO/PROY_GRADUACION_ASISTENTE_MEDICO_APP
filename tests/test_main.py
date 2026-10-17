"""
Pruebas unitarias para el backend inicial (manage/health y manage/info).
Utiliza exclusivamente la biblioteca estándar de Python y pytest.
"""

import re
from app.main import check_health, get_info, APP_NAME, SEMVER_REGEX


def test_check_health_liveness_and_readiness_up():
    """Verifica que la comprobación devuelva código HTTP 200 y una estructura con liveness y readiness ambos en estado 'UP'."""
    payload, status_code = check_health()

    assert status_code == 200
    assert payload["status"] == "UP"
    assert payload["checks"]["liveness"]["status"] == "UP"
    assert payload["checks"]["readiness"]["status"] == "UP"


def test_check_health_readiness_down_on_failure():
    """Verifica que ante la simulación de un recurso dependiente no disponible, la función clasifique readiness como 'DOWN' y emita estado 503."""
    failing_probe = lambda: False
    payload, status_code = check_health(readiness_probes=[failing_probe])

    assert status_code == 503
    assert payload["status"] == "DOWN"
    assert payload["checks"]["liveness"]["status"] == "UP"
    assert payload["checks"]["readiness"]["status"] == "DOWN"


def test_get_info_semver_format_and_app_name():
    """Verifica que la información retorne el nombre de la aplicación y que el formato de la versión cumpla la expresión regular oficial de SemVer (MAJOR.MINOR.PATCH)."""
    payload, status_code = get_info()

    assert status_code == 200
    assert payload["name"] == APP_NAME
    assert "version" in payload
    assert re.match(SEMVER_REGEX, payload["version"]) is not None
