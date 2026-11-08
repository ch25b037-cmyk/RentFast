---
description: Implement one item from IMPROVEMENTS.md safely, with tests and tracking
agent: agent
---
Implement improvement **${input:imp:IMP-001}** from `docs/IMPROVEMENTS.md`.

1. Read the row, the relevant specs and the code it touches. Confirm all roadmap milestones it depends on are closed.
2. Set its status to `doing`. Write a short plan in `docs/PROGRESS.md` under "In progress".
3. Implement it with the matching skill, tests included. Update spec documents if behaviour changes and add a row to `docs/DECISIONS.md`.
4. Run all area checks and `python scripts/verify.py`.
5. Set the status to `done` (or `dropped` with the reason). Update the registry and progress files.

One improvement per run. If you discover new ideas, add them as new rows; do not implement them.
