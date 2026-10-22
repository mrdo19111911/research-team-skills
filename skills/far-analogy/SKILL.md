---
name: far-analogy
description: Get past a concrete obstacle by borrowing a tool from a distant field, through a structured analogy that ends in a testable prediction. Use when in-field routes are exhausted or someone asks "how does another field solve this". Not for in-field or adjacent-field ideas.
---

# Far analogy

Far-field ideas are cheap and mostly wrong. This skill kills shallow ones fast and passes on only
analogies with real structure. **Search by structure, not by topic**: distant fields use different words.

## Procedure
1. **Strip field names.** Restate what makes the obstacle hard, without field-specific nouns.
   Alternatively start from a key motif of the problem (`references/motifs.md`); ask the user
   where they have seen it before searching yourself.
2. **Find fields with the same obstacle.** At least 3 distant fields (`references/far-fields.md`);
   search with the source field's own vocabulary. Check the graph with `scripts/find_path.py`
   instead of recalling from memory.
3. **Correspondence table** (source ↔ target): objects, relations, operations. Relations beat
   attributes; one-to-one; systematic. **State where the mapping breaks.**
4. **Bring the tool home** as a concrete statement or procedure, not an inspiration.
5. **One testable prediction and one kill test**, with cost (cheap / medium / expensive).
   No prediction → stop. Run the kill test on small cases if it is cheap.

## Graph tools
- `data/core_en.yaml` (103 edges) and `data/graph_vi.yaml` (~2,100 machine-generated edges,
  statuses likely inflated). Schema and operations: `references/graph.md`.
- `python scripts/find_path.py --find "<kw>" | --edges "<node>" | "<start>" "<goal>" [maxlen] | --families "<start>" "<goal>" | --stats`
- A path's hypotheses are the union of its edges' hypotheses; one heuristic edge, or any family hop,
  makes the whole path heuristic. Most common failure: every edge true, composition false.
- Sources are unverified (`source_checked: no`) until `scripts/check_arxiv.py` or a human confirms
  them. Never cite an unchecked source as fact; never invent one (write "none").
- Only the user upgrades an edge to "theorem". Record new and dead edges, with their breaks.

## Reject at once
Word-level similarity ("both are networks"); field chosen for fame; attributes only, no relations;
no break stated; no prediction, or one true in every case.

## Output
```
OBSTACLE:  <field-free sentence>
SOURCE:    <field>, <tool>, <reference or "none">
TABLE:     <source ↔ target>
BREAKS:    <relations with no counterpart>
TOOL HOME: <statement or procedure>
PREDICTION: <X> | KILL TEST: <Y> | COST: <cheap/medium/expensive> | SMALL TEST: alive/dead/not run
```
In a team-formation team this is the tool of No. 7 (far field) and No. 11 (adjacent field):
send the card to No. 14 (Examples), who runs the kill test on the example library or the worked example;
only a card with SMALL TEST = alive goes on to No. 10, never directly to No. 9; label it agent-level.
Worked examples: `references/examples.md`.
