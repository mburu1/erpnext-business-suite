# Deployment Rollback Runbook

## Trigger conditions

Consider rollback when a deployment introduces a reproducible regression affecting availability, data integrity, authentication, critical workflows, or integrations and mitigation cannot safely contain it.

## 1. Stop the change

- Stop further rollout.
- Record the deployed commit/release.
- Capture logs, correlation IDs, and failing requests before restarting services.
- Identify whether migrations or data changes have already run.

## 2. Determine rollback type

### Application-only regression

If the release changed application code without an incompatible schema/data migration, restore the previously verified application release using the normal deployment mechanism.

### Migration/schema regression

Do **not** blindly roll back code across a migration boundary. First determine whether the migration is backward-compatible and whether data has been transformed. Use an approved database recovery/migration procedure when it is not.

## 3. Restore the known-good release

Use the deployment process documented for the target environment. The repository's deployment workflow should remain an explicit controlled step; production rollback must not depend on an ad-hoc local checkout.

After restoring the release:

```bash
bench --site <site-name> migrate
bench --site <site-name> clear-cache
```

Run only the commands appropriate to the installed release and environment. A rollback should not introduce a migration mismatch.

## 4. Validate

Perform, at minimum:

- health check
- authentication check
- representative read operation
- representative write/workflow operation in a safe test context
- integration queue check
- error-rate/log review

## 5. Close the incident

Record:

- failed release/commit
- restored release/commit
- migration state
- user impact window
- root cause or current hypothesis
- validation evidence
- follow-up corrective action

Never delete the failed deployment evidence before the incident review is complete.
