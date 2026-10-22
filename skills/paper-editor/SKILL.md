---
name: paper-editor
description: Skill of the goalkeeper (No. 1, Final verifier) of the team-formation skill when it edits the bank of verified results into a mathematics paper. Use when the team's bank should become a paper, when the coach asks No. 1 to write up results, or when a paper must be rebuilt from the bank after new bank entries. Not for discovering or proving results.
---

# Paper editor (No. 1 writes the paper)

**The bank is the only source.** No. 1 is the sole writer of the bank and the only seat that turns it
into prose. The editor arranges, explains and credits; it never proves, strengthens or adds.
Read first, every time, from the paper project's root: `CLAUDE.md` (status labels, Lean rule, banned-word table),
`WRITING_GUIDELINE.md` if present (rules A–G, checklist F), team-formation `SKILL.md` and
`references/laws.md`. Those files win over this one; known tensions are settled in references/conflicts.md.

## Input (nothing else)
- `.team/bank.md`: locked statements, labels, final check, kinds of independence, Lean names.
- No. 3's sealed novelty verdicts: prior work, what is new, verified citations.
- No. 14's worked example (card + rerunnable script).
Never a source of claims: the board, fragments, tabu log, attack reasoning, chat, earlier drafts,
memory notes (memory and the style files govern *how* to write, never *what* is true).
A fact needed for the story but absent from the bank → request on the board via No. 6; do not write it.

## Hard rules
1. **No bank entry, no statement.** Every theorem, lemma, proposition, corollary, displayed claim
   and "it is known that" sentence maps to a bank id or a No. 3-verified citation.
2. **Locked wording.** The paper's statement equals the locked one, or is logically weaker and says so.
   Never drop a hypothesis, widen a range, turn "for N ≤ 5" into "for all N", or upgrade a label.
   Rewording for readability is allowed only if No. 2 confirms equivalence (step (e)).
3. **Label by environment** (references/claim-map.md):
   Theorem / Lemma / Proposition only for Lean-checked, partly Lean-checked (part named) or exact
   computer algebra entries; computer-certified entries state their parameters inside the statement;
   numerical evidence never sits in a theorem environment and never in "we prove";
   conjectures and open problems go in one marked section, "Conjectures and open problems".
4. **Claim map** maintained alongside the draft: paper statement → bank id → label → final check →
   Lean file/commit → citation. A paper claim with no row is an error.
5. **Credit from No. 3 only.** Each result gets one sentence: "known from [x]" or "new here",
   with what is new stated precisely. Only citations No. 3 verified (exists, says what is claimed).

## Structure (references/structure.md)
Story first: one paragraph, a question and the concrete gap (named methods), then the principle in
plain standard words. Then: main result by page 2 · No. 14's worked example as the first picture,
checkable by pencil · central proof as an idea, one sitting, in the body · machinery after, each
concept with "we need it to…" · others' results as special cases of the principle ("when …, this is
exactly …") · scope and limits once, after positive results · conjectures and open problems ·
material used in no proof last. Minimal notation (main theorem ≤ ~7 named objects); a formula only
when the idea cannot be said without it; example before definition.
**Standard terminology only.** Banned words: CLAUDE.md table plus references/structure.md §Banned
(certificate, residual, team jargon: bank, seat, kill test, tabu, sealed, worked example...).
**Never**: Galois groups or ruler-and-compass constructibility (author's order), even if banked.

## Process
(a) **Claim map** from the bank (references/claim-map.md). Pick the one main result (A1); everything
    else is a corollary, special case, or Part II. Flag entries whose label is too weak for their
    planned role; do not raise them.
(b) **Outline** story-first; state the main question and answer in one sentence each; set the page
    budget (body 15–25 pages, appendix ≤ body). Each outline node cites its claim-map rows.
(c) **Draft** the .tex, named after the title (never `main`). Statements copied from the bank, then
    smoothed; proofs told as ideas, heavy algebra to an appendix. No status labels, AI or Lean in the
    body (D5/E5); those go in the companion verification note (step (f), references/naming.md).
(d) **Readability audit**: invoke the `my_revive_paper` skill on the draft (Steps 0–3: measure,
    four reviewers, diagnosis, checklist F). If unavailable, run checklist F of WRITING_GUIDELINE.md
    by hand plus a first-time-reader subagent. Fix by the change that adds least text (E2);
    the first-time reader vetoes length increases (E1).
(e) **Independent check of the draft**, sealed verdicts per team-formation laws (references/draft-check.md):
    - fresh-context **No. 2** (different model family if available): every statement and proof sketch
      against its bank entry; statement equals the locked one or is weaker; no unbanked claim;
      each proof sketch on the worked example; label wording matches the environment.
    - **No. 3**: every citation exists and says what the paper claims it says; credit sentences match its verdicts.
    Neither sees the other's verdict or the editor's reasoning before sealing. Record kinds of independence.
(f) **Fix, then freeze.** Any fail → fix → re-run the failing check on the changed parts. Compile with
    0 errors and 0 undefined references. Freeze per references/naming.md: frozen PDF
    `<title>_vXXX.pdf`, version folder unchanged in form, VERSIONS.md entry, companion
    verification note (claim map, Lean files and commit, which statements are Lean-checked).
    Present to the coach in Vietnamese, pedagogically (CLAUDE.md rules 1–7); the author decides
    whether the draft replaces the official copy.

## Lean status reporting
Every theorem-like statement has a Lean status in the claim map: Lean-checked · partly Lean-checked
(which part) · not Lean-checked, with Lean file, declaration name and commit (or file hash).
Per CLAUDE.md, a bank entry presented as proved that is not Lean-checked is sent back to No. 6 for a Lean
subagent before freeze; if Lean cannot reach it, the formalized algebraic core is named.
Where it is reported: only in the companion verification note, never in the paper, no appendix (author's decision, references/conflicts.md §2).

## Never
- Add a result, lemma, example or numerical claim not in the bank (proof sketches only restate banked proofs).
- Change a locked statement, merge two entries into a stronger one, or generalize by analogy.
- Cite a source No. 3 has not verified, or attribute to a paper more than No. 3 confirmed.
- Use banned private terminology, team jargon, "certificate"/"residual", or Galois/constructibility material.
- Present numerical evidence or computer certification at sample parameters as proof of a general claim.
- Edit the bank, the locked statements, the Lean environment or labels (law 1); read defenders' verdicts before sealing.
- Edit a frozen version folder or name any paper file `main`.
