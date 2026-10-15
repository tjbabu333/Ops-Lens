"""OpsLens: safe, local-only simulated incident-to-recovery workflow.

No live HTTP requests, AWS SDK calls, cloud resource creation, or real restarts.
Every input and observation in this program is SYNTHETIC.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_FILE = PROJECT_ROOT / "configs" / "scenarios.json"
REPORT_DIR = PROJECT_ROOT / "reports"
AUDIT_DIR = PROJECT_ROOT / "logs"
SCHEMA_VERSION = "1.0"
ALLOWED_ACTION = "simulated_restart"
CHANGE_WINDOW_MINUTES = 15


def utc_time(value: datetime) -> str:
    """Return an ISO 8601 UTC timestamp."""
    if value.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat()


def load_scenarios(path: Path = SCENARIOS_FILE) -> dict:
    """Load named synthetic incident configurations."""
    with Path(path).open("r", encoding="utf-8") as stream:
        scenarios = json.load(stream)
    if not isinstance(scenarios, dict) or not scenarios:
        raise ValueError("Scenario file must contain a non-empty JSON object")
    return scenarios


def validate_scenario(scenario: dict) -> None:
    """Reject malformed/unsafe simulation configurations."""
    if not isinstance(scenario, dict):
        raise ValueError("Scenario must be a JSON object")
    if not isinstance(scenario.get("service"), str) or not scenario["service"].strip():
        raise ValueError("Scenario requires a non-empty service string")
    status = scenario.get("initial_http_status")
    if type(status) is not int or not 100 <= status <= 599:
        raise ValueError("initial_http_status must be an integer from 100 to 599")
    if status not in (200, 500, 502, 503):
        raise ValueError("This local demo supports HTTP 200, 500, 502 or 503 only")
    evidence = scenario.get("evidence")
    if not isinstance(evidence, list) or any(
        not isinstance(item, dict)
        or not isinstance(item.get("type"), str)
        or not isinstance(item.get("detail"), str)
        for item in evidence
    ):
        raise ValueError("evidence must be a list of {type, detail} objects")
    for key in ("simulated_approval", "simulated_recovery_succeeds"):
        if type(scenario.get(key)) is not bool:
            raise ValueError(f"{key} must be true or false")
    if not isinstance(scenario.get("allowed_actions"), list) or any(
        not isinstance(action, str) for action in scenario["allowed_actions"]
    ):
        raise ValueError("allowed_actions must be a list of strings")
    changes = scenario.get("changes", [])
    if not isinstance(changes, list):
        raise ValueError("changes must be a list")
    for change in changes:
        if (not isinstance(change, dict)
            or not isinstance(change.get("change_id"), str)
            or type(change.get("minutes_before_incident")) is not int
            or change["minutes_before_incident"] < 0):
            raise ValueError("Each change needs change_id and nonnegative minutes_before_incident")


def run_scenario(scenario_id: str, scenario: dict, now: datetime | None = None) -> dict:
    """Pure simulation; constructs a report and does not write files or call networks."""
    validate_scenario(scenario)
    now = now or datetime.now(timezone.utc)
    timestamp = utc_time(now)
    initial = scenario["initial_http_status"]
    incident_detected = initial >= 500
    timeline = []

    def event(step: str, detail: str) -> None:
        timeline.append({"timestamp": timestamp, "step": step, "detail": detail})

    event("detect", f"Synthetic health check returned HTTP {initial}")
    evidence = list(scenario["evidence"])
    event("collect_evidence", f"Collected {len(evidence)} synthetic evidence item(s)")

    all_changes = [
        {
            "change_id": item["change_id"],
            "timestamp": utc_time(now - timedelta(minutes=item["minutes_before_incident"])),
            "minutes_before_incident": item["minutes_before_incident"],
        }
        for item in scenario.get("changes", [])
    ]
    nearby_changes = [
        change for change in all_changes
        if 0 <= change["minutes_before_incident"] <= CHANGE_WINDOW_MINUTES
    ] if incident_detected else []
    event("correlate_changes", f"Found {len(nearby_changes)} change(s) within 15 minutes")

    block_reasons = []
    if not incident_detected:
        block_reasons.append("Service is healthy; recovery not needed")
    if not evidence:
        block_reasons.append("No diagnostic evidence; automatic recovery prohibited")
    if not scenario["simulated_approval"]:
        block_reasons.append("Simulated operator approval was not granted")
    if ALLOWED_ACTION not in scenario["allowed_actions"]:
        block_reasons.append("Simulated restart is not in the action allowlist")
    permitted = incident_detected and not block_reasons
    event("guardrails", "Recovery permitted" if permitted else "; ".join(block_reasons))

    attempted = False
    recovered = False
    final = initial
    if permitted:
        attempted = True
        event("recovery", "Performed SIMULATED restart (no real systems changed)")
        final = 200 if scenario["simulated_recovery_succeeds"] else initial
        recovered = final == 200
        event("verify", f"Synthetic post-recovery health check returned HTTP {final}")
        recovery_result = "verified" if recovered else "failed_verification"
    elif not incident_detected:
        recovery_result = "not_needed"
    else:
        recovery_result = "blocked"

    if incident_detected:
        event("close_or_escalate", "Simulation resolved" if recovered else "Escalation recommended")

    return {
        "schema_version": SCHEMA_VERSION,
        "incident_id": f"SIM-{uuid4().hex[:10].upper()}",
        "simulated": True,
        "aws_connected": False,
        "scenario_id": scenario_id,
        "service": scenario["service"],
        "created_at": timestamp,
        "incident_detected": incident_detected,
        "initial_http_status": initial,
        "final_http_status": final,
        "evidence": evidence,
        "change_correlation": {
            "window_minutes": CHANGE_WINDOW_MINUTES,
            "nearby_changes": nearby_changes,
            "temporal_association_detected": bool(nearby_changes),
            "causation_confirmed": False,
            "explanation": "Timing alone cannot prove a deployment/change caused an incident.",
        },
        "diagnosis": {
            "hypothesis": "Possible application/service failure" if incident_detected else "No failure observed",
            "root_cause_status": "unconfirmed" if incident_detected else "not_applicable",
            "limitations": [
                "All inputs are synthetic; no actual HTTP service was contacted.",
                "No infrastructure was inspected or changed.",
                "Temporal change proximity does not prove causation.",
            ],
        },
        "guardrails": {
            "simulated_approval": scenario["simulated_approval"],
            "allowlisted": ALLOWED_ACTION in scenario["allowed_actions"],
            "evidence_present": bool(evidence),
            "blocked_reasons": block_reasons,
            "permitted": permitted,
        },
        "recovery": {
            "action": ALLOWED_ACTION,
            "attempted": attempted,
            "result": recovery_result,
            "verified": recovered,
        },
        "recovered": recovered,
        "verification": {"simulated_health_check_status": final, "passed": recovered},
        "timeline": timeline,
        "preventive_actions": [
            "Add verified telemetry before enabling any real recovery action.",
            "Require explicit approval, least privilege and an audited action allowlist.",
            "Correlate deployments and incidents without asserting unsupported causation.",
        ],
    }


def save_report(report: dict, report_dir: Path = REPORT_DIR, audit_dir: Path = AUDIT_DIR) -> Path:
    """Write readable latest report, archived report, and append-only local audit events."""
    report_dir = Path(report_dir)
    audit_dir = Path(audit_dir)
    archive_dir = report_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    body = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    latest = report_dir / "incident-report.json"
    latest.write_text(body, encoding="utf-8")
    (archive_dir / f"{report['incident_id']}.json").write_text(body, encoding="utf-8")
    audit_path = audit_dir / "audit.jsonl"
    with audit_path.open("a", encoding="utf-8") as audit:
        for item in report["timeline"]:
            audit.write(json.dumps({
                "incident_id": report["incident_id"],
                "simulated": True,
                **item,
            }, ensure_ascii=False) + "\n")
    return latest


def main() -> None:
    parser = argparse.ArgumentParser(description="OpsLens safe local-only incident simulator")
    parser.add_argument("--scenario", default="http-500-after-deploy", help="Scenario name")
    parser.add_argument("--list-scenarios", action="store_true", help="List built-in synthetic scenarios")
    args = parser.parse_args()
    try:
        scenarios = load_scenarios()
        if args.list_scenarios:
            print("Available SYNTHETIC scenarios:")
            for name in scenarios:
                print(f"  {name}")
            return
        if args.scenario not in scenarios:
            parser.error(f"Unknown scenario '{args.scenario}'. Use --list-scenarios")
        report = run_scenario(args.scenario, scenarios[args.scenario])
        saved_to = save_report(report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(status=1, message=f"OpsLens error: {exc}\n")
    print("OpsLens LOCAL SIMULATION — AWS calls: 0, real restarts: 0")
    print(f"Scenario: {args.scenario}")
    print(f"Incident ID: {report['incident_id']}")
    print(f"Initial HTTP status: {report['initial_http_status']}")
    print(f"Synthetic evidence items: {len(report['evidence'])}")
    print(f"Changes within 15 min: {len(report['change_correlation']['nearby_changes'])} (causation unconfirmed)")
    print(f"Recovery result: {report['recovery']['result']}")
    print(f"Final HTTP status: {report['final_http_status']}")
    print(f"Recovered: {report['recovered']}")
    print(f"Report: {saved_to}")
    print(f"Audit: {AUDIT_DIR / 'audit.jsonl'}")


if __name__ == "__main__":
    main()
