"""Static production-readiness gate for the ERPNext Business Suite repository.

The gate intentionally uses only the Python standard library so it can run before
a deployment without installing application dependencies. It validates release
metadata, critical runtime/deployment files, immutable-image safeguards, and
documentation coverage. It does not claim that external infrastructure has been
verified; live smoke, backup-restore, TLS, DNS, and repository governance checks
remain deployment-environment responsibilities.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "docs/README.md",
    "docs/deployment/production.md",
    "docs/deployment/ci-cd-hardening.md",
    "docs/deployment/release-readiness.md",
    "docs/security/hardening.md",
    "docs/observability/monitoring.md",
    "docs/troubleshooting/runbooks.md",
    "deployment/docker/Dockerfile",
    "deployment/docker/docker-compose.prod.yml",
    "deployment/docker/.env.production.example",
    "deployment/nginx/erpnext.conf",
    "deployment/production/deploy.sh",
    "deployment/production/healthcheck.sh",
    "deployment/production/backup.sh",
    "deployment/production/rollback.sh",
    ".github/workflows/ci.yml",
    ".github/workflows/security.yml",
    ".github/workflows/deploy.yml",
)


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"Missing release-critical file: {relative}")

    init_text = (ROOT / "apps/business_suite/business_suite/__init__.py").read_text(
        encoding="utf-8"
    )
    pyproject_text = (ROOT / "apps/business_suite/pyproject.toml").read_text(
        encoding="utf-8"
    )
    init_match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
    project_match = re.search(
        r'^version\s*=\s*"([^"]+)"', pyproject_text, re.MULTILINE
    )
    if not init_match or not project_match:
        errors.append("Package version metadata is incomplete.")
    elif init_match.group(1) != project_match.group(1):
        errors.append("Package version metadata is inconsistent.")
    elif init_match.group(1) != "1.0.0":
        errors.append(f"Release version must be 1.0.0; found {init_match.group(1)}.")

    compose = (
        ROOT / "deployment/docker/docker-compose.prod.yml"
    ).read_text(encoding="utf-8")
    if "sites/$SITE_NAME" in compose or 'bench --site "$SITE_NAME"' in compose:
        errors.append("docker-compose.prod.yml contains an invalid Compose/Bash site-name expansion.")
    if "sites/$SITE_NAME" not in compose or 'bench --site "$SITE_NAME"' not in compose:
        errors.append("docker-compose.prod.yml must preserve SITE_NAME for the container shell with $ escaping.")
    if "MARIADB_ROOT_PASSWORD" not in compose:
        errors.append("MariaDB root password is not wired through deployment configuration.")

    deploy = (
        ROOT / "deployment/production/deploy.sh"
    ).read_text(encoding="utf-8")
    rollback = (
        ROOT / "deployment/production/rollback.sh"
    ).read_text(encoding="utf-8")
    if "40-character Git commit SHA" not in deploy:
        errors.append("Production deployment does not enforce immutable Git-SHA image tags.")
    if "docker pull \"$CUSTOM_IMAGE:$CUSTOM_TAG\"" not in deploy:
        errors.append("Production deployment must consume the published image instead of rebuilding on the target host.")
    if "40-character Git commit SHA" not in rollback:
        errors.append("Rollback does not enforce immutable Git-SHA releases.")

    for name in ("deploy.sh", "healthcheck.sh", "backup.sh", "rollback.sh"):
        path = ROOT / "deployment/production" / name
        if path.is_file() and not (path.stat().st_mode & 0o111):
            errors.append(f"Production script is not executable: {name}")

    workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")
    security = (ROOT / ".github/workflows/security.yml").read_text(encoding="utf-8")
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    for required in (
        "provenance: true",
        "sbom: true",
        "attestations: write",
        "id-token: write",
    ):
        if required not in workflow:
            errors.append(f"Production workflow missing: {required}")

    for required in ("gitleaks", "pip-audit", "actionlint"):
        if required not in security:
            errors.append(f"Security workflow missing: {required}")

    if "production_readiness_audit.py" not in ci:
        errors.append("CI does not execute the production-readiness audit.")

    for name in ("deploy.sh", "rollback.sh"):
        result = subprocess.run(
            ["bash", "-n", str(ROOT / "deployment/production" / name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            errors.append(f"{name} shell syntax failed: {result.stderr.strip()}")

    if errors:
        print("Production readiness audit FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Production readiness audit PASSED: repository release gates are satisfied.")
    print(
        "External gates still required: CI green, staging smoke, backup/restore "
        "drill, TLS/DNS verification, and protected production approval."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
