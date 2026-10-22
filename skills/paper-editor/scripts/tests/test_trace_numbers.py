"""Tests for trace_numbers.py. Run: python scripts/tests/test_trace_numbers.py"""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import trace_numbers as tn  # noqa: E402


def doc(body, preamble=""):
    return "\\documentclass{article}\n" + preamble + "\\begin{document}\n" + body + "\n\\end{document}\n"


def nums(body, **kw):
    return [f[2] for f in tn.scan_text(doc(body), **kw)]


class Scan(unittest.TestCase):
    def test_prose_number_flagged_with_line(self):
        found = tn.scan_text(doc("Intro.\nOur method reaches 84.3 accuracy."))
        self.assertEqual([(f[0], f[2], f[3]) for f in found], [(4, "84.3", "prose")])

    def test_macro_use_not_flagged(self):
        self.assertEqual(nums("Our method reaches \\resAccMain\\% accuracy."), [])

    def test_percent_integer_and_negative(self):
        self.assertEqual(nums("gains 3\\% and -0.7 points"), ["3", "-0.7"])

    def test_thousands_and_scientific(self):
        self.assertEqual(nums("trained for 12,000 steps with rate 3e-4"), ["12,000", "3e-4"])

    def test_preamble_comments_trace_ok(self):
        body = "a 0.25 here % 0.99 in a comment\nlr 0.001 % trace-ok: stated by the venue\n"
        self.assertEqual([f[2] for f in tn.scan_text(doc(body, "\\setlength{\\parindent}{12pt}\n\\def\\q{0.5}\n"))],
                         ["0.25"])

    def test_years_and_dates(self):
        self.assertEqual(nums("Since 2017, and on 2026-10-22, see [3, 7]."), [])
        self.assertEqual(nums("Since 2017.", keep_years=True), ["2017"])
        self.assertEqual(nums("gain 2017\\% here"), ["2017"])

    def test_references_citations_labels(self):
        body = ("As in Section 3, Figure~2, Table 4, Eq. (5), Appendix 1 and page 7 \\cite[p.~12]{smith2020}, "
                "\\citep{a1}, see \\ref{fig:1}, \\eqref{eq:2}\\label{sec:3}.")
        self.assertEqual(nums(body), [])

    def test_names_units_lengths(self):
        body = ("CIFAR-10, ResNet-50, top-1, L2, fp16, a 1-D case, 3D, 7B, 1st, 2pt, "
                "\\includegraphics[width=0.5\\linewidth]{fig1.pdf} \\vspace{-3mm} 0.8\\textwidth \\\\[4pt]")
        self.assertEqual(nums(body), [])

    def test_math_integers_skipped_decimals_flagged(self):
        body = "$x_1 + 2y^2$, $k = 3$, \\[ \\sum_{i=1}^{N} a_i \\] and $q = 0.25$ and $5 \\pm 1$ and $10^{-4}$"
        found = tn.scan_text(doc(body))
        self.assertEqual([(f[2], f[3]) for f in found], [("0.25", "math"), ("5", "math"), ("1", "math"), ("10", "math")])

    def test_math_environment(self):
        body = "\\begin{equation} f(x) = 2x + 1.5 \\label{eq:7} \\end{equation}"
        self.assertEqual(nums(body), ["1.5"])

    def test_table_numbers_flagged_spec_skipped(self):
        body = ("\\begin{table}[t]\\begin{tabular}{l c r}\n"
                "\\multicolumn{2}{c}{Method} & Acc \\\\ \\cmidrule(lr){2-3}\n"
                "Ours & $5$ & 84.3 \\\\\n"
                "Base & \\resAccBase & $82.1 \\pm 0.4$ \\\\\n"
                "\\end{tabular}\\end{table}")
        found = tn.scan_text(doc(body))
        self.assertEqual([(f[2], f[3]) for f in found], [("5", "table"), ("84.3", "table"), ("82.1", "table"), ("0.4", "table")])

    def test_verbatim_and_newcommand_in_body(self):
        body = "\\begin{verbatim}lr = 0.1\\end{verbatim} \\verb|x=3.2| \\newcommand{\\half}{0.5} ok"
        self.assertEqual(nums(body), [])

    def test_undefined_result_macros(self):
        text = doc("We get \\resAccMain{} and \\resAccTypo, \\result.")
        res = "\\newcommand{\\resAccMain}{84.3} % source: a.json#/x | bank: B1\n"
        self.assertEqual([u[2] for u in tn.undefined_result_macros(text, res, "res")], ["\\resAccTypo"])


