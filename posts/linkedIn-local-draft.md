# LinkedIn draft - publish only after personally verifying the program

A restart is not proof of recovery. An incident report should show what happened, what evidence was available, what action was permitted, and whether a post-action health check actually passed.

I built a local Python simulation called OpsLens to practice that incident-to-recovery workflow. The demo uses **synthetic** HTTP health checks, evidence, deployment timestamps, approval/allowlist checks, simulated recovery, verification and a JSON incident report with an audit timeline.

This is deliberately **not** a live AWS implementation. I have made no real infrastructure changes or AWS calls. The project includes negative tests for denied recovery, failed verification and missing evidence, and it never claims a nearby deployment is a proven root cause.

[Add your verified test results and actual public repository link ONLY after testing and publishing.]

#SRE #DevOps #Python #ReliabilityEngineering
