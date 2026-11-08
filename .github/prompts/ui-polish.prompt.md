---
description: Polish the UI of a screen or the whole app to the design system (states, motion, a11y, responsive)
agent: agent
---
Act as the **UI Designer-Engineer** (see `.github/agents/ui-designer.agent.md`) and use the `sleek-ui` skill.

Target: ${input:target:Screen name, or "all screens built so far"}

1. Read `docs/DESIGN_SYSTEM.md` and open the target screens in the running app.
2. List the defects against the UI definition of done (DESIGN_SYSTEM §8) with a severity for each.
3. Fix them: tokens, hierarchy, spacing, states, motion, responsive layout, accessibility, copy.
4. Re-verify at 360 / 768 / 1280 px, light and dark, keyboard only, reduced motion.
5. Run `npm run lint && npm test -- --run && npm run build`.
6. Update `docs/FILE_REGISTRY.md` and `docs/PROGRESS.md`; park new ideas in `docs/IMPROVEMENTS.md`.

Do not change business logic or the API layer.
