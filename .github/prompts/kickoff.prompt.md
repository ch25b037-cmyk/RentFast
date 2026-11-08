---
description: First-ever run. Orient on all docs, confirm understanding, then complete milestone M0 (scaffold and tooling)
agent: agent
---
This is the kickoff for CampusLend.

1. Read, in order: `.github/copilot-instructions.md`, `docs/PROJECT_BRIEF.md`, `docs/ARCHITECTURE.md`, `docs/DATA_MODEL.md`, `docs/API_CONTRACT.md`, `docs/SAFETY_SPEC.md`, `docs/DESIGN_SYSTEM.md`, `docs/ROADMAP.md`, `docs/DECISIONS.md`.
2. Reply with a 10-line summary: what we are building, the stack, the milestone list, and the three rules you consider most important. Flag any contradiction you found between documents; fix the document, log it in `docs/DECISIONS.md`.
3. Check the working environment: Python version (3.11+), Node version (LTS), git status. If something is missing, tell me exactly what to install and stop.
4. Execute **milestone M0** from `docs/ROADMAP.md` following the operating loop. Use the `fastapi-feature`, `react-feature` and `progress-tracking` skills. Do not start M1.
5. When M0's acceptance lines are true, run `python scripts/verify.py`, update `docs/PROGRESS.md` (set `NEXT ACTION` to M1), register all files in `docs/FILE_REGISTRY.md`.

Copy `backend/.env.example` to `backend/.env` and `frontend/.env.example` to `frontend/.env` locally; never print or commit them.
