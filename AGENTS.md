# AGENTS.md

Project: **CampusLend** — campus lending platform (FastAPI + React/JSX).

Read `.github/copilot-instructions.md` first. It holds the full operating loop and hard rules.

Essentials (details live in the files above):
1. Start every session by reading `docs/PROGRESS.md` (`NEXT ACTION`) and the current milestone in `docs/ROADMAP.md`.
2. Build in batches of at most 5 files; after each batch update `docs/FILE_REGISTRY.md` and run the area checks.
3. Never invent endpoints, fields or packages — `docs/API_CONTRACT.md` and `docs/DATA_MODEL.md` are the source of truth.
4. Safety rules in `docs/SAFETY_SPEC.md` outrank convenience. Receiver shows the code, giver enters it.
5. Finish a milestone only after `python scripts/verify.py` passes. Update `docs/PROGRESS.md` before stopping.
6. Ideas outside the current milestone go in `docs/IMPROVEMENTS.md`, not into the code.
