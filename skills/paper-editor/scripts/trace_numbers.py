#!/usr/bin/env python3
"""Number traceability for a paper written from the bank (Python standard library only).

Every number in the paper's text and tables must come from a macro in a generated results file,
and every macro must equal the run log (or bank export) it cites. Three commands:

  --scan PAPER.tex [--results results.tex] [--prefix res] [--keep-years]
      List every bare number typed by hand in prose and tables (file:line:col), and, with
      --results, every \\res... macro used in the paper but not defined in the results file.
  --check results.tex --logs DIR_OR_JSON
      Check each macro against the source it cites (JSON pointer into a JSON log), after the
      stated scale and rounding; recompute derived macros from full-precision sources.
  --build spec.json --logs DIR_OR_JSON -o results.tex
      Generate the results file from a spec: values read from logs, derived values computed here.

Results-file line format (one macro per line, value a plain number):
  \\newcommand{\\resAccMain}{84.3} % source: runs/main.json#/test/acc_mean | scale: 100 | bank: B12
  \\newcommand{\\resAccGain}{2.2}  % derived: \\resAccMain - \\resAccBase | bank: B12
Fields: exactly one of `source:` (FILE#/json/pointer; FILE relative to --logs, may be omitted when
--logs is a single JSON file) or `derived:` (arithmetic + - * / ( ) abs() over other macros and
constants); `bank:` mandatory; `scale:` optional (default 1). The displayed number of decimals is
the number of digits after the point in the value; rounding is half-up.

Scanner heuristics are listed in references/number-tracing.md. Exit code 0 = clean, 1 = findings
or failures, 2 = usage or input error.
"""
import argparse
import ast
import json
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, getcontext

getcontext().prec = 40

# ---------------------------------------------------------------- scanner tables
# command -> number of mandatory brace arguments whose content is masked (never a result number)
MASK_ARGS = {
    **{c: 1 for c in ("cite citep citet citealp citealt citeauthor citeyear citeyearpar parencite "
                      "textcite autocite footcite nocite ref eqref pageref cref Cref autoref nameref "
                      "vref label url input include includegraphics bibliography bibliographystyle "
                      "usepackage RequirePackage documentclass vspace hspace cline cmidrule scalebox "
                      "raisebox color pagecolor hypersetup geometry linespread addvspace "
                      "includeonly externaldocument").split()},
    **{c: 2 for c in ("setlength addtolength setcounter addtocounter multicolumn multirow resizebox "
                      "rule fontsize textcolor colorbox").split()},
    "definecolor": 3, "href": 1,
    "newcommand": 2, "renewcommand": 2, "providecommand": 2, "DeclareMathOperator": 2,
    "newenvironment": 3, "renewenvironment": 3, "newtheorem": 2,
}
NO_OPT_MASK = set("left right middle big Big bigg Bigg bigl bigr Bigl Bigr biggl biggr Biggl Biggr".split())
TABULAR_ENVS = {"tabular": 1, "tabular*": 2, "tabularx": 2, "tabulary": 2, "array": 1, "longtable": 1,
                "tabu": 1, "xltabular": 2, "supertabular": 1, "minipage": 1, "wrapfigure": 2}
TABLE_SPAN_ENVS = {"tabular", "tabular*", "tabularx", "tabulary", "longtable", "tabu", "xltabular", "supertabular"}
VERBATIM_ENVS = {"verbatim", "verbatim*", "Verbatim", "lstlisting", "minted", "comment", "alltt"}
MATH_ENVS = {"equation", "equation*", "align", "align*", "alignat", "alignat*", "gather", "gather*",
             "multline", "multline*", "flalign", "flalign*", "eqnarray", "eqnarray*", "displaymath", "math"}
LENGTH_CMDS = ("textwidth linewidth columnwidth textheight paperwidth paperheight baselineskip hsize vsize "
               "parindent parskip linewidth unitlength").split()
REF_WORDS = (r"section|sections|sec\.|secs\.|figure|figures|fig\.|figs\.|table|tables|tab\.|equation|equations|"
             r"eq\.|eqs\.|appendix|appendices|app\.|theorem|thm\.|lemma|proposition|prop\.|corollary|cor\.|"
             r"definition|def\.|remark|chapter|ch\.|algorithm|alg\.|line|lines|step|steps|part|example|"
             r"assumption|conjecture|problem|phase|page|pages|p\.|pp\.|footnote|item|row|column|col\.")
