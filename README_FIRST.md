# README_FIRST — how to run the CampusLend build with GitHub Copilot

This folder is a **harness**: instructions, skills, agents, prompts, specs, trackers and checkers. It contains no application code. Copilot writes the app (FastAPI backend, React frontend) by following these files.

## 1. One-time setup (15 minutes)
1. Install: Python 3.11+, Node.js LTS, Git, VS Code with the extensions in `.vscode/extensions.json`.
2. Put this folder at the root of a new repo and run `git init`. Open it in VS Code.
3. In VS Code Settings confirm Copilot picks up repo instructions and prompt files. `.vscode/settings.json` already enables them and raises the agent request limit to 100. If VS Code shows an unknown-setting warning, your version renamed that key; search Settings for "agent max requests", "instruction files" and "AGENTS.md" and set them by hand.
4. Open Copilot Chat, switch to **Agent** mode, and choose your model (Luna) in the model picker.
5. Answer the "Open for you" questions at the bottom of `docs/DECISIONS.md` as far as you can (college email domain, first admin emails). You can also answer them later in `backend/.env`.

## 2. Running the build
| Step | What you type in Copilot Chat | What happens |
|------|-------------------------------|--------------|
| 1 | `/kickoff` | Reads all docs, confirms the environment, builds milestone M0 |
| 2 | `/build-milestone` then `M1` | Builds that milestone with a check after every batch |
| 3 | `/milestone-close` then `M1` | Verifies acceptance lines, runs strict checks and an audit, updates progress |
| 4 | Repeat steps 2–3 for M2 … M12 | |
| any time | `/resume` | Continues from `NEXT ACTION` after a limit, crash or new chat |
| any time | `/audit` | Independent audit of every file, writes a report in `docs/audits/` |
| any time | `/fix-errors` | Works through failing checks and audit blockers |
| UI work | `/ui-polish` | Design-system pass on a screen or the whole app |
| after M12 | `/improve` then `IMP-001` | Implements one backlog item |
| before launch | `/security-review` | Attacker-minded review against `docs/SAFETY_SPEC.md` |

You can also pick the **Builder**, **Auditor** or **UI Designer** agent from the agent picker for free-form requests.

Long builds will hit per-turn limits. That is expected: type `/resume`. Progress lives in `docs/PROGRESS.md`, not in the chat.

## 3. The regular checks (what keeps it honest)
- After every batch of up to 5 files: Copilot registers the files in `docs/FILE_REGISTRY.md`, runs lint and tests, fixes failures, logs real errors in `docs/ERRORS_LOG.md`, updates `docs/PROGRESS.md`.
- You can run the whole-repo check yourself any time:
  ```
  python scripts/verify.py            # normal
  python scripts/verify.py --quick    # static only, a few seconds
  python scripts/verify.py --strict   # warnings fail, frontend build runs (used at milestone close)
  ```
  Run it inside the activated backend virtualenv. Results are written to `docs/VERIFY_LAST_RUN.md`. It checks: harness integrity, secrets, env-file sync, forbidden patterns, layering, registry vs real files, API contract drift, ruff, pytest, eslint, vitest, build, and whether PROGRESS.md is stale.
- VS Code tasks (Terminal → Run Task) wrap the same commands.

## 4. Files you should know
| File | Why |
|------|-----|
| `docs/PROGRESS.md` | Where the build is and what happens next |
| `docs/IMPROVEMENTS.md` | Ideas parked for later (15 seeded) |
| `docs/ERRORS_LOG.md` | Every real problem and its fix |
| `docs/DECISIONS.md` | Choices already made; change one by adding a new row |
| `docs/SAFETY_SPEC.md` | The lending safety rules and required tests |
| `docs/DESIGN_SYSTEM.md` | Colours, type, motion, screens |
| `backend/.env.example`, `frontend/.env.example` | Environment templates; copy to `.env` and never commit |

## 5. If Copilot misbehaves
| Symptom | Fix |
|---------|-----|
| Prompt runs in Ask mode, not Agent | In the `.prompt.md` frontmatter replace `agent: agent` with `mode: agent` (older VS Code) or pick Agent mode manually |
| Skills or instructions seem ignored | Start your message with "Follow `.github/copilot-instructions.md`", and confirm the instruction-file settings are on |
| It starts building the next milestone early | Reply: "Stop. Milestone MX is not closed. Run /milestone-close MX." |
| It invents endpoints or fields | Reply: "Use docs/API_CONTRACT.md as the contract. If it must change, change the doc and log a decision." |
| Same error keeps recurring | Run `/fix-errors`; after three failed attempts it logs the problem as UNRESOLVED and moves on |
| It claims things are done that are not | Run `/audit`; the Auditor runs the checks itself and does not trust earlier claims |

## 6. Honest limits
- These files were written and structurally verified (`verify.py` passes on the harness itself) but were **not run inside Copilot**. Custom-agent and prompt-file frontmatter keys change between VS Code releases, so expect to adjust one line if something is ignored.
- I do not know the behaviour or limits of the Luna model. The instructions are written to be explicit and model-agnostic. If it loses the thread, `/resume` re-orients it from the files.
- The safety design is a strong baseline for a campus lending app, not a substitute for your college's policies or for a real security review before wide launch.
