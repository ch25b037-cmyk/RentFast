---
name: react-feature
description: Build or change a React (JSX) frontend feature end-to-end (API module, query hooks, components, page, route, states, tests). Use for any screen or data-driven UI in CampusLend.
---
# react-feature

Build one screen or one interaction at a time.

## Before you start
1. Read the screen spec in `docs/DESIGN_SYSTEM.md` §5, the endpoints in `docs/API_CONTRACT.md`, and the ROADMAP milestone.
2. Confirm the backend endpoints exist and match the contract (open `/docs` on the running backend). If not, build against the contract with `msw` handlers and record the gap in PROGRESS.md.

## Steps
1. **API module** (`src/api/<resource>.js`): one function per endpoint, returns zod-parsed data, throws the shared `ApiError` (`src/api/errors.js`).
2. **Query hooks** (`src/hooks/use<Thing>.js`): `useQuery` / `useMutation` wrappers with sensible `staleTime`, invalidation of related keys, optimistic updates only where rollback is simple.
3. **Components** (`src/components/<feature>/`): presentational, typed with JSDoc, built from `components/ui` primitives. No data fetching inside them.
4. **Page** (`src/pages/<Name>.jsx`): composes hooks and components; handles **loading / empty / error / success**.
5. **Route** (`src/app/routes.jsx`): add lazy route; guard if it needs auth.
6. **Forms:** react-hook-form + zod; inline errors with `aria-describedby`; submit disabled while pending.
7. **Tests:** at least render states + one key interaction + one error path (`vitest`, testing-library, `msw`).
8. **Visual pass:** follow the `sleek-ui` skill checklist.
9. **Run checks:** `cd frontend && npm run lint && npm test -- --run && npm run build`.
10. **Register files** in `docs/FILE_REGISTRY.md`; **update** `docs/PROGRESS.md`.

## Definition of done for a frontend slice
- [ ] Data only through `src/api` + hooks; responses validated with zod
- [ ] Four states present and visually designed
- [ ] Only design tokens; no raw hex
- [ ] Keyboard path, labels and focus verified
- [ ] 360px / 768px / 1280px checked
- [ ] No tokens, codes or personal data in storage, URLs or logs
- [ ] No console errors, no React key warnings
- [ ] lint, tests, build green

## Common mistakes to avoid
- `fetch` inside a component.
- Storing the access token in `localStorage`.
- Skeletons that do not match final layout (causes layout shift).
- Using index as a list key for reorderable data.
- Showing raw error codes to users; map `error.code` to friendly copy in one place.
- Putting a handover code anywhere except in component state.
