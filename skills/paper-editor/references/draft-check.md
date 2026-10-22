# Independent check of the draft (step e)
Team-formation laws apply unchanged: sealed verdicts, no voting, evidence only, independence recorded by kind.
No. 1 (the editor) is the party being judged here, so it does not judge its own draft.

## Setup
- Freeze the draft as a candidate (PDF + .tex hash) before spawning judges; judges see that exact file.
- The draft check is a submission with id `draft-<short-hash>`. Each judge files a sealed verdict at
  `.team/verdicts/draft-<short-hash>/<seat>.md` (in the campaign's `.team/`, not in the paper folder);
  team-formation's `guard_sealed.py` hook keeps it unreadable by the other judge until No. 6 writes `SEALED` there, once both
  have filed. No. 6 sees "submitted / not yet" only.
- Spawn fresh agents (bench), never agents that saw the drafting.

## No. 2: statements and proof sketches
RECEIVES: draft PDF/.tex, the bank, the claim map, No. 14's worked example. NOT the editor's notes or No. 3's verdict.
For every claim-map row and every theorem-like environment:
1. paper wording vs locked wording: identical / equivalent (give the argument) / weaker / STRONGER (fail);
2. hypotheses: none dropped, ranges not widened, quantifiers not swapped;
3. environment and verb match the final check (claim-map.md table);
4. proof sketch: restates the banked proof's idea, adds no unbanked step; each step evaluated on the worked example
   (a wrong value is an error; agreement proves nothing general);
5. scan prose for unbanked claims ("it follows", "in general", "one can show", numbers): each must map to a row.
Verdict: pass / fail, with row, page and the evidence.

## No. 3: citations and credit
RECEIVES: draft, bibliography, No. 3's earlier novelty verdicts. NOT No. 2's verdict.
For every citation: exists (DOI / arXiv id resolved) · says what the sentence claims (theorem or page located) ·
credit sentence ("known from [x]" / "new here") matches the novelty verdict · no prior work omitted that the
verdict named. Search criteria and sources stated. Verdict: pass / fail per citation.

## ml mode additions (ml-mode.md §6)
No. 2 also receives the run logs, the results spec and `results.tex`: runs `trace_numbers.py --check` and `--scan`
itself; recomputes at least one table from raw logs; checks every claim sentence states dataset/split, budget,
seeds and statistic; "outperforms"/"significant" only where the bank's pre-registered test passed; ablations on
validation; failed runs listed match the bank. No. 3 also: concurrent arXiv work (queries, dates); every cited
number against the cited paper's table (table and row in the verdict).

## Verdict template
```
SEAT: | DRAFT: (file, hash) | VERDICT: pass / fail | ROWS FAILED: (paper ref, bank id) |
EVIDENCE: (locked vs typeset wording / step k on the example / source page) | SEARCH LOG: | INDEPENDENCE: model / context / tool
```

## After sealing
Any fail → No. 1 fixes the cheapest way (E2: fix the statement, add a hypothesis, add a sentence) and the
failing judge's seat re-checks the changed rows only, in a fresh context. A fail that needs a stronger result is not
fixed in the paper: the claim is weakened to the locked one, or the request goes to No. 6 for the team.
After sealing, No. 1 copies both verdicts, with their independence, into the companion verification note.
A re-check after a fix is a new submission `draft-<new-short-hash>`, judged in a fresh context.
