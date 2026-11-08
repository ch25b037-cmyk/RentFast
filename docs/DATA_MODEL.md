# Data Model

All tables: `id` UUID PK, `created_at` UTC (default now). Mutable tables also have `updated_at`. Soft delete only where `deleted_at` is listed.
Enums are stored as strings with a CHECK constraint.

## Tables

### user
`email` (unique, lowercase) · `display_name` · `department` (nullable) · `hostel` (nullable, private until a loan is accepted) · `avatar_url` · `role` (`student`|`admin`) · `status` (`active`|`suspended`|`deleted`) · `email_verified_at` · `trust_score` (int 0–100, default 50) · `completed_loans` · `on_time_returns` · `late_returns` · `last_seen_at`

### email_otp
`email` · `code_hash` · `expires_at` · `attempts` · `consumed_at` · `ip_hash`

### refresh_token
`user_id` FK · `token_hash` · `expires_at` · `revoked_at` · `user_agent`

### category
`slug` (unique) · `name` · `icon` · `max_loan_hours` · `is_prohibited` (bool) — seed list in `docs/SAFETY_SPEC.md` §5

### item
`owner_id` FK · `category_id` FK · `title` · `description` · `condition` (`new`|`good`|`fair`) · `value_tier` (`low`|`mid`|`high`) · `photo_urls` (JSON) · `is_available` · `deleted_at`

### request
`requester_id` FK · `category_id` FK · `title` · `description` · `needed_from` · `needed_until` · `preferred_spot_id` FK nullable · `status` (`open`|`matched`|`fulfilled`|`cancelled`|`expired`) · `expires_at`

### offer
`request_id` FK · `owner_id` FK · `item_id` FK nullable · `message` · `status` (`pending`|`accepted`|`declined`|`withdrawn`|`expired`)
Unique: one `pending` offer per (`request_id`, `owner_id`).

### loan
`request_id` · `offer_id` · `item_id` · `lender_id` · `borrower_id` · `spot_id` · `scheduled_start` · `due_at` · `status` (`pending_handover`|`active`|`overdue`|`returned`|`disputed`|`cancelled`|`closed`) · `agreement_version` · `borrower_agreed_at` · `lender_agreed_at` · `handed_over_at` · `returned_at` · `closed_at` · `late_penalty_applied` (bool)
Check: `lender_id != borrower_id`.

### loan_code
`loan_id` FK · `purpose` (`handover`|`return`) · `code_hash` · `shown_to_id` FK (the receiver) · `expires_at` · `attempts` · `consumed_at`

### loan_event (append-only)
`loan_id` FK · `actor_id` FK nullable (null = system) · `type` · `payload` (JSON)
Never updated or deleted by application code.

### message
`offer_id` FK · `sender_id` FK · `body` (max 1000) · `masked` (bool, contact details were masked) · `flagged`

### review
`loan_id` FK · `reviewer_id` · `reviewee_id` · `rating` (1–5) · `tags` (JSON) · `comment`
Unique: (`loan_id`, `reviewer_id`).

### report
`reporter_id` · `target_user_id` nullable · `target_loan_id` nullable · `target_message_id` nullable · `reason` (`no_show`|`damaged`|`not_returned`|`harassment`|`fake_listing`|`unsafe_meetup`|`other`) · `details` · `status` (`open`|`reviewing`|`actioned`|`dismissed`) · `resolved_by` nullable · `resolved_at` nullable
Check: at least one target set.

### block
`blocker_id` · `blocked_id` · Unique pair. A block hides each party from the other in feeds, offers and chat.

### notification
`user_id` · `type` · `title` · `body` · `data` (JSON) · `read_at`

### meetup_spot
`name` · `description` · `location_hint` · `is_active`

### audit_log
`actor_id` nullable · `action` · `entity_type` · `entity_id` · `metadata` (JSON) · `ip_hash`
Written for: auth events, admin actions, suspensions, dispute resolutions, account deletion.

## Loan state machine (the only legal transitions)
```
pending_handover → active        (confirm_handover with valid code)
pending_handover → cancelled     (either party, before handover)
active           → returned      (confirm_return with valid code, or return-claim auto-accepted)
active           → overdue       (system, now > due_at)
overdue          → returned      (confirm_return)
active|overdue   → disputed      (either party)
disputed         → closed        (admin resolution)
returned         → closed        (both reviews submitted, or 48h elapsed)
```
Any other transition raises `LOAN_INVALID_STATE`. The transition table lives in ONE place: `services/loan_state.py`.

## Request / Offer interplay
- Accepting an offer: Offer → `accepted`, all other pending offers on that request → `declined`, Request → `matched`, Loan created. All in one transaction.
- Loan `cancelled` before handover: Request returns to `open` if it has not expired, else `expired`.
- Loan `closed` after a normal return: Request → `fulfilled`.

## Indexes (add in the migration that creates the table)
`request(status, needed_from)` · `request(category_id, status)` · `offer(request_id, status)` · `loan(lender_id, status)` · `loan(borrower_id, status)` · `loan(status, due_at)` · `notification(user_id, read_at)` · `loan_event(loan_id, created_at)`
