# OpsLens on a Dell Windows 11 laptop: complete LOCAL project build guide

**Based on:** OpsLens Portable Project Runbook (14 October 2026).  
**Scope:** Complete the free, local synthetic workflow and portfolio documentation before GitHub.  
**Out of scope:** Real AWS calls, AWS spending, real infrastructure changes, real HTTP health checks, real restart/rollback, publishing to GitHub now. Those require separate steps and explicit consent where applicable.

## Milestone 0 - Prerequisites

Install VS Code (https://code.visualstudio.com/) and Python 3.11+ (https://www.python.org/downloads/windows/). In VS Code, install the *Python* extension published by Microsoft. In VS Code, **Terminal -> New Terminal -> PowerShell**:

```powershell
py -3 --version
python --version
```

If `py -3` is unavailable but `python --version` works, use `python` in its place below. After installing Python, close and reopen VS Code before retrying.

## Milestone 1 - Put the project files on disk

Download `opslens-windows-local-project.zip` supplied in this conversation and save it under **Downloads**. Create the intended project path and extract the ZIP:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\Documents\OpsLens" | Out-Null
Expand-Archive -LiteralPath "$HOME\Downloads\opslens-windows-local-project.zip" -DestinationPath "$HOME\Documents\OpsLens" -Force
Set-Location "$HOME\Documents\OpsLens"
Get-ChildItem -Force
```

Expected: `README.md`, `.gitignore`, `app`, `configs`, `tests`, `docs`, `reports`, `logs`, `posts`. If the ZIP was saved elsewhere, substitute its actual location.

In VS Code, **File -> Open Folder -> Documents -> OpsLens**, then open **Terminal -> New Terminal**. Run `Get-Location`; it should end in `\Documents\OpsLens`.

## Milestone 2 - Create and activate a Python environment

From project root in the **PowerShell terminal**:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip --version
```

If activation is blocked by PowerShell execution policy, either:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

or **without any policy changes** run `\.venv\Scripts\python.exe` everywhere this guide uses `python`.

Expected activated prompt: `(.venv) PS C:\Users\...\Documents\OpsLens>`.

No `pip install` is necessary: OpsLens uses Python's standard library only. **The `.venv` folder is local and is excluded from Git.**

## Milestone 3 - Study and execute the core code

Open `app/opslens.py` in VS Code. Its functions are:

| Function | What it does |
|---|---|
| `load_scenarios()` | Reads synthetic scenarios from `configs/scenarios.json` |
| `validate_scenario()` | Rejects invalid HTTP values, missing booleans or malformed evidence/change events |
| `run_scenario()` | Builds the full synthetic detect -> evidence -> change correlation -> guardrails -> simulate recovery -> verify -> report object |
| `save_report()` | Writes JSON reports, archives, and local JSONL audit events |
| `main()` | Parses command-line arguments and prints a readable result |

Open `configs/scenarios.json` to inspect the synthetic health checks, approval flags, allowlist and simulated changes.

List scenarios:

```powershell
python -m app.opslens --list-scenarios
```

Run the main incident (simulated HTTP 500 -> simulated HTTP 200):

```powershell
python -m app.opslens --scenario http-500-after-deploy
```

Expected key lines (IDs/paths vary):

```text
OpsLens LOCAL SIMULATION — AWS calls: 0, real restarts: 0
Initial HTTP status: 500
Changes within 15 min: 1 (causation unconfirmed)
Recovery result: verified
Final HTTP status: 200
Recovered: True
```

Open the generated report and the audit timeline:

```powershell
Get-Content .\reports\incident-report.json
Get-Content .\logs\audit.jsonl -Tail 12
Get-ChildItem .\reports\archive
```

Expected: a JSON report with `"simulated": true`, `"aws_connected": false`, evidence, diagnosis with root cause `unconfirmed`, guardrails, verification, nearby change correlation, timeline, and recommended preventive actions. Archived reports have distinct simulated incident IDs.

## Milestone 4 - Negative tests and incident correlation

Run one scenario at a time, inspect the printed output and `reports/incident-report.json`:

```powershell
python -m app.opslens --scenario approval-denied
python -m app.opslens --scenario failed-verification
python -m app.opslens --scenario missing-evidence
python -m app.opslens --scenario unapproved-action
python -m app.opslens --scenario healthy-service
python -m app.opslens --scenario unrelated-change
```

What you should see:

| Scenario | Recovery result | Why |
|---|---|---|
| `http-500-after-deploy` | `verified` | Approved synthetic restart and synthetic HTTP 200 |
| `approval-denied` | `blocked` | Approval not granted |
| `failed-verification` | `failed_verification` | Restart simulation does not fix HTTP 500 |
| `missing-evidence` | `blocked` | No diagnostic evidence |
| `unapproved-action` | `blocked` | Restart not on allowlist |
| `healthy-service` | `not_needed` | Already HTTP 200 |
| `unrelated-change` | `verified` | Recovery succeeds, but old deployment does not count as a nearby change |

Change-to-incident correlation searches only the simulated **15-minute window**. It expressly does **not** establish the cause of an incident.

## Milestone 5 - Automated testing

```powershell
python -m unittest discover -s tests -v
```

Expected final lines:

```text
Ran 14 tests in ...s

OK
```

If a test fails, **stop and fix it before moving on**. Test code is in `tests/test_opslens.py`, and the full plan is in `docs/test-plan.md`.

## Milestone 6 - Review documentation and prepare local demo

Read:

```text
README.md
docs/architecture.md
docs/decision-log.md
docs/test-plan.md
docs/project-status.md
posts/linkedIn-local-draft.md
```

In `docs/project-status.md`, check boxes only for steps **you actually completed on Windows**. Take local screenshots of the successful simulation and 14 passing tests. Don't publish synthetic output as real production evidence.

Optional: demonstrate editable scenario settings by changing only the values in `configs/scenarios.json`, such as `"simulated_recovery_succeeds": false`, rerun the scenario, verify `Recovered: False`, and revert the value to `true`. JSON requires lowercase `true` and `false` and correct commas/quotes.

## Local definition of done

- [ ] Python works on your Dell Windows 11 laptop.
- [ ] OpsLens lives in `Documents\OpsLens` and is open in VS Code.
- [ ] `.venv` works (activated or used by direct interpreter path).
- [ ] All seven scenarios run with their expected distinct outcomes.
- [ ] One successful scenario goes from synthetic HTTP 500 to synthetic HTTP 200.
- [ ] Denied/missing-evidence/failed-verification cases do not claim recovery.
- [ ] Change correlation explicitly does not prove root cause.
- [ ] 14 unit tests pass **on your laptop**.
- [ ] JSON incident reports, archived reports, and audit timeline have been inspected.
- [ ] README, architecture, test plan and decision log match actual behavior.
- [ ] No AWS provisioning/costs; no employer or real customer data used.

**Only after the above:** review `.gitignore`, create a new public GitHub repository, and push the project (to be handled in a later step, as you requested). The **AWS integration milestone is not part of the zero-cost local completion**: it needs explicit cost approval before any AWS resources are created.
