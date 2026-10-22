# Frame for every seat prompt (references/seats/<n>.md)

Each seat file is the full system prompt of that seat's agent. `scripts/init_team.py` copies it into
`.team/seats/<n>.md` with the campaign header (TEAM_SEAT, variant, problem) on top. An agent reads only
its own file, `.team/bulletin.md`, the board, the bank and `.team/templates/`; it does not have this skill's
other references. So a seat file must be self-contained: everything the seat needs to act is in it.

## Sections, in this order
1. `# No. <n> <Name>`, then one line: line on the pitch, core seat or wing seat.
2. `## Why this seat exists` — one short paragraph: the failure this seat prevents, and why the seat
   is separate from its neighbours. Reason first; it is what lets the agent act well in a case the rules miss.
3. `## You receive` — what arrives, from which seat, in what form, where (board section, file).
4. `## What you do` — numbered steps, imperative, each step one action. Where the variants differ, the
   step says so in one line ("Math: ... ML: ...").
5. `## What you hand over` — the exact output template, inline in a code block (copy of the matching
   template in `.team/templates/`), and to whom it goes.
6. `## Done when` — the stop condition of one task, and what to report to No. 6.
7. `## Never` — each prohibition with its reason in a few words.
8. `## Failures to watch for` — 3 to 6 concrete ways this seat goes wrong, each with the check that catches it.
9. `## Example` — one good and one bad output, a few lines each, from a small made-up case.
10. `## By variant` — a small table: what this seat means in math, ml, software, algorithm research
    (the ml and algorithm rows follow references/coding-team.md).

Length: 500–1000 words of prose (copied template blocks not counted). English. Plain imperative sentences. No private coinages: standard terms only
(Lyapunov function, interpolation inequality, worst-case chain, ...; never ledger, clock, leak, kick, aim,
straightening, chord, reservoir, cash-in). Team words (board, bank, seat, tabu log, kill test) are allowed
inside the team but are defined in one plain line the first time a seat file uses them.

## Rules every seat file must carry (lessons of the Grothendieck-constant case study, arXiv 2608.11195)
- **A number never travels without its label.** Wherever a seat writes a value (board, handoff, report,
  message), the value carries its label and its caveat ("numerical evidence only, float search, not certified").
  A summary that drops a caveat is wrong. (There, an exploration-only value lost its caveat over many summaries
  and became the record.)
- **Proved facts live in the bank, not in summaries.** Handoff notes and reports cite bank ids; a bench agent
  reads the bank before any summary. (There, a proved criterion was lost in a handoff and reproved 25 days later.)
- **Scope is stated.** Every result says whether it closes a node on the path to the main result or only a
  restricted case off that path. (There, 20 sessions of restricted cases were recorded as global progress.)
- **Same obstruction twice is a signal.** When a seat fails twice against the same obstruction, it writes the
  obstruction's name in its tabu entry; No. 6 counts them (rule in No. 6's file).
- **Read `.team/bulletin.md` first, at the start of every task.** It holds the coach's directives; a directive
  beats any older instruction on the board.
- **Plan before you compute or prove** (No. 9, No. 10, No. 14, No. 8): write a three-line plan on the board
  saying why this route can reach the main result, before spending budget.

## Variants (the meaning of "accepted" changes; the formation does not)
- `math`: accepted = true in every case: Lean-checked, exact computer algebra, or computer-certified at stated parameters.
- `ml` (empirical machine learning: training, benchmarks, baselines): accepted = a measured, reproducible claim on a
  stated dataset, compute budget and seeds, with statistics, frozen before the sealed test set is opened once.
  Theory of ML (convergence rates, bounds) runs as `math`. Details: references/coding-team.md, section ML research.
- `software`, `algorithm`: references/coding-team.md.
