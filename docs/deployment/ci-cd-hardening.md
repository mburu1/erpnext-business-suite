# CI/CD Hardening

## Purpose

The repository treats CI/CD as a controlled software supply-chain boundary. The pipeline must prove that source changes are syntactically valid, tests pass, dependencies are reviewable, secrets are not committed, workflow files are valid, and production images are traceable to an exact Git commit.

## Implemented controls

- Least-privilege workflow permissions (`contents: read` by default).
- Explicit `packages: write` only for the production image publisher.
- Workflow concurrency prevents stale duplicate validation and production builds.
- Job-level timeouts prevent hung runners from consuming resources indefinitely.
- Deterministic Ruff version and Python version are declared in CI.
- Pip caching is enabled for repeatable, faster validation.
- Repository hygiene checks reject committed local production configuration and unresolved merge markers.
- `pip-audit` checks Python project dependencies for known vulnerabilities.
- Gitleaks checks the repository for committed secret material.
- Actionlint validates GitHub Actions workflow syntax.
- Dependabot monitors GitHub Actions and Python dependencies weekly.
- Production images are tagged by immutable Git SHA as well as the `production` channel tag.
- OCI provenance and SBOM attestations are emitted by Buildx.
- Production image metadata is retained as a short-lived GitHub Actions artifact.

## Pull request gate

Every pull request runs the deterministic CI suite and supply-chain checks. A pull request should not be merged unless the required status checks are green.

Recommended repository settings:

1. Protect `main` with a ruleset or branch protection rule.
2. Require pull requests before merging.
3. Require the CI, security, and action-lint checks to pass.
4. Require branches to be up to date before merging when practical.
5. Disable force pushes and branch deletion for `main`.
6. Require signed commits if the team's GitHub policy supports it.
7. Restrict who can bypass the ruleset.

These repository settings are intentionally not encoded as application code because they are GitHub repository governance controls.

## Production release model

The workflow publishes a production image from `main` only for application/deployment changes or an explicit manual dispatch. The immutable SHA tag is the release reference; `production` is a movable channel tag.

Production deployment itself should use a protected GitHub Environment (for example `production`) with required reviewers and environment-scoped secrets. The deployment target should consume the immutable SHA image rather than relying on an unqualified `production` tag.

## Rollback

Rollback should select a previously published SHA image from the GitHub Container Registry and redeploy that exact digest/tag. Do not rebuild an old commit during an incident: rebuilding can change dependency resolution or the base image.

## Supply-chain maintenance

Dependabot creates update pull requests for GitHub Actions and the Python application dependency set. Dependency changes still pass the normal CI and security gates before merge.

## Operational evidence

For each production image build, retain:

- Git commit SHA
- ERPNext base image reference
- Published image SHA tag
- Build provenance
- SBOM
- CI run URL

This makes a production artifact traceable from deployment back to source control.