REF_BEFORE = re.compile(r"(?:^|[^A-Za-z])(?:" + REF_WORDS + r")\s*(?:~|\\,|\\ )?\s*\(?$", re.I)
NUM_RE = re.compile(r"(?<![A-Za-z0-9_.@])(-)?(\d{1,3}(?:,\d{3})+|\d{1,3}(?:\{,\}\d{3})+|\d+)(\.\d+)?([eE][-+]?\d+)?")
DATE_RE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")
MANUAL_CITE_RE = re.compile(r"\[\d+(?:\s*[,\u2013-]\s*\d+)*\]")
TRACE_OK_RE = re.compile(r"(?<!\\)%\s*trace-ok")


def _escaped(text, i):
    n, j = 0, i - 1
    while j >= 0 and text[j] == "\\":
        n, j = n + 1, j - 1
    return n % 2 == 1


def _group_end(text, i, open_ch, close_ch):
    """i points at open_ch; return index just past the matching close_ch (or len(text))."""
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return len(text)


def _skip_ws(text, i):
    while i < len(text) and text[i] in " \t\n":
        i += 1
    return i


class Masker:
    def __init__(self, text):
        self.text = text
        self.mask = bytearray(len(text))

    def set(self, a, b):
        for k in range(max(a, 0), min(b, len(self.text))):
            self.mask[k] = 1

    def masked_text(self):
        return "".join(" " if (m and c != "\n") else c for c, m in zip(self.text, self.mask))


def _strip_comments(m):
    t = m.text
    for i, c in enumerate(t):
        if c == "%" and not _escaped(t, i):
            j = t.find("\n", i)
            m.set(i, len(t) if j < 0 else j)


def _mask_trace_ok_lines(m):
    pos = 0
    for line in m.text.split("\n"):
        if TRACE_OK_RE.search(line):
            m.set(pos, pos + len(line))
        pos += len(line) + 1


def _mask_outside_document(m):
    t = m.text
    b = t.find("\\begin{document}")
    if b >= 0:
        m.set(0, b + len("\\begin{document}"))
    e = t.find("\\end{document}")
    if e >= 0:
        m.set(e, len(t))


def _mask_verbatim(m):
    t = m.text
    for env in VERBATIM_ENVS:
        for mo in re.finditer(r"\\begin\{" + re.escape(env) + r"\}", t):
            end = t.find("\\end{" + env + "}", mo.end())
            m.set(mo.start(), len(t) if end < 0 else end + len(env) + 6)
    for mo in re.finditer(r"\\verb\*?(.)", t):
        end = t.find(mo.group(1), mo.end())
        m.set(mo.start(), len(t) if end < 0 else end + 1)


