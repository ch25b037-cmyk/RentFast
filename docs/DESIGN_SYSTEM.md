# Design System

Direction: **"campus noticeboard meets modern fintech."** Warm paper surfaces, confident ink typography, one loud signal colour for urgency, one calm teal for trust. Clean, quick, a little playful. Mobile-first (students are on phones between classes).

Do NOT produce: purple-to-blue gradient heroes, identical grey card grids, emoji used as icons, lorem ipsum, stock-photo placeholders, centre-aligned walls of text.

## 1. Tokens (`frontend/src/styles/tokens.css`)
Define as CSS variables on `:root` and `[data-theme="dark"]`; map them in the Tailwind config. Components use tokens only — never raw hex.

| Token | Light | Dark |
|-------|-------|------|
| `--bg` | #F7F4EE | #0F1114 |
| `--surface` | #FFFFFF | #171A1F |
| `--surface-2` | #EFEBE2 | #1F232A |
| `--line` | #E2DDD1 | #2A2F37 |
| `--ink` | #15181C | #F2EFE8 |
| `--ink-muted` | #5B6168 | #A2A8B0 |
| `--signal` (urgency, primary CTA) | #FF6A2B | #FF7A3D |
| `--on-signal` | #15181C | #15181C |
| `--trust` (verified, success-ish) | #0B7A6B | #2BC4AE |
| `--on-trust` | #FFFFFF | #0F1114 |
| `--danger` | #C62828 | #FF6B6B |
| `--warning` | #B26A00 | #F2A93B |
| `--success` | #1F7A3D | #4CC375 |

Contrast values above were estimated by hand. **Verify with a script** (WCAG AA: 4.5:1 body text, 3:1 large text/UI) during M8 and record results in `docs/audits/`. Adjust the hex values if anything fails.

Typography: headings **Bricolage Grotesque**, body **Inter**, codes and countdowns **JetBrains Mono** (self-host or Google Fonts with `font-display: swap`).
Scale: display 40/44 · h1 32/38 · h2 24/30 · h3 20/26 · body 16/24 · small 14/20 · caption 12/16. Tight tracking on headings (−0.02em).
Spacing: 4px base (4, 8, 12, 16, 24, 32, 48, 64). Radius: 8 inputs · 14 cards · 22 sheets · 999 pills.
Elevation: 3 levels, soft and layered (low-opacity ink shadows); in dark mode use borders + subtle surface lift instead of shadows.
Texture: a very light grain overlay (≤4% opacity) and one soft radial glow behind hero areas. Restrained.

## 2. Motion
- Durations 150–250 ms, ease `cubic-bezier(0.2, 0.8, 0.2, 1)`; sheets and dialogs use a gentle spring (framer-motion).
- Page transitions: fade + 8px rise. List items stagger in (30 ms).
- Success moments (offer accepted, handover confirmed): a brief, tasteful confirmation animation — never confetti spam.
- **Honour `prefers-reduced-motion`**: disable transforms, keep opacity fades.

## 3. Signature components
| Component | Spec |
|-----------|------|
| `UrgencyChip` | Shows "needed in 2h 10m" with a live countdown; colour steps: >24h neutral, <24h warning, <3h signal pulse |
| `TrustBadge` | Shield icon + tier label; teal for Trusted, neutral for Member, muted for New |
| `RequestCard` | Category glyph, title, time window, urgency chip, requester name + trust badge, offer count, one primary action |
| `HandoverCode` | Six large mono digit boxes, ring timer showing time left, "Show this to {name}" caption; hidden behind a "Reveal" tap; blurred on app background |
| `CodeEntry` | Six-box OTP-style input, auto-advance, paste support, clear error shake |
| `LoanTimeline` | Vertical stepper bound to `LoanEvent`s; current step highlighted; times in local format |
| `MeetupSpotPicker` | Cards with name + hint, single select |
| `EmptyState` | Small illustration (inline SVG, original), one-line explanation, one action |
| `Skeleton` | Shape-accurate placeholders for cards, lists, detail pages |
| `Toast` | `sonner`, bottom on mobile, top-right desktop |
Primitives to build first (M8): Button (primary/secondary/ghost/danger, loading), Input, Textarea, Select, Chip, Card, Sheet/Dialog, Tabs, Avatar, Badge, Tooltip, Skeleton, Toast, Stepper.

## 4. Layout
- **Mobile (<768px):** bottom tab bar — Home · Requests · **+** (create) · Loans · Me. Safe-area padding.
- **Desktop:** left rail navigation, content max-width 1120px, optional right column for notifications/active loan.
- Touch targets ≥ 44px. Works down to 360px width with no horizontal scroll.

## 5. Screens (each needs loading / empty / error states)
1. **Welcome + sign-in** — value prop in one line, email field, OTP step with `CodeEntry`.
2. **Home** — active-loan banner (if any), "Needed soon" horizontal rail, live feed with category filter chips.
3. **Create request** — 3-step sheet: what → when → where. Live summary card. Inline validation.
4. **Request detail** — summary, requester trust, offers list (owner view) / "Offer to lend" sheet (lender view).
5. **My items** — grid, add item sheet, availability toggle.
6. **Offer chat** — message thread, masked-contact notice, accept/decline bar for the requester.
7. **Loan detail** — timeline, agreement step, spot + time, `HandoverCode` / `CodeEntry` depending on role, countdown to due, report/dispute in an overflow menu.
8. **Profile** — public view + edit, trust tier explainer, reviews.
9. **Notifications** — grouped by day, unread dot, tap to deep link.
10. **Safety centre** — plain-language rules, meetup tips, block list, how to report.
11. **Admin** — reports queue, disputes, meetup spots, audit log (desktop-optimised table).

## 6. Accessibility
Semantic HTML first; visible focus ring (2px `--signal` offset 2px); labels on every input; `aria-live` for toasts and code errors; dialog focus trap; colour never the only signal; AA contrast; keyboard path for every flow.

## 7. Copy and tone
Short, direct, friendly. Verbs on buttons ("Send offer", "Show my code"). Errors say what happened and what to do next. Time language is relative ("in 2h") with the absolute time on hover/tap.

## 8. UI definition of done (checked by `sleek-ui` skill and `/ui-polish`)
- [ ] Only tokens used; no raw hex in components
- [ ] Light and dark both reviewed
- [ ] 360px, 768px, 1280px reviewed
- [ ] Loading, empty, error, success states present
- [ ] Focus order and keyboard path verified
- [ ] Reduced motion respected
- [ ] No console errors or React key warnings
- [ ] Screenshot saved to `docs/audits/screens/` (if Playwright available)
