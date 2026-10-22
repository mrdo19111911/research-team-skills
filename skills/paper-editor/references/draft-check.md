# Independent check of the draft (step e)
Team-formation laws apply unchanged: sealed verdicts, no voting, evidence only, independence recorded by kind.
No. 1 (the editor) is the party being judged here, so it does not judge its own draft.

## Setup
- Freeze the draft as a candidate (PDF + .tex hash) before spawning judges; judges see that exact file.
- Each judge writes to its own file `<paper folder>/review_notes/draft_check/<seat>_<hash>.md`, unreadable by
  the other until both are sealed. No. 6 sees "submitted / not yet" only.
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

## Verdict template
```
SEAT: | DRAFT: (file, hash) | VERDICT: pass / fail | ROWS FAILED: (paper ref, bank id) |
EVIDENCE: (locked vs typeset wording / step k on the example / source page) | SEARCH LOG: | INDEPENDENCE: model / context / tool
```

## After sealing
Any fail → No. 1 fixes the cheapest way (E2: fix the statement, add a hypothesis, add a sentence) and the
failing judge re-checks the changed rows only, in a fresh context. A fail that needs a stronger result is not
fixed in the paper: the claim is weakened to the locked one, or the request goes to No. 6 for the team.
Record both verdicts and their independence in the companion verification note.
