# Documentation Synchronization

## Purpose

Documentation is part of the implementation contract. This layer keeps the engineering documentation map aligned with the repository and turns documentation drift into a CI failure instead of an after-the-fact cleanup task.

## What is synchronized

- The canonical `docs/README.md` index covers every implemented engineering layer.
- Internal Markdown links are validated automatically.
- Required documentation files are checked for existence.
- CI runs the validator on every push, pull request, and manual workflow dispatch.
- Documentation changes follow the same review and release path as application changes.

## Required documentation layers

The repository currently documents:

1. Architecture and component boundaries
2. ERD and custom DocTypes
3. OOAD and domain behavior
4. Business workflows
5. API and integration contracts
6. Security and RBAC
7. Performance and scalability
8. Observability and monitoring
9. Testing and E2E/integration validation
10. Deployment, production, and CI/CD hardening
11. Troubleshooting and operational runbooks

## Source-of-truth rules

- `README.md` is the portfolio-level project overview.
- `docs/README.md` is the canonical engineering documentation index.
- Detailed documents under each domain directory are authoritative for that domain.
- Code and configuration are authoritative for implemented runtime behavior; documentation must be updated whenever that behavior changes.
- Roadmap statements must not be presented as implemented functionality.

## CI enforcement

`python scripts/validate_documentation.py` performs two classes of checks:

1. **Index completeness** — all required documentation entries exist.
2. **Link integrity** — relative Markdown links resolve to files or directories in the repository.

This intentionally uses only the Python standard library so the check can run before application dependencies are installed.

## Change procedure

When adding or changing an implementation layer:

```text
Implementation change
        |
        v
Update domain documentation
        |
        v
Update docs/README.md index
        |
        v
Run validate_documentation.py
        |
        v
Run normal CI/test gates
        |
        v
Commit implementation + documentation together
```

## Operational expectation

A merged feature is considered documentation-complete when a maintainer can trace the change from the project overview to the detailed engineering document without encountering a broken link, a missing required document, or an undocumented cross-cutting operational dependency.
