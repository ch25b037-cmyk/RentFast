---
description: Build a whole milestone (e.g. M3) task by task with checks after every batch
agent: agent
---
Build milestone **${input:milestone:M1, M2, M3 ...}** of CampusLend.

1. Read `docs/PROGRESS.md`, then that milestone's section in `docs/ROADMAP.md` and every spec row it references (`API_CONTRACT`, `DATA_MODEL`, `SAFETY_SPEC` S-xx rows, `DESIGN_SYSTEM` screens).
2. Refuse to start if the previous milestone is not marked closed in `docs/PROGRESS.md`; say so and stop.
3. Break the milestone into steps of at most 5 files each and write them under "In progress" in `docs/PROGRESS.md`.
4. For each step: build (use the matching skill) → run area checks → fix → register files → update progress. Do not move on while a check is red.
5. Keep going until every acceptance line of the milestone is true or you reach a stop condition from `copilot-instructions.md` §5. If you run out of room, update `NEXT ACTION` in PROGRESS.md so the `/resume` prompt can continue.
6. At the end run `python scripts/verify.py` and the `file-audit` skill. Report: acceptance lines (true/false), check results, anything parked in IMPROVEMENTS.

Do not add features outside this milestone.