class Check(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "runs"))
        with open(os.path.join(self.d, "runs", "main.json"), "w", encoding="utf-8") as f:
            json.dump({"test": {"acc_mean": 0.84351, "ci95": 0.0042},
                       "base": {"acc_mean": 0.82140}, "seeds": [1, 2, 3, 4, 5], "a/b": 7}, f)
        self.logs = tn.Logs(self.d)

    def tearDown(self):
        shutil.rmtree(self.d)

    def run_check(self, text):
        return tn.check_results(text, self.logs)

    def test_ok_with_scale_and_rounding(self):
        ok, fail = self.run_check(
            "\\newcommand{\\resAccMain}{84.4} % source: runs/main.json#/test/acc_mean | scale: 100 | bank: B12\n"
            "\\newcommand{\\resAccCI}{0.42} % source: runs/main.json#/test/ci95 | scale: 100 | bank: B12\n"
            "\\newcommand{\\resSeeds}{5} % source: runs/main.json#/seeds/4 | bank: B12\n"
            "\\newcommand{\\resEsc}{7} % source: runs/main.json#/a~1b | bank: B12\n")
        self.assertEqual(fail, [])
        self.assertEqual(len(ok), 4)

    def test_mismatch_fails(self):
        ok, fail = self.run_check("\\newcommand{\\resAccMain}{84.3} % source: runs/main.json#/test/acc_mean | scale: 100 | bank: B12\n")
        self.assertEqual(len(fail), 1)
        self.assertIn("source gives 84.4", fail[0])

    def test_derived_uses_full_precision(self):
        # displayed 84.4 - 82.1 = 2.3, but full precision 84.351 - 82.140 = 2.211 -> 2.2
        head = ("\\newcommand{\\resAccMain}{84.4} % source: runs/main.json#/test/acc_mean | scale: 100 | bank: B12\n"
                "\\newcommand{\\resAccBase}{82.1} % source: runs/main.json#/base/acc_mean | scale: 100 | bank: B12\n")
        ok, fail = self.run_check(head + "\\newcommand{\\resGain}{2.2} % derived: \\resAccMain - \\resAccBase | bank: B12\n")
        self.assertEqual(fail, [])
        ok, fail = self.run_check(head + "\\newcommand{\\resGain}{2.3} % derived: \\resAccMain - \\resAccBase | bank: B12\n")
        self.assertEqual(len(fail), 1)

    def test_missing_bank_key_and_bad_value(self):
        ok, fail = self.run_check(
            "\\newcommand{\\resA}{84.4} % source: runs/main.json#/test/acc_mean | scale: 100\n"
            "\\newcommand{\\resB}{1} % source: runs/main.json#/test/nope | bank: B1\n"
            "\\newcommand{\\resC}{84.4\\%} % source: runs/main.json#/test/acc_mean | scale: 100 | bank: B1\n"
            "\\newcommand{\\resD}{1} % bank: B1\n")
        self.assertEqual(len(fail), 4)
        self.assertIn("bank", fail[0])
        self.assertIn("not found", fail[1])
        self.assertIn("plain number", fail[2])
        self.assertIn("exactly one", fail[3])

    def test_cycle_and_duplicate(self):
        ok, fail = self.run_check("\\newcommand{\\resA}{1} % derived: \\resB + 1 | bank: B1\n"
                                  "\\newcommand{\\resB}{1} % derived: \\resA - 1 | bank: B1\n")
        self.assertTrue(all("cycle" in f for f in fail) and len(fail) == 2)
        with self.assertRaises(tn.TraceError):
            self.run_check("\\newcommand{\\resA}{1} % source: x.json#/a | bank: B1\n"
                           "\\newcommand{\\resA}{1} % source: x.json#/a | bank: B1\n")

    def test_single_json_logs(self):
        logs = tn.Logs(os.path.join(self.d, "runs", "main.json"))
        ok, fail = tn.check_results(
            "\\newcommand{\\resA}{84.4} % source: #/test/acc_mean | scale: 100 | bank: B1\n"
            "\\newcommand{\\resB}{84.4} % source: main.json#/test/acc_mean | scale: 100 | bank: B1\n"
            "\\newcommand{\\resC}{84.4} % source: other.json#/test/acc_mean | scale: 100 | bank: B1\n", logs)
        self.assertEqual(len(ok), 2)
        self.assertEqual(len(fail), 1)

    def test_build_then_check_cli(self):
        spec = {"macros": [
            {"name": "resAccMain", "source": "runs/main.json#/test/acc_mean", "scale": 100, "decimals": 1, "bank": "B12"},
            {"name": "resAccBase", "source": "runs/main.json#/base/acc_mean", "scale": 100, "decimals": 1, "bank": "B12"},
            {"name": "resGain", "derived": "\\resAccMain - \\resAccBase", "decimals": 1, "bank": "B12"}]}
        sp, out = os.path.join(self.d, "spec.json"), os.path.join(self.d, "results.tex")
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(spec, f)
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(tn.main(["--build", sp, "--logs", self.d, "-o", out]), 0)
            self.assertEqual(tn.main(["--check", out, "--logs", self.d]), 0)
        with open(out, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("\\newcommand{\\resGain}{2.2} % derived: \\resAccMain - \\resAccBase | bank: B12", text)
        self.assertIn("check: 3 ok, 0 failed", buf.getvalue())

    def test_scan_cli_exit_codes(self):
        paper, res = os.path.join(self.d, "p.tex"), os.path.join(self.d, "r.tex")
        with open(res, "w", encoding="utf-8") as f:
            f.write("\\newcommand{\\resA}{1} % source: runs/main.json#/seeds/0 | bank: B1\n")
        with open(paper, "w", encoding="utf-8") as f:
            f.write(doc("Value \\resA, over \\resA seeds."))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(tn.main(["--scan", paper, "--results", res]), 0)
        with open(paper, "w", encoding="utf-8") as f:
            f.write(doc("Value 0.5 and \\resB."))
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(tn.main(["--scan", paper, "--results", res]), 1)
        self.assertIn("scan: 1 bare number(s), 1 undefined result macro(s)", buf.getvalue())
        with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
            self.assertEqual(tn.main(["--check", res, "--logs", os.path.join(self.d, "missing")]), 2)


if __name__ == "__main__":
    unittest.main()
