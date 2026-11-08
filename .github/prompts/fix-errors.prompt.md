---
description: Systematically fix failing checks, errors or the latest audit blockers
agent: agent
---
Fix the current problems in CampusLend methodically.

1. Gather the failures: run `python scripts/verify.py`, read `docs/VERIFY_LAST_RUN.md`, the newest file in `docs/audits/`, and any `UNRESOLVED` entries in `docs/ERRORS_LOG.md`. If I pasted an error, start with that.
2. Order them: blockers first, then failing tests, then lint, then needs-fix items.
3. For each problem: reproduce it, find the **root cause** (not the symptom), fix it, add or adjust a test that would have caught it, re-run the check.
4. Do not weaken tests, loosen lint rules or delete code to get green. If a requirement is wrong, change the spec and log it in `docs/DECISIONS.md`.
5. After three different failed attempts at one problem, write it as `UNRESOLVED` in `docs/ERRORS_LOG.md` with the evidence and hypotheses, then move on to the next problem.
6. Log every non-trivial fix in `docs/ERRORS_LOG.md` using the format from the `progress-tracking` skill; update `docs/FILE_REGISTRY.md` and `docs/PROGRESS.md`.

Finish with `python scripts/verify.py` and report the before/after counts.
