# ML mode (campaign variant `ml`; also the algorithm-research variant)
An empirical claim is true only in its setting. So the setting is part of the claim and is written in the body,
next to the claim, every time. Source of the rules: team-formation references/coding-team.md, sections
"ML research" and "Acceptance standards"; the shared core of SKILL.md applies unchanged.

## 1. Bank entry → paper claim
The bank entry (coding-team.md) gives: metric M on test set T (held out, opened once on a date) · mean ± CI over
k seeds · baselines (reproduced yes/no, their reported vs our number) · compute per method · test name and p ·
contamination check · config hash · run logs · scope (main claim / restricted setting).
- **Claim sentence** carries dataset and split, metric, compute budget, seeds and statistic:
  "On ImageNet-1k (validation split as test), our method reaches \resAccMain\% top-1 accuracy, mean ±
  \resAccMainCI{} (\resCILevel\% CI over \resSeeds{} seeds), at the same \resBudgetGPUh{} GPU-hour budget as
  every baseline." (Every number, the CI level and the budget included, is a macro.)
  Never "our method is better", "state of the art", "robust", "scales" without the setting that the bank states.
- **Comparison words follow the bank's test.** "Outperforms" / "improves" only if the bank records a
  pre-registered test that passed (name, p); else "matches", "is within the CI of", or report the numbers only.
  "Significant" only with the test named. A difference computed by the script is a number, not a claim of superiority.
- **Scope by section.** Main claim (the bank's scope "main") → abstract, introduction, main results table.
  Restricted setting (one dataset, one scale, one budget) → its own subsection or table, with its setting in the
  caption, never in the abstract as a general statement. Validation-set results are never called test results.
- **No theorem environments for empirical results.** A Proposition / Theorem appears only for a math-mode bank
  entry (theory of ML) under the math rules (claim-map.md).

## 2. Mandatory sections (order may follow the venue)
1. **Question and gap**: what fails today, named methods and the measured gap (from the bank or a verified citation).
2. **Method**, told as an idea first; one paragraph on why it should help, before equations.
3. **Experimental setup**: datasets and splits (sizes, how the test set was held out, contamination check
   and its result) · metric and the pre-registered win condition · baselines: each reproduced on our harness
   with our budget, a table of their reported number vs our reproduced number (bank: reproduced yes/no), gap
   explained in one sentence or left as "unexplained" · tuning budget per method (same for all) · compute:
   hardware, GPU-hours per method and in total.
4. **Results with uncertainty**: every cell mean ± CI (or median and IQR) over k seeds, k stated in the caption;
   the test and p for each comparison claimed; per-dataset numbers, not only an average.
5. **Ablations**, on the validation set, one mechanism per row, said so in the caption.
6. **Limitations**: "holds on these datasets, this budget, these seeds"; what was not tried; settings where it
   loses or ties (from the bank and the failed-runs list).
7. **Failed runs reported**: every run the bank lists as failed or discarded (diverged, crashed, lost), with
   the reason and whether it was rerun; no silent seed replacement.
8. **Reproducibility statement**: code (repository and commit), configs (frozen config hash), seeds, data
   versions, environment (library versions), how to rerun one table. All numbers in it are macros too.
9. **Related work** (below) and conclusion. Story-first and "others' results as special cases" still apply
   when the method genuinely contains a known one ("with the extra term set to zero, this is exactly [x]").

## 3. Number traceability (references/number-tracing.md)
No number is typed by hand in prose, captions or tables. Each comes from a macro in a generated `results.tex`
(`\newcommand{\resAccMain}{84.3} % source: runs/main.json#/test/acc_mean | scale: 100 | bank: B12`).
Derived numbers (differences, ratios, relative gains, averages over datasets) are computed by
`trace_numbers.py --build` from full-precision sources, never from the rounded displayed values.
Before step (e) and before freeze: `--scan` of every .tex file and `--check` of `results.tex` both exit 0;
the output goes into the companion verification note. Setting numbers (k seeds, budget, sizes) are traced
the same way; a number the venue imposes or that is not a result (a model name, a dataset name) may stay
typed with a `% trace-ok: <reason>` comment on that line.

## 4. Novelty and related work
- No. 3 searches ML venues and recent arXiv, including **concurrent work** (posted within the last months or
  after the campaign started). Concurrent work is cited as such ("concurrently, [x] ...") with what differs;
  never omitted, never claimed as prior to us or after us without dates.
- **Every cited number is checked against the cited paper's table** (table number and row recorded in No. 3's
  verdict). A number we reproduced is reported as ours, beside the reported one, never in place of it.
- Benchmark pitfalls known from the literature (leakage, label noise, test-set reuse) are named in setup or
  limitations, with citations No. 3 verified.

## 5. Claim-map row, ml
```
PAPER REF: (label key or table/cell) | PAPER WORDING: | BANK ID: | LOCKED CLAIM: (copied, with setting)
SETTING: dataset/split, metric, budget, k seeds, statistic | SCOPE: main / restricted (which)
RELATION: identical / reworded-equivalent (No. 2 confirms) / weaker (say how)
FINAL CHECK: measured claim, sealed test opened once on <date> / validation only / numerical evidence only
TEST: name, p, pre-registered: yes/no | MACROS: \res... names | RUN LOGS: paths | CONFIG: hash | COMMIT:
CITATION: (No. 3 verdict; "new here" / "known from [x]"; cited numbers checked: table, row) | INDEPENDENCE:
```
Every macro in `results.tex` appears in some row; every row's numbers appear only as its macros.

## 6. Draft check additions (draft-check.md)
No. 2 also: runs `trace_numbers.py --check` itself on the run logs (tool independence from the editor's run);
recomputes at least one table from raw run logs; checks each claim sentence states its setting; checks
"outperforms"/"significant" only where the bank's test passed; checks ablations are on validation.
No. 3 also: concurrent arXiv search with dates and queries; each cited number against its source table.

## 7. Venue
Use the venue's official template and style file, downloaded by the author or the coach from the venue;
none is bundled with this skill. Follow the venue's page limit, anonymization and checklist (e.g. a
reproducibility or responsible-research checklist); the checklist answers are drawn from the bank and the macros.
