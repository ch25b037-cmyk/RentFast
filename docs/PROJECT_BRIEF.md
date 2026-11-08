# CampusLend — Project Brief

> Working name. Change it in ONE place: `frontend/.env` (`VITE_APP_NAME`) and `backend/.env` (`APP_NAME`). Never hard-code the name in components.

## 1. The problem
Students regularly need an item for a very short time: a scientific calculator for one exam, a drafter for one lab, a lab coat, an extension board, a blazer for one interview. Buying is expensive and wasteful for a few hours of use. Meanwhile other students own the same item sitting idle.

## 2. The product
A campus-only platform where a verified student **posts a Request** ("need a Casio fx-991EX tomorrow 9:00–12:30"), and students who own the item **send an Offer**. The borrower accepts one offer, they meet at a **safe campus meetup spot**, hand over the item using a **two-person handover code**, and later return it the same way. Everything is time-boxed and leaves an audit trail.

Speed is the core value: a request should go from "posted" to "item in hand" in minutes.

## 3. Users
| Role | Description |
|------|-------------|
| Borrower | Student who posts requests and accepts offers |
| Lender | Student who owns items, sends offers, hands over and receives returns |
| Admin | Trusted student/staff who moderates reports, disputes, meetup spots |

One account can be both borrower and lender.

## 4. Core loop
1. Sign in with college email (OTP, no password).
2. Borrower creates a Request (item, needed_from, needed_until, preferred meetup spot).
3. Lenders (notified if they own a matching item category) send an Offer.
4. Borrower accepts one Offer → a Loan is created (`pending_handover`).
5. Both accept the lending agreement. They chat in-app to settle the time.
6. At the meetup spot: **receiver shows code, giver enters code** → Loan `active`.
7. Return the same way → Loan `returned`.
8. Both leave a review → trust scores update → Loan `closed`.

## 5. v1 scope (IN)
Email-OTP auth with college-domain allowlist · profiles · item inventory · requests · offers · in-app chat per offer · loans with handover/return codes · overdue handling · reviews and trust score · reports, blocks, admin moderation and disputes · in-app notifications · curated meetup spots · responsive, polished UI (mobile-first).

## 6. v1 scope (OUT — recorded in `docs/IMPROVEMENTS.md`)
Payments or deposits handled by the platform · delivery · native apps · multi-campus · push notifications · AI features · photo-evidence flow (planned v1.1).

## 7. Success criteria
- A borrower can post a request in under 60 seconds and a lender can offer in under 30 seconds.
- Every loan transition is recorded in `LoanEvent` and is only possible from a legal prior state.
- No endpoint lets a user read or change another user's private data (object-level authorization tested).
- `python scripts/verify.py` passes on every milestone close.
- Every screen has loading, empty and error states and works at 360px wide.

## 8. Constraints
- Backend: FastAPI + SQLAlchemy 2 + Alembic + Pydantic v2. Frontend: React (JavaScript/JSX) + Vite.
- No secrets in code or in git. Config only via environment variables.
- All timestamps stored in UTC, rendered in the viewer's local time.

## 9. Glossary
| Term | Meaning |
|------|---------|
| Request | A borrower's "I need X from A to B" post |
| Offer | A lender's "I can lend X" reply to a Request |
| Item | A thing a student registers as lendable |
| Loan | The accepted arrangement; has a strict state machine |
| Handover code | 6-digit one-time code proving both people are physically together |
| Receiver shows, giver enters | The rule for every code exchange (see `docs/SAFETY_SPEC.md`) |
| Trust score | 0–100 number derived from behaviour; gates what a user may do |
| Meetup spot | Admin-curated public campus location |
