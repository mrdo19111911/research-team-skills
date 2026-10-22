# Coding team (same formation, grader = tests + CI)
| Seat | Math | Software | Project role |
|---|---|---|---|
| 1 | Lean | CI on the real integration path, in-place counters | DevOps |
| 2 | step errors, lock statement | code review, co-lock acceptance tests | QA |
| 4 | counterexamples | test generation, fuzzing, hidden tests | QA |
| 3 | prior work | existing library? dependencies, licenses, vulnerabilities | Security |
| 8 | lemma graph | API contract, frozen | SA |
| 9 | proof | API, business logic, data | BE |
| 11 | adjacent field | UI | FE |
| 7 | far field | mobile / data / infra; cross-field ideas by default | per project |
| 10 | literature | read codebase, docs | Dev |
| 14 | examples | benchmark, profiling | Performance |
| 6 | coordinator | tasks, issue tracker | Tech lead / PM |
| Coach | problems | spec, acceptance tests | PO / BA |
Bank = main branch (only CI merges). Board = issue tracker + architecture decision records. In software, No. 11 and No. 7 take UI and mobile/data/infra work; the cross-field idea search they do in math is benched.

Six coding rules: acceptance tests written and locked before implementation · never edit tests/CI/benchmarks ·
one branch (git worktree) per agent, only CI merges · catch "built but never wired": counters on the real path, 0 calls = does not exist ·
tools before LLM review (tests, fuzzing, types, static analysis), then different-family review, keep hidden tests ·
parity before replacing slow code with fast code (zero divergence on a large input corpus).
FE/BE: talk only through SA's contract; contract tests are the shared grader; each side has its own grader
(FE: E2E, visual regression, accessibility; BE: integration, load, contract).

## Algorithm research (e.g. VRP): two referees
No. 1 = correctness referee: goalkeeper, a player among the 11 (full recomputation from raw data).
Performance referee = an off-pitch official, NOT a 12th player and NOT a seat: owns instance sets (incl. sealed set), harness, statistics.
It sits with the bank and the scoreboard, outside the offside line: no seat can edit it, and it plays for no side.
(Earlier drafts called it "No. 5, libero"; that name is retired.)
Measurement discipline: train / validation / sealed sets (sealed opened once) · gap to best known, feasibility rate, anytime curve ·
many seeds, medians and IQR, statistical tests · per-instance reporting · same hardware, one core, same time cap, startup inside budget ·
ladder: toy → medium → full (all on train/validation), kill at the cheapest tier; the sealed set is report-only, never a tier ·
one flag per mechanism, kill conditions pre-registered · learned components off by default, enabled only by a pre-registered
on/off win on the validation set.
Sealed-set rule: every selection decision (on/off flags, mechanism choice, parameters, win conditions) is made and pre-registered
on the validation set; the sealed set is opened exactly once, by the performance referee, after the configuration is frozen, only
to report the final number; a disappointing sealed result may not be used to re-tune and re-open it; any later sealed evaluation
needs a fresh sealed set, and the report says so.
Phases: 0 measure instance structure, slow reference, lock plug-in contract · 1 many cheap ideas, evolutionary squad on No. 14 ·
2 regression on an instance group → swarm it · 3 full benchmark, ablations (validation), freeze configuration, sealed set opened once, novelty.
Outer loop: No. 14 runs generate–score–keep; No. 6 optimizes how the inner loop searches.

## Acceptance standards (shared seats, different meaning of "accepted")
Software: accepted = acceptance tests written from the spec and locked before implementation all pass in CI, plus review.
It means no failure was found on those cases; it does NOT mean the program is correct on all inputs.
Bank entry: "spec tests pass: N tests (hidden: M), coverage X%, CI run <id>, reviewer <family>, commit <hash>".
Algorithm research: accepted = a measured performance claim on a stated instance distribution, hardware, time cap and seeds,
with statistics. It is NOT a claim about other distributions, hardware or time caps.
Bank entry: "gap to best known on set S: median / IQR over k seeds, feasibility rate, test <name> p = ..., hardware H, cap T,
configuration frozen at <hash>, sealed set opened once on <date> (fresh sealed set: yes/no)".
