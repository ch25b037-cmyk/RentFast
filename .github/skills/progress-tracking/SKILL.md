---
name: progress-tracking
description: Exact formats and update rules for PROGRESS, FILE_REGISTRY, ERRORS_LOG, IMPROVEMENTS and DECISIONS. Use whenever you create files, hit an error, make a decision, finish a step, or are about to stop a session.
---
# progress-tracking

These files let a fresh session (with zero chat memory) continue exactly where the last one stopped.

## docs/PROGRESS.md
Sections: **Status**, **NEXT ACTION**, **In progress**, **Milestones** (checkbox table), **Blockers**, **Session log**.
- After each batch: tick completed items, adjust **In progress**.
- Before stopping, rewrite **NEXT ACTION** as 2–5 sentences: current milestone, last file touched, what failed or remains, the exact first command to run.
- Session log is append-only, one line: `YYYY-MM-DD HH:MM | M<n> | what was done | check result`.

## docs/FILE_REGISTRY.md
Row format: `| path | purpose | milestone | status | last check |`
- `status`: `new` (just created, unchecked) · `ok` (checked and green) · `needs-fix` (known issue, see ERRORS_LOG or IMPROVEMENTS).
- `last check`: `YYYY-MM-DD <command or audit id> pass|fail`.
- Update the row in place when a file changes. Remove the row when the file is deleted.
- Keep rows sorted by path.

## docs/ERRORS_LOG.md
Entry format (append at the bottom, next number):
```
### E-### <short title>
- Date / milestone:
- Symptom (exact message):
- Root cause:
- Fix:
- Prevention (test, lint rule, doc change):
- Status: RESOLVED | UNRESOLVED
```
Log an error when it took more than one attempt to fix, touched safety, or could recur. Trivial typos need no entry.

## docs/IMPROVEMENTS.md
Row format: `| IMP-### | area | idea | impact (H/M/L) | effort (S/M/L) | status |`
`status`: `idea` → `planned` → `doing` → `done` / `dropped`. Do not implement mid-milestone; add the row and continue.

## docs/DECISIONS.md
Row format: `| D-### | date | decision | why | alternatives rejected |`. Append only. To reverse, add a new row that says `supersedes D-###`.

## Update triggers (do these automatically)
| Event | Update |
|-------|--------|
| Created or changed a file | FILE_REGISTRY |
| Finished a batch | PROGRESS (In progress + log) |
| Error needing >1 attempt | ERRORS_LOG |
| Spec deviation or ambiguity resolved | DECISIONS (+ the spec doc itself) |
| Idea outside current milestone | IMPROVEMENTS |
| Milestone closed | PROGRESS (Milestones table), audit report, verify run |
| About to stop for any reason | PROGRESS NEXT ACTION |
