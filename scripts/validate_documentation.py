"""Validate the repository's engineering documentation index and Markdown links."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS_INDEX = ROOT / "docs" / "README.md"

REQUIRED_DOCS = (
    "docs/architecture/system-architecture.md",
    "docs/architecture/component-boundaries.md",
    "docs/erd/erd.md",
    "docs/erd/custom-doctypes.md",
    "docs/ooad/use-cases.md",
    "docs/ooad/domain-model.md",
    "docs/ooad/sequence-diagrams.md",
    "docs/workflows/stock-request.md",
    "docs/workflows/customer-onboarding.md",
    "docs/workflows/integration-processing.md",
    "docs/integrations/api-contracts.md",
    "docs/integrations/webhook-flows.md",
    "docs/security/security-model.md",
    "docs/security/rbac.md",
    "docs/security/hardening.md",
    "docs/performance/scalability.md",
    "docs/observability/monitoring.md",
    "docs/testing/e2e-integration-validation.md",
    "docs/deployment/deployment-architecture.md",
    "docs/deployment/production.md",
    "docs/deployment/ci-cd-hardening.md",
    "docs/troubleshooting/runbooks.md",
    "docs/troubleshooting/application-errors.md",
    "docs/troubleshooting/background-workers.md",
    "docs/troubleshooting/database.md",
    "docs/troubleshooting/deployment-rollback.md",
    "docs/troubleshooting/diagnostic-commands.md",
    "docs/troubleshooting/health-checks.md",
    "docs/troubleshooting/incident-response.md",
    "docs/troubleshooting/integrations.md",
)

MARKDOWN_LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")


def iter_markdown_files() -> list[Path]:
    files = [ROOT / "README.md"]
    files.extend((ROOT / "docs").rglob("*.md"))
    return sorted(set(path for path in files if path.is_file()))


def normalize_target(source: Path, target: str) -> Path | None:
    target = target.strip().split(" ", 1)[0].strip("<>")
    parsed = urlparse(target)

    if parsed.scheme or parsed.netloc:
        return None
    if target.startswith("#"):
        return None

    path = unquote(parsed.path)
    if not path:
        return None

    candidate = (source.parent / path).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return candidate


def validate_links() -> list[str]:
    errors: list[str] = []
    for source in iter_markdown_files():
        text = source.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK.findall(text):
            candidate = normalize_target(source, target)
            if candidate is None:
                continue
            if not candidate.exists():
                errors.append(
                    f"Broken Markdown link: {source.relative_to(ROOT)} -> {target}"
                )
    return errors


def validate_index() -> list[str]:
    errors: list[str] = []
    if not DOCS_INDEX.is_file():
        return ["Missing canonical documentation index: docs/README.md"]

    index = DOCS_INDEX.read_text(encoding="utf-8")
    for relative_path in REQUIRED_DOCS:
        path = ROOT / relative_path
        if not path.is_file():
            errors.append(f"Missing required documentation: {relative_path}")
            continue
        if relative_path.removeprefix("docs/") not in index:
            errors.append(f"Documentation index does not reference: {relative_path}")
    return errors


def main() -> int:
    errors = validate_index() + validate_links()
    if errors:
        print("Documentation validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    markdown_count = len(iter_markdown_files())
    print(
        "Documentation validation passed: "
        f"{len(REQUIRED_DOCS)} required documents and {markdown_count} Markdown files checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