def _mask_commands(m, view):
    """Mask arguments of commands that never carry result numbers; view = text with comments blanked."""
    for mo in re.finditer(r"\\([A-Za-z@]+)(\*?)|\\\\(\*?)", view):
        name = mo.group(1)
        i = mo.end()
        if name is None:  # line break \\[2pt]
            j = _skip_ws(view, i)
            if j < len(view) and view[j] == "[":
                m.set(j, _group_end(view, j, "[", "]"))
            continue
        nargs = MASK_ARGS.get(name, 0)
        if name in ("begin", "end"):
            j = _skip_ws(view, i)
            if j < len(view) and view[j] == "{":
                k = _group_end(view, j, "{", "}")
                env = view[j + 1:k - 1].strip()
                m.set(j, k)
                if name == "begin" and env in TABULAR_ENVS:
                    j = _skip_ws(view, k)
                    if j < len(view) and view[j] == "[":
                        k = _group_end(view, j, "[", "]")
                        m.set(j, k)
                        j = _skip_ws(view, k)
                    for _ in range(TABULAR_ENVS[env]):
                        j = _skip_ws(view, j)
                        if j < len(view) and view[j] == "{":
                            k = _group_end(view, j, "{", "}")
                            m.set(j, k)
                            j = k
                elif name == "begin":  # options like [t], [h!] of floats
                    j = _skip_ws(view, k)
                    if j < len(view) and view[j] == "[":
                        m.set(j, _group_end(view, j, "[", "]"))
            continue
        j = i
        if name in ("def", "gdef", "edef"):
            j = _skip_ws(view, j)
            mm = re.match(r"\\[A-Za-z@]+[^{]*", view[j:])
            if mm:
                j += mm.end()
            if j < len(view) and view[j] == "{":
                m.set(j, _group_end(view, j, "{", "}"))
            continue
        if name == "cmidrule":
            j = _skip_ws(view, j)
            if j < len(view) and view[j] == "(":
                k = view.find(")", j)
                m.set(j, k + 1)
                j = k + 1
        # optional arguments [..] after any command (except delimiter sizers)
        if name not in NO_OPT_MASK:
            j2 = _skip_ws(view, j)
            while j2 < len(view) and view[j2] == "[":
                k = _group_end(view, j2, "[", "]")
                m.set(j2, k)
                j = k
                j2 = _skip_ws(view, j)
        for _ in range(nargs):
            j = _skip_ws(view, j)
            if j < len(view) and view[j] == "[":  # newcommand{\x}[1]{...}
                k = _group_end(view, j, "[", "]")
                m.set(j, k)
                j = _skip_ws(view, k)
            if j < len(view) and view[j] == "{":
                k = _group_end(view, j, "{", "}")
                m.set(j, k)
                j = k
            elif j < len(view) and view[j] == "\\":  # \newcommand\foo{...}
                mm = re.match(r"\\[A-Za-z@]+", view[j:])
                j += mm.end() if mm else 1
            else:
                break


def _env_spans(view, envs):
    spans = []
    for mo in re.finditer(r"\\begin\{([^}]+)\}", view):
        env = mo.group(1).strip()
        if env in envs:
            end = view.find("\\end{" + env + "}", mo.end())
            spans.append((mo.start(), len(view) if end < 0 else end))
    return spans


def _math_spans(view):
    spans = _env_spans(view, MATH_ENVS)
    i, n, start, closer = 0, len(view), None, None
    while i < n:
        c = view[i]
        if c == "\\" and i + 1 < n:
            nxt = view[i + 1]
            if start is None and nxt in "([":
                start, closer = i, "\\" + (")" if nxt == "(" else "]")
            elif start is not None and view[i:i + 2] == closer:
                spans.append((start, i + 2))
                start = None
            i += 2
            continue
        if c == "$":
            dd = view[i:i + 2] == "$$"
            tok = "$$" if dd else "$"
            if start is None:
                start, closer = i, tok
            elif closer == tok:
                spans.append((start, i + len(tok)))
                start = None
            i += len(tok)
            continue
        i += 1
    return spans


def _in(spans, p):
    return any(a <= p < b for a, b in spans)


def scan_text(text, keep_years=False):
    """Return a list of (line, col, number, where, context) for bare numbers typed by hand."""
    m = Masker(text)
    _mask_trace_ok_lines(m)
    _strip_comments(m)
    _mask_outside_document(m)
    _mask_verbatim(m)
    view = m.masked_text()
    _mask_commands(m, view)
    for mo in DATE_RE.finditer(view):
        m.set(mo.start(), mo.end())
    s = m.masked_text()
    math = _math_spans(view)
    tables = _env_spans(view, TABLE_SPAN_ENVS)
    for mo in MANUAL_CITE_RE.finditer(s):
        if not _in(math, mo.start()):
            m.set(mo.start(), mo.end())
    s = m.masked_text()

    line_starts = [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]
    raw_lines = text.split("\n")
    out = []
    for mo in NUM_RE.finditer(s):
        a, b = mo.start(), mo.end()
        intpart, frac, expo = mo.group(2), mo.group(3), mo.group(4)
        before = s[max(0, a - 40):a]
        after = s[b:b + 30]
        # attached to a name: CIFAR-10, top-1, ResNet-50, L2, fp16 (letter, or letter + hyphen, before)
        if re.search(r"[A-Za-z]-$", before):
            continue
        # followed by a letter: units (2pt, 3cm), ordinals (1st), sizes (1k, 7B), 3D; or a compound (1-D, 5-fold)
        if re.match(r"[A-Za-z]", after) or re.match(r"-[A-Za-z]", after):
            continue
        # followed by a length command: 0.5\linewidth
        if re.match(r"\s*\\(?:" + "|".join(LENGTH_CMDS) + r")(?![A-Za-z])", after):
            continue
        # section / figure / table / equation / page numbers typed after their word
        if REF_BEFORE.search(before):
            continue
        is_int = frac is None and expo is None
        if is_int and not keep_years and re.fullmatch(r"19\d\d|20[0-3]\d", intpart) and not re.match(r"\s*\\?%", after):
            continue
        where = "prose"
        if _in(tables, a):
            where = "table"
        elif _in(math, a):
            where = "math"
            sci_base = intpart == "10" and re.match(r"\s*\^\s*\{?\s*[-+]?\s*\d", after)
            pm = re.search(r"\\pm\s*\{?\s*$", before) or re.match(r"\s*\}?\s*\\pm(?![A-Za-z])", after)
            pct = re.match(r"\s*\}?\s*\\%", after)
            if is_int and not (sci_base or pm or pct):
                continue  # integers in math: indices, exponents, small constants of definitions
        line = next(k for k in range(len(line_starts) - 1, -1, -1) if line_starts[k] <= a)
        col = a - line_starts[line] + 1
        ctx = raw_lines[line].strip()
        out.append((line + 1, col, s[a:b], where, ctx[:100]))
    return out


