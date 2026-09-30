# Final Release / Production Readiness Audit

## Release identity

- Application version: **1.0.0**
- Release artifact: immutable Git-SHA-tagged container image
- Base image: \`frappe/erpnext:v16.36.0\`
- Production channel tag: \`production\` (publishing convenience only; deployments must use the immutable SHA tag)

## Repository gates

The repository now has deterministic gates for:

- Python compilation and Ruff linting.
- Documentation synchronization and internal Markdown links.
- Unit/quality, security, performance, observability, and E2E contract tests.
- Dependency vulnerability scanning with \`pip-audit\`.
- Secret detection with Gitleaks.
- GitHub Actions syntax validation with Actionlint.
- Production image SBOM/provenance generation and registry-backed provenance attestation.
- Immutable image-tag enforcement in the production deployment script.
- Immutable Git-SHA rollback enforcement.
- Production deployment script shell syntax.
- Critical runtime/deployment file presence.
- Release version consistency.
- Production compose bootstrap syntax safeguards.

Run the repository-only gate locally:

\`\`\`bash
python scripts/production_readiness_audit.py
\`\`\`

CI runs the same gate before the normal test/integration job completes.

## Release procedure

1. Confirm the intended commit is on \`main\`.
2. Wait for CI and security checks to pass.
3. Confirm the production image workflow published the commit-SHA image.
4. Record the image digest, attestation, and workflow run URL as release evidence.
5. Take a fresh application/database/files backup.
6. Perform the staging smoke test against the exact image SHA.
7. Deploy the exact image SHA to the protected production environment.
8. Run the production health check and verify:
   - HTTP reachability
   - Frappe/ERPNext login
   - custom app installation
   - database connectivity
   - background worker activity
   - representative API/report/dashboard behavior
9. Monitor 5xx, latency, worker failures, database capacity, integration failures, and backup status.
10. Keep the previous immutable image SHA and compatible database backup available for rollback.

## Rollback procedure

Use the previous immutable Git SHA:

\`\`\`bash
./deployment/production/rollback.sh <40-character-git-sha>
./deployment/production/healthcheck.sh
\`\`\`

Do not rebuild an old commit during an incident. A rebuild can resolve dependencies or base-image layers differently from the originally published artifact.

Database rollback requires special care: application image rollback and database schema rollback are separate operations. Prefer a forward-compatible migration or restore a verified compatible backup rather than assuming schema changes are reversible.

## External production gates

A repository audit cannot verify deployment infrastructure that is not present in source control. Before declaring an environment production-ready, the operator must verify:

| Gate | Evidence |
|---|---|
| CI | Green required GitHub Actions checks |
| Image | Published immutable SHA tag and digest |
| Attestation | Verifiable provenance/SBOM attestation |
| Staging | Smoke test against exact release image |
| Database | Fresh backup plus successful restore drill |
| TLS/DNS | Valid certificate, hostname, HTTPS redirect, renewal path |
| Secrets | Runtime secret store/site configuration only |
| Access | Protected production environment and reviewer approval |
| Monitoring | Logs, request IDs, 5xx/latency, worker and DB alerts |
| Rollback | Previous image SHA and compatible backup identified |
| Operations | Runbooks and incident response available |

## Release decision record

The repository is **release-candidate ready at source level** after the deterministic audit passes. This document deliberately does not claim that a live production environment has been verified; infrastructure evidence must be captured during the actual deployment.
