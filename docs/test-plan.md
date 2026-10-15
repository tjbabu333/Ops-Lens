# OpsLens test plan

Run `python -m unittest discover -s tests -v` after activating `.venv`.

1. HTTP 500 with synthetic approval -> restart simulated, HTTP 200, recovered true.
2. Approval denied -> no restart.
3. Recovery fails -> postcheck fails, recovered false.
4. Evidence missing -> automatic recovery blocked.
5. Action excluded from allowlist -> no restart.
6. Healthy service -> no unnecessary restart.
7. Nearby deployment -> temporal association detected.
8. Old deployment -> no temporal association.
9. Nearby change -> causation still never asserted.
10. Malformed status -> reject early.
11. Malformed change -> reject early.
12. Missing approval value -> reject early.
13. Report/archive/audit files -> all created and parsable.
14. Simulation flags -> no AWS connection claimed.

Also perform a manual CLI demo with all seven scenarios. Screenshot results only after verifying them on your Windows laptop.
