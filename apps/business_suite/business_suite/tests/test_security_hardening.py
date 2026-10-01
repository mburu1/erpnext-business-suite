"""Static regression tests for security controls that do not require a live Frappe site."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
APP_ROOT = REPO_ROOT / "apps" / "business_suite" / "business_suite"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_security_module_contains_bounded_validation_controls():
    source = read(APP_ROOT / "security.py")
    assert "MAX_WEBHOOK_BODY_BYTES = 1_048_576" in source
    assert "SAFE_INTEGRATION_NAME" in source
    assert "validate_handler_path" in source
    assert "redact_sensitive" in source


def test_http_security_headers_are_registered():
    hooks = read(APP_ROOT / "hooks.py")
    security = read(APP_ROOT / "security.py")
    assert 'after_request = [' in hooks
    assert '"business_suite.security.apply_security_headers"' in hooks
    for header in (
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Permissions-Policy",
    ):
        assert header in security
    assert "Strict-Transport-Security" in security


def test_guest_webhook_is_rate_limited_and_size_bounded():
    source = read(APP_ROOT / "api" / "webhook_api.py")
    assert '@rate_limit(limit=30, seconds=60, ip_based=True, methods="POST")' in source
    assert "validate_webhook_body_size(raw_body)" in source
    assert "validate_event_id" in source


def test_webhook_handlers_cannot_be_configured_to_arbitrary_modules():
    source = read(APP_ROOT / "integrations" / "webhooks" / "handler.py")
    assert "validate_handler_path" in source
    assert 'method_path = validate_handler_path(config.get("handler"))' in source
    assert 'frappe.get_attr(method_path)(payload)' in source


def test_security_documentation_exists():
    document = REPO_ROOT / "docs" / "security" / "hardening.md"
    assert document.is_file()
    source = read(document)
    for term in ("rate limiting", "HMAC", "secrets", "security headers", "webhook"):
        assert term.lower() in source.lower()
