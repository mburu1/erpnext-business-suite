"""Repository-level quality gates for the automated test-hardening stage."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
APP_ROOT = REPO_ROOT / "apps" / "business_suite" / "business_suite"
TEST_ROOT = APP_ROOT / "tests"


def test_test_suite_has_all_required_validation_levels():
    expected = {
        "test_unit_rbac.py",
        "test_unit_workflows.py",
        "test_api.py",
        "test_integrations.py",
        "test_permissions.py",
        "test_e2e_contracts.py",
        "test_performance.py",
    }
    actual = {path.name for path in TEST_ROOT.glob("test_*.py")}
    assert expected <= actual


def test_workflow_policy_is_separated_from_frappe_runtime():
    policy = APP_ROOT / "workflow_definitions.py"
    enforcement = APP_ROOT / "workflow.py"
    assert policy.is_file()
    assert enforcement.is_file()
    assert "import frappe" not in policy.read_text(encoding="utf-8")
    assert "from business_suite.workflow_definitions import WORKFLOWS" in enforcement.read_text(
        encoding="utf-8"
    )


def test_role_vocabulary_is_separated_from_frappe_runtime():
    role_definitions = APP_ROOT / "role_definitions.py"
    permissions = APP_ROOT / "permissions.py"
    assert role_definitions.is_file()
    assert "import frappe" not in role_definitions.read_text(encoding="utf-8")
    assert "from business_suite.role_definitions import" in permissions.read_text(
        encoding="utf-8"
    )


def test_repository_does_not_contain_obvious_committed_secret_literals():
    source_roots = [APP_ROOT, REPO_ROOT / "scripts"]
    suspicious = (
        "BEGIN RSA " + "PRIVATE KEY",
        "BEGIN OPENSSH " + "PRIVATE KEY",
        "AK" + "IA",
    )

    for root in source_roots:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert not any(marker in text for marker in suspicious), path


def test_ci_runs_the_deterministic_quality_suite():
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    assert "pytest" in workflow
    assert "test_unit_rbac.py" in workflow
    assert "test_unit_workflows.py" in workflow
    assert "test_quality_contracts.py" in workflow
    assert "test_performance.py" in workflow
