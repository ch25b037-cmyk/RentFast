# Errors Log

Append new entries at the bottom with the next number. Log an error when it took more than one attempt, touched safety, or could recur. Mark entries that are not fixed `UNRESOLVED`.

Entry format:
```
### E-### <short title>
- Date / milestone:
- Symptom (exact message):
- Root cause:
- Fix:
- Prevention (test, lint rule, doc change):
- Status: RESOLVED | UNRESOLVED
```

Rule: three different failed fix attempts on one problem → write the evidence and hypotheses, mark `UNRESOLVED`, move on or stop (see `.github/copilot-instructions.md` §5).

---
_(no entries yet)_

### E-001 M0 verification environment issues
- Date / milestone: 2026-11-08 / M0
- Symptom (exact message): `UnicodeEncodeError: 'charmap' codec can't encode characters` from `python scripts/verify.py`; frontend Vitest/Vite reported `Error: spawn EPERM` inside the sandbox.
- Root cause: Windows cp1252 console output could not render verifier detail, and the sandbox blocked esbuild child-process creation.
- Fix: Run the verifier with `PYTHONIOENCODING=utf-8`; run frontend tests/build with approved elevated execution. Ruff's Alembic import issue was fixed with the formatter.
- Prevention (test, lint rule, doc change): Keep verifier output UTF-8 in CI and document that Vite/Vitest may require an unrestricted runner on this managed Windows host.
- Status: RESOLVED

### E-002 M1-M7 SQLite and vertical-slice integration fixes
- Date / milestone: 2026-11-08 / M1-M7
- Symptom (exact message): `TypeError: can't compare offset-naive and offset-aware datetimes`; malformed Alembic template; `ValidationError` for ORM loan events; repeated test logins hit the in-process auth limit.
- Root cause: SQLite drops timezone metadata, the custom migration template had an incomplete docstring, Pydantic event schemas lacked attribute parsing, and API tests reused the same process-limiter bucket.
- Fix: Added `as_utc`, corrected the template, enabled `from_attributes`, and reset only the test limiter fixture; production rate limiting remains enabled.
- Prevention (test, lint rule, doc change): Frozen-clock/timezone helper, migration upgrade check, ORM response tests, and isolated test fixtures.
- Status: RESOLVED

### E-003 M11 hardening dependency and test-discovery follow-up
- Date / milestone: 2026-11-08 / M11
- Symptom (exact message): frontend `npm audit` reported 7 vulnerabilities; `pip-audit` reported vulnerable pinned runtime/dev packages; Vitest attempted to collect `e2e/app.spec.js`.
- Root cause: stale dependency pins and no Vitest exclusion for the separate Playwright test tree.
- Fix: upgraded frontend Vitest/Vite/zod/plugin dependencies, backend FastAPI/PyJWT/python-multipart/Pillow/pytest pins, and excluded `e2e/**` from Vitest; added repeatable Playwright and axe checks.
- Prevention (test, lint rule, doc change): npm audit, pip-audit, strict verifier, 5 passing Playwright scenarios and progress/audit evidence.
- Status: RESOLVED
