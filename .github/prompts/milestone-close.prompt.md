---
description: Formally close a milestone - verify acceptance lines, run all checks, audit, update progress
agent: agent
---
Close milestone **${input:milestone:M1}**.

1. Open the milestone in `docs/ROADMAP.md`. For every acceptance line, show the evidence (test name, command output, or a quick manual check you performed). Mark each true or false.
2. Run `python scripts/verify.py --strict` (warnings count as failures; the frontend build runs). Run backend and frontend area checks too.
3. Run the `file-audit` skill and write the audit report.
4. Confirm every SAFETY_SPEC row assigned to this milestone has passing tests.
5. If anything is false or red, do **not** close: fix it (or list it clearly) and stop.
6. If everything is true, tick the milestone in `docs/PROGRESS.md`, rewrite `NEXT ACTION` to start the next milestone, append the session-log line, and make sure `docs/FILE_REGISTRY.md` is current.
7. If git is initialised, create one commit `M<n>: close milestone` when all is green.
