---
name: fastapi-feature
description: Build or change a FastAPI backend feature end-to-end (model, migration, schema, service, router, tests, contract, registry). Use for any backend endpoint, model or business rule in CampusLend.
---
# fastapi-feature

Build one **vertical slice** at a time. Do the steps in order; do not skip the checks.

## Before you start
1. Read the ROADMAP milestone, the relevant rows in `docs/API_CONTRACT.md`, `docs/DATA_MODEL.md`, and any `S-xx` rows in `docs/SAFETY_SPEC.md` that apply.
2. List the files you will touch (max 5 per batch; split the slice into batches if larger).

## Steps
1. **Model** (`app/models/<aggregate>.py`): `Mapped[...]` columns, constraints and indexes exactly as in DATA_MODEL. Import it in `app/models/__init__.py`.
2. **Migration:** `alembic revision --autogenerate -m "<what>"`. Read the generated file; confirm constraints and indexes; run `alembic upgrade head` on a scratch DB.
3. **Schemas** (`app/schemas/<name>.py`): separate `Create`, `Update`, `Read` models. No internal fields in `Read`.
4. **Service** (`app/services/<name>.py`): all rules, authorization-aware loaders (`get_for_user(db, user, id)`), domain errors only. For loans use `services/loan_state.py`.
5. **Router** (`app/routers/<name>.py`): thin; explicit `response_model`, status codes, `Depends` for auth and rate limit. Register it in `app/main.py` under `/api/v1`.
6. **Tests:** `tests/unit/test_<name>_service.py` (rules, failure paths) and `tests/api/test_<name>.py` (happy path, validation, auth, **cross-user access**, rate limit where required).
7. **Contract sync:** if you changed or added anything vs `docs/API_CONTRACT.md`, update it now and add a `docs/DECISIONS.md` row.
8. **Run checks:** `cd backend && ruff check . && pytest -q`. Fix until green.
9. **Register files** in `docs/FILE_REGISTRY.md`; **update** `docs/PROGRESS.md`.

## Definition of done for a backend slice
- [ ] Matches the contract (paths, bodies, status codes, error codes)
- [ ] Business rules only in services; router has no logic
- [ ] Object-level access checked for every ID
- [ ] Failure-path tests present (invalid, wrong state, wrong user, limit hit)
- [ ] No secrets, OTPs, codes or tokens in logs or responses (except the one-time code response)
- [ ] Migration applies cleanly from an empty DB
- [ ] `ruff` and `pytest` green
- [ ] Registry and progress updated

## Common mistakes to avoid
- Returning ORM objects or hashes directly.
- Committing in the middle of a multi-row operation.
- Using `datetime.utcnow()` directly (use `core/clock.py`).
- Forgetting to invalidate older unused codes when issuing a new one.
- Checking permissions in the router instead of the service loader.
- Adding an enum value in code but not in the DB check constraint.
