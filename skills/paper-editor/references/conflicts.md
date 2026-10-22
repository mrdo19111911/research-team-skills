# Tensions between the author's rules and team-formation, and how this skill settles them
Default settlements below; items marked AUTHOR are open until the author decides. Author rules win otherwise.

1. **Two label systems.** CLAUDE.md: proved by hand / exact computer algebra / computer-certified / numerical
   evidence / conjecture, plus Lean status. Team ladder: Lean-checked / exact computer algebra / computer-certified
   at stated parameters / numerical evidence only. "Proved by hand" is a proof route, not a final check.
   Settlement: claim map carries both columns (LABEL and FINAL CHECK).
2. **Lean status in the paper vs no status in the paper.** The brief asks for Lean status reporting in the paper;
   WRITING_GUIDELINE D5/E5 and my_revive_paper say the body mentions no status labels, AI or Lean, and
   verification lives in a separate companion document. Settlement: companion verification note (naming.md);
   label strength shows in the paper only through environment and verb (claim-map.md). DECIDED by the author
   (2026-10-22): no appendix and no pointer in the paper; Lean status lives only in the companion verification note.
3. **What counts as "proved".** Team-formation: Lean-checked or exact computer algebra count as proved without
   qualification. CLAUDE.md: nothing is presented as proved before a Lean subagent checks it (or its algebraic
   core). Settlement: the stricter rule; exact-CAS-only rows get a Lean attempt before freeze, status recorded.
4. **Principle first vs gap first.** CLAUDE.md / writing-style: state the principle first. WRITING_GUIDELINE A2:
   do not open with an abstract principle; open with a concrete gap; G1 first sentence a question.
   Settlement: the story paragraph opens with the question and the named gap, then states the principle
   in words, all before the main theorem on page ≤ 2.
5. **Coach sees only goals and phase reports** (team-formation) vs **my_revive_paper stops after diagnosis for
   the author to choose (a)/(b)/(c)** and the author decides on replacing the official copy. Settlement: a paper
   draft is a phase report; the editor stops for the author at the diagnosis and at freeze.
6. **"Nothing cut" vs Galois ban.** v9 decisions and my_revive_paper forbid cutting results without consent; the
   author ordered Galois/constructibility removed. Settlement: the order is that consent; banked Galois entries
   stay in the bank but never enter the paper.
7. **Team vocabulary.** team-formation's own words (bank, kill test, tabu, sealed, worked example, goal) are private
   vocabulary by the author's standard. Settlement: allowed inside the team, banned from the paper.
8. **Model independence.** No. 2 should be another model family; the brief asks for a "fresh-context No. 2".
   Settlement: different family when available, else fresh context and different prompt, recorded as
   context independence only (laws.md: never claim more).
9. **"Deepest idea before theorems"** (structure-first) vs **main result by page 2** (B1). Settlement: the idea is
   told in words in the story paragraph; the theorem follows on page ≤ 2; the full idea of the proof follows the example.
