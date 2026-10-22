# Files, versions, companion note
From memory notes file-naming-by-title and version-naming (author's rules, 2026-10-06).

## Names
- `<title>` = the paper's `\title`: spaces → `_`, hyphens kept, `:` `,` and other punctuation dropped, case kept.
  Example: `The_uniqueness_of_the_optimal_fixed-step_method_for_smooth_strongly_convex_minimization`.
- Working .tex/.pdf named `<title>.tex` / `<title>.pdf`, never `main`. Renaming an existing `main.tex`:
  update every `\externaldocument[X-]{../folder/main}` in companion papers and recompile them all.
- Never rename LaTeX label keys.

## Freeze
- Folder `versions\<project>_<X>\<project>_<X>_vXXX\` under the project root (3 digits); PDF beside it `<title>_vXXX.pdf`,
  with the title of that version. A title change applies to new versions only.
- Log every freeze in `versions\VERSIONS.md`. Never edit a frozen folder. Working folder names never change (xr).
- If several copies of the paper exist: ask the author which copy is official before writing.
- Compile 3 passes, 0 errors, 0 undefined references; recompile xr-linked papers.

## Companion verification note
`<paper folder>/verification/<title>_vXXX_verification.md`, frozen with the version. Contains:
claim map (claim-map.md rows) · per statement: Lean-checked / partly Lean-checked (which part) / not Lean-checked,
Lean file, declaration, commit or file hash, `#print axioms` output · CAS and certification scripts with parameters ·
No. 2 and No. 3 draft-check verdicts with kinds of independence · readability audit score (checklist F, before/after).
The paper body does not mention it (E5) unless the author chooses otherwise (conflicts.md §2).

## Reporting to the author
Vietnamese, pedagogical (CLAUDE.md 1–7): the story of the paper in words, what is new, each main claim with its
status label and Lean status, what is still missing, page counts vs budget, PDF paths of old and new versions.
In chat math: at most one `_` per expression (latex-rendering note).
