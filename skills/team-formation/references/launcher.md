# Launcher: running a campaign from one Claude Code session
The orchestrating session is No. 6's harness: it spawns seat agents with the Agent tool, keeps the board and
reports to the coach. The coach (human) only sets the problem and receives goals and phase reports.
A multi-agent Workflow script could automate the loop below, but running a Workflow needs the user's explicit
opt-in; without it, run the steps by hand with the Agent tool.

## 0. Set up (once)
1. `python <skill>/scripts/init_team.py <campaign-dir> --variant math|software|algorithm --problem "<one line>"`.
   Rerunning is safe: existing files are skipped; `--refresh-seats` rebuilds `seats/*.md` from the role cards.
2. Merge `.team/hooks.settings.json` into `<campaign-dir>/.claude/settings.json` (guard_locked, guard_sealed,
   precompact_handoff, by absolute path). Hooks load at session start: restart the session after merging.
3. Choose families: defenders (No. 2, No. 3) on a different model family from the attack; No. 4 on a different
   family from No. 10. If only one family is available: different prompt, fresh context, no shared notes, and
   write "independence: context only (same family)" in every bank entry and in `metrics.md`.
4. Write the baseline plan in `metrics.md`: one agent, same budget, same problem, same tools, same start files.

## 1. One spawn
Prompt = the full text of `.team/seats/<n>.md` + the board excerpt the seat needs (current phase, its task,
relevant fragments, tabu log, its requests) + the task in one paragraph with its budget and the file to write.
- Tell the agent its seat: "You are No. <n>. TEAM_SEAT=<n>." The hooks read the environment variable TEAM_SEAT,
  and every Agent-tool subagent inherits the orchestrator's environment (start the orchestrator with TEAM_SEAT=6, so
  it may write SEALED). Agent-tool spawns therefore cannot be told apart by the hooks. For No. 2, No. 3 and No. 1,
  whose verdict and bank writes the hooks check per seat, run a separate headless session with its own environment
  (e.g. `TEAM_SEAT=2 claude -p "<prompt>"` in the campaign directory, or No. 1 in its own worktree); if you use the
  Agent tool for them anyway, the sealed-verdict rule holds by prompt only: record that on the board.
- One task per spawn. The agent returns a board fragment (templates.md); No. 6 appends it to the board at agent-level.
- Spawn a seat only when there is a task and budget for it. Core seats: 6, 14, 10, 8, 4, 9, 2, 3, 1.
  Wings 11 and 7: only after No. 6 writes "switched on" for them in the board's "Seats switched on" table.
- Independent tasks go out in one message (parallel spawns). Generator squads: 3–5 agents, play alone first (squads.md).

## 2. Phases (phases.md; No. 6 alone switches phase and writes budget and stop condition on the board first)
1. **Phase −1 Examples.** Spawn No. 10 (literature seeds) and No. 14 (meaningful examples) in parallel; then No. 14
   computes the worked example with a rerunnable script in `.team/examples/`; No. 10 writes a conjecture matching the
   library and hands it to No. 4; No. 4 hunts counterexamples at the edge of each hypothesis and picks a new case with
   a written prediction; then No. 14 computes it. No. 9 off. Ends when a prediction written before computing is right.
2. **Phase 0 Lock.** Spawn No. 1 and No. 2 in parallel, each formalizing the conjecture alone; diff; lock; add the
   locked paths to `.team/locked.txt`. No. 3 quick literature scan; No. 10 proposes, No. 8 builds the first lemma graph;
   No. 14 checks the statement on the whole library. Software: acceptance tests from the spec, locked before code.
3. **Phase 1 Explore.** No. 10 → No. 8 (next lemma) → No. 4 tries to break it → No. 9 proves and submits.
   No. 3 runs the quick novelty check on each new branch and load-bearing lemma. Cross-field cards from No. 11 / No. 7
   go to No. 14's kill test, then No. 10, never straight to No. 9.
4. **Phase 2 Counter-press** (a load-bearing lemma broke). Spawn 14, 4, 10, 8, 9 on that exact point within a window;
   No. 2 gives only the error location; the patch goes to a fresh No. 2.
5. **Phase 3 Verify.** Sealed verdict flow (step 3), with No. 2 as a squad if the budget allows; No. 14 feeds data to No. 2;
   wings and No. 10 off. Pass → No. 1 → bank → back to Phase 1 for the next lemma; fail → Phase 2.

## 3. Sealed verdicts (every submission)
1. No. 9 writes the submission (templates.md); No. 6 creates `.team/verdicts/<submission-id>/`.
2. Spawn No. 2 and No. 3 in parallel, each in a fresh agent (No. 2: a new agent per submission, never resumed), each
   given only the submission, the locked statement, the worked example (No. 2) and its seat file; not the board
   discussion, the attack's reasoning or No. 4's search log.
3. Each writes `.team/verdicts/<submission-id>/<seat>.md` (2.md, 3.md; squad members 2b.md, ...).
4. No. 6 checks only which files exist ("submitted / not yet"), never their content. When all exist, the orchestrator
   writes the file `SEALED` in that directory. Only then it reads the verdicts and opens discussion on the board.
5. Any sealed failure with evidence → back to No. 9 (or No. 14 if it failed on an example). No voting.
   Both pass → spawn No. 1 for the final check; No. 1 alone appends to `.team/bank.md` with the final-check label and
   the kinds of independence achieved (model / context / tool).

## 4. Substitution
1. The PreCompact hook writes a handoff note to `.team/handoff/`; otherwise No. 6 checks the token estimate between
   tasks (default 50% of the context window) and watches for fatigue (repeats, re-entering tabu, losing definitions).
2. Retire that agent; spawn a fresh one with: seat file + handoff note + board summary + tabu log + the task.
3. Record the handoff on the board (seat, date, context level, note file).

## 5. Stop criteria
- Per direction, written on the board before it starts: budget spent · window expired · killed by counterexample ·
  superseded. Any one met → stop, tabu entry with reason and scope; no extension without a new entry and reason.
- Per campaign: total budget spent, or the coach's goal is in the bank. Report to the coach: bank entries and phase reports only.

## 6. Baseline and report
1. Spawn one agent (no seat file; the problem, the same budget, the same tools, the same start files) in a separate
   directory so it cannot read `.team/`. Run it to the same budget.
2. Fill `.team/metrics.md` for both: verified results with final-check label · time and cost to first verified result ·
   wrong directions killed early and their cost · catch rate of planted false variants · total spend · independence achieved.
3. Team does not beat baseline → shrink the team (switch seats off, shrink squads) for the next campaign.