def defined_macros(results_text):
    return {mo.group(1) for mo in re.finditer(r"\\(?:newcommand|renewcommand|providecommand)\*?\s*\{?\s*\\([A-Za-z]+)", results_text)} | \
           {mo.group(1) for mo in re.finditer(r"\\def\s*\\([A-Za-z]+)", results_text)}


def undefined_result_macros(text, results_text, prefix):
    m = Masker(text)
    _strip_comments(m)
    _mask_outside_document(m)
    _mask_verbatim(m)
    s = m.masked_text()
    known = defined_macros(results_text)
    out = []
    line_starts = [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]
    for mo in re.finditer(r"\\(" + re.escape(prefix) + r"[A-Z][A-Za-z]*)", s):
        if mo.group(1) not in known:
            line = next(k for k in range(len(line_starts) - 1, -1, -1) if line_starts[k] <= mo.start())
            out.append((line + 1, mo.start() - line_starts[line] + 1, "\\" + mo.group(1)))
    return out


# ---------------------------------------------------------------- results file and logs
LINE_RE = re.compile(r"^\s*\\(?:newcommand|renewcommand|providecommand)\*?\s*\{?\s*\\([^\s{}]+?)\s*\}?\s*"
                     r"\{([^{}]*)\}\s*(?:%(.*))?$")


class TraceError(Exception):
    pass


def parse_meta(comment):
    meta = {}
    for part in (comment or "").split("|"):
        if ":" in part:
            k, v = part.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    return meta


def parse_results(text):
    """Return ordered dict name -> {'value', 'meta', 'line'}; raise TraceError on duplicates."""
    macros = {}
    for n, line in enumerate(text.split("\n"), 1):
        mo = LINE_RE.match(line)
        if not mo:
            continue
        name, value, comment = mo.group(1), mo.group(2).strip(), mo.group(3)
        if name in macros:
            raise TraceError("line %d: macro \\%s defined twice (first at line %d)" % (n, name, macros[name]["line"]))
        macros[name] = {"value": value, "meta": parse_meta(comment), "line": n}
    return macros


class Logs:
    def __init__(self, root):
        self.root = root
        self.cache = {}
        if not os.path.exists(root):
            raise TraceError("logs path does not exist: %s" % root)
        self.single = os.path.isfile(root)

    def _load(self, path):
        if path not in self.cache:
            try:
                with open(path, encoding="utf-8") as f:
                    self.cache[path] = json.load(f, parse_float=Decimal, parse_int=Decimal)
            except (OSError, ValueError) as e:
                raise TraceError("cannot read JSON log %s: %s" % (path, e))
        return self.cache[path]

    def get(self, source):
        if "#" not in source:
            raise TraceError("source '%s' has no '#/json/pointer'" % source)
        fname, pointer = source.split("#", 1)
        fname = fname.strip()
        if self.single:
            if fname and os.path.basename(fname) != os.path.basename(self.root):
                raise TraceError("source cites %s but --logs is the single file %s" % (fname, self.root))
            path = self.root
        else:
            if not fname:
                raise TraceError("source '%s' names no file and --logs is a directory" % source)
            path = os.path.join(self.root, fname)
        node = self._load(path)
        if pointer not in ("", "/") and not pointer.startswith("/"):
            raise TraceError("pointer '%s' must start with '/'" % pointer)
        for tok in [t.replace("~1", "/").replace("~0", "~") for t in pointer.split("/")[1:]]:
            if isinstance(node, list):
                try:
                    node = node[int(tok)]
                except (ValueError, IndexError):
                    raise TraceError("source %s: no list index '%s'" % (source, tok))
            elif isinstance(node, dict) and tok in node:
                node = node[tok]
            else:
                raise TraceError("source %s: key '%s' not found" % (source, tok))
        if isinstance(node, bool) or not isinstance(node, (Decimal, str)):
            raise TraceError("source %s is not a number" % source)
        try:
            return Decimal(str(node))
        except InvalidOperation:
            raise TraceError("source %s is not a number: %r" % (source, node))


