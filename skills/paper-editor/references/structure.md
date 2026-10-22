# Structure and style
Sources: CLAUDE.md "Writing style for the paper"; WRITING_GUIDELINE.md A–G; my_revive_paper exemplars
(Taylor–Drori arXiv 2101.09741: main result p. 2, 17-page body, one-page Lyapunov proof in the body,
limit cases μ → 0 / k → ∞ recover OGM / TMM; Weinstein: first sentence a question, example before
definition, old results as special cases, honest first-person limits). Memory notes: writing-style,
structure-first, narrative-framing, elementary-means-simple, ideas-not-formulas, readability-guideline.

## Outline (default order)
1. **Story paragraph.** First sentence a question (G1). Second: what is known, by name, and the concrete
   gap (A2). Then the principle in one plain paragraph: what moves, on what space, by what rule, what each
   object is for (narrative framing), before any symbol.
2. **Main result** by page 2, full formula (B1). Notation budget: ≤ ~7 named objects (C2).
3. **First picture: No. 14's worked example**, smallest case (N = 1, one dimension), told as a game in
   words with one figure, checkable by pencil (B2, elementary-means-simple). Exact formulas to an appendix.
4. **Deepest idea, then the central proof** as its idea ("add two known inequalities; the remainder is a
   square"), one sitting, in the body (B3, structure-first). Repetitive algebra to the appendix, never ideas.
5. **Machinery** after its use is known, each concept with "we need it to…" (B4), example before definition (G2).
6. **Special cases: others' results recovered** from the principle, one sentence each "when …, this is
   exactly [known result] [cite]" (B6, G4). Prior work is framed as consequences, credit kept exact (No. 3).
7. **Scope and limits**, each limit once (B5, D1); counterexamples here, never opening a section.
8. **Conjectures and open problems**, clearly marked; evidence and what is missing, one sentence each.
9. **Related work** grouped by theme, each group ending in what it leaves open (A4). Material used in no
   proof (geometric interpretation, far applications) last or Part II (B7). Longest section = main result.

## Sentences
- Topic sentence per paragraph; first sentences alone retell the section (D6).
- One idea per sentence, ≤ 2 new concepts per sentence (D2). Assertive; no repeated hedges (D1).
- Strange-looking quantities get "this may look unnatural, but it means…" (C5).
- No trace of the writing process: no "previous version", "referee", status labels, AI, Lean (D5, E5).
- No abbreviation invented to shorten a formula; every acronym spelled out at first use (C1, C3).
- New words only for genuinely new objects, with a precise definition (G7); otherwise the standard term.

## Banned
CLAUDE.md table, with replacements: ledger → Lyapunov (potential) function · clock → weight sequence A_k,
step-size schedule · leak → defect or slack term of the one-step identity · junction → coupling
(convex-combination) step, query point · kick → dual (momentum) update · aim z_k → dual sequence,
aggregated gradient · straightening → Taylor–Hendrickx–Glineur reduction · edges of the cone → extremal
functions, extreme rays of F_{μ,L} · edge chain → worst-case (resisting) chain · chord → interpolation
inequality · reservoir → terms of the Lyapunov function · the film → time reversal, H-duality · cash-in →
final (terminal) step. Allowed geometric terms: contactomorphism, Legendrian, Dirac structure,
port-Hamiltonian, metriplectic, Wall form.
Also banned (certificate-terminology note): "certificate" → weighted sum of interpolation inequalities
(multipliers λ); "residual" → remainder; "exact certificate" → weighted sum that proves a tight bound.
"certificate" may appear at most once, citing Shu–Wang. Never rename LaTeX label keys.
Team jargon never reaches the paper: bank, board, seat, No. N, kill test, tabu, sealed verdict, goal,
label ladder, "worked example" as a team term (write "example").
Galois groups, ruler-and-compass constructibility: excluded from text, framing and selling points.
Check: `rg -n -w -i` over all .tex sources for every banned word; count must be 0 (C3).
