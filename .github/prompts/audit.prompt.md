---
description: Full audit of every file created so far - checks, registry, contract drift, safety coverage, report
agent: agent
---
Act as the **Auditor** (see `.github/agents/auditor.agent.md`). Run the `file-audit` skill end to end on the whole repository.

- Run every automated check yourself; do not trust claims in `docs/PROGRESS.md`.
- Reconcile `docs/FILE_REGISTRY.md` with the real files.
- Compare routers, client API modules and `docs/API_CONTRACT.md`.
- Check SAFETY_SPEC rows for every finished milestone have tests that exist and pass.
- Write the report to `docs/audits/AUDIT_<today>_<current milestone>.md`.

Do not modify source code. List blockers with file, line, reason and suggested fix. End with a five-line summary.
