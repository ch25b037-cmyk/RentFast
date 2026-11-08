---
applyTo: "frontend/**"
description: Rules for all React frontend code and styling
---
# Frontend rules

Design source of truth: `docs/DESIGN_SYSTEM.md`. API source of truth: `docs/API_CONTRACT.md`.

1. **Language:** JavaScript with JSX (project decision D-004). Use JSDoc `@typedef` for shared shapes and zod schemas as the runtime contract.
2. **Data access:** only through `src/api/*` modules and TanStack Query hooks. No `fetch` or `axios` inside components or pages.
3. **Validate responses** with zod in the API layer. A schema mismatch becomes a visible, logged error, not a silent `undefined`.
4. **Styling:** Tailwind utilities that map to tokens in `src/styles/tokens.css`. No raw hex colours, no magic pixel values outside the spacing scale.
5. **Every async view has four states:** loading (skeleton shaped like the content), empty (helpful + action), error (what happened + retry), success.
6. **Forms:** react-hook-form + zod. Inline errors tied to inputs with `aria-describedby`. Disable submit while pending and show progress.
7. **Accessibility:** semantic elements, labelled controls, visible focus, keyboard path, `aria-live` for toasts and code errors, respect `prefers-reduced-motion`.
8. **Security:** never store access tokens in `localStorage`; keep them in memory and rely on the httpOnly refresh cookie. Never put a loan code in the URL, storage, logs or analytics. Render user text as text (no `dangerouslySetInnerHTML`).
9. **Routing:** route-level code splitting for heavy pages. A guarded route redirects unauthenticated users to sign-in and restores the target afterwards.
10. **Performance:** memoise only after measuring; keep list items light; paginate lists; set sensible `staleTime`.
11. **Tests:** vitest + testing-library for primitives and for each feature's key interaction (render states, submit, error). Test behaviour, not implementation.
12. **Files:** one component per file, PascalCase; hooks `useThing.js`; keep files under ~250 lines.

Checks before you finish a batch: `npm run lint && npm test -- --run` from `frontend/`. For visible work also follow the `sleek-ui` skill and tick the UI definition of done.
Use the `react-feature` skill for any new feature.
