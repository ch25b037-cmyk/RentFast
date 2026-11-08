---
applyTo: "docs/**"
description: Rules for editing the tracking and specification documents
---
# Editing docs

- `PROGRESS.md`: the session log is **append-only**; never rewrite history. Keep `NEXT ACTION` to one short paragraph a fresh session can act on without any chat context.
- `FILE_REGISTRY.md`: one row per file; update the row in place when a file changes. Never list files that do not exist.
- `ERRORS_LOG.md`: append new entries at the bottom with the next `E-###`. Mark unresolved ones `UNRESOLVED`.
- `IMPROVEMENTS.md`: add ideas, do not implement them mid-milestone. Keep the impact/effort columns honest.
- `DECISIONS.md`: append only. To reverse a decision add a new row that supersedes it.
- Spec docs (`API_CONTRACT`, `DATA_MODEL`, `SAFETY_SPEC`, `DESIGN_SYSTEM`, `ARCHITECTURE`): change them in the same edit as the code that deviates, and add a DECISIONS row.
- Files in `docs/audits/` are generated reports: never edit them by hand after creation.
- Use exact formats from the `progress-tracking` skill. Dates are ISO (`YYYY-MM-DD`).
