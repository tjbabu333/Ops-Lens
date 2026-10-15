# Windows 11 setup: PowerShell (Dell laptop)

The commands below are executed inside **VS Code -> Terminal -> New Terminal (PowerShell)**.

## Verify Python

```powershell
py -3 --version
python --version
```

If both fail, install a supported Python 3 from https://www.python.org/downloads/windows/ and reopen the terminal. `py -3` may not be available for every installation; `python` works as an alternative if in PATH.

## Prepare a local virtual environment

From the project root (`README.md` must be visible):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Or avoid activation entirely using `\.venv\Scripts\python.exe` instead of `python`. This does not require policy changes.

## Execute

```powershell
python -m app.opslens --list-scenarios
python -m app.opslens --scenario http-500-after-deploy
python -m unittest discover -s tests -v
Get-Content .\reports\incident-report.json
Get-Content .\logs\audit.jsonl -Tail 10
```

## Scenario commands

```powershell
python -m app.opslens --scenario approval-denied
python -m app.opslens --scenario failed-verification
python -m app.opslens --scenario missing-evidence
python -m app.opslens --scenario unapproved-action
python -m app.opslens --scenario healthy-service
python -m app.opslens --scenario unrelated-change
```

Last-run report gets replaced each time; archived reports remain under `reports/archive`.

## Troubleshooting

- `py` not recognized: try `python`; if missing, install Python and reopen terminal.
- `No module named app`: run from **OpsLens project root**, not inside `app` or `tests`.
- Scripts disabled: use the temporary `Set-ExecutionPolicy` command or direct `.venv` Python executable.
- Nothing appeared under reports: check terminal error before continuing.
