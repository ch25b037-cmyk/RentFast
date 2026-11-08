# API Contract (v1)

Source of truth for both backend and frontend. **If you deviate from this file, update it in the same change** and log a line in `docs/DECISIONS.md`.

Base: `/api/v1`. Auth = Bearer access token unless marked `public`. Errors use the shape in `docs/ARCHITECTURE.md` §4.
Roles: `U` = any active signed-in user, `A` = admin.

## Auth
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/auth/otp/request` | public | body `{email}`; always returns 202 (no account enumeration); rejects non-allowlisted domains with `EMAIL_DOMAIN_NOT_ALLOWED` |
| POST | `/auth/otp/verify` | public | body `{email, code}` → `{access_token, user}` + sets refresh cookie; creates the user on first success |
| POST | `/auth/refresh` | cookie | rotates refresh token, returns new access token |
| POST | `/auth/logout` | U | revokes refresh token |

## Users
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/users/me` | U | own profile incl. trust tier |
| PATCH | `/users/me` | U | display_name, department, hostel, avatar |
| DELETE | `/users/me` | U | delete account (blocked while loans are active) |
| GET | `/users/{id}` | U | public profile: name, avatar, trust tier, counts, recent reviews. Never email or hostel |

## Categories and meetup spots
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/categories` | U | list (non-prohibited) |
| GET | `/meetup-spots` | U | active spots |

## Items
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/items` | U | own items |
| POST | `/items` | U | create (prohibited categories rejected) |
| POST | `/items/photos` | U | upload one JPEG, PNG, or WebP image (validated size/type; metadata stripped) |
| GET/PATCH/DELETE | `/items/{id}` | U (owner) | read / update / soft-delete |

## Requests
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/requests` | U | feed. Filters: `category`, `status` (default `open`, or `all` with `mine=true`), `q`, `urgent=true`, `mine=true`. Sort: soonest `needed_from`. Hides blocked users |
| POST | `/requests` | U | create. Validates window against category `max_loan_hours`, trust limits, daily cap |
| GET | `/requests/{id}` | U | detail |
| PATCH | `/requests/{id}` | U (owner) | edit while `open` and no accepted offer |
| POST | `/requests/{id}/cancel` | U (owner) | cancel |

## Offers
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/requests/{id}/offers` | U | body `{item_id?, message}`; cannot offer on own request |
| GET | `/requests/{id}/offers` | U (request owner) | offers on my request |
| GET | `/offers/mine` | U | offers I made |
| POST | `/offers/{id}/accept` | U (request owner) | creates the Loan (transactional) |
| POST | `/offers/{id}/decline` | U (request owner) | |
| POST | `/offers/{id}/withdraw` | U (offer owner) | |
| GET | `/offers/{id}/messages` | U (the two parties) | chat |
| POST | `/offers/{id}/messages` | U (the two parties) | body `{body}`; contact details masked before acceptance |

## Loans
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/loans` | U | my loans (as lender or borrower), filter `status`, `role` |
| GET | `/loans/{id}` | U (parties, admin) | detail + timeline of `LoanEvent` |
| POST | `/loans/{id}/agree` | U (party) | accept agreement `agreement_version` |
| POST | `/loans/{id}/spot` | U (party) | body `{spot_id, scheduled_start}` |
| POST | `/loans/{id}/codes/handover` | U (borrower) | **receiver shows**: generates code, returned ONLY to the borrower |
| POST | `/loans/{id}/confirm-handover` | U (lender) | **giver enters**: body `{code}` → `active` |
| POST | `/loans/{id}/codes/return` | U (lender) | receiver (lender) generates return code |
| POST | `/loans/{id}/confirm-return` | U (borrower) | giver (borrower) enters code → `returned` |
| POST | `/loans/{id}/return-claim` | U (borrower) | borrower says "I returned it"; auto-accepted after 24h unless lender disputes |
| POST | `/loans/{id}/cancel` | U (party) | only from `pending_handover` |
| POST | `/loans/{id}/dispute` | U (party) | body `{reason, details}` |
| POST | `/loans/{id}/reviews` | U (party) | body `{rating, tags, comment}`; only after `returned` |

## Safety
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/reports` | U | create report |
| POST | `/blocks` | U | body `{user_id}` |
| DELETE | `/blocks/{user_id}` | U | unblock |
| GET | `/blocks` | U | my blocks |

## Notifications
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/notifications` | U | paginated, `unread=true` filter |
| POST | `/notifications/{id}/read` | U | |
| POST | `/notifications/read-all` | U | |

## Admin
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/admin/reports` | A | filter by status |
| POST | `/admin/reports/{id}/resolve` | A | body `{action: dismiss|warn|suspend, note}` |
| GET | `/admin/disputes` | A | disputed loans |
| POST | `/admin/disputes/{id}/resolve` | A | body `{outcome, note}`; applies trust effects |
| POST | `/admin/users/{id}/suspend` | A | suspend an account (audit-logged) |
| POST | `/admin/users/{id}/unsuspend` | A | restore an account |
| GET/POST/PATCH | `/admin/meetup-spots` | A | manage spots |
| PATCH | `/admin/meetup-spots/{spot_id}` | A | update one curated meetup spot |
| GET | `/admin/audit-log` | A | filter by entity |

## Health
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/health` | public | `{status:"ok", version, time}` |

## Error codes (minimum set)
`VALIDATION_ERROR` · `UNAUTHENTICATED` · `FORBIDDEN` · `NOT_FOUND` · `RATE_LIMITED` · `EMAIL_DOMAIN_NOT_ALLOWED` · `OTP_INVALID` · `OTP_EXPIRED` · `OTP_LOCKED` · `ACCOUNT_SUSPENDED` · `TRUST_LIMIT_REACHED` · `PROHIBITED_ITEM` · `REQUEST_NOT_OPEN` · `OFFER_NOT_PENDING` · `LOAN_INVALID_STATE` · `CODE_INVALID` · `CODE_EXPIRED` · `CODE_LOCKED` · `AGREEMENT_REQUIRED` · `BLOCKED` · `CONFLICT` · `INTERNAL_ERROR`
