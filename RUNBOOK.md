# CampusLend runbook

## Local development

1. `cd backend && python -m pip install -r requirements-dev.txt`
2. `cd backend && python -m alembic upgrade head && python ..\scripts\seed.py`
3. `cd backend && uvicorn app.main:app --reload`
4. In another terminal: `cd frontend && npm install && npm run dev`

For browser verification, from `frontend/` run `npx playwright install chromium` once, then `npm run e2e`. The suite also runs the critical axe scan and writes a reviewable screenshot to `frontend/test-results/welcome.png`.

With `MAIL_BACKEND=console`, the development OTP is printed by the running API's console mail seam; enter that six-digit code in the browser. It is not returned by the API. Use a college domain listed in `backend/.env`.

## Verification

From the repository root run `set PYTHONIOENCODING=utf-8 && python scripts\verify.py --strict`. For dependency checks run `python -m pip_audit -r backend\requirements.txt`, `python -m pip_audit -r backend\requirements-dev.txt`, and `cd frontend && npm audit --audit-level=high`. On managed Windows hosts, frontend Vite/Vitest may need an unrestricted runner so esbuild can spawn.

## Production checklist

- Set a strong `SECRET_KEY`, real college domains, admin emails, SMTP settings, secure cookies and explicit CORS origins.
- Run migrations before starting the API.
- Run `python scripts/verify.py --strict` and complete the safety review in `docs/SAFETY_SPEC.md`.
- Back up the database and keep meetup spots current through the admin surface.
