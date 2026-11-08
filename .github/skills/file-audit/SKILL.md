---
name: file-audit
description: Regular verification of every file created so far - runs checks, compares files to the registry, scans for placeholders and secrets, and writes an audit report. Use at every checkpoint, milestone close, or whenever something feels off.
---
# file-audit

Purpose: catch problems early and keep the repo honest. Run at **every milestone close**, and after any session that created more than ~10 files.

## Procedure
1. **Run the automated check:** `python scripts/verify.py --strict` at milestone close (plain `python scripts/verify.py` for mid-milestone audits). Read its output fully; it writes `docs/VERIFY_LAST_RUN.md`. Run it inside the activated backend virtualenv so ruff and pytest are found.
2. **Enumerate files:** list all files under `backend/`, `frontend/src/`, `scripts/`, `docs/`, `.github/`. Compare with `docs/FILE_REGISTRY.md`.
   - File exists but not registered → register it (or delete it if it is stray).
   - Registered but missing → fix the registry, or restore the file if it was deleted by mistake.
3. **Backend checks:** `cd backend && ruff check . && pytest -q`. Then search for: `TODO|FIXME|NotImplementedError|pass  # `, `print(`, `random.` used for codes, `utcnow`, hard-coded secrets.
4. **Frontend checks:** `cd frontend && npm run lint && npm test -- --run && npm run build`. Then search for: `TODO|FIXME`, `console.log`, `dangerouslySetInnerHTML`, `localStorage` near token or code, raw hex colours outside `tokens.css`.
5. **Contract drift:** compare `app/routers/*` routes with `docs/API_CONTRACT.md` and `src/api/*` with both. Report missing, extra and mismatched routes.
6. **Layering:** routers importing `models` directly or containing queries; services importing `fastapi`; components calling `fetch`.
7. **Safety spot-check:** open `docs/SAFETY_SPEC.md` §2 and, for every row whose milestone is done, confirm the named tests exist and pass.
8. **Write the report** to `docs/audits/AUDIT_<YYYY-MM-DD>_<milestone>.md` using the template below.
9. **Fix or log:** fix every `blocker` now. Log the rest as `needs-fix` in the registry and as entries in `docs/IMPROVEMENTS.md` or `docs/ERRORS_LOG.md`.
10. **Update** `docs/PROGRESS.md` with the audit result.

## Report template
```
# Audit <date> — <milestone>
Result: PASS | PASS WITH NOTES | FAIL
Automated check: <pass/fail counts from verify.py>
## Blockers (fixed or not)
## Contract drift
## Layering violations
## Safety coverage (S-xx → tests found?)
## Placeholders / secrets scan
## Registry reconciliation (added / removed / corrected)
## Follow-ups (with IDs in IMPROVEMENTS or ERRORS_LOG)
```

## Severity
- **blocker:** failing check, secret in repo, missing safety test for a done milestone, contract mismatch that breaks the client.
- **needs-fix:** layering violation, missing state (loading/empty/error), missing test for a non-safety path.
- **note:** style, naming, small cleanup.

Never mark an audit PASS if any blocker remains.
