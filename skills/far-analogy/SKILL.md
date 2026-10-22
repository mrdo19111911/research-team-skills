---
name: far-analogy
description: Get past a concrete obstacle by borrowing a tool from a distant field, through a structured analogy that ends in a testable prediction. Use by default whenever a research problem has a concrete obstacle (in a team-formation campaign it is the tool of No. 7, which is always on), and when someone asks "how does another field solve this". Every card is recorded in the graph. Not for in-field ideas.
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
6. **Record the connection, always.** Right after the card, alive or dead:
   `python scripts/add_connection.py --name ... --a ... --b ... --map "x = y; ..." --breaks ... --small-test alive|dead|"not run" [--source ...] [--problem ...]`.
   Reuse existing node names (`find_path.py --find`) so the new edge joins the graph. When a kill test or a source
   check comes back later: `--update F<id> --small-test ... | --source-checked exists`. Dead edges stay on record
   (find_path.py skips them) so nobody proposes them again.

## Graph tools
- `data/core_en.yaml` (103 edges), `data/graph_vi.yaml` (~2,100 machine-generated edges,
  statuses likely inflated) and `data/found.yaml` (connections found by cards, written only by `add_connection.py`). Schema and operations: `references/graph.md`.
- `python scripts/find_path.py --find "<kw>" | --edges "<node>" | "<start>" "<goal>" [maxlen] | --families "<start>" "<goal>" | --stats`
- A path's hypotheses are the union of its edges' hypotheses; one heuristic edge, or any family hop,
  makes the whole path heuristic. Most common failure: every edge true, composition false.
- Sources are unverified (`source_checked: no`) until `scripts/check_arxiv.py` or a human confirms
  them. Never cite an unchecked source as fact; never invent one (write "none").
- Only the user upgrades an edge to "theorem" (add_connection.py never writes it). Record new and dead edges, with their breaks.

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
In a team-formation team this is the tool of No. 7 (far field, core seat, on by default) and No. 11 (adjacent field, switched on per problem):
send the card to No. 14 (Examples), who runs the kill test on the example library or the worked example;
only a card with SMALL TEST = alive goes on to No. 10, never directly to No. 9; label it agent-level.
No. 7 records the card at once with `--small-test "not run"` and updates it with No. 14's result.
Worked examples: `references/examples.md`.
