# OpsLens - AWS Incident-to-Recovery Platform (LOCAL EDITION)

**Status:** Local milestones 1, 2, 3 and documentation milestone 5 are implemented in this training project. AWS integration is **NOT implemented** and requires explicit approval of a costed design. The repository/GitHub publication has NOT been completed for you.

OpsLens is a synthetic incident-to-recovery workflow built with only the Python standard library. It demonstrates detection, evidence capture, change-to-incident temporal correlation, approval/allowlist/evidence guardrails, simulated restart, post-action verification, JSON incident reports, and an auditable event timeline.

> SAFETY: Runs locally. **Zero AWS calls, zero cloud resources, zero real service restarts, zero real HTTP requests.** Every outcome is a simulation. Change proximity does **not** prove the change caused the incident. Root cause is unconfirmed.

## Windows 11 quick start (PowerShell in VS Code)

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m app.opslens --list-scenarios
python -m app.opslens --scenario http-500-after-deploy
python -m unittest discover -s tests -v
Get-Content .\reports\incident-report.json
```

If activation is disallowed, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for the current PowerShell session, or run `\.venv\Scripts\python.exe -m app.opslens` directly without activation. `py -3` may be replaced by `python` if Python is configured that way.

No external packages are needed for the local simulator.

## Scenarios

- `http-500-after-deploy`: simulated HTTP 500, synthetic evidence, nearby deployment, guarded recovery, simulated HTTP 200
- `approval-denied`: simulated operator does not approve action
- `failed-verification`: simulated restart occurs but the service still returns a 500
- `missing-evidence`: no diagnostic evidence; automatic recovery blocked
- `unapproved-action`: action not on allowlist; recovery blocked
- `healthy-service`: HTTP 200; no restart attempted
- `unrelated-change`: an older deployment is not considered a nearby change

Run with `python -m app.opslens --scenario NAME`. See all via `--list-scenarios`.

## Output (generated, kept local)

- `reports/incident-report.json`: newest simulated incident report
- `reports/archive/SIM-....json`: archived report for each run
- `logs/audit.jsonl`: local append-only audit trail of timeline events

These outputs are excluded from Git by `.gitignore` to avoid accidentally publishing private logs. The app uses only synthetic data, but the policy remains strict by design.

## Tests

```powershell
python -m unittest discover -s tests -v
```

There are 14 unit tests covering positive and negative scenarios, guardrails, correlation limitations, malformed inputs and file output.

## Design and roadmap

See `docs/architecture.md`, `docs/decision-log.md`, `docs/test-plan.md`, `docs/windows-setup.md`, and `docs/project-status.md`. AWS integrations, real observability, dynamic service checks, infrastructure changes, real approvals and real root-cause determination are **future work** and are not claimed to be implemented.
