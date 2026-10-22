# Number traceability (`scripts/trace_numbers.py`, Python standard library only)
Idea (also seen in data-to-paper-style pipelines; nothing copied): a number typed by hand can drift from the run
that produced it, so no number is typed by hand. The run logs (JSON) are the source, a generated `results.tex`
holds one macro per number, and the paper uses only the macros. ml mode: mandatory. math mode: optional.

## Files
- **Spec** `<paper folder>/results_spec.json`, written by No. 1 from the bank:
  `{"macros": [{"name": "resAccMain", "source": "runs/main.json#/test/acc_mean", "scale": 100, "decimals": 1, "bank": "B12"},
  {"name": "resGain", "derived": "\\resAccMain - \\resAccBase", "decimals": 1, "bank": "B12"}]}`.
  `source` = file relative to the logs folder + `#` + JSON pointer (RFC 6901: `/key/0/key`, `~1` for `/`).
  `derived` = `+ - * / ( ) abs()` over other macros and constants; computed from full-precision sources.
  `decimals` = digits shown; rounding half-up. `bank` mandatory. Logs in other formats (CSV, TensorBoard)
  are exported to JSON by the run pipeline first; the script reads JSON only.
- **Results file** `<paper folder>/results.tex`, generated, never edited by hand, `\input` in the preamble:
  `\newcommand{\resAccMain}{84.4} % source: runs/main.json#/test/acc_mean | scale: 100 | bank: B12`.
  Macro names: prefix `res`, letters only (LaTeX forbids digits): `\resAccCifarTen`, not `\resAcc10`.

## Commands (exit 0 = clean, 1 = findings or failures, 2 = input error)
```
python scripts/trace_numbers.py --build results_spec.json --logs <logs dir or one .json> -o results.tex
python scripts/trace_numbers.py --check results.tex --logs <logs dir or one .json>
python scripts/trace_numbers.py --scan <paper>.tex --results results.tex [--keep-years]
```
`--check`: each macro value must equal its source × scale rounded to the shown decimals; derived macros are
recomputed from unrounded sources (shown 84.4 − 82.1 = 2.3, but 84.351 − 82.140 = 2.211 → 2.2 is correct);
fails on a missing bank id, unknown key, non-number value, duplicate name, cycle. `--scan` with `--results`
also reports `\res...` macros used but not defined. Run `--scan` on every .tex file the paper inputs.
Tests: `python scripts/tests/test_trace_numbers.py`.

## What `--scan` ignores (heuristics) and what it still misses
Ignored: preamble (before `\begin{document}`) and after `\end{document}` · comments · lines with
`% trace-ok: <reason>` (the reason is mandatory by this skill's rule, not checked by the script) · verbatim,
lstlisting, minted, `\verb` · arguments of citation, reference and label commands (`\cite[p.~3]{x}`,
`\ref`, `\eqref`, `\cref`, `\label`, ...), `\url`, `\href` (first argument), `\includegraphics`, `\input`,
package and class options, `\newcommand`/`\def` bodies, `\vspace`, `\setlength`, `\setcounter`, colors, box
sizes · optional arguments `[...]` of any command except delimiter sizers (`\left[` keeps its content), and of
`\\[4pt]` · table column specs, `\multicolumn{2}{c}`, `\multirow`, `\cline`, `\cmidrule(lr){2-3}` · LaTeX
lengths: a number followed by a letter (2pt, 3cm) or a length command (0.5\linewidth) · numbers attached to
a name: after a letter or letter-hyphen (CIFAR-10, ResNet-50, top-1, L2, fp16), or followed by a letter
or hyphen-letter (1st, 7B, 3D, 1-D, 5-fold, 10-shot) · years 1900–2039 as plain integers (not before `\%`;
`--keep-years` turns this off) and ISO dates · numbers right after Section, Figure, Table, Equation, Eq.,
Appendix, Theorem, Lemma, Algorithm, Line, Step, page, p., pp. and similar words, with `~` or `(` · manual
citations in prose `[3, 7]` · inside math: integers (indices, exponents, small constants of definitions),
unless next to `\pm` or `\%`; decimals in math and `10^{...}` are reported.
Inside tables every number is reported, math included.
Known misses (false negatives): integers in math away from `\pm`/`\%` (`$k = 5$ seeds` is missed: write
`$k = \resSeeds$`) · the base of `3 \times 10^{-4}` (only the `10` is reported) · numbers in compounds
(5-fold, 10-shot, 3-layer) and in names (ResNet-50) · a plain-integer count that looks like a year
(2000 steps) without `--keep-years` · numbers in `\text{}` inside math are treated as math · numbers
written in words ("five seeds") · leading-dot decimals (.5) are not seen at all · numbers inside figures (PDF/PNG) and in `\input` files
not scanned separately · macros defined elsewhere than the results file are not traced.
Known false positives: library versions (PyTorch 2.1), hand-typed section numbers after unlisted words,
"Tables 2 and 3": silence each with a `% trace-ok:` reason or turn it into a macro.

## Math mode (optional use)
Numerical constants and computer-certified bounds (e.g. a contraction factor at q = 0.25, a certified
worst case at N = 2, …, 6) may be traced the same way: the source is the certification script's JSON output,
the bank id its entry. Each such number has its own claim-map row with its label. A number whose final
check is "numerical evidence only" never appears as a theorem's constant or inside a theorem environment;
it appears only in a Remark / Observation or the conjectures section, with "numerically we observe".
Exact constants from exact computer algebra or a proof (1/2, (1 − q)²) are not traced: they are part of the
statement and checked by No. 2 against the bank.
