---
applyTo: "backend/**"
description: Rules for all FastAPI backend code
---
# Backend rules

Layout and layering are defined in `docs/ARCHITECTURE.md` §2–3. Highlights you must follow:

1. **Routers are thin.** Parse input → call ONE service function → return a response schema. No queries, no business rules.
2. **Services own the rules.** They accept a `Session` plus plain values, raise errors from `core/errors.py`, and never import FastAPI. Loan transitions only via `services/loan_state.py`.
3. **Every route with an ID** loads the object through a service that checks the caller may access it. Return `NOT_FOUND` (not `FORBIDDEN`) when a user should not even know the object exists.
4. **Schemas:** explicit `response_model` on every route; never return ORM objects; never include `*_hash`, tokens or codes except the one-time code response defined in the contract.
5. **Validation:** Pydantic constraints (lengths, enums, ranges) are mandatory. Strip and bound all free text.
6. **Time:** `datetime.now(UTC)` via a single `core/clock.py` helper so tests can freeze it.
7. **Transactions:** a service function that changes more than one row commits once, at the end, and rolls back on any error. Accepting an offer is one transaction.
8. **Errors:** raise domain errors; do not return ad-hoc dicts. Error codes must exist in `docs/API_CONTRACT.md`.
9. **Logging:** structured, with `request_id`. Never log OTPs, codes, tokens, full emails.
10. **Rate limits:** apply the limiter dependency to every route listed under S-15.
11. **Migrations:** autogenerate, then read the diff by eye; add the indexes listed in `docs/DATA_MODEL.md`.
12. **Tests:** each router gets `tests/api/test_<name>.py` including at least one cross-user access test; each service with rules gets `tests/unit/test_<name>.py`. Use a fresh in-memory/SQLite DB per test and a frozen clock for time logic.

Checks before you finish a batch: `ruff check .` and `pytest -q` from `backend/`.
Use the `fastapi-feature` skill for any new feature.
