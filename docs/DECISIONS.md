# Decisions

Append-only. Format: `| D-### | date | decision | why | alternatives rejected |`. To reverse a decision add a new row saying `supersedes D-###`.
The human owner may edit the "Open for you" list below before the build starts; the Builder must not change those rows without asking.

| ID | Date | Decision | Why | Alternatives rejected |
|----|------|----------|-----|-----------------------|
| D-001 | 2026-11-08 | Working name **CampusLend**, changeable via env (`APP_NAME`, `VITE_APP_NAME`) | Name is not decided; avoid hard-coding | Hard-coded name |
| D-002 | 2026-11-08 | Backend: FastAPI + SQLAlchemy 2 + Alembic + Pydantic v2; SQLite dev, PostgreSQL prod | Requested stack; same models both DBs | Django, raw SQL |
| D-003 | 2026-11-08 | Passwordless auth: college-email OTP + JWT access + rotating refresh cookie | No password storage; email domain doubles as verification | Passwords, OAuth social login |
| D-004 | 2026-11-08 | Frontend in JavaScript (JSX), with zod runtime validation and JSDoc types | You asked for React JS; zod gives runtime error checking | TypeScript now (kept as IMP-003) |
| D-005 | 2026-11-08 | Sync SQLAlchemy sessions and sync route functions unless an async driver is chosen later | Fewer pitfalls for AI-generated code; FastAPI runs sync routes in a threadpool | Async everywhere |
| D-006 | 2026-11-08 | No money handling in v1 | Payments need legal, compliance and fraud work | Built-in deposits |
| D-007 | 2026-11-08 | "Receiver shows, giver enters" for every code exchange | Giver cannot confirm alone; receiver proves physical possession | Single code confirmed by one side |
| D-008 | 2026-11-08 | Meetups only at admin-curated spots | Keeps handovers in public, known places | Free-text locations |
| D-009 | 2026-11-08 | Polling in v1 for live updates; SSE later (IMP-001) | Simplest reliable approach | WebSockets now |
| D-010 | 2026-11-08 | Access token kept in memory on the client; refresh token in httpOnly cookie | Limits XSS token theft | localStorage tokens |
| D-011 | 2026-11-08 | Trust score weights and tier limits live in config, not code | Tunable without code changes | Hard-coded numbers |
| D-012 | 2026-11-08 | Scheduled jobs run in-process with APScheduler in v1 | One process to run for a campus-scale app | Celery + Redis |

## Open for you (human) — answer before or during M1
| Question | Default if unanswered |
|----------|----------------------|
| Which email domain(s) may sign up? (`ALLOWED_EMAIL_DOMAINS`) | `example.edu` placeholder; sign-in works only for that domain until you set the real one |
| Real meetup spots on your campus? | 6 generic sample spots from the seed script |
| Who are the first admins? (`ADMIN_EMAILS`) | none; you add yourself in `backend/.env` |
| Final product name? | CampusLend |
| Where will it be hosted? | undecided; M12 produces Dockerfiles only |

## Decisions made during the build
| D-013 | 2026-11-08 | Admin meetup spot updates use `/admin/meetup-spots/{spot_id}` | Object-level update route is required for PATCH semantics and keeps the base collection route unambiguous | Mutating the collection path |
| D-014 | 2026-11-08 | Item photos use a validated `/items/photos` upload boundary with generated filenames and metadata-stripping transcode | Prevents arbitrary file paths, spoofed image payloads and EXIF leakage while keeping v1 storage simple | Unvalidated client URLs; direct filesystem names |
_(the Builder appends new `D-013…` rows here as they occur)_
