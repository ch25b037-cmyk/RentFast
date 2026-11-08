---
name: loan-safety
description: Implement or review anything touching loans, handover/return codes, trust, reports, blocks or authorization in CampusLend. Use whenever a change could affect user safety or the loan state machine.
---
# loan-safety

Source of truth: `docs/SAFETY_SPEC.md` and the state machine in `docs/DATA_MODEL.md`. This skill is the working checklist.

## The invariants (never violate)
1. **Receiver shows, giver enters.** Handover: borrower shows, lender enters. Return: lender shows, borrower enters.
2. Codes: 6 digits from `secrets` (not `random`), stored hashed (HMAC with server secret or a slow hash), expire in `HANDOVER_CODE_TTL_MINUTES`, single-use, lock after `CODE_MAX_ATTEMPTS`.
3. Plain code appears in **one** response to the receiver only. Never in logs, notifications, events, errors or tests' printed output.
4. All state changes go through `services/loan_state.py`'s transition table and write a `LoanEvent`.
5. Issuing a new code invalidates the previous unused code for that (loan, purpose).
6. No codes before **both** parties accepted the agreement and a meetup spot is set.
7. Meetup spots come from the curated table only.
8. Blocked or suspended users cannot create offers, messages, loans or codes.
9. Every ID route verifies the caller is a party (or an admin where allowed).

## Implementation steps (code service)
1. `issue_code(db, loan, receiver)` → verifies state, agreement, role; invalidates old code; creates hashed code; returns plain code once.
2. `confirm_code(db, loan, giver, code)` → verifies role is the giver; checks attempts, expiry, lock; constant-time compare; increments attempts on failure; on success consumes the code and calls the transition.
3. Wrap each in a single transaction; write `LoanEvent` in the same transaction.

## Tests you must write (names are suggestions)
- `test_issue_code_requires_agreement`
- `test_only_receiver_can_issue_code` / `test_only_giver_can_confirm`
- `test_wrong_code_increments_attempts_and_locks_after_limit`
- `test_expired_code_rejected` (frozen clock)
- `test_code_cannot_be_reused`
- `test_new_code_invalidates_previous`
- `test_code_for_other_loan_rejected`
- `test_every_illegal_transition_raises` (parametrised over the full matrix)
- `test_blocked_user_cannot_create_offer_or_message`
- `test_cross_user_cannot_read_loan`
- `test_plain_code_not_present_in_logs` (capture logs)

## Review checklist (use when auditing)
- [ ] Any use of `random` for codes? (must be `secrets`)
- [ ] Any `==` comparing code hashes? (use `hmac.compare_digest`)
- [ ] Any code or token in `logger.*` calls or exception messages?
- [ ] Any state write outside the transition function?
- [ ] Any route returning a loan to a non-party?
- [ ] Any free-text location accepted?
- [ ] Are penalties idempotent (`late_penalty_applied`)?
- [ ] Are trust weights read from config, not inline?
