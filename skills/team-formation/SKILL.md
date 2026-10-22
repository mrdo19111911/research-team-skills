---
name: team-formation
description: Set up and run an 11-seat multi-agent research team (math proofs, empirical machine learning, algorithm research, or software) laid out as a football formation, with an untouchable grader, independent defenders and phase changes. Use when asked to organize agents for a hard problem, start a research campaign, decide how many agents per seat, or change team shape mid-campaign.
---

# Team formation

**Generation is cheap, judgment is scarce.** The attack generates freely; nothing counts until it
passes two defenders who judge independently and a goalkeeper who checks mechanically.
Nobody on the attack may touch the grader.

## The 11 seats (details in references/formation.md, one card per seat in references/role-cards.md)
A seat is a role on the roster, not a running agent. No. 6 spawns an agent for a seat only when it has a task
and budget for it; a seat with no agent costs nothing.
**Ten core seats**, staffed in every campaign: 6, 14, 10, 8, 4, 9, 2, 3, 1 (the goal path runs through them) and **No. 7 Far-field, on by default**:
every task No. 6 assigns also goes to No. 7 as an obstacle, and every card No. 7 makes is recorded in the far-analogy graph.
**One wing seat**, No. 11 (adjacent field), is switched on by No. 6 per problem.
Top to bottom: front three 14 – 9 – 4 · No. 8 · midfield 11 – 10 – 7 · No. 6 · back line 3 – 2 · goalkeeper 1.
Front three: examples, proof and counterexamples attack together. No. 8 links midfield to attack. Midfield builds and feeds. A thin, independent back line judges.
| Line | Seat | Job |
|---|---|---|
| Attack | **No. 14 Examples (left)** | hunts meaningful examples; computes one worked example A to Z; keeps the example library; runs kill tests for every seat; leads Phase −1. The most important seat after the grader: strongest model |
| | No. 9 Prover (center) | proves the next lemma handed down by No. 8, using the worked example from No. 14; asks No. 4 to break a lemma before investing in it; submits |
| | No. 4 Breaker (right) | kills conjectures and lemmas with counterexamples at the edge of each hypothesis; picks the new test case for each conjecture |
| Link | No. 8 Blueprint (between attack and midfield) | turns No. 10's conjectures into a lemma graph; hands No. 9 the next lemma; asks No. 14 for examples of each lemma; locks shared definitions with No. 1 |
| Midfield | No. 11 Adjacent-field (left) | ideas from nearby fields, as far-analogy cards: short pass to No. 14 for the kill test, then No. 10 |
| | No. 10 In-field (center) | literature; turns the example library into conjectures; passes them up to No. 8 (in Phase −1, before any lemma graph, straight to No. 4) |
| | No. 7 Far-field (right, core, on by default) | ideas from distant fields, as far-analogy cards: long ball to No. 14 for the kill test, then No. 10; records every card in the graph (`far-analogy/scripts/add_connection.py`) |
| Base | No. 6 Coordinator | assigns tasks, sets phase and budgets, kills directions; owns the board; talks to the coach |
| Defense | No. 2 Proof-checker | step errors; runs each step on the worked example; hunts counterexamples to each lemma of a submitted proof; co-locks the statement with No. 1 |
| | No. 3 Novelty | prior work; checks every citation exists and says what is claimed |
| Goal | No. 1 Final verifier and editor | Lean / exact check / hidden tests; sole writer of the bank; edits the bank into the paper (skill `paper-editor`) |

**Why No. 4 plays up front and No. 2 judges alone:** counterexamples are cheapest while a conjecture is still
forming, so No. 4 attacks next to No. 14. Having watched the conjecture grow, No. 4 is no longer independent, so it
never judges a submitted proof. That judgment stays with No. 2 (fresh context, different model family), who
hunts counterexamples to every lemma of the submission. Still 11 seats, one kind of job per seat.

