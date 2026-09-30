# Incident Response Runbook

## Incident lifecycle

`Detect -> Triage -> Contain -> Recover -> Verify -> Communicate -> Review`

## Severity guidance

### Critical

Use when the ERP site is broadly unavailable, critical business transactions cannot complete, or there is a credible data-integrity/security incident.

Immediate actions: stabilize service, preserve evidence, restrict risky changes, and escalate to the production owner.

### High

Use when a major workflow, integration, or user population is materially degraded but core service remains available.

Prioritize containment and a reversible workaround.

### Normal

Use for isolated defects, non-critical report failures, or operational issues with an established workaround.

## Incident record

Every incident should capture:

```text
Incident ID:
Start time (UTC):
Environment/site:
Severity:
Affected capability:
Detection source:
Current release/commit:
Correlation/request ID(s):
User/business impact:
Evidence collected:
Containment action:
Recovery action:
Verification result:
Root cause:
Follow-up actions:
Owner:
```

## Evidence handling

Collect the smallest useful log window. Redact secrets and unnecessary personal data. Preserve exact error messages and tracebacks where safe because paraphrasing can remove diagnostic details.

## Communication cadence

For an active production incident, communicate facts separately from hypotheses:

- **Confirmed:** directly observed evidence.
- **Suspected:** working hypothesis requiring validation.
- **Next action:** concrete diagnostic or mitigation step.
- **Risk:** known possible side effects.

Do not claim resolution until verification has succeeded.

## Post-incident review

Document:

1. technical root cause;
2. contributing conditions;
3. why existing tests/monitoring did not catch it;
4. exact remediation;
5. prevention work;
6. runbook/documentation updates.

Link follow-up engineering work to the incident record so operational knowledge becomes part of the maintained system.