def _eval_expr(expr, values):
    """Evaluate arithmetic over \\macro names with Decimal; values: name -> callable returning Decimal."""
    py = re.sub(r"\\([A-Za-z]+)", r"__m_\1", expr)
    try:
        tree = ast.parse(py, mode="eval")
    except SyntaxError:
        raise TraceError("cannot parse derived expression '%s'" % expr)

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return Decimal(str(node.value))
        if isinstance(node, ast.Name) and node.id.startswith("__m_"):
            return values(node.id[4:])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            v = ev(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            l, r = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Add):
                return l + r
            if isinstance(node.op, ast.Sub):
                return l - r
            if isinstance(node.op, ast.Mult):
                return l * r
            if r == 0:
                raise TraceError("division by zero in '%s'" % expr)
            return l / r
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "abs" and len(node.args) == 1:
            return abs(ev(node.args[0]))
        raise TraceError("unsupported element in derived expression '%s'" % expr)

    return ev(tree)


def _decimals(value):
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", value):
        raise TraceError("value '%s' is not a plain number (digits, optional '-' and '.')" % value)
    return len(value.split(".")[1]) if "." in value else 0


def _round(x, d):
    return x.quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)


class Resolver:
    """Full-precision value of each macro (source * scale, or derived expression), with cycle detection."""

    def __init__(self, specs, logs):
        self.specs, self.logs, self.memo, self.stack = specs, logs, {}, []

    def value(self, name):
        if name in self.memo:
            return self.memo[name]
        if name not in self.specs:
            raise TraceError("derived expression uses unknown macro \\%s" % name)
        if name in self.stack:
            raise TraceError("cycle in derived macros: %s" % " -> ".join("\\" + n for n in self.stack + [name]))
        self.stack.append(name)
        try:
            meta = self.specs[name]
            has_src, has_der = bool(meta.get("source")), bool(meta.get("derived"))
            if has_src == has_der:
                raise TraceError("\\%s needs exactly one of 'source:' or 'derived:'" % name)
            try:
                scale = Decimal(str(meta.get("scale", "1")))
            except InvalidOperation:
                raise TraceError("\\%s: scale '%s' is not a number" % (name, meta.get("scale")))
            raw = self.logs.get(meta["source"]) if has_src else _eval_expr(meta["derived"], self.value)
            v = raw * scale
        finally:
            self.stack.pop()
        self.memo[name] = v
        return v


def check_results(results_text, logs):
    """Return (ok_lines, fail_lines)."""
    macros = parse_results(results_text)
    if not macros:
        raise TraceError("no \\newcommand{\\name}{value} lines found in the results file")
    res = Resolver({k: v["meta"] for k, v in macros.items()}, logs)
    ok, fail = [], []
    for name, mac in macros.items():
        tag = "line %d \\%s" % (mac["line"], name)
        try:
            if not re.fullmatch(r"[A-Za-z]+", name):
                raise TraceError("name must be letters only (LaTeX macro)")
            if not mac["meta"].get("bank"):
                raise TraceError("no 'bank:' id in the comment")
            d = _decimals(mac["value"])
            expected = _round(res.value(name), d)
            if Decimal(mac["value"]) != expected:
                raise TraceError("typeset %s but source gives %s (full precision %s)"
                                 % (mac["value"], expected, res.value(name)))
            ok.append("OK   %s = %s  [%s]" % (tag, mac["value"], mac["meta"].get("source") or "derived: " + mac["meta"]["derived"]))
        except TraceError as e:
            fail.append("FAIL %s: %s" % (tag, e))
    return ok, fail


