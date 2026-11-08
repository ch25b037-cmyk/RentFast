# CampusLend — Copilot Operating Instructions

You are building **CampusLend**, a campus-only platform where students lend and borrow items for short periods (e.g. a calculator for one exam). Backend: **FastAPI**. Frontend: **React (JavaScript/JSX) + Vite**. You are working on a long build across many sessions. These rules exist so the work stays correct, checked and resumable.

## 0. Where the truth lives
Read these before you write any code. Do not rely on memory of earlier chats.
| File | Purpose |
|------|---------|
| `docs/PROGRESS.md` | What is done, what is next (`NEXT ACTION`). **Read first, update last.** |
| `docs/ROADMAP.md` | Milestones M0–M12 with acceptance criteria |
| `docs/PROJECT_BRIEF.md` | Product, scope, glossary |
| `docs/ARCHITECTURE.md` | Stack, layout, layering rules, conventions |
| `docs/DATA_MODEL.md` | Tables, enums, loan state machine |
| `docs/API_CONTRACT.md` | Every endpoint and error code |
| `docs/SAFETY_SPEC.md` | Safety controls with required tests |
| `docs/DESIGN_SYSTEM.md` | Tokens, components, screens, UI definition of done |
| `docs/DECISIONS.md` | Decisions already made (do not relitigate) |
| `docs/FILE_REGISTRY.md` | Every file you created and its last check |
| `docs/ERRORS_LOG.md` | Errors met and how they were fixed |
| `docs/IMPROVEMENTS.md` | Ideas parked for later |

If two documents disagree, stop and fix the document that is wrong (log it in `docs/DECISIONS.md`), then continue.

## 1. The operating loop (follow it every session)
1. **Orient.** Read `docs/PROGRESS.md`. Identify the current milestone and `NEXT ACTION`. Read the ROADMAP entry and the docs it touches.
2. **Plan small.** Write the task list for this step into `docs/PROGRESS.md` under "In progress". One step = a change you can verify in minutes (a model + migration + service + router + tests, or one screen).
3. **Build in batches of at most 5 files.** Prefer the matching skill (`fastapi-feature`, `react-feature`, `loan-safety`, `sleek-ui`).
4. **Check after every batch** (this is the "regular check"):
   - Register every created or changed file in `docs/FILE_REGISTRY.md` (path, purpose, milestone, status).
   - Run the area check: backend `ruff check . && pytest -q`; frontend `npm run lint && npm test -- --run`.
   - Fix failures now. Re-run until green. Non-trivial errors get an entry in `docs/ERRORS_LOG.md`.
5. **Checkpoint.** Update `docs/PROGRESS.md` (tick items, rewrite `NEXT ACTION`, append a session-log line).
6. **Milestone close.** When acceptance criteria are met: run `python scripts/verify.py --strict` (warnings count as failures and the frontend build runs), run the `file-audit` skill, then update PROGRESS. During normal batches `python scripts/verify.py` is enough; add `--quick` for a fast static-only pass. Do not start the next milestone before this is green.
7. **Never end a session silently.** Before stopping for any reason (limit reached, blocked, done), make sure PROGRESS.md says exactly where to resume.

## 2. Hard rules
- **Never invent.** Do not guess an endpoint, field, enum or package. Use `docs/API_CONTRACT.md` and `docs/DATA_MODEL.md`. If you must deviate, change the doc in the same edit and log it in `docs/DECISIONS.md`.
- **Dependencies:** add a library to `requirements.txt` / `package.json` *and install it* before importing it. Use current stable versions; check that the import works.
- **No placeholders in finished work:** no `TODO`, `pass` bodies, `NotImplementedError`, fake data in production paths, or "implement later" comments. If something is deferred, put it in `docs/IMPROVEMENTS.md` and keep the code honest.
- **Secrets:** never put secrets in code, docs, tests or commit messages. Only `.env.example` with fake values. Real `.env` files stay out of git.
- **Security first:** follow `docs/SAFETY_SPEC.md`. Every ID route checks object-level access. Business rules live in `services/`, not in routers or components.
- **Tests with the feature**, not after. A router without tests is not finished. Safety rows in SAFETY_SPEC list the tests required.
- **Migrations:** every model change has an Alembic migration. Never edit an applied migration; add a new one.
- **Scope discipline:** do not refactor unrelated code, rename files, or add features outside the current milestone. Put ideas in `docs/IMPROVEMENTS.md`.
- **Do not weaken a check to make it pass.** Fix the cause. Never delete a failing test unless the requirement itself changed (and say so in DECISIONS).
- **Explain uncertainty.** If a requirement is ambiguous and no document answers it, pick the safest reading, record it in DECISIONS.md, and continue. Ask the human only for the stop conditions in §5.

## 3. Code standards
**Backend (Python 3.11+):** type hints everywhere, Pydantic v2 schemas, SQLAlchemy 2.0 style (`select()`, `Mapped[...]`), async routes only if the DB driver is async (otherwise use sync `def` routes; follow `docs/DECISIONS.md`). Domain errors from `core/errors.py` become the standard error shape. Use `ruff` defaults plus `I` and `B` rule sets. Functions short and named for behaviour.
**Frontend (React, JSX):** function components + hooks. Data access only via `src/api/*` with TanStack Query. Validate API responses with zod at the boundary. Styling via Tailwind classes that reference tokens from `src/styles/tokens.css`. No inline hex values. Accessible by default (labels, focus, roles). Every async view has loading, empty, error states.
**Both:** small files (aim under 250 lines), clear names, comments explain *why* not *what*.

## 4. Tracking formats
Exact formats are in the `progress-tracking` skill. Summary:
- `FILE_REGISTRY.md`: one row per file — `path | purpose | milestone | status (new/ok/needs-fix) | last check`.
- `ERRORS_LOG.md`: `E-### | date | milestone | symptom | root cause | fix | prevention`.
- `IMPROVEMENTS.md`: `IMP-### | area | idea | impact | effort | status`.
- `DECISIONS.md`: `D-### | date | decision | why | alternatives`.
- `PROGRESS.md`: milestone checklist, `NEXT ACTION`, append-only session log.

## 5. Stop conditions (ask the human, then stop)
- A required value only the human has (SMTP credentials, production domain, the college's email domains).
- A change that would delete data or rewrite git history.
- The same error persists after **three** different fix attempts — log it in ERRORS_LOG.md as `UNRESOLVED`, write the evidence and your hypotheses, then stop.
- A request that conflicts with `docs/SAFETY_SPEC.md` rule §1.

## 6. Commands cheat-sheet
```
# backend
cd backend && python -m venv .venv && (activate) && pip install -r requirements-dev.txt
uvicorn app.main:app --reload
alembic revision --autogenerate -m "msg" && alembic upgrade head
ruff check . && pytest -q
# frontend
cd frontend && npm install && npm run dev
npm run lint && npm test -- --run && npm run build
# whole repo
python scripts/verify.py
```

## 7. Commit hygiene (if git is initialised)
One logical change per commit, message `M<n>: <what>` (e.g. `M5: add handover code service and tests`). Commit only when the area check is green.

## 8. Reply style while working
Be brief. Say what you are about to do, do it, report what changed and the check result in one or two lines. No long recaps. The files are the record, not the chat.
