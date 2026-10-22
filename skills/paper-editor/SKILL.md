---
name: paper-editor
description: Skill of the goalkeeper (No. 1, Final verifier) of the team-formation skill when it edits the bank of verified results into a paper, in two modes - a mathematics paper (theorems, Lean-checked or computer-certified results) or an empirical machine-learning paper (experiments, baselines, seeds, every number traced to its run log). Use when the team's bank should become a paper, when the coach asks No. 1 to write up results, or when a paper must be rebuilt from the bank after new bank entries. Not for discovering or proving results, nor for running experiments.
---

# Paper editor (No. 1 writes the paper)

**The bank is the only source.** No. 1 is the sole writer of the bank and the only seat that turns it
into prose. The editor arranges, explains and credits; it never proves, strengthens, reruns or adds.
Read first, every time, from the paper project's root: `CLAUDE.md` (status labels, Lean rule, banned-word table),
`WRITING_GUIDELINE.md` if present (rules A–G, checklist F), team-formation `SKILL.md` and
`references/laws.md`. Those files win over this one; known tensions are settled in references/conflicts.md.

## Mode = campaign variant (set at team setup, `init_team.py --variant`)
- **math** (also theory of ML: rates, bounds, convergence): everything below plus references/claim-map.md,
  structure.md. Unchanged from before; no rule is weakened.
- **ml** (empirical machine learning; the algorithm-research variant uses it too, with its own bank format):
  the shared core below plus references/ml-mode.md, which replaces the label-by-environment rule and the
  math outline. Variant unclear → ask No. 6; never mix modes inside one paper.

## Input (nothing else)
- `.team/bank.md`: locked statements, labels, final check, kinds of independence; Lean names (math) or
  metric, split, seeds, statistic, compute, run logs, config hash, scope (ml, team-formation coding-team.md).
- No. 3's sealed novelty verdicts: prior work, what is new, verified citations (ml: and each cited number).
- No. 14's worked example (math: card + rerunnable script; ml: the reproduced baseline and smallest run).
- ml only: the run logs and frozen configs the bank entries name, read-only, for number tracing.
Never a source of claims: the board, fragments, tabu log, attack reasoning, chat, earlier drafts,
memory notes (memory and the style files govern *how* to write, never *what* is true).
A fact needed for the story but absent from the bank → request on the board via No. 6; do not write it.

## Hard rules (both modes)
1. **No bank entry, no statement.** Every theorem, lemma, proposition, corollary, empirical claim,
   displayed claim, "we observe" and "it is known that" sentence maps to a bank id or a No. 3-verified citation.
2. **Locked wording, locked scope.** The paper's claim equals the locked one or is weaker and says so.
   Never drop a hypothesis or a setting, widen a range, turn "for N ≤ 5" into "for all N" or "on CIFAR-10"
   into "on image classification", or upgrade a label. Rewording only if No. 2 confirms equivalence (step (e)).
3. **Strength shown in the paper.** math: by environment and verb (references/claim-map.md table):
   Theorem / Lemma / Proposition only for Lean-checked, partly Lean-checked (part named) or exact computer
   algebra; computer-certified states its parameters in the statement; numerical evidence never in a theorem
   environment or "we prove"; conjectures in one section "Conjectures and open problems".
   ml: by the stated setting (references/ml-mode.md): "on X (split), mean ± CI over k seeds, budget B";
   main claim vs restricted setting as in the bank entry; never "our method is better" without its setting.
4. **Claim map** alongside the draft: paper claim → bank id → label → final check → evidence (Lean file and
   commit, or run logs and config hash) → citation. A paper claim with no row is an error.
5. **Credit from No. 3 only.** Each result gets one sentence: "known from [x]" or "new here",
   with what is new stated precisely. Only citations No. 3 verified (exists, says what is claimed).
6. **No number typed by hand** (ml mandatory, math optional): numbers come from macros in a generated
   `results.tex`, each citing its log and bank id; derived numbers computed by the script
   (`scripts/trace_numbers.py`, references/number-tracing.md).

