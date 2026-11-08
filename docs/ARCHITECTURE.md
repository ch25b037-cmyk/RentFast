# Architecture

## 1. Stack
| Layer | Choice | Notes |
|-------|--------|-------|
| API | FastAPI (Python 3.11+) | async routes, Pydantic v2 schemas |
| ORM / DB | SQLAlchemy 2.x, Alembic | SQLite in dev, PostgreSQL in prod, same models |
| Auth | Email OTP → short-lived JWT access token + rotating refresh token (httpOnly cookie) | no passwords stored |
| Jobs | APScheduler in-process | overdue sweeper, request-expiry sweeper, OTP cleanup |
| Mail | `MAIL_BACKEND=console` in dev (prints OTP), `smtp` in prod | |
| Frontend | React (JavaScript/JSX) + Vite | see `docs/DESIGN_SYSTEM.md` |
| Frontend libs | react-router, @tanstack/react-query, tailwindcss, framer-motion, lucide-react, zod, react-hook-form, sonner, date-fns | install latest stable, lock versions |
| Tests | pytest + httpx (backend), vitest + @testing-library/react (frontend), Playwright (e2e, M11) | |
| Lint | ruff (backend), eslint (frontend) | |

## 2. Repository layout (target)
```
backend/
  app/
    main.py              # app factory, middleware, router registration
    deps.py              # get_db, get_current_user, require_admin
    core/                # config.py, security.py, rate_limit.py, errors.py, logging.py
    db/                  # base.py, session.py
    models/              # one file per aggregate (user.py, loan.py, ...)
    schemas/             # Pydantic request/response models
    services/            # business logic; NO fastapi imports here
    routers/             # thin HTTP layer; calls services only
    jobs/                # scheduled sweepers
    mail/                # console + smtp backends
  alembic/               # migrations
  tests/                 # unit/ (services) and api/ (routers)
  requirements.txt  requirements-dev.txt  pyproject.toml  .env.example
frontend/
  src/
    main.jsx
    app/                 # App.jsx, routes.jsx, providers.jsx, layout shells
    api/                 # client.js, one file per resource, zod schemas
    components/ui/       # design-system primitives (Button, Card, Sheet, ...)
    components/          # feature components (RequestCard, HandoverCode, ...)
    pages/               # route-level screens
    hooks/  lib/  styles/ (tokens.css, index.css)
    tests/
  index.html  package.json  vite.config.js  tailwind config  eslint config  .env.example
docs/   .github/   scripts/
```

## 3. Layering rules (enforced by `file-audit`)
1. `routers/` parse HTTP, call one service function, return a schema. No business logic, no direct DB queries beyond `Depends`.
2. `services/` hold all business rules, including the loan state machine. They take a `Session` and plain arguments, raise domain errors from `core/errors.py`, and never import FastAPI.
3. `models/` contain no logic beyond column definitions, constraints and simple properties.
4. `schemas/` never expose internal columns (hashes, tokens). Responses use explicit response models.
5. Frontend: pages compose components; data access only through `src/api/*` hooks; no `fetch` inside components.

## 4. Conventions
- **IDs**: UUID4 strings everywhere (non-enumerable).
- **Time**: UTC in DB and API (ISO 8601 with `Z`). Frontend converts for display.
- **Prefix**: all routes under `/api/v1`. Health at `/api/v1/health`.
- **Pagination**: `limit` (default 20, max 50) + `offset`; response `{items, total, limit, offset}`.
- **Error shape** (every non-2xx):
```json
{"error": {"code": "LOAN_INVALID_STATE", "message": "Human readable", "details": {}, "request_id": "uuid"}}
```
Error codes are SCREAMING_SNAKE, defined once in `core/errors.py`, mirrored in `frontend/src/api/errors.js`.
- **Auth header**: `Authorization: Bearer <access>`; refresh via cookie on `/api/v1/auth/refresh`.
- **Rate limits**: per-IP and per-user, thresholds from env.
- **Logging**: structured JSON, include `request_id`; never log OTPs, codes, tokens, or full emails.

## 5. Request lifecycle
`client → CORS → request-id middleware → rate limit → router → dependency (auth) → service → DB → response model → error handler`.

## 6. Background jobs
| Job | Every | Does |
|-----|-------|------|
| `expire_requests` | 1 min | open requests past `expires_at` → `expired`; pending offers → `expired` |
| `sweep_overdue` | 1 min | active loans past `due_at` → `overdue`, notify, apply trust penalty once |
| `loan_reminders` | 5 min | notify at T-60 min and T-0 |
| `cleanup_otps` | 1 hour | delete expired OTP rows and revoked refresh tokens |
Jobs call service functions; they are idempotent and covered by tests with a frozen clock.

## 7. Real-time
v1 uses polling via TanStack Query (`refetchInterval` on notifications and active loan). SSE is an improvement item (`IMP-001`).

## 8. Local development
| Thing | Value |
|-------|-------|
| Backend | `cd backend && uvicorn app.main:app --reload` → http://localhost:8000 (docs at `/docs`) |
| Frontend | `cd frontend && npm run dev` → http://localhost:5173 |
| Migrations | `alembic revision --autogenerate -m "msg"` then `alembic upgrade head` |
| Tests | `pytest -q` (backend), `npm test` (frontend) |
| Full check | `python scripts/verify.py` |

## 9. Config
All config via `backend/app/core/config.py` (pydantic-settings) reading env. Every variable is documented in `backend/.env.example`. Missing required values in `APP_ENV=prod` must crash at startup with a clear message.
