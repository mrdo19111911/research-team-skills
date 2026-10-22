# Claim map
File: `<paper folder>/claim_map.md`, written by No. 1 only, rebuilt from the bank at step (a), updated at every edit.
One row per statement the reader could quote: theorem-like environments, displayed inequalities used later,
"it is known that", "we observe", every special-case sentence, every number in the abstract and introduction.

## Row
```
PAPER REF: (label key, e.g. thm:main) | PAPER WORDING: (as typeset) | BANK ID: | LOCKED WORDING: (copied)
RELATION: identical / reworded-equivalent (No. 2 confirms) / weaker (say how)
LABEL: (CLAUDE.md) proved by hand / exact computer algebra / computer-certified / numerical evidence / conjecture
FINAL CHECK: (team ladder) Lean-checked / partly Lean-checked: <part> / exact computer algebra / computer-certified at <parameters> / numerical evidence only
LEAN: file, declaration, commit or file hash, `#print axioms` clean: yes/no | SCRIPT: (CAS / certification script)
CITATION: (No. 3 verdict id; "new here" or "known from [x]", what is new) | INDEPENDENCE: model / context / tool, as in the bank
```
A citation-only row (a result of others stated in the paper) has BANK ID "none", CITATION mandatory, LABEL "literature".

## Label → environment
| Final check | Allowed in paper | Wording |
|---|---|---|
| Lean-checked | Theorem / Lemma / Proposition / Corollary | "we prove" |
| partly Lean-checked | same, if the remaining part is exact computer algebra or a proof by hand passed by No. 2 | "we prove"; companion note names the unchecked part |
| exact computer algebra | same | "we prove"; proof says "a direct (symbolic) computation shows", script in companion note |
| computer-certified at stated parameters | Proposition, parameters inside the statement ("for N = 2, …, 6 and q in …") | "verified by computer for …"; never "for all" |
| numerical evidence only | Remark / Observation, or the conjectures section | "numerically we observe"; never a theorem environment, never in the abstract as a fact |
| conjecture, open problem | section "Conjectures and open problems" only | "we conjecture"; state the evidence and what is missing in one sentence |

CLAUDE.md Lean rule: before freeze, every row presented as proved has LEAN filled. Empty → back to No. 6 for a
Lean subagent; if only the algebraic core can be formalized, LEAN names that core and the row says "partly".

## Checks the map makes mechanical
- Every `\begin{theorem|lemma|proposition|corollary}` label key has a row (grep the .tex against the map).
- No row without a paper ref, no paper ref without a row.
- RELATION "weaker" rows: the paper text never claims the locked (stronger) form elsewhere.
- Abstract and introduction numbers: each traced to a row; say in the text where the number comes from and its normalization.
