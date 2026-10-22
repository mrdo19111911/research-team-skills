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

## ML mode (added 2026-10-22)
10. **No status labels in the body vs settings and uncertainty in the body.** D5/E5 keep status labels, AI and Lean
   out of the body; an ML claim is meaningless without its dataset/split, budget, seeds and statistic. Settlement:
   the setting and the uncertainty are part of the claim itself, not a status label; they are written next to the
   claim. What stays out of the body is unchanged: verification labels, Lean, AI, team process, the claim map.
11. **No trace of AI in the paper vs venue disclosure policies.** Some venues require a statement on the use of
   language models. Settlement (default): where the venue requires it, one statement in the place the venue names,
   written by the author; nothing else about AI or the team. AUTHOR: confirm per venue.
12. **Page budget.** Math mode: body 15–25 pages (unchanged). ML mode: the venue's page limit wins; appendix per
   venue rules; the main result still by page 2.
13. **"The editor never computes" vs derived numbers.** A difference, ratio or average of banked numbers is
   arithmetic, not a new result: computed by `trace_numbers.py` from full-precision sources, never by hand. A claim
   of superiority or significance is not arithmetic: it needs the bank's pre-registered test.
14. **Failed runs vs "no trace of the writing process".** Failed and discarded runs are results of the experiment,
   not of the writing; they are reported (ml-mode.md §2.7). Drafting history stays out.
15. **Team word "sealed".** "Sealed test set" is team jargon; the paper says "held-out test set, evaluated once".
16. **Reproducibility statement vs double-blind review.** Code, commit and configs are named; for anonymous review the
   link points to an anonymized copy of the same commit, replaced by the real one in the final version.
17. **"Conjectures and open problems" section.** Math mode only. In ML mode, claims the bank does not support
   (validation-only, one seed, untested settings) go to limitations or future work, worded as untested, never as results.