def build_results(spec, logs, spec_name="spec"):
    items = spec.get("macros") if isinstance(spec, dict) else None
    if not isinstance(items, list) or not items:
        raise TraceError("spec must be {\"macros\": [ ... ]}")
    specs = {}
    for it in items:
        name = it.get("name", "")
        if not re.fullmatch(r"[A-Za-z]+", name):
            raise TraceError("macro name '%s' must be letters only" % name)
        if name in specs:
            raise TraceError("macro %s listed twice" % name)
        if not it.get("bank"):
            raise TraceError("macro %s has no bank id" % name)
        if not isinstance(it.get("decimals"), int) or it["decimals"] < 0:
            raise TraceError("macro %s needs an integer 'decimals' >= 0" % name)
        specs[name] = {k: str(v) for k, v in it.items() if k in ("source", "derived", "scale", "bank")}
    res = Resolver(specs, logs)
    lines = ["% Generated by trace_numbers.py --build from " + spec_name + ". Do not edit by hand:",
             "% change the spec or the logs and rebuild. Check with trace_numbers.py --check."]
    for it in items:
        name = it["name"]
        val = _round(res.value(name), it["decimals"])
        if val == 0:
            val = abs(val)
        fields = []
        if it.get("source"):
            fields.append("source: " + it["source"])
        else:
            fields.append("derived: " + it["derived"])
        if "scale" in it:
            fields.append("scale: " + str(it["scale"]))
        fields.append("bank: " + str(it["bank"]))
        if it.get("note"):
            fields.append("note: " + str(it["note"]).replace("|", "/"))
        lines.append("\\newcommand{\\%s}{%s} %% %s" % (name, format(val, "f"), " | ".join(fields)))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- CLI
def _read(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return f.read()
    except OSError as e:
        raise TraceError("cannot read %s: %s" % (path, e))


def main(argv=None):
    p = argparse.ArgumentParser(description="Trace every number in a paper to a generated results macro and its run log.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--scan", metavar="PAPER_TEX")
    g.add_argument("--check", metavar="RESULTS_TEX")
    g.add_argument("--build", metavar="SPEC_JSON")
    p.add_argument("--results", metavar="RESULTS_TEX", help="with --scan: also report undefined result macros")
    p.add_argument("--prefix", default="res", help="prefix of result macros (default: res)")
    p.add_argument("--keep-years", action="store_true", help="with --scan: do not skip 4-digit numbers 1900-2039")
    p.add_argument("--logs", metavar="DIR_OR_JSON")
    p.add_argument("-o", "--output", metavar="RESULTS_TEX")
    a = p.parse_args(argv)
    try:
        if a.scan:
            found = scan_text(_read(a.scan), keep_years=a.keep_years)
            for line, col, num, where, ctx in found:
                print("%s:%d:%d: bare number %s (%s): %s" % (a.scan, line, col, num, where, ctx))
            undef = undefined_result_macros(_read(a.scan), _read(a.results), a.prefix) if a.results else []
            for line, col, name in undef:
                print("%s:%d:%d: result macro %s is not defined in %s" % (a.scan, line, col, name, a.results))
            print("scan: %d bare number(s), %d undefined result macro(s)" % (len(found), len(undef)))
            return 1 if (found or undef) else 0
        if not a.logs:
            p.error("--check and --build need --logs")
        logs = Logs(a.logs)
        if a.check:
            ok, fail = check_results(_read(a.check), logs)
            for s in ok + fail:
                print(s)
            print("check: %d ok, %d failed" % (len(ok), len(fail)))
            return 1 if fail else 0
        if not a.output:
            p.error("--build needs -o RESULTS_TEX")
        try:
            spec = json.loads(_read(a.build))
        except ValueError as e:
            raise TraceError("spec %s is not JSON: %s" % (a.build, e))
        out = build_results(spec, logs, os.path.basename(a.build))
        with open(a.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(out)
        print("build: wrote %d macro(s) to %s" % (out.count("\\newcommand"), a.output))
        return 0
    except TraceError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
