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
| 7 | far field | cross-field ideas, on by default (also mobile / data / infra if the project needs it) | per project |
| 10 | literature | read codebase, docs | Dev |
| 14 | examples | benchmark, profiling | Performance |
| 6 | coordinator | tasks, issue tracker | Tech lead / PM |
| Coach | problems | spec, acceptance tests | PO / BA |
Bank = main branch (only CI merges). Board = issue tracker + architecture decision records. In software, No. 11 takes UI work; No. 7 keeps the cross-field idea search on by default, and takes mobile/data/infra work only when the project needs it.

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

## ML research (empirical machine learning): same two referees
Builds on the algorithm-research rules above (train / validation / sealed sets, pre-registration, many seeds, the sealed set
opened once). Theory of ML (rates, bounds, convergence) runs as the math variant.
| Seat | ML meaning |
|---|---|
| 14 | small fast experiments; reproduces each baseline first (its reported number, on our harness) before anything is compared to it |
| 4 | breaks results: data leakage, test-set contamination (also in pretraining data), untuned or unfair baselines, one lucky seed, metric chosen after the fact |
| 9 | builds the method and the experiment code |
| 8 | experiment plan: claims → experiments → ablations, each with a pre-registered win condition |
| 10 | literature, open benchmarks and their known pitfalls; proposes hypotheses |
| 2 | code and statistics review; reruns from raw data; checks every table cell against the run logs |
| 3 | novelty against ML venues and recent arXiv (concurrent work); checks each cited number against its source |
| 1 | reruns the frozen configuration from a clean environment (pinned lockfile or container, stated hardware); then the performance referee opens the sealed test set once and No. 1 records the number |
| 7 | far field, on by default: tools from physics, biology, economics, statistics ... |
Performance referee (off pitch): owns datasets and splits, the sealed test set, the harness, the compute budget and the statistics.
Measurement discipline: same compute budget for every method (tuning budget included) · k ≥ 5 seeds, mean with CI or median with IQR ·
pre-registered metric and win condition · ablation per mechanism (validation set) · report compute (GPU-hours) and every failed run ·
contamination check of the test set · every number in the paper traced to the run that produced it.

## Acceptance standards (shared seats, different meaning of "accepted")
Software: accepted = acceptance tests written from the spec and locked before implementation all pass in CI, plus review.
It means no failure was found on those cases; it does NOT mean the program is correct on all inputs.
Bank entry: "spec tests pass: N tests (hidden: M), coverage X%, CI run <id>, reviewer <family>, commit <hash>".
Algorithm research: accepted = a measured performance claim on a stated instance distribution, hardware, time cap and seeds,
with statistics. It is NOT a claim about other distributions, hardware or time caps.
Bank entry: "gap to best known on set S: median / IQR over k seeds, feasibility rate, test <name> p = ..., hardware H, cap T,
configuration frozen at <hash>, sealed set opened once on <date> (fresh sealed set: yes/no)".
ML research: accepted = a measured claim on a stated dataset and split, compute budget and seeds, against baselines reproduced on
the same harness and budget, with statistics. It is NOT a claim about other datasets, scales or budgets.
Bank entry: "metric M on test set T (sealed, opened once on <date>): mean ± CI over k seeds; baselines (reproduced: yes/no, their
reported vs our number); compute per method; test <name> p = ...; contamination check: <method, result>; config frozen at <hash>;
run logs <paths>; scope: <main claim / restricted setting>".
