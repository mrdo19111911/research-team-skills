# Formation (math variant)

Top to bottom: front three 14 – 9 – 4 · No. 8 · midfield 11 – 10 – 7 · No. 6 · back line 3 – 2 · goalkeeper 1.
Research starts by attacking concrete cases: examples (14) and counterexamples (4) play next to the prover (9).
No. 8 sits between attack and midfield: every conjecture reaches the front three as a lemma graph.
Core seats (solid border): 6, 14, 10, 8, 4, 9, 2, 3, 1, and No. 7 (far field, on by default). Wing seat switched on per problem (dashed border): 11.

## Seats
Front three: No. 14 Examples (left; hunts meaningful examples, computes the worked example A to Z, keeps the
example library, runs kill tests for every seat; leads Phase −1) · No. 9 Prover (center forward; receives the next
lemma from No. 8 and the worked example from No. 14, asks No. 4 to break a lemma before investing in it, writes the
proof, submits) · No. 4 Breaker (right; kills conjectures and lemmas with counterexamples at the edge of each
hypothesis, Lakatos labels; picks the new test case for each conjecture).
Link: No. 8 Blueprint (between the front three and No. 10; turns No. 10's conjectures into a lemma graph, hands No. 9
the next lemma, asks No. 14 for examples of each lemma, locks shared definitions in Lean with No. 1 early).
Midfield: No. 11 Adjacent-field (left, under No. 14; ideas from nearby fields → short pass to No. 14 for the kill test → No. 10) ·
No. 10 In-field (center; reads literature, turns the example library into conjectures, passes them up to No. 8) ·
No. 7 Far-field (right; core, on by default; ideas from distant fields → long ball to No. 14 for the kill test → No. 10; records every card in the far-analogy graph).
Base: No. 6 Coordinator (assigns tasks, kills directions, changes formation, retracts nodes; owns the board; talks to the coach).
Defense: No. 3 Novelty (left back; citations, prior work, credit) · No. 2 Proof-checker (right back; step errors,
runs each step on the worked example, hunts counterexamples to each lemma of a submitted proof; co-locks the
statement with the goalkeeper) · No. 1 Final verifier and editor (goalkeeper; Lean, ATP, hidden tests; sole writer of the bank; writes the paper from the bank with the paper-editor skill).
No. 4 never judges a submitted proof: it watched the conjecture grow, so it is not independent. No. 2 does that job.
Off pitch: Coach (human, optionally with a different-family chat model as thinking partner; sets problems, picks, receives goals only) ·
Bench (fresh agents, empty context) · Sparring team (outside the 11; plants false variants, measures catch rate).

## Goal path (numbered as on the formation slide)
1 coach ⇄ 6 (problem in, results out) · 2 6 → 14 (assign) · 3 14 → 10 (example library) · 4 10 → 8 (conjecture) ·
5 8 → 9 (next lemma) · 6 9 ⇄ 4 (No. 4 tries to break the lemma first) · 7 9 submits → No. 2 and No. 3 (independently) ·
8 both pass → 1 · 9 1 → bank · 10 1 → 6 (result recorded).
Fail at any defender → back to 9 with evidence. Fail on an example → back to 14.
In Phase −1 there is no lemma graph yet: No. 10 hands each conjecture straight to No. 4.

## The front triangle (all three work on the same conjecture)
14 → 9 the worked example · 9 ⇄ 4 a lemma No. 9 wants to use, and "broken" (with the counterexample) or "not broken"
(with the search log) · 4 ⇄ 14 a new case, prediction written first, and numerical data for the hunt.
No. 4 attacks only what has not been submitted; a submitted proof is judged by No. 2.

## Additional passing routes (evidence only, after each defender has judged independently)
a 10→4 a new conjecture, before No. 9 works on it (Phase −1; later via No. 8 and No. 9) · b 4→14 new test case, prediction written first ·
c 3→2 result already in literature · d 3→2 known counterexample of a nearby variant ·
e 6→defense depth of verification per load level (never a hint about the conclusion) ·
f 3→10 adjacent papers found during novelty check · g 14→4 numerical data for counterexample hunting ·
h 8↔1 lock shared definitions in Lean early · i 2→9 error location, 9 patches · j 8↔14 blueprint asks, examples answer ·
k 7/11→14 cross-field card, kill test on the library before No. 10 sees it · l 14→9 the worked example (data, not an idea) ·
m 2↔14 No. 2 runs each proof step on the worked example; a mismatch goes back to 14 to recheck the computation ·
n 10→8 a conjecture becomes a lemma graph · o 8→9 the next lemma to prove · p 9↔4 a lemma is attacked before No. 9 invests in it.

## Offside rule: "do not move the goalposts"
Attack may not edit: locked statement, Lean environment and axioms, tests, hidden tests, labels in the graph.

## Lakatos labels for counterexamples (No. 4)
local (kills a lemma) vs global (kills the claim); response type: monster-barring, exception-barring, lemma-incorporation.

## Officials (off pitch, not players)
Coach · bench · sparring team · bank/scoreboard · performance referee (algorithm-research variant only).
