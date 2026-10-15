"""Tests use simulated configs only; no network or AWS access."""
import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.opslens import load_scenarios, run_scenario, save_report, validate_scenario

FIXED_TIME = datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc)


class OpsLensTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios = load_scenarios()

    def run_named(self, name):
        return run_scenario(name, copy.deepcopy(self.scenarios[name]), now=FIXED_TIME)

    def test_http_500_recovers_and_verifies(self):
        report = self.run_named("http-500-after-deploy")
        self.assertEqual(report["initial_http_status"], 500)
        self.assertEqual(report["final_http_status"], 200)
        self.assertTrue(report["recovered"])
        self.assertEqual(report["recovery"]["result"], "verified")

    def test_recovery_not_attempted_without_approval(self):
        report = self.run_named("approval-denied")
        self.assertFalse(report["recovery"]["attempted"])
        self.assertEqual(report["final_http_status"], 503)
        self.assertEqual(report["recovery"]["result"], "blocked")

    def test_failed_verification_not_called_recovered(self):
        report = self.run_named("failed-verification")
        self.assertTrue(report["recovery"]["attempted"])
        self.assertEqual(report["recovery"]["result"], "failed_verification")
        self.assertFalse(report["recovered"])

    def test_missing_evidence_blocks_recovery(self):
        report = self.run_named("missing-evidence")
        self.assertFalse(report["guardrails"]["evidence_present"])
        self.assertFalse(report["recovery"]["attempted"])

    def test_nonallowlisted_action_is_blocked(self):
        report = self.run_named("unapproved-action")
        self.assertFalse(report["guardrails"]["allowlisted"])
        self.assertFalse(report["recovery"]["attempted"])

    def test_healthy_service_not_restarted(self):
        report = self.run_named("healthy-service")
        self.assertFalse(report["incident_detected"])
        self.assertEqual(report["recovery"]["result"], "not_needed")
        self.assertFalse(report["recovery"]["attempted"])

    def test_nearby_deployment_detected(self):
        report = self.run_named("http-500-after-deploy")
        self.assertTrue(report["change_correlation"]["temporal_association_detected"])
        self.assertEqual(len(report["change_correlation"]["nearby_changes"]), 1)

    def test_old_deployment_not_correlated(self):
        report = self.run_named("unrelated-change")
        self.assertFalse(report["change_correlation"]["temporal_association_detected"])

    def test_change_does_not_prove_causation(self):
        report = self.run_named("http-500-after-deploy")
        self.assertFalse(report["change_correlation"]["causation_confirmed"])
        self.assertEqual(report["diagnosis"]["root_cause_status"], "unconfirmed")

    def test_malformed_http_status_rejected(self):
        scenario = copy.deepcopy(self.scenarios["http-500-after-deploy"])
        scenario["initial_http_status"] = "500"
        with self.assertRaises(ValueError):
            validate_scenario(scenario)

    def test_malformed_change_rejected(self):
        scenario = copy.deepcopy(self.scenarios["http-500-after-deploy"])
        scenario["changes"] = [{"change_id": "X", "minutes_before_incident": -1}]
        with self.assertRaises(ValueError):
            validate_scenario(scenario)

    def test_missing_approval_config_rejected(self):
        scenario = copy.deepcopy(self.scenarios["http-500-after-deploy"])
        del scenario["simulated_approval"]
        with self.assertRaises(ValueError):
            validate_scenario(scenario)

    def test_report_and_audit_created(self):
        report = self.run_named("http-500-after-deploy")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = save_report(report, base / "reports", base / "logs")
            self.assertTrue(path.exists())
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["incident_id"], report["incident_id"])
            archive = base / "reports" / "archive" / f"{report['incident_id']}.json"
            self.assertTrue(archive.exists())
            audit = base / "logs" / "audit.jsonl"
            lines = audit.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), len(report["timeline"]))
            self.assertTrue(all(json.loads(line)["simulated"] for line in lines))

    def test_no_aws_calls_reported(self):
        report = self.run_named("http-500-after-deploy")
        self.assertTrue(report["simulated"])
        self.assertFalse(report["aws_connected"])


if __name__ == "__main__":
    unittest.main()
