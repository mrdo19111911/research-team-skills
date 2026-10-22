# Tempo: kick off at once, pass directly, coordinate in parallel

Why: in the pilots the coordinator (No. 6) was the bottleneck. Seats waited while it planned, read every return and
relayed every hand-over, so agents started late and one at a time. Parallel work pays only if agents start at
minute 0 and their progress is visible at once. Four rules fix this.

## 1. Kickoff at minute 0
`init_team.py` writes `.team/kickoff.md`: one ready prompt per kickoff agent. Right after setup, in ONE message, the
orchestrator spawns every agent listed there, in parallel, before writing anything else. No planning first: board
details, budget refinements and the bulletin are written while the wave runs.

| Seat | Agents | Kickoff task |
|---|---|---|
| 10 In-field | 2 (classic sources / last three years) | literature review: where the coach's idea already lives, what is open |
| 14 Examples | 2 (smallest case / one realistic case) | concrete instances, the worked example A to Z |
| 3 Novelty | 1 | quick scan: is the coach's claim already known; the five nearest papers |
| 7 Far field | 1 | far-analogy cards on the obstacle as the coach stated it |
| 4 Breaker | 1 | edges: where the claim must fail; the simple baseline it must beat |
| 6 Coordinators | head + one per lane (rule 3) | open the board lanes, set the wave budget |

No. 8 starts the moment No. 10's first conjecture lands in its inbox; No. 9 the moment No. 8 names a next lemma.
Both are off at minute 0 only because there is nothing to build on yet.
The kickoff No. 3 scans; the No. 3 that later judges a submission is a fresh agent, so independence is unchanged.
Default wave budget: written in `kickoff.md`; No. 6 may change it after the wave starts, never before.

## 2. Direct passes (no coordinator in the middle)
A pass is a file in the receiver's inbox, `.team/inbox/<to>/<HHMMSS>-from<from>-<topic>.md` (what, its label, where
the full work is), plus `log_event.py pass --from <a> --to <b> --what "<topic>"`.

Open lanes (attack and midfield pass freely):
14 ⇄ 10 · 14 ⇄ 4 · 10 ⇄ 4 · 7 → 14 and 11 → 14 (kill test) · 10 → 8 · 8 → 4 · 8 → 9 · 4 → 9 · 14 → 9 ·
10 → 3 and 8 → 3 (novelty request) · 3 → 10 and 3 → 8 (novelty answer, quick scan only).
Closed lanes (independence of the judges):
- nothing goes directly to No. 2, No. 1, or to a No. 3 judging a submission; they receive only a submission, through
  the sealed-verdict flow (laws.md);
- No. 4 never receives a proof to judge; only No. 1 writes the bank.

**Work goes direct; decisions go through a coordinator.** A pass that only moves work (an example, a paper, a card,
a counterexample, a baseline) goes straight to the receiver; the lane coordinator reads the inbox copy afterwards, in
parallel, and never stands in the way. Four kinds of pass are gated: the sender writes it to the lane coordinator's
inbox (`.team/inbox/6/`) instead, and the receiver starts only after the coordinator writes `GO <pass file>` (or
`NO <pass file>: <reason>`) on its lane file:
1. **starting a costly direction**: anything that asks No. 9 to prove or build, or opens a new branch of the lemma
   graph (why: a "win" can flip under one parameter; in the UAV pilot a first result flipped with a tolerance and the
   gate stopped No. 9 from building on it);
2. **crossing lanes** (scouting → build, build → verification);
3. **stopping or killing a direction** (the head No. 6 owns stop criteria);
4. **anything bound for a judge** (No. 2, No. 1, a judging No. 3): it goes through the sealed-verdict flow, never as a pass.
A coordinator answers a gated pass before any other work (target: its next action). If it has not answered by the time
the sender's next task ends, the head No. 6 answers instead.

Who wakes the receiver:
- **Teammate messaging available** (agents that can message each other, e.g. Claude Code agent teams with
  SendMessage): the sender messages the receiver directly, and also writes the inbox file (it is the record).
- **Otherwise, the dispatcher rule**: whenever any agent returns, the orchestrator at once spawns one agent for each
  new inbox file whose seat has no running agent, with the inbox file as its task. It does not read, judge or plan
  first; the dispatch is mechanical. Review by the coordinator happens on the board, later, in parallel.

## 3. Several coordinators
The head coordinator (No. 6) keeps only what must have one owner: phase switch, stop criteria per direction, budget,
and the sealed-verdict bookkeeping (expected judges, SEALED). Lane coordinators run beside it, one per lane:

| Lane | Coordinator | Seats | Owns |
|---|---|---|---|
| Scouting | 6a | 14, 10, 7, 11, kickoff No. 3 | `.team/board/lane-scouting.md` |
| Build | 6b | 8, 4, 9 | `.team/board/lane-build.md` |
| Verification | 6c | verdict flow, No. 1 hand-offs | `.team/board/lane-verify.md` |

Each lane coordinator turns its seats' returns into board fragments, keeps its lane's tabu entries, and writes one
summary line per return into its own lane file; it never writes another lane's file. The head merges lane summaries
into `.team/board.md`. Rule of thumb: one coordinator per five running agents. In the match log, lane coordinators are
seat 6 with agent ids 6a, 6b, 6c.

## 4. Progress at once
Every agent writes progress as it goes, to `.team/progress/<seat>-<agent>.md` and with
`log_event.py note --seat <n> --agent <id> --note "<one line>"`:
- within its first minute: its plan in one line;
- after each partial result (a paper found, an example computed, a card made, a counterexample), with its label;
- at the end: the result, its label, and where it is.
The coach reads progress directly; nobody relays it. The live view (`view_match.py --live`) shows the latest line under
each glowing seat. A progress line is agent-level: it is not a result until it is a board fragment, and not verified
until it is in the bank.

## 5. Cost and measurement
A kickoff wave is 7–8 agents at once, so tokens go fast. Record in `metrics.md`: time to the first progress line, time
to the first verified result, total spend. After each wave read the workload table: a seat busy all the wave gets a
second agent; two agents producing the same thing means the split was wrong; a seat that never ran is switched off.

## Rules for every seat (appended to each seat prompt by init_team.py)
- **Start by reading your inbox** `.team/inbox/<your seat>/` and `.team/bulletin.md`.
- **Progress at once.** Within your first minute write your plan in one line; after each partial result write one line
  with its label; at the end write the result and where it is. Both to `.team/progress/<seat>-<agent>.md` and with
  `log_event.py note --seat <seat> --agent <id> --note "..."`.
- **Pass directly** along the open lanes (inbox file + `log_event.py pass`); do not wait for No. 6 to relay.
  Open lanes: 14 ⇄ 10, 14 ⇄ 4, 10 ⇄ 4, 7 → 14, 11 → 14, 10 → 8, 8 → 4, 8 → 9, 4 → 9, 14 → 9, 10 → 3, 8 → 3, 3 → 10, 3 → 8.
- **Work goes direct; decisions go through a coordinator.** Send to `.team/inbox/6/` and wait for `GO` when the pass
  would start a costly direction (asks No. 9 to prove or build, opens a new branch), crosses lanes, or stops a direction.
- **Never pass directly to a judge** (No. 2, No. 1, a judging No. 3): they receive only submissions through the
  sealed-verdict flow. Only No. 1 writes the bank.
- **If a tool refuses or a library is missing, report it in a progress line; do not work around it.**
