# Templates
## Board fragment
```
ID: | SEAT: | TYPE: lemma / counterexample / obstacle / dead-direction / data / idea
STATEMENT: (locked wording if it touches an interface)
LABEL: agent-level   (only the ladder raises it)
DEPENDS ON: [ids] | SOURCE: (paper / computation / none) | EVIDENCE: (file, log, Lean name)
```
## Handoff note
```
SEAT: | DOING: | TRIED (and result): | STUCK AT: | DO NOT RETRY: | NEXT STEP I WOULD TAKE: | FILES:
```
## Submission (No. 9 → defense)
```
TARGET LEMMA (locked id): | PROOF FILE: | USES: [ids with labels] | KNOWN WEAK STEPS:
```
## Sealed defender verdict (No. 2, No. 3, every judging-squad member; written alone, before seeing any other verdict)
File: `.team/verdicts/<submission-id>/<seat>.md` (squad member: `<seat>-<member>.md`), one file per judge.
`.team/verdicts/<submission-id>/SEALED` is written only when every expected judge has filed; until then
`scripts/guard_sealed.py` blocks reading other judges' files. Never edited after sealing; a second look is a new, dated file.
```
SEAT: | SUBMISSION ID: | VERDICT: pass / fail
EVIDENCE: counterexample (with check script) / wrong step k (value on the worked example) / prior paper (exact reference)
SEARCH LOG: (what was tried, cases run, where the search stopped)
CRITERIA + SOURCES SEARCHED (No. 3): (what counts as "known"; databases, queries, date range)
INDEPENDENCE ACHIEVED: model family: | context: fresh yes / no, had read: | tools:
SEALED AT: (timestamp)
```
## Bank entry, math (No. 1 only; software and algorithm entries: references/coding-team.md, Acceptance standards)
```
RESULT ID: | STATEMENT: (as locked, verbatim) | LABEL: (ladder in laws.md)
FINAL CHECK: Lean-checked / partly Lean-checked: (which part) / exact computer algebra / computer-certified at (parameters) / numerical evidence only
LEAN FILE: | #print axioms: (summary: standard axioms only? no sorry, no custom axiom, no native_decide)
VERDICT FILES: (.team/verdicts/<submission-id>/*) | INDEPENDENCE ACHIEVED: (per judge: model / context / tool; never more)
DEPENDS ON: [bank ids] | NOVELTY: prior work found (refs) / none found, searched: (sources, queries) | DATE:
```
## Campaign report, team vs baseline (baseline = one agent, same budget, same problem)
```
| Measure                                         | Team | Baseline |
|-------------------------------------------------|------|----------|
| Verified results (with final-check labels)      |      |          |
| Time to first verified result                   |      |          |
| Cost to first verified result                   |      |          |
| Wrong directions killed early (count, cost)     |      |          |
| Catch rate of planted false variants (sparring) |      |          |
| Total spend                                     |      |          |
TEAM BEATS BASELINE? yes / no. If not: shrink to (seats / squads kept)
```
## Direction card (No. 6 writes it on the board before the direction starts)
```
DIRECTION ID: | OWNER SEAT: | BUDGET: | WINDOW:
STOP WHEN (any one): budget spent / window expired / killed by counterexample (id) / superseded by (id)
EXTENSION: only as a new dated entry with its reason; never by editing this card
```
## Quick novelty check (No. 3, when a branch opens or No. 8 adds a load-bearing lemma)
```
CHECKED: (branch id / load-bearing lemma id) | QUERIES + DATABASES SEARCHED:
VERDICT: known / partly known / not found | REFERENCES: (verified to exist)
DECISION (No. 6): cite and reuse / stop / continue
```
## Paper claim map (No. 1 as editor; the paper is written from the bank only)
```
| Paper item (Thm / Lemma / Prop no.) | Bank id | Label | Final check |
|-------------------------------------|---------|-------|-------------|
No bank id, or wording stronger than the locked statement → the claim does not enter the paper.
Before release: a fresh No. 2 checks each row against its bank entry, No. 3 each citation (sealed verdicts, as above).
CONJECTURES / OPEN PROBLEMS (listed separately, marked as such): | Item | Evidence (example / board id) | Status: conjecture |
```
## Example card (No. 14 → library)
```
ID: | CASE: (parameters) | WHY MEANINGFUL: all hypotheses active / separates conjectures A,B / attains the bound / edge of hypothesis H
COMPUTED: (every object of the theory, intermediate values) | METHOD: exact CAS / numerical | SCRIPT: (reruns)
KILLS: [conjecture ids] | SUPPORTS: [conjecture ids] | LABEL: numerical evidence (a counterexample is decisive)
```
## Worked example (one per problem, every seat reads it before playing)
```
CASE: | WHY THIS ONE: | OBJECTS, IN ORDER: (each with its exact value) | WHAT IS TIGHT / ZERO / NONZERO:
SCRIPT: | RECHECKED BY: No. 2
```
## Prediction before computing (No. 4 picks the case)
```
CONJECTURE: | NEW CASE: | PREDICTED VALUE (written before computing): | COMPUTED BY No. 14: | MATCH: yes / no
```
## Far-analogy card (No. 7/11 → No. 14 kill test → No. 10)
```
OBSTACLE | SOURCE FIELD + TOOL + REF | TABLE | BREAKS | TRANSLATED TOOL | PREDICTION | KILL TEST | COST | SMALL TEST | LABEL
```
## Tabu entry
```
DIRECTION: | DIED AT: | REASON / EVIDENCE: | SCOPE (what exactly was ruled out):
```
