# Hooks
Three Claude Code hooks enforce what prompts alone cannot. Python 3, stdlib only. Each reads the hook JSON on stdin;
exit 2 blocks the tool call and shows stderr to the agent, exit 0 allows it. Tests: `python scripts/tests/test_hooks.py`.

## TEAM_SEAT
Each seat's agent runs with env `TEAM_SEAT` set to its number: `2`, `3`, `6`, `3b` (squad member). `No. 2` is read as `2`.
Set it where the agent is launched (shell env, or `"env": {"TEAM_SEAT": "3"}` in that seat's `.claude/settings.json`).
Unset → seat `unknown`: owns no verdict file, cannot read unsealed ones; handoff notes are named `unknown-*.md`.

## guard_locked.py (PreToolUse)
Blocks Edit/Write/MultiEdit/NotebookEdit on paths matching `.team/locked.txt` (and on that file). Install for attack and midfield.

## guard_sealed.py (PreToolUse)
Verdicts: `.team/verdicts/<submission-id>/<seat>.md`; `SEALED` in that directory means all are filed (law 2, laws.md).

| Call | Unsealed submission | Sealed |
|---|---|---|
| Read / Edit / Write own `<seat>.md` | allowed | read allowed, edit blocked (immutable) |
| Read / Edit / Write another seat's file | blocked | read allowed, edit blocked |
| Grep inside the directory | blocked | allowed |
| Grep over an ancestor (project root, `.team`) | blocked if it would hit other seats' files; a `glob`/`type` excluding `.md` passes | allowed |
| Glob (names only = "submitted / not yet") | No. 6 only | allowed |
| Bash naming a path under `.team/verdicts/` | own file allowed; No. 6 may `ls`/`dir` the directory (no `;`, `&`, `|`); else blocked | allowed; writes to `.md` blocked |
| Create `SEALED` (Edit/Write, or Bash with a write token) | No. 6 or No. 1 only | – |

Fail closed: unparseable input or an internal error blocks the call if its raw text mentions `verdicts`, otherwise allows it
(the hook must not break unrelated tools). Install for every judging seat (No. 2, No. 3, squad members) and No. 6.

## precompact_handoff.py (PreCompact)
Writes `.team/handoff/<seat>-<YYYYmmdd-HHMMSS>.md` in the handoff template (templates.md) before compaction.
It cannot ask the model, so it fills mechanically from `transcript_path` (JSONL): last user/assistant messages (8, clipped),
last 20 tool calls with errors flagged, files edited (Edit/Write/MultiEdit/NotebookEdit), files read.
STUCK AT / DO NOT RETRY / NEXT STEP are written as `fill in: ...` for the bench agent. Missing or broken transcript → a
skeleton note with the reason. Always exits 0: never blocks compaction. Mention it in the seat's CLAUDE.md (substitution.md).

## settings.json
```json
{
  "env": {"TEAM_SEAT": "3"},
  "hooks": {
    "PreToolUse": [
      {"matcher": "Edit|Write|MultiEdit|NotebookEdit",
       "hooks": [{"type": "command", "command": "python scripts/guard_locked.py"}]},
      {"matcher": "Read|NotebookRead|Grep|Glob|Bash|PowerShell|Edit|Write|MultiEdit|NotebookEdit",
       "hooks": [{"type": "command", "command": "python scripts/guard_sealed.py"}]}
    ],
    "PreCompact": [
      {"matcher": "manual|auto",
       "hooks": [{"type": "command", "command": "python scripts/precompact_handoff.py"}]}
    ]
  }
}
```
Paths are relative to the project root; if the session may `cd` elsewhere use
`python "$CLAUDE_PROJECT_DIR/team-formation/scripts/guard_sealed.py"` (adjust to where the skill lives).

## Known limits
- **Bash/PowerShell check is a string match.** It catches paths written literally (`cat .team/verdicts/S1/2.md`, globs,
  backslashes). It misses indirection: `cd .team && cat verdicts/S1/2.md`, variables, `grep -r x .`, scripts that open the
  file. For real isolation deny Bash to judges, or keep each judge in its own worktree / OS user until SEALED.
- **Hooks see only tool calls.** Subagents, MCP tools not in the matcher, other processes and the human are not checked.
- **Seat identity is an env var**; an agent that can edit its settings or env can change it. Do not give judges write access
  to `.claude/`.
- SEALED is trusted as written; the hook does not check that every expected seat has filed.
- The handoff note is a skeleton: what the agent was thinking is lost unless it wrote it to the board first.

## guard_locked.py and No. 1
The lock guard lets `TEAM_SEAT=1` edit locked paths (No. 1 is the sole writer of the bank and the locked statement); `.team/locked.txt` itself stays locked for every seat and is edited by the coach. Because subagents inherit `TEAM_SEAT`, run No. 1 in its own session.
