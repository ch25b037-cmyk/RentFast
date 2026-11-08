---
description: Continue exactly where the last session stopped (use after a limit, crash or new chat)
agent: agent
---
You are continuing a long build with no memory of earlier chats.

1. Read `docs/PROGRESS.md` and follow `NEXT ACTION`. Read the last 10 lines of the session log and any open items in `docs/ERRORS_LOG.md` marked `UNRESOLVED`.
2. Run `python scripts/verify.py` and the area check for the work in progress. State the baseline: what is green and what is red **before** you change anything.
3. If the baseline is red because of the last session's unfinished work, fix that first.
4. Continue the milestone with the operating loop in `.github/copilot-instructions.md` §1.
5. Before you stop, rewrite `NEXT ACTION` so the next session can resume without this chat.

Do not redo finished work. Do not restart the milestone.
