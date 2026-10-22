# Phases (No. 6 alone switches phase)
Seats are roles; No. 6 spawns an agent for a seat only when it has a task and budget for it. "Off" = no agent running.
One order in every phase: proposal (10) → lemmas (8) → early counterexample attack (4) → proof (9) → independent check (2, 3) → final check (1).
Phase −1 exception: no lemma graph yet, No. 10 hands conjectures straight to No. 4. Backtracking only with evidence.
| Phase | Shape | When | Who runs | Ends when |
|---|---|---|---|---|
| −1 Examples | warm-up, scouting | start of each problem, before any statement exists | No. 14 leads: hunts meaningful examples, computes the worked example A to Z; No. 10 seeds from literature and writes conjectures matching the library, handing each straight to No. 4; No. 4 hunts counterexamples at the edge of each hypothesis and picks the new test case; No. 6 sets budget. No. 9 off | a conjecture predicts a case written down before No. 14 computes it, and the prediction is right |
| 0 Build from the back | GK playing with feet | after Phase −1 | No. 1 + No. 2 lock statement; No. 3 quick literature scan; No. 10 proposes, No. 8 builds the initial lemma graph (No. 3 quick novelty check on each load-bearing lemma); No. 14 checks the statement on the whole library. No. 9 and the wings off | statement locked, definitions in Lean, first lemmas |
| 1 Explore, 2-3-5 | five up front | after Phase 0 | 10 proposes (fed by 11, 7 via 14's kill test) → 8 adds lemmas → 4 attacks each lemma → 9 proves and submits; squads allowed; No. 3 inverts into midfield feeding No. 10 and runs the quick novelty check on each new branch and load-bearing lemma; sparse passing, submit before seeing others | a load-bearing lemma has a proof, or exploration budget spent |
| 2 Counter-press | swarm the obstacle | a load-bearing lemma just broke | seats nearest the obstacle (14, 4, 10, 8, 9) attack that exact point within a window set by No. 6; No. 2 gives only the error location; the patch goes to a fresh No. 2 | patched → resubmit; window over → tabu, back to Phase 1; the break shows the conjecture is wrong → back to Phase −1 with the counterexample as a new row |
| 3 Verify and lock, 5-4-1 | drop deep | a load-bearing proof exists | No. 2 becomes a multi-agent different-family squad (step check + counterexamples to each lemma); 14 feeds data to 2; 8 updates blueprint; 9 waits for patches; wings and No. 10 rest | No. 2 and No. 3 (full source check) pass, then No. 1 passes → bank, next lemma (Phase 1); broken → Phase 2 |
Rules: the nine core seats (6, 14, 10, 8, 4, 9, 2, 3, 1) are staffed in every campaign; only the wings 11 and 7 are switched on per problem; rest defense (No. 2 and No. 3) is never fully off; No. 4 plays up front in every phase and never judges a submitted proof; No. 14 is never off (every seat tests on its examples); a seat with no agent costs nothing; substitution applies in every phase.

## Early novelty check (No. 3)
When a branch opens and when No. 8 adds a load-bearing lemma: a quick search, "is this already known?", before effort is spent.
Known → No. 6 decides (cite and reuse, or stop). The full source check (citations exist, content matches) stays before the bank.

## Stop criteria per direction (No. 6)
Written on the board before the direction starts: budget spent · window expired · killed by counterexample · superseded.
Any one met → stop and log to tabu; No. 6 does not extend a direction without a new board entry and reason.
No. 6 sees only "submitted / not yet" from each defender until all verdicts are sealed, never their content.

Football mapping: Cruyff's 3-4-3 diamond gives the roles; modern football gives shape changes by phase
(build-up, rest defense, inverted full-back, counter-press, ball-playing keeper). Explore like Cruyff, judge like Mourinho.
