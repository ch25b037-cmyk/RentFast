---
description: Security and safety review against SAFETY_SPEC, with the pre-launch checklist
agent: agent
---
Act as the **Auditor** with a security mindset and the `loan-safety` skill.

1. Walk through `docs/SAFETY_SPEC.md` §2: for each control, find the implementation and the tests. Mark `done`, `partial` or `missing`.
2. Try to break it by reading the code as an attacker: ID guessing across users, state-machine skips, code brute force, replayed codes, refresh-token reuse, rate-limit bypass, mass assignment, XSS through user text, CORS misconfiguration, secrets in logs.
3. Check dependencies for known vulnerabilities (`pip-audit` and `npm audit` if available; otherwise say they were not run).
4. Complete the pre-launch checklist in SAFETY_SPEC §7.
5. Write `docs/audits/SECURITY_<today>.md` with findings ranked blocker / high / medium / low, each with file, line, impact and a fix.

Do not edit source. Hand findings to the Builder via `docs/ERRORS_LOG.md` (`UNRESOLVED`) and the report.
