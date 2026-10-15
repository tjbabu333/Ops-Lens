# OpsLens local architecture

```text
configs/scenarios.json  (synthetic input)
        |
        v
Python CLI (app/opslens.py)
        |
        +--> validate synthetic scenario
        +--> detect health-check failure (HTTP 500/502/503)
        +--> collect synthetic evidence
        +--> correlate synthetic change timestamp within 15 min
        |       NOTE: timing alone does not establish causation
        +--> guardrails: evidence + simulated approval + action allowlist
        +--> simulate restart if allowed; NEVER restart real systems
        +--> verify simulated HTTP 200; otherwise escalate
        |
        +--> reports/incident-report.json and reports/archive/*.json
        +--> logs/audit.jsonl
        |
        v
Unit tests (14) and repeatable terminal demo
```

## Implemented

Local deterministic scenario behaviors, synthetic evidence and changes, controlled simulated recovery, explicit post-action verification, JSON schema version 1.0, timeline, archive and audit log, tests.

## Not implemented

AWS CloudWatch/EventBridge/SNS/Lambda/SSM, IAM roles, real HTTP checks, live incidents, live restarts, alert delivery, true root-cause identification, distributed tracing, dashboard, rollback. Any AWS design requires a separately approved cost plan. The use of `AWS` in the product name is aspirational until that integration is built and tested.

## Safety

This program imports only Python's standard library and makes no network calls. Reports always include `simulated: true` and `aws_connected: false`. Approvals are values in local scenario fixtures, not real operator approvals.
