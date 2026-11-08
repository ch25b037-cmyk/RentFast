# Safety Specification

Safety is a feature, not a layer. Every item below has an ID (`S-xx`), a priority, a milestone, and **required tests**. The `loan-safety` skill and the `auditor` agent check against this file.

Priority: **P0** = must exist before any real user. **P1** = before public launch. **P2** = later.

## 1. Rules that never bend
1. **Receiver shows, giver enters.** In every code exchange, the person *receiving* the item displays the code and the person *giving* it types it in. Handover: borrower shows, lender enters. Return: lender shows, borrower enters.
2. Codes are 6 digits, single-use, expire in `HANDOVER_CODE_TTL_MINUTES` (default 10), are stored **hashed**, and lock after `CODE_MAX_ATTEMPTS` (default 5) wrong tries.
3. A code is returned in an API response **once**, to the receiver only, never logged, never in a notification body.
4. Loan state changes happen only through `services/loan_state.py`. Each writes a `LoanEvent`.
5. Every endpoint that takes an ID checks the caller is allowed to see that object (no IDOR). Tests prove it.
6. Public profiles never expose email, hostel, or phone.
7. Money is out of scope for v1. The platform never handles payments or deposits.

## 2. Controls
| ID | Pri | Milestone | Control | Required tests |
|----|-----|-----------|---------|----------------|
| S-01 | P0 | M1 | Email domain allowlist (`ALLOWED_EMAIL_DOMAINS`), OTP login, one account per email | non-allowlisted domain rejected; OTP reuse rejected; expired OTP rejected |
| S-02 | P0 | M1 | OTP: 6 digits, hashed, TTL 10 min, max 5 attempts, per-email + per-IP rate limit, no account enumeration | lockout after N wrong; identical 202 for unknown/known email |
| S-03 | P0 | M1 | JWT access (15 min) + rotating refresh token in httpOnly, Secure, SameSite=Lax cookie; refresh reuse revokes the family | rotated token reuse fails |
| S-04 | P0 | M1 | Suspended users blocked at the auth dependency (`ACCOUNT_SUSPENDED`) | suspended user gets 403 everywhere |
| S-05 | P0 | M2 | Prohibited categories (see §5) cannot be created as items or requests | creation rejected |
| S-06 | P0 | M3 | Request limits: max open requests per user, max window = category `max_loan_hours`, no past start | each limit has a test |
| S-07 | P0 | M5 | Handover and return codes per rule §1 | wrong code, reused code, expired code, locked code, wrong role, wrong loan |
| S-08 | P0 | M5 | Loan state machine with one transition table | every illegal transition raises `LOAN_INVALID_STATE` |
| S-09 | P0 | M5 | Lending agreement acknowledged by both before codes can be issued (`AGREEMENT_REQUIRED`) | code request without agreement fails |
| S-10 | P0 | M5 | Meetup only at admin-curated spots (no free-text location) | unknown spot rejected |
| S-11 | P0 | M4 | In-app chat only; phone numbers and emails masked in messages before the offer is accepted | masking unit tests |
| S-12 | P0 | M6 | Blocks hide users from each other in feed, offers and chat | blocked user cannot offer or message |
| S-13 | P0 | M6 | Reports with reasons; admin review queue | create + resolve flow |
| S-14 | P0 | all | Object-level authorization on every ID route | one cross-user test per router |
| S-15 | P0 | M1 | Rate limiting on auth, request creation, offers, messages, code attempts | 429 `RATE_LIMITED` tests |
| S-16 | P0 | M0 | No secrets in code; `.env` ignored; prod crashes if `SECRET_KEY` is default | config tests + verify.py secret scan |
| S-17 | P1 | M6 | Trust score and tiers (see §3), limits by tier | score math unit tests |
| S-18 | P1 | M6 | Overdue handling: reminders T-60 and T-0, status `overdue`, one-time penalty | frozen-clock job tests |
| S-19 | P1 | M7 | Disputes freeze both users' new loans until resolved; admin outcome applies trust effects | dispute flow test |
| S-20 | P1 | M7 | Audit log for auth, admin and moderation actions | action writes row |
| S-21 | P1 | M11 | Security headers, strict CORS, upload validation (type, size, EXIF stripped) | header + upload tests |
| S-22 | P1 | M11 | Account deletion and data minimisation | deletion test |
| S-23 | P2 | later | Photo evidence at handover/return (IMP-004) | — |
| S-24 | P2 | later | Reputation-based auto-suspension suggestions | — |

## 3. Trust score
Start 50. Clamp 0–100. All weights in `core/config.py`, never inline.
| Event | Change |
|-------|--------|
| Loan closed, returned on time | +4 |
| Loan closed, returned late | −8 (once per loan) |
| Review received (rating r) | (r − 3) × 2 |
| Report upheld against you | −15 |
| Dispute lost | −25 |
| Dispute won | +5 |

Tiers: **Restricted** < 30 · **Member** 30–69 · **Trusted** ≥ 70.
| Tier | Max active loans as borrower | Item value tiers borrowable | Max open requests |
|------|------------------------------|-----------------------------|-------------------|
| Restricted | 0 (cannot create requests) | — | 0 |
| Member | 1 (first 3 loans: low value only) | low, mid | 2 |
| Trusted | 3 | low, mid, high | 5 |
Lending is never blocked by tier (lenders take the risk, and they can see the borrower's tier on the request).

## 4. Threat model (quick)
| Threat | Mitigation |
|--------|-----------|
| Stranger signs up | S-01 allowlist + OTP |
| OTP brute force | S-02 |
| Stolen token | S-03 short TTL, rotation |
| Borrower keeps the item | S-09 agreement, S-18 overdue, S-17 trust, S-13 reports |
| Fake "handed over" claim | S-07 two-person codes |
| Lender falsely claims "not returned" | return codes + return-claim auto-accept + disputes (S-19) |
| Unsafe meetup | S-10 curated public spots, `unsafe_meetup` report reason |
| Harassment in chat | S-11, S-12, S-13 |
| Reading others' data via ID guessing | UUIDs + S-14 |
| Spam requests/offers | S-06, S-15 |
| Credential leak in repo | S-16 + secret scan |
| Malicious upload | S-21 |

## 5. Category seed (prohibited marked ✗)
Calculators (max 24h) · Drafting & lab gear (72h) · Electronics accessories (48h) · Formal wear (48h) · Books & notes (168h) · Sports gear (48h) · Tools (48h) · Other (24h, review by admin) · ✗ Medicines · ✗ Alcohol/tobacco · ✗ Weapons · ✗ Exam papers or any material for cheating · ✗ ID cards/documents · ✗ Vehicles

## 6. Loan code protocol (reference sequence)
```
Handover:  borrower POST /codes/handover → code shown on borrower's phone
           lender   POST /confirm-handover {code} → active, due_at fixed, LoanEvent(handover_confirmed)
Return:    lender   POST /codes/return → code shown on lender's phone
           borrower POST /confirm-return {code} → returned, LoanEvent(return_confirmed)
Fallback:  borrower POST /return-claim → lender has 24h to confirm or dispute, else auto-returned
```
Generating a new code invalidates the previous unused one for that loan + purpose.

## 7. Pre-launch checklist (used by `/security-review`)
- [ ] All P0 rows have passing tests
- [ ] Cross-user access test exists for every router
- [ ] No secret in git history (`python scripts/verify.py` secret scan)
- [ ] CORS allows only configured origins
- [ ] Prod boot fails on default `SECRET_KEY`
- [ ] OTP and codes never appear in logs
- [ ] Admin routes return 403 for non-admins
- [ ] A suspended account cannot do anything