Off pitch (officials, not players, no number): **Coach** (the human: sets problems, writes directives in `.team/bulletin.md`
(every seat reads it first; persist-or-reframe decisions are the coach's), receives goals and phase reports) ·
**Bench** (fresh agents for substitution) · **Sparring team** (plants false variants, measures defenders' catch rate) ·
**Bank / scoreboard** · **Performance referee** (ML and algorithm research only: owns datasets or instance sets, sealed set, harness and
statistics; outside the offside line, no seat can edit it). There is no 12th player.
ML, software and algorithm-research variants reuse the same seats: references/coding-team.md. Full seat prompts: references/seats/.

**Goal path:** 6 → 14 (examples) → 10 (conjecture) → 8 (lemma graph) → 9 ⇄ 4 (No. 4 tries to break each lemma
before No. 9 invests in it) → 9 submits → 2, 3 independently → 1 → bank, and No. 1 reports back to No. 6.
One order everywhere: proposal (10) → lemmas (8) → early counterexample attack (4) → proof (9) → independent check
(2, 3) → final check (1). Phase −1 exception: no lemma graph yet, so No. 10 hands conjectures straight to No. 4.
Backtracking only with evidence: any defender fails it → back to 9 with the evidence; a failure on an example → back to 14.
**Early novelty check:** when a branch opens, and when No. 8 puts a load-bearing lemma (one the main result cannot do without) into the graph, No. 3 asks
"is this already known?" (a quick search, before effort is spent). The full source check stays before the bank.
**The front three form a triangle**, all working on the same conjecture: 14 → 9 the worked example · 9 ⇄ 4 a lemma
No. 9 wants to use, and "broken" or "not broken" · 4 ⇄ 14 a new case (prediction written first) and numerical data.
No. 4 only attacks what has not been submitted; a submitted proof is judged by No. 2.
**No. 14 is the testing ground for every seat.** Two routes go through it:
- 7 / 11 → **14** → 10 (No. 11 a short pass from below, No. 7 a long ball across the pitch): a cross-field card reaches No. 10 only after No. 14 ran its kill test on the library
  or the worked example; an idea that dies there goes to the tabu log with the example that killed it.
- 14 → 9: the worked example goes straight to the prover (data, not an idea: its only failure mode is a
  miscomputation, which No. 2 rechecks). Its tight inequalities and nonzero weights often show the proof's skeleton.
No. 14 computes and records; it never judges whether an idea is good. Requests go on the board; No. 6 orders them.
No. 14 may be a squad: one lead owns the worked example and the library, the others take requests.

## Examples first (Phase −1; cards in references/templates.md)
Research does not start from a statement; the statement comes out of examples. Before Phase 0:
1. No. 10 seeds the library with examples from the literature; No. 14 hunts more.
2. No. 14 picks one **worked example** and computes every object of the theory on it, intermediate
   quantities included, exactly (computer algebra), with a script that reruns. Every seat reads it before playing.
3. No. 4 hunts counterexamples at the edge of the hypotheses (drop one hypothesis → the example fails).
4. No. 10 writes a conjecture that matches the whole library.
5. No. 4 picks a new case; everyone writes the prediction down; only then No. 14 computes it.
   Right → No. 6 moves to Phase 0. Wrong → new row in the library, back to 4.

**Meaningful example** (at least one): every hypothesis is active (nothing vanishes, no symmetry collapses it),
smallest such first · separates two competing conjectures · attains the bound · sits on the edge of a hypothesis.
**Trivial**: degenerate, or every candidate statement holds on it. Examples are labelled numerical evidence;
a counterexample is decisive.

**Worked-example rule:** every submitted proof is run step by step on the worked example by No. 2.
A step that gives a wrong value there is wrong. Passing proves nothing general; failing is final.

## Four laws (references/laws.md)
1. **Do not move the goalposts.** The attack never edits the locked statement, tests, Lean environment,
   benchmarks or labels. Enforced by `scripts/guard_locked.py`, not by trust.
2. **Judge independently, by evidence.** Each defender writes a verdict before seeing the others. No voting.
3. **Measure before adding agents.** The 11 seats are roles; agents run only where No. 6 has a task and budget.
   Several agents in one seat only where the work is parallel and a measured need exists; Prover and Final
   verifier keep 1–2 (references/squads.md).
4. **Tired → substitute.** Handoff note, bench agent takes over. Trigger: a PreCompact hook writes the note before
   compaction; else a token estimate (default 50%, tunable, not a measured optimum); also on visible fatigue (references/substitution.md).

## Setup (once per campaign)
1. **Pick the variant**: math (incl. theory of ML), ml (empirical machine learning), software, or algorithm research.
2. **Phase −1, examples** (above), then **Phase 0, lock the problem**: No. 1 and No. 2 formalize the conjecture
   independently, diff, lock; the locked statement must hold on the whole example library and reject every counterexample.
   Software: acceptance tests from the spec first.
3. **Scaffold**: `python scripts/init_team.py <campaign-dir> --variant math|ml|software|algorithm --problem "..."` creates
   `.team/` (board, bank, bulletin.md for the coach's directives, templates/, locked.txt, verdicts/, handoff/, examples/, metrics.md) and one system-prompt file per seat
   from the role cards; list locked paths in `.team/locked.txt`; install the hooks (below). Running a campaign: references/launcher.md.
4. **Model families**: defenders (No. 2, No. 3) on a different model family from the attack; No. 4 on a different family from No. 10 (else at least a fresh context). If none is available,
   use different prompts and no shared context, and record in the bank that independence is weaker.
5. **Create the board and the bank** (`.team/board.md`, `.team/bank.md`). Board = working state, structure owned by No. 6.
   Bank = verified results, written only by No. 1.
6. **Baseline**: one agent, same budget, same problem. Measure both, every campaign: verified results (with their
   final-check label) · time and cost to the first verified result · wrong directions killed early, and at what cost ·
   catch rate of planted false variants (sparring team) · total spend. Team does not beat baseline → shrink the team.

## Tempo (references/tempo.md)
- **Parallel by default (mandatory)**: every set of tasks that do not need each other's results goes out in ONE
  message; a task waits only for a named input, written on the lane file.
- **Never leave the coach in silence (mandatory)**: report at minute 0, after every return, and at least every
  3 minutes while agents run (how many run, each one's latest progress line).
- **Speed per agent**: short context pack (`.team/seats/brief/`), model tier per seat (fast / strong / strongest),
  time box per spell (10 min or 40 tool calls, then `NEXT:` to a fresh agent), shared cache `.team/cache/`, libraries
  checked at setup.
- **Kickoff at minute 0**: right after setup, spawn every agent in `.team/kickoff.md` in ONE message (two No. 10 on
  literature, two No. 14 on examples, No. 3 novelty scan, No. 7, No. 4), before writing anything else.
- **Direct passes**: attack and midfield pass work to each other through `.team/inbox/<seat>/`, not through No. 6.
  Decisions are gated: a pass that starts a costly direction (No. 9 to prove or build, a new branch), crosses lanes or
  stops a direction waits for its lane coordinator's `GO`. Judges (No. 2, No. 1, a judging No. 3) receive only
  submissions, through the sealed-verdict flow.
- **Several coordinators**: head No. 6 keeps phase, stop criteria, budget and SEALED; lane coordinators 6a scouting,
  6b build, 6c verification each own one lane file in `.team/board/`. About one coordinator per five running agents.
- **Progress at once**: every agent writes its plan within its first minute and one line per partial result
  (`.team/progress/`, `log_event.py note`); the coach reads them live in `view_match.py --live`.

## Run loop
- No. 6 sets the phase (references/phases.md) and writes each phase's budget and stop condition on the board.
- Before a direction starts, No. 6 writes its stop criteria on the board: budget spent · window expired ·
  killed by counterexample · superseded. Any one met → the direction stops; No. 6 does not renegotiate.
- No. 6 sees only "submitted / not yet" from each defender until all verdicts are sealed, never their content.
- Every result enters the board as a fragment (references/templates.md) at the lowest label.
- Labels rise only with evidence, computed from the append-only evidence log.
- Every dead direction goes to the tabu log with its reason and scope.
- Every far-analogy card, alive or dead, is recorded in the far-analogy graph the moment it is made, and updated
  when No. 14's kill test comes back (No. 7 runs `add_connection.py`; far-analogy SKILL.md, step 6).

## Label ladder
agent-level → not wrong on the worked example (a filter: passing proves nothing general) → survived counterexample search (No. 4 on the conjecture, No. 2 on each lemma) → step-checked → novelty-cleared → then the strongest check available:
**Lean-checked** · **exact computer algebra** · **computer-certified at stated parameters** · **numerical evidence only**.
The bank records which one. Only Lean-checked or exact computer algebra counts as "proved" without qualification.

## Hooks (details and the full settings snippet: references/hooks.md)
- `scripts/guard_locked.py` (PreToolUse): blocks edits to locked paths.
- `scripts/guard_sealed.py` (PreToolUse): blocks reading another judge's verdict before `.team/verdicts/<id>/SEALED` exists.
- `scripts/precompact_handoff.py` (PreCompact): writes the handoff note before context compaction.
- `scripts/log_event.py` (PostToolUse, Stop, SubagentStop; also a CLI for No. 6): appends to `.team/events.jsonl` who
  ran when and who passed what to whom. `scripts/view_match.py` replays it as `.team/match.html`: active seats glow, a
  ball flies for each pass, and a workload table shows which seat needs more agents next time (references/match-log.md).
Each seat sets `TEAM_SEAT`. Minimal guard install in the attack's and midfield's `.claude/settings.json`:
```json
{"hooks": {"PreToolUse": [{"matcher": "Edit|Write|MultiEdit|NotebookEdit",
  "hooks": [{"type": "command", "command": "python scripts/guard_locked.py"}]}]}}
```
It does not see shell commands (`sed`, `>`); also deny write access to locked paths in Bash for those seats,
or run No. 1 in its own worktree that alone holds the locked files.

## Write-up (No. 1 as editor, skill `paper-editor`)
No. 1 writes the paper from the bank only: a claim map (paper statement → bank id → label and final check), story first,
others' results as special cases. A fresh-context No. 2 checks every statement against its bank entry and No. 3 every
citation, as sealed verdicts, before the paper leaves the team.

## Never
- A claim enters the paper without a bank entry, or stronger than its locked statement.
- An agent raises the label of its own result.
- A defender reads another defender's verdict first.
- No. 7 or No. 11 passes straight to No. 9 or No. 10 without No. 14's kill test.
- A citation enters the bank unverified (references/evidence.md lists which of this skill's own sources are unchecked).
