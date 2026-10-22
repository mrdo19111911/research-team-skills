# Laws
1. **Do not edit the grader.** Attack only submits. Nobody but No. 1 touches the locked statement, the Lean environment or the bank. Labels are computed from the evidence log, never typed by anyone.
2. **Judge independently, by evidence only.** Each judge seals its verdict before seeing any other (below). No voting; a counterexample or Lean decides.
   No voting does not create truth: Lean or exact computation decides only the formalized statement. The weak point is the statement lock (Phase 0, two independent formalizations, diffed). Novelty, reading of sources and usefulness of a hypothesis need their own stated criteria and named sources.
3. **Measure before adding agents.** The 11 seats are roles; No. 6 spawns an agent only where there is a task and budget. Fan out a generator seat into a squad when the work is parallelizable. Prover and verifier keep 1–2 agents.
4. **Tired → substitute.** A PreCompact hook writes the handoff note before compaction (fallback: token estimate, default 50%, tunable; or visible fatigue); the new agent reads it and the board before playing.

## Three kinds of independence (record which were achieved; never claim more)
- **Model**: a different model family from the seat whose work is judged.
- **Context**: different prompt, fresh context; has not read the other judges' notes, the board discussion or the attack's reasoning.
- **Tool**: a different checking tool (Lean vs computer algebra vs a second, separate formalization).
The bank entry lists, per result, which kinds each judge had. "Independent" with no kind named is not allowed.

## Sealed verdicts
Each judge (No. 2, No. 3, every member of a judging squad) writes its verdict alone to its own file, unreadable by the others, and seals it.
Only after all verdicts are sealed are they and the shared board opened to the judges. No. 6 sees "submitted / not yet", never content, until then.

## Two stores
- **Bank (verified results)** – owned by the goalkeeper; written only by No. 1, with the strength of the final check recorded (see ladder). Like the official scoreboard.
- **Board (working state)** – structure owned by No. 6: fragments, failures, tabu log, dependencies.

| Action | Who | Rule |
|---|---|---|
| Read both | every seat, coach | read before playing; never re-enter tabu |
| Post fragment | attack, midfield | enters at lowest label |
| Mark refuted, add counterexample | No. 4, No. 2 | with evidence; dead direction → tabu |
| Add source, credit | No. 3 | name the paper |
| Link dependencies, retract | No. 6 | refuted node demotes everything resting on it; never edits labels |
| Write to bank | No. 1 | after No. 2 and No. 3 pass; record the final check and the kinds of independence achieved |
| Write the paper | No. 1 (editor) | from the bank only, with a claim map; a fresh No. 2 and No. 3 check it before release |
| Delete | nobody | append and annotated corrections only; failures are kept |

## Label ladder (computed from evidence, never typed by hand)
agent-level → not wrong on the worked example (No. 2 runs each step on it; a filter: a failure there is a real error, passing proves nothing general) → survived counterexample search (No. 4 on the conjecture, No. 2 on each lemma) → step-checked → novelty-cleared → bank, tagged with the strongest final check:
Lean-checked · exact computer algebra · computer-certified at stated parameters · numerical evidence only.
Only the first two count as "proved" without qualification; when only part is Lean-checked, say which part.
Literature enters at agent-level. Labels are recomputed from the evidence log; the log is append-only.
