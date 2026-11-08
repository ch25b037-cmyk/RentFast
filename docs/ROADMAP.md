# Roadmap

Rules: build **one milestone at a time**, in order, unless the dependency note says otherwise. A milestone is done only when every acceptance line is true **and** `python scripts/verify.py` passes **and** `docs/PROGRESS.md` is updated. Run `/milestone-close` to do that.

Check commands (when the folders exist):
- Backend: `cd backend && ruff check . && pytest -q`
- Frontend: `cd frontend && npm run lint && npm test -- --run && npm run build`
- Everything: `python scripts/verify.py`

---
## M0 — Scaffold and tooling
**Deliver:** backend app factory, config via pydantic-settings, `/health`, DB session, Alembic wired, pytest + ruff configured, error handler + request-id middleware. Frontend Vite app, Tailwind, router, tokens.css, API client skeleton, eslint + vitest configured. `.gitignore` verified.
**Accept:** `uvicorn` boots; `GET /api/v1/health` returns ok; `npm run dev` renders a page; both test suites run (even if with 1 test); verify.py green.

## M1 — Auth and users (S-01…S-04, S-15, S-16)
**Deliver:** OTP request/verify, domain allowlist, user creation, JWT + refresh rotation, `/users/me` get/patch, rate limiting, console mailer, suspended check.
**Accept:** all S-01…S-04 tests pass; OTP never logged; refresh reuse revokes family.

## M2 — Items, categories, meetup spots (S-05)
**Deliver:** models + migrations, seed script for categories and 6 sample spots, items CRUD, prohibited-category rejection.
**Accept:** owner-only item access test; seed is idempotent.

## M3 — Requests and feed (S-06)
**Deliver:** requests CRUD, feed filters and sorting, limits, `expire_requests` job.
**Accept:** limit tests; feed hides blocked users (stub until M6 then re-test); expiry job test with frozen clock.

## M4 — Offers, chat, notifications (S-11)
**Deliver:** offers lifecycle, accept creates Loan in one transaction, chat with contact masking, notification service + endpoints, notify matching lenders on new request.
**Accept:** accept transaction rolls back fully on failure; masking tests; cross-user tests.

## M5 — Loans, codes, agreement (S-07…S-10, S-14)
**Deliver:** `services/loan_state.py`, agree/spot endpoints, handover and return codes, return-claim, cancel, loan events, loan timeline endpoint.
**Accept:** every illegal transition test; every code failure mode test (see SAFETY_SPEC S-07); a full happy-path API test from request → closed.

## M6 — Trust, reviews, overdue, reports, blocks (S-12, S-13, S-17, S-18)
**Deliver:** reviews, trust score service, tier limits applied, `sweep_overdue` + `loan_reminders` jobs, reports, blocks.
**Accept:** score math table test; frozen-clock overdue test applies penalty once; block tests.

## M7 — Admin and disputes (S-19, S-20)
**Deliver:** admin routes, dispute flow, suspension, audit log.
**Accept:** non-admin gets 403 on every admin route; dispute freezes new loans; audit rows written.

## M8 — Frontend foundation *(may start after M0; needs M1 for auth screens)*
**Deliver:** tokens, fonts, all primitives from DESIGN_SYSTEM §3, app shell (mobile tab bar + desktop rail), theme toggle, auth screens, auth state and API client with refresh handling, error boundary, toasts.
**Accept:** contrast audit recorded; keyboard path through auth; 360px layout clean; component tests for primitives.

## M9 — Frontend: feed, create request, offers *(needs M3–M4)*
**Deliver:** Home, Requests feed, Create Request sheet, Request detail, Offer sheet, offer chat, notifications screen.
**Accept:** all states present; optimistic UI where safe; zod validation of API responses.

## M10 — Frontend: items, loans, profile, safety *(needs M5–M7)*
**Deliver:** My items, Loan detail with `HandoverCode` and `CodeEntry`, timeline, reviews, profile, safety centre, block/report flows, admin screens.
**Accept:** full happy path works in the browser against the real backend; code UI never persists the code in storage or URL.

## M11 — Hardening
**Deliver:** security headers, CORS audit, upload validation, account deletion, Playwright e2e (happy path + two failure paths), a11y pass, performance pass (bundle size, query caching), `/security-review` completed.
**Accept:** SAFETY_SPEC checklist §7 fully ticked; e2e green; no console errors.

## M12 — Polish and deploy prep
**Deliver:** motion pass, empty-state illustrations, seed/demo data script, Dockerfiles + compose, README, runbook, `docs/IMPROVEMENTS.md` triaged.
**Accept:** fresh clone → documented steps → working app; final audit report in `docs/audits/`.

---
## After M12
Work from `docs/IMPROVEMENTS.md`, highest impact/effort ratio first, one item per `/improve` run.
