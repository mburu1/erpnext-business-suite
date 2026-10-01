"""End-to-end and integration contract validation for Business Suite.

The live HTTP tests run only when BUSINESS_SUITE_BASE_URL is configured.
The contract checks remain deterministic and do not require a running Frappe site.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
APP_ROOT = REPO_ROOT / "apps" / "business_suite"


def _get(url: str, timeout: int = 15) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"raw": body}
        return exc.code, payload


def test_required_integration_boundaries_exist() -> None:
    required = [
        APP_ROOT / "business_suite" / "api" / "crud_api.py",
        APP_ROOT / "business_suite" / "api" / "workflow_api.py",
        APP_ROOT / "business_suite" / "api" / "integration_api.py",
        APP_ROOT / "business_suite" / "integrations" / "clients" / "rest_client.py",
        APP_ROOT / "business_suite" / "integrations" / "webhooks" / "handler.py",
    ]

    missing = [str(path.relative_to(REPO_ROOT)) for path in required if not path.is_file()]
    assert not missing, f"Missing integration boundaries: {missing}"


def test_ci_contains_integration_validation_job() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert "Integration validation" in workflow
    assert "run_e2e_validation.py" in workflow
    assert "python scripts/run_e2e_validation.py" in workflow


@pytest.mark.skipif(
    not os.getenv("BUSINESS_SUITE_BASE_URL"),
    reason="Set BUSINESS_SUITE_BASE_URL to run live ERPNext HTTP E2E checks.",
)
def test_live_health_endpoint() -> None:
    base_url = os.environ["BUSINESS_SUITE_BASE_URL"].rstrip("/")
    status, payload = _get(
        f"{base_url}/api/method/business_suite.api.common.get_correlation_id"
    )

    assert status == 200
    assert isinstance(payload, dict)


@pytest.mark.skipif(
    not os.getenv("BUSINESS_SUITE_BASE_URL"),
    reason="Set BUSINESS_SUITE_BASE_URL to run live ERPNext HTTP E2E checks.",
)
def test_live_api_requires_authentication() -> None:
    base_url = os.environ["BUSINESS_SUITE_BASE_URL"].rstrip("/")
    status, payload = _get(
        f"{base_url}/api/method/business_suite.api.integration_api.list_logs"
    )

    assert status in {401, 403}
    assert isinstance(payload, dict)
