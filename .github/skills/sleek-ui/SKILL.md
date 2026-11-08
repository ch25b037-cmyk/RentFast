---
name: sleek-ui
description: Implement and review polished, distinctive UI for CampusLend following docs/DESIGN_SYSTEM.md - tokens, typography, motion, states, responsive and accessibility checks. Use for any visible frontend work and for /ui-polish.
---
# sleek-ui

The look is defined in `docs/DESIGN_SYSTEM.md` ("campus noticeboard meets modern fintech"). This skill turns it into a repeatable process.

## Build process
1. **Tokens first.** Confirm `src/styles/tokens.css` and the Tailwind mapping exist (M8). Never reach for raw hex or arbitrary pixel values.
2. **Primitives before pages.** Compose pages only from `components/ui`. If a needed primitive is missing, build it (with states: hover, focus, active, disabled, loading) before the page.
3. **Hierarchy.** One primary action per view, in `--signal`. Headings in Bricolage Grotesque with tight tracking; body Inter; codes/countdowns JetBrains Mono. Generous whitespace; align to the 4px scale.
4. **Depth and texture.** Layered soft elevation in light mode, borders + surface lift in dark. A very light grain and one soft radial glow behind hero areas, nothing more.
5. **Motion.** 150–250 ms ease-out; list stagger 30 ms; spring on sheets. Wrap with a `useReducedMotion` check.
6. **States.** Skeleton shaped like the final content; empty state with an original inline SVG and one action; error state with retry; success with a short confirmation moment.
7. **Responsive.** Design at 360px first; then 768px and 1280px. Bottom tab bar on mobile, left rail on desktop.
8. **Content.** Real, specific copy (no lorem ipsum). Buttons start with a verb. Times are relative with absolute on hover/tap.

## Signature moments to get right
- `HandoverCode`: large mono digits in separate boxes, ring timer, "Reveal" tap, hides when the tab loses focus.
- `UrgencyChip`: live countdown, colour steps by time left.
- `LoanTimeline`: the loan's story at a glance.
- Request cards that feel like pinned notes: crisp, scannable, one action.

## Self-review (do this before ticking the UI definition of done)
1. Run the app. Look at each changed screen at 360 / 768 / 1280 and in light + dark.
2. If Playwright is installed, capture screenshots into `docs/audits/screens/` and inspect them.
3. Tab through the screen: is the order logical, is focus always visible?
4. Turn on reduced motion in the OS or devtools: does everything still work?
5. Throttle the network: do skeletons appear and match the final layout?
6. Check the console: zero errors and warnings.
7. Run a contrast check on every text/background token pair you used; record it in `docs/audits/`.

## Anti-patterns (reject on sight)
- Purple/blue gradient hero, generic glassmorphism everywhere, identical grey cards.
- Emoji as icons (use `lucide-react`), stock placeholder images, lorem ipsum.
- More than one competing primary button.
- Colour as the only status signal.
- Animations that block interaction or run forever.
- Layout shift when data arrives.
- Text below 14px for anything essential.
