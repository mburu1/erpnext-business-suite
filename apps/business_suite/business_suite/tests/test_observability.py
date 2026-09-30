"""Regression contracts for application observability."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
APP_ROOT = REPO_ROOT / "apps" / "business_suite" / "business_suite"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_observability_module_defines_request_lifecycle_and_health_contracts():
    source = read(APP_ROOT / "observability.py")
    for term in (
        "before_request",
        "after_request",
        "X-Request-ID",
        "Server-Timing",
        "get_observability_status",
        "requests_total",
        "requests_slow",
        "SELECT 1",
    ):
        assert term in source


def test_observability_hooks_are_registered_without_replacing_security_hooks():
    source = read(APP_ROOT / "hooks.py")
    assert 'before_request = ["business_suite.observability.before_request"]' in source
    assert '"business_suite.security.apply_security_headers"' in source
    assert '"business_suite.observability.after_request"' in source


def test_observability_documentation_exists():
    document = REPO_ROOT / "docs" / "observability" / "monitoring.md"
    assert document.is_file()
    source = read(document)
    for term in ("request correlation", "structured logs", "health", "metrics", "slow requests"):
        assert term.lower() in source.lower()