## Structure
math (references/structure.md): story first (a question, the named gap, the principle in plain words) ·
main result by page 2 · worked example as the first picture, checkable by pencil · central proof as an idea,
in the body · machinery after, each concept with "we need it to…" · others' results as special cases ·
scope and limits once · conjectures and open problems · material used in no proof last.
ml (references/ml-mode.md): question and gap · claim with its setting · experimental setup · results with
uncertainty · ablations · related work and concurrent work · limitations · failed runs · reproducibility
statement. Venue page limit and the venue's official template (never bundled here).
Both: minimal notation, a formula only when the idea cannot be said without it, example before definition.
**Standard terminology only.** Banned words: CLAUDE.md table plus references/structure.md §Banned
(certificate, residual, team jargon: bank, seat, kill test, tabu, sealed, worked example...).
**Never**: Galois groups or ruler-and-compass constructibility (author's order), even if banked.

## Process
(a) **Claim map** from the bank (references/claim-map.md; ml rows in ml-mode.md). Pick the one main result;
    everything else is a corollary, special case, restricted setting or Part II. Flag entries whose label is
    too weak for their planned role; do not raise them. ml: write the results spec and build `results.tex`.
(b) **Outline** story-first; state the main question and answer in one sentence each; set the page
    budget (math: body 15–25 pages, appendix ≤ body; ml: the venue limit). Each outline node cites its rows.
(c) **Draft** the .tex, named after the title (never `main`). Statements copied from the bank, then
    smoothed; proofs told as ideas, heavy algebra to an appendix. No status labels, AI or Lean in the
    body (D5/E5); those go in the companion verification note (references/naming.md). ml: every number is a
    macro; `trace_numbers.py --scan` and `--check` both exit 0.
(d) **Readability audit**: invoke the `my_revive_paper` skill on the draft (Steps 0–3: measure,
    four reviewers, diagnosis, checklist F). If unavailable, run checklist F of WRITING_GUIDELINE.md
    by hand plus a first-time-reader subagent. Fix by the change that adds least text (E2);
    the first-time reader vetoes length increases (E1).
(e) **Independent check of the draft**, sealed verdicts per team-formation laws (references/draft-check.md):
    - fresh-context **No. 2** (different model family if available): every claim against its bank entry;
      equal or weaker; no unbanked claim; math: each proof sketch on the worked example, label wording
      matches the environment; ml: every table cell and macro against the run logs, settings stated.
    - **No. 3**: every citation exists and says what the paper claims; credit sentences match its verdicts;
      ml: every cited number matches the cited paper's table, concurrent arXiv work searched.
    Neither sees the other's verdict or the editor's reasoning before sealing. Verdicts are filed as sealed verdicts
    in `.team/verdicts/draft-<short-hash>/<seat>.md` (guarded by `guard_sealed.py`), not in the paper folder;
    after sealing, No. 1 copies them, with kinds of independence, into the companion verification note.
(f) **Fix, then freeze.** Any fail → fix → re-run the failing check on the changed parts. Compile with
    0 errors and 0 undefined references. Freeze per references/naming.md: frozen PDF
    `<title>_vXXX.pdf`, version folder unchanged in form, VERSIONS.md entry, companion
    verification note (claim map; math: Lean files and commit; ml: results spec, check output, run logs, commit).
    Present to the coach in Vietnamese, pedagogically (CLAUDE.md rules 1–7); the author decides
    whether the draft replaces the official copy.

## Lean status reporting (math mode)
Every theorem-like statement has a Lean status in the claim map: Lean-checked · partly Lean-checked
(which part) · not Lean-checked, with Lean file, declaration name and commit (or file hash).
Per CLAUDE.md, a bank entry presented as proved that is not Lean-checked is sent back to No. 6 for a Lean
subagent before freeze; if Lean cannot reach it, the formalized algebraic core is named.
Where it is reported: only in the companion verification note, never in the paper, no appendix (author's decision, references/conflicts.md §2).
In ml mode the same place holds the evidence column: run logs, config hash, `--check` output.

## Never
- Add a result, lemma, example, experiment or number not in the bank (proof sketches only restate banked proofs).
- Change a locked statement or setting, merge two entries into a stronger one, or generalize by analogy.
- Cite a source No. 3 has not verified, or attribute to a paper more than No. 3 confirmed.
- Use banned private terminology, team jargon, "certificate"/"residual", or Galois/constructibility material.
- Present numerical evidence or computer certification at sample parameters as proof of a general claim;
  give a numerical-evidence-only number as a theorem's constant.
- Type a result number by hand, round it by hand, or compute a difference or ratio by hand (ml).
- Edit the bank, the locked statements, the Lean environment, labels, run logs or configs (law 1);
  read defenders' verdicts before sealing.
- Edit a frozen version folder or name any paper file `main`.
