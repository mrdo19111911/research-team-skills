# Several agents in one seat (a squad)
Two kinds. **Generator squads** (No. 14, No. 9, No. 10, No. 11, No. 7) share a board. **Judging squads** (No. 2 in Phase 3, any defender fanned out) do not: their rules are below.

## Generator squads
Loop: (1) play alone, board unseen · (2) post fragments: checked lemmas, counterexamples, obstacles, dead directions ·
(3) read board, continue own route using the best checked fragment · (4) squad lead merges into the lemma graph, no voting.
Sparse rounds early, denser late.
Rules: shared board, no private side chats · one owner per proof; others propose, owner edits ·
copy the best checked fragment, not the majority · keep one member deliberately off-consensus · disagreements settled by Lean or computation · 3–5 agents per squad; more → split by blueprint branch.

Per seat:
- **Several No. 10**: split literature domains; submit ideas before sharing; pass only what only you know; copy best-verified idea, not majority.
- **Several No. 9, different lemmas**: pass locked statements at interfaces; pass requests "need lemma X in form Y"; never edit each other's proofs.
- **Several No. 9 racing one lemma**: no passing during the race; loser documents what was tried and where it got stuck.
- **No. 11 and No. 7**: no passing while searching; after submission pass the abstract framework, not the analogy; unit of passing = correspondence table + one testable prediction; all cross-field ideas go through No. 14's kill test, then No. 10, before No. 9.
- **Several No. 14**: one lead owns the worked example and the library, the others take computation requests from the board in No. 6's order; two members compute the worked example independently and compare before it is published.

## Judging squads (sealed verdicts; laws.md)
- Each member gets the submission alone, in a fresh context, with its own prompt; it has not read the board discussion, the attack's reasoning or another member's notes.
- Each member writes its verdict to its own file, unreadable by the others, and seals it. No shared board, no side chats, before all are sealed.
- Only after every verdict is sealed are the verdicts and the board opened to the members. A verdict is never edited after sealing; a second look is a new, dated entry.
- No. 6 sees only "submitted / not yet" per member until all are sealed.
- No merging by majority: one sealed failure with evidence (a wrong step, a counterexample) sends the proof back to No. 9.
- Vary the members where possible: different model families, different tools (Lean, computer algebra, a separate formalization). Record which kinds of independence each member had.
