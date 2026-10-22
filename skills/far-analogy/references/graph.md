# Dictionary graph
- **Node** = a "world": a framework with its own objects and operations.
- **Edge** = a dictionary between two worlds, with status and hypotheses.
- **Super-motif** = a type shared by many dictionaries (quantization, decategorification, space–algebra duality...).
- **Family** = coarse grouping of nodes (data/families.yaml). A family hop is NOT a correspondence.

## Edge schema
```yaml
- id: X01
  name: <usual name>
  a: <world A>            # reuse existing node names exactly
  b: <world B>
  status: theorem | conditional | heuristic | conjecture
  hyp: <hypotheses under which it holds>
  map: [[<object or operation in A>, <in B>], ...]   # must include relations/operations
  breaks: <where it fails outside the hypotheses>
  motif: <super-motif>
  source: <DOI, arXiv id, or book + theorem number; "none" if unsure>
  source_checked: no | exists | content-matches
```
Edges in `data/found.yaml` also carry `small_test: alive | dead | not run`, `found: <date>` and `seen:` (one line per
card that met the connection again, with date, problem and kill-test result). IDs are F001, F002, ...
(The Vietnamese graph uses ten/trang_thai/gia_thiet/dich/cho_gay/nguon/nguon_da_kiem; the tools read both.)

## Four operations
1. **Locate** the problem's world(s).
2. **Find paths** to a world with strong tools.
3. **Compose the translation table along the path and check composed hypotheses** (their union).
   Most common failure: every edge is true, the composition is not.
4. **Find holes**: a super-motif present for many pairs but missing for the needed pair = conjecture.

## Super-motifs (seed)
| Super-motif | Idea | Examples |
|---|---|---|
| quantization / dequantization | classical geometry ↔ quantum or combinatorial object | Kirillov (quantization), tropical (dequantization) |
| categorification / decategorification | rich object ↔ number or function | sheaf → function; cohomology → Euler characteristic |
| space–algebra duality | space ↔ algebra of functions | Gelfand; Prim as a "space" |
Kirillov and Mikhalkin sit at opposite ends of the same quantum–classical axis. A hole worth hunting:
for a dictionary known in one direction, what does the other direction look like?
