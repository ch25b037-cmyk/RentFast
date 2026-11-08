---
applyTo: "**/tests/**,**/*.test.js,**/*.test.jsx,**/*.spec.js"
description: Rules for writing and changing tests
---
# Tests

- A test states one behaviour in its name: `test_confirm_handover_rejects_reused_code`.
- Arrange–act–assert, no hidden shared state. Backend tests use a fresh database per test and a frozen clock (`core/clock.py`) for anything time-based.
- **Safety tests are mandatory.** Each row in `docs/SAFETY_SPEC.md` §2 lists the tests it needs; do not close a milestone with a missing one.
- Every router has at least one **cross-user test**: user B tries to read or change user A's object and gets `NOT_FOUND` or `FORBIDDEN`.
- Cover the failure paths, not just the happy path: invalid input, wrong state, wrong role, expired, locked, rate limited.
- Never weaken or delete a failing test to get green. If the requirement changed, record it in `docs/DECISIONS.md` first.
- Never use real emails, real codes or real secrets. Use `example.edu` addresses and obviously fake values.
- Frontend tests query by role and label (`getByRole`, `getByLabelText`), never by CSS class or test-id unless there is no accessible alternative.
- Do not mock what you own (your own services); mock only the network edge (`msw` or the API client) and the clock.
- Keep tests fast. A single test file should run in seconds.
