# OpsLens engineering decision log

| Decision | Why | Trade-off |
|---|---|---|
| Local-first standard library | Zero budget, fast reproducible setup | No real cloud telemetry |
| Synthetic HTTP status | Demonstrates workflow with no dependency on a service | Does not measure real availability |
| Evidence required for recovery | Safer than blind restarts | Missing evidence blocks automation |
| Synthetic approval and action allowlist | Teaches approval gating | Does not model real identity verification |
| Post-recovery health check | A restart alone isn't proof of recovery | Simulated check only |
| 15-minute change window | Demonstrates temporal association | Correlation is never treated as causation |
| JSON report + JSONL audit log | Inspectable, machine-readable evidence | Locally stored, no central retention or integrity controls |
| Ignore generated artifacts in Git | Prevents accidental leak of incident data | Users must run demo to see fresh reports |
| No AWS without explicit consent | Avoid charges and unexpected cloud changes | Cloud milestone deliberately deferred |
