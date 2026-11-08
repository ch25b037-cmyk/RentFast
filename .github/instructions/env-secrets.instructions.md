---
applyTo: "**/.env*,backend/app/core/config.py,frontend/vite.config.js"
description: Rules for environment files, configuration and secrets
---
# Environment, config and secrets

- Real `.env` files are **never** committed, printed in chat, copied into docs or pasted into tests. Only `.env.example` files exist in the repo, containing obviously fake values.
- Every environment variable is declared in `backend/app/core/config.py` (pydantic-settings) with a type, a default only where safe, and a comment. Every variable in config appears in `backend/.env.example` and vice versa. `scripts/verify.py` checks this.
- Frontend variables must start with `VITE_` and must never contain secrets (they ship to the browser).
- In `APP_ENV=prod` the app must refuse to start if `SECRET_KEY` is missing, short (< 32 chars) or equal to the example value, if `CORS_ORIGINS` contains `*`, or if `MAIL_BACKEND=console`.
- Generate secrets with `python -c "import secrets; print(secrets.token_urlsafe(48))"`; never write one into a file you create.
- When you add a variable: update config.py, `.env.example`, `docs/ARCHITECTURE.md` §9 if it is user-facing, and add a config test.
- If the human must supply a value (SMTP credentials, real college domains), stop and ask (`copilot-instructions.md` §5).
