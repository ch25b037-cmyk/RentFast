# File Registry

One row per file the project owns (source, config, tests, docs). Format: `| path | purpose | milestone | status | last check |`.
`status`: `new` · `ok` · `needs-fix`. `last check`: `YYYY-MM-DD <command or audit id> pass|fail`.
Keep rows sorted by path. Update in place; remove the row if the file is deleted. A glob row (for example `backend/alembic/versions/*.py` or `frontend/src/components/ui/*.jsx`) may cover many similar files; use one only for generated or very uniform files, and keep real purposes in the row. `python scripts/verify.py` warns about unregistered files under `backend/` and `frontend/src/`.

## Harness (created with the project; maintained by humans)
| path | purpose | milestone | status | last check |
|------|---------|-----------|--------|------------|
| AGENTS.md | short pointer + essentials for coding agents | harness | ok | 2026-11-08 harness check |
| .github/copilot-instructions.md | operating loop and hard rules | harness | ok | 2026-11-08 harness check |
| .github/instructions/*.instructions.md | path-scoped rules (backend, frontend, env, docs, tests) | harness | ok | 2026-11-08 harness check |
| .github/agents/*.agent.md | Builder, Auditor, UI Designer | harness | ok | 2026-11-08 harness check |
| .github/prompts/*.prompt.md | slash prompts | harness | ok | 2026-11-08 harness check |
| .github/skills/*/SKILL.md | six skills | harness | ok | 2026-11-08 harness check |
| docs/*.md | specs and tracking files | harness | ok | 2026-11-08 harness check |
| scripts/verify.py | automated repo check | harness | ok | 2026-11-08 harness check |
| README_FIRST.md | human setup guide: how to run the build | harness | ok | 2026-11-08 harness check |
| .gitignore | keeps secrets, caches and build output out of git | harness | ok | 2026-11-08 harness check |
| .vscode/*.json | Copilot settings, verify tasks, extension list | harness | ok | 2026-11-08 harness check |
| backend/.env.example | backend environment template (fake values) | harness | ok | 2026-11-08 harness check |
| frontend/.env.example | frontend environment template (fake values) | harness | ok | 2026-11-08 harness check |

## Application files (the Builder fills this table)
| path | purpose | milestone | status | last check |
|------|---------|-----------|--------|------------|
| backend/alembic.ini | Alembic configuration | M0 | ok | 2026-11-08 ruff pass |
| backend/alembic/env.py | Alembic migration environment | M0 | ok | 2026-11-08 ruff pass |
| backend/alembic/script.py.mako | Migration template | M0 | ok | 2026-11-08 verify pass |
| backend/alembic/versions/*.py | Alembic schema migrations | M1-M2 | ok | 2026-11-08 alembic upgrade pass |
| backend/Dockerfile | Backend production container | M12 | ok | 2026-11-08 verify pass |
| backend/app/*.py | FastAPI application entrypoints and dependencies | M0 | ok | 2026-11-08 pytest pass |
| backend/app/*/*.py | Core, database, schema and router modules | M0 | ok | 2026-11-08 pytest pass |
| backend/pyproject.toml | Ruff and pytest configuration | M0 | ok | 2026-11-08 ruff pass |
| backend/requirements-dev.txt | Backend development dependencies | M0 | ok | 2026-11-08 install pass |
| backend/requirements.txt | Backend runtime dependencies | M0 | ok | 2026-11-08 install pass |
| backend/tests/*.py | Backend M0 tests | M0 | ok | 2026-11-08 pytest pass |
| frontend/e2e/app.spec.js | Playwright happy and failure-path browser tests plus a11y scan | M11 | ok | 2026-11-08 e2e pass |
| frontend/eslint.config.js | Frontend lint configuration | M0 | ok | 2026-11-08 lint pass |
| frontend/index.html | Vite HTML entrypoint | M0 | ok | 2026-11-08 build pass |
| frontend/package.json | Frontend dependencies and scripts | M0 | ok | 2026-11-08 install pass |
| frontend/playwright.config.js | Playwright browser test configuration | M11 | ok | 2026-11-08 e2e pass |
| frontend/postcss.config.js | PostCSS configuration | M0 | ok | 2026-11-08 build pass |
| frontend/src/*.js | Frontend API and test support modules | M0 | ok | 2026-11-08 lint/test pass |
| frontend/src/*.jsx | Frontend React application and tests | M0 | ok | 2026-11-08 lint/test pass |
| frontend/src/*/*.js | Frontend API and app support modules | M0 | ok | 2026-11-08 lint/test pass |
| frontend/src/*/*.jsx | Frontend React application and tests | M0 | ok | 2026-11-08 lint/test pass |
| frontend/src/styles/*.css | Frontend design tokens and base styles | M0 | ok | 2026-11-08 build pass |
| frontend/tailwind.config.js | Tailwind token mapping | M0 | ok | 2026-11-08 build pass |
| frontend/vite.config.js | Vite and Vitest configuration | M0 | ok | 2026-11-08 build/test pass |
| frontend/Dockerfile | Frontend production container | M12 | ok | 2026-11-08 verify pass |
| scripts/seed.py | Idempotent catalog and meetup seed | M2 | ok | 2026-11-08 seed pass |
