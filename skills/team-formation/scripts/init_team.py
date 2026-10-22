"""Create the .team/ workspace for one campaign of the team-formation skill.

Usage:
    python init_team.py <campaign-dir> --variant math|ml|software|algorithm --problem "<one line>"
                        [--refresh-seats]

Creates <campaign-dir>/.team/ with board.md, bank.md, locked.txt, metrics.md, verdicts/, handoff/,
examples/, bulletin.md (coach directives), templates/templates.md, seats/<seat>.md (one system prompt per
seat: references/seats/<seat>.md if it exists, else the role card from references/role-cards.md, plus
references/laws.md) and hooks.settings.json (hook snippet to merge into the campaign's
.claude/settings.json). Idempotent: an existing file is never overwritten (board and bank are
append-only); seat files are rewritten only with --refresh-seats. Python 3 standard library only.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
REFS = SKILL / "references"
SCRIPTS = SKILL / "scripts"

CORE = [6, 14, 10, 8, 4, 9, 2, 3, 1, 7]
WINGS = [11]
SEATS = CORE + WINGS
# Fallback names, used only if a card header cannot be parsed.
NAMES = {1: "Final verifier", 2: "Proof-checker", 3: "Novelty", 4: "Breaker", 6: "Coordinator",
         7: "Far-field", 8: "Blueprint", 9: "Prover", 10: "In-field", 11: "Adjacent-field", 14: "Examples"}
VARIANTS = ("math", "ml", "software", "algorithm")


def read(name):
    p = REFS / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


def parse_cards(text):
    """Return {seat: card text}. A card is a paragraph starting with **...No. N...**;
    continuation lines (not starting with **) belong to it. One card may cover several seats."""
    cards, current, seats = {}, [], []

    def flush():
        for s in seats:
            cards[s] = "\n".join(current).strip()

    for line in text.splitlines():
        m = re.match(r"\*\*(.+?)\*\*", line)
        if m:
            flush()
            current, seats = [line], [int(n) for n in re.findall(r"No\.\s*(\d+)", m.group(1))]
        elif current and line.strip() and not line.startswith("#"):
            current.append(line)
        else:
            flush()
            current, seats = [], []
    flush()
    return cards


def card_name(card, seat):
    m = re.match(r"\*\*(.+?)\*\*", card or "")
    if m:
        for part in m.group(1).split("/"):
            mm = re.search(r"No\.\s*%d\s+([^(]+)" % seat, part)
            if mm:
                return mm.group(1).strip()
    return NAMES[seat]


def card_format(text):
    m = re.search(r"^Format:.*$", text, re.M)
    return m.group(0) if m else "Format: RECEIVES · PRODUCES · MAY WRITE · FORBIDDEN · TOOLS · MODEL"


def four_laws(text):
    """The numbered laws of laws.md: from the top heading to the first ## section."""
    body = text.split("\n## ")[0]
    lines = [l for l in body.splitlines() if not l.startswith("# ")]
    return "\n".join(lines).strip() or "(references/laws.md not found)"


def variant_roles(text):
    """{seat: (software meaning, project role)} from the table in coding-team.md."""
    roles = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0].isdigit():
            roles[int(cells[0])] = (cells[2], cells[3])
    return roles


def ml_roles(text):
    """{seat: ML meaning} from the two-column table under "## ML research" in coding-team.md."""
    roles, on = {}, False
    for line in text.splitlines():
        if line.startswith("## "):
            on = line.startswith("## ML research")
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if on and len(cells) == 2 and cells[0].isdigit():
            roles[int(cells[0])] = cells[1]
    return roles


def seat_file(seat):
    """Full seat prompt from references/seats/<seat>.md, or "" if absent."""
    p = REFS / "seats" / f"{seat}.md"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def bank_formats(text):
    """The acceptance standards and bank-entry formats of the other variants, from coding-team.md."""
    part = text.split("## Acceptance standards", 1)
    return ("\n## Acceptance standards and bank entries, software / algorithm / ml (from coding-team.md)"
            + part[1]) if len(part) == 2 else ""


def seat_prompt(seat, variant, problem, cards, fmt, laws, roles, mlroles=None):
    card = cards.get(seat)
    name = NAMES[seat]  # names as in SKILL.md; card headers abbreviate some
    wing = seat in WINGS
    out = [f"# No. {seat} {name} — system prompt (team-formation)", "",
           f"TEAM_SEAT={seat}",
           "(The orchestrator sets the environment variable TEAM_SEAT to this value for this seat's agent;"
           " the hooks guard_locked.py, guard_sealed.py and precompact_handoff.py read it.)", "",
           f"Campaign variant: {variant}", f"Problem (set by the coach): {problem}", ""]
    if wing:
        out += ["STATUS: wing seat, switched on per problem. No agent runs in this seat until No. 6 writes"
                " on the board that it is switched on (every in-field direction is dead, or a cross-field idea"
                " is wanted).", ""]
    else:
        out += ["STATUS: core seat (staffed in every campaign; an agent runs only when No. 6 has a task and"
                " budget for it).", ""]
    if variant == "ml" and seat in (mlroles or {}):
        out += [f"In the ml variant (empirical machine learning) this seat means: {mlroles[seat]}.",
                "Accepted = a measured, reproducible claim on a stated dataset, compute budget and seeds, with statistics;"
                " the sealed test set is opened once, by the performance referee, after the configuration is frozen.", ""]
    elif variant != "math" and seat in roles:
        meaning, role = roles[seat]
        out += [f"In the {variant} variant this seat means: {meaning} (project role: {role}).",
                "See references/coding-team.md for the grader and acceptance standard of this variant.", ""]
    if variant in ("algorithm", "ml"):
        out += ["The performance referee (off pitch, not a seat) owns the instance sets or datasets and splits,"
                " the sealed set, the harness, the compute budget and the statistics. No seat edits them.", ""]
    full = seat_file(seat)
    if full:
        out += [full.replace("<far-analogy skill>", (SKILL.parent / "far-analogy").as_posix()), "", "## The four laws (from references/laws.md)", laws, ""]
        return "\n".join(out) + "\n"
    out += ["## Your role card (from references/role-cards.md)", fmt, "",
            card or f"(no card found for No. {seat} in references/role-cards.md)", "",
            "## The four laws (from references/laws.md)", laws, "",
            "## Files", "- Read `.team/board.md` (working state) and `.team/bank.md` (verified results) before playing.",
            "- Never re-enter a direction in the tabu log.",
            "- Read `.team/bulletin.md` (coach directives) first, at the start of every task.",
            "- Post results as board fragments at the lowest label (template in `.team/templates/templates.md`).",
            "- Paths listed in `.team/locked.txt` are the grader: do not edit them.",
            "- Before you run out of context, write a handoff note to `.team/handoff/` (template in `.team/templates/templates.md`).",
            ]
    if seat in (2, 3):
        out += [f"- Write your verdict alone to `.team/verdicts/<submission-id>/{seat}.md`. Do not read any other"
                " verdict file or the board discussion of this submission until `.team/verdicts/<submission-id>/SEALED`"
                " exists."]
    if seat == 1:
        out += ["- You are the sole writer of `.team/bank.md`: append only; record the final check and the kinds of"
                " independence achieved (model / context / tool), never more than achieved."]
    if seat in (7, 11):
        add = (SKILL.parent / "far-analogy" / "scripts" / "add_connection.py").as_posix()
        out += ["- Use the far-analogy skill for every card. Record each card in its graph the moment you make it:",
                f"  `python {add} --name ... --a ... --b ... --map \"x = y; ...\" --breaks ... --small-test \"not run\""
                f" --problem \"{problem}\"`; when No. 14 reports the kill test, run `--update F<id> --small-test alive|dead`.",
                "  Dead connections are recorded too: they stop the next agent from proposing them again."]
    if seat == 14:
        out += ["- You own `.team/examples/`: the example library and the worked example with its rerunnable script."]
    if seat == 6:
        out += ["- You own the board structure, phase, budgets, stop criteria and `.team/metrics.md`.",
                "- You see only \"submitted / not yet\" per defender until a submission is SEALED."]
    return "\n".join(out) + "\n"


def bulletin_text(problem, today):
    return f"""# Bulletin (coach directives; every seat reads this first, at the start of every task)
Problem: {problem} | Created: {today}
Only the coach writes here. A directive beats any older instruction on the board. Ids B1, B2, ... with a date;
seats cite the id of the directive a decision follows ("follows B3"). Never edit an old directive: add a new one that replaces it.

| Id | Date | Directive | Replaces |
|---|---|---|---|
"""


def board_text(variant, problem, today):
    return f"""# Board (working state; structure owned by No. 6; append-only, annotated corrections only)
Problem (coach): {problem}
Variant: {variant} | Created: {today}

## Phase
Current phase: −1 Examples (No. 6 alone switches phase; references/phases.md)
| Date | Phase | Budget | Stop condition | Set by |
|---|---|---|---|---|
| {today} | −1 Examples | (set by No. 6) | a conjecture predicts a case written down before No. 14 computes it, and the prediction is right | No. 6 |

## Seats switched on
Core (staffed every campaign): 6, 14, 10, 8, 4, 9, 2, 3, 1, 7 (No. 7 far field on by default). Wing (off until No. 6 switches it on here): 11.
| Date | Seat | On/off | Task | Budget | Model family |
|---|---|---|---|---|---|

## Directions (stop criteria written before the direction starts)
Any one stop criterion met → the direction stops and goes to the tabu log; no renegotiation without a new entry and reason.
| ID | Direction | Owner seat | Budget | Window | Killed by counterexample | Superseded by | Sent to No. 7 | Status |
|---|---|---|---|---|---|---|---|---|

## Requests to No. 14 (ordered by No. 6)
| Order | From seat | Request | Status |
|---|---|---|---|

## Submissions and defender status (No. 6 sees only "submitted / not yet" until SEALED)
| Submission | Target lemma | No. 2 | No. 3 | SEALED | No. 1 |
|---|---|---|---|---|---|

## Fragments (template: .team/templates/templates.md; every fragment enters at agent-level; every value carries its label)

## Tabu log (DIRECTION | DIED AT | OBSTRUCTION (name it; same name twice is a signal) | REASON / EVIDENCE | SCOPE)

## Persist or reframe (No. 6, every 5 tasks and whenever three directions die on the same obstruction)
| Date | Obstruction or question | Evidence | Decision (persist / reframe / ask coach) | Bulletin directive followed |
|---|---|---|---|---|

## Open for the main result (No. 8 updates after each bank entry; restricted cases are listed apart)

## Dependencies (claim graph; a refuted node demotes everything resting on it)
| Node | Depends on | Status |
|---|---|---|

## Handoffs (seat, date, context level, note file)
"""


def bank_text(variant, problem, today):
    return f"""# Bank (verified results; written only by No. 1; append-only)
Problem: {problem}
Variant: {variant} | Created: {today}
Each entry: ID | STATEMENT (locked wording) | FINAL CHECK: Lean-checked / exact computer algebra /
computer-certified at stated parameters / numerical evidence only (software: spec tests + CI run; algorithm:
measured claim with set, hardware, cap, seeds, statistics; ml: metric on the sealed test set opened once, mean ± CI over
k seeds, reproduced baselines, compute, contamination check) | SCOPE: main result / restricted case | JUDGES and kinds of independence each had
(model / context / tool) | EVIDENCE | DATE
Weaker independence (same model family for attack and defense) must be stated in the entry.

## Entries
"""


LOCKED_EXAMPLES = {
    "math": ["lean/Statement.lean", "lean/lakefile.lean", "lean/lean-toolchain", "lean/lake-manifest.json"],
    "software": ["tests/acceptance/**", "tests/hidden/**", ".github/workflows/**", "benchmarks/**"],
    "algorithm": ["instances/**", "harness/**", "stats/**", "sealed/**"],
    "ml": ["data/splits/**", "sealed/**", "harness/**", "eval/**", "configs/frozen/**"],
}


def locked_text(variant):
    ex = "\n".join("# " + p for p in LOCKED_EXAMPLES[variant])
    return f"""# locked.txt — the grader ("do not move the goalposts", law 1).
# One glob per line, relative to the campaign root (the directory that holds .team/).
# scripts/guard_locked.py (PreToolUse hook) blocks Edit / Write / MultiEdit / NotebookEdit on any match.
# This file itself is always locked. Lines starting with # are ignored.
# The hook does not see shell commands (sed, >): also deny Bash writes to these paths for the
# attack and midfield, or run No. 1 in its own worktree that alone holds the locked files.
# Add paths here in Phase 0, when the statement / acceptance tests / instance sets are locked.
# Typical entries for the {variant} variant (uncomment when they exist):
{ex}
# The bank is written only by No. 1; locking it here blocks every other seat. The hook lets
# TEAM_SEAT=1 through; subagents inherit TEAM_SEAT, so run No. 1 in its own session.
.team/bank.md
"""


def metrics_text(variant, problem, today):
    return f"""# Campaign report: team vs baseline
Problem: {problem}
Variant: {variant} | Created: {today}
Baseline = one agent, same budget, same problem, same tools, started from the same files.
Rule: team does not beat baseline → shrink the team.

## Budget
| | Team | Baseline |
|---|---|---|
| Budget (tokens / dollars / wall time) | | |
| Model(s) and families used | | |

## Measures
| Measure | Team | Baseline | Note |
|---|---|---|---|
| Verified results (with final-check label each) | | | |
| Time to first verified result | | | |
| Cost to first verified result | | | |
| Wrong directions killed early (count) | | | |
| Cost spent on directions before they were killed | | | |
| Catch rate of planted false variants (sparring team) | | | |
| Total spend | | | |

## Independence achieved (per bank entry: model / context / tool)

## Handoffs (count per seat, context level at handoff)

## Verdict
Team better / equal / worse than baseline, and what to change (seats to switch off, squads to shrink):
"""


def hooks_json():
    py = sys.executable.replace("\\", "/") if sys.executable else "python"

    def cmd(script):
        return {"type": "command", "command": f'"{py}" "{(SCRIPTS / script).as_posix()}"'}

    return {"hooks": {
        "PreToolUse": [
            {"matcher": "Edit|Write|MultiEdit|NotebookEdit", "hooks": [cmd("guard_locked.py")]},
            {"matcher": "Read|NotebookRead|Edit|Write|MultiEdit|NotebookEdit|Grep|Glob|Bash|PowerShell", "hooks": [cmd("guard_sealed.py")]},
        ],
        "PostToolUse": [{"matcher": "Read|NotebookRead|Write|Edit|MultiEdit|NotebookEdit", "hooks": [cmd("log_event.py")]}],
        "Stop": [{"hooks": [cmd("log_event.py")]}],
        "SubagentStop": [{"hooks": [cmd("log_event.py")]}],
        "PreCompact": [{"hooks": [cmd("precompact_handoff.py")]}],
    }}


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("campaign_dir")
    ap.add_argument("--variant", required=True, choices=VARIANTS)
    ap.add_argument("--problem", required=True)
    ap.add_argument("--refresh-seats", action="store_true",
                    help="rewrite seats/*.md from the current role cards (board and bank are never rewritten)")
    a = ap.parse_args(argv)
    problem = " ".join(a.problem.split())
    team = pathlib.Path(a.campaign_dir).resolve() / ".team"
    today = datetime.date.today().isoformat()
    created, skipped = [], []

    def mkdir(p):
        (skipped if p.is_dir() else created).append(p.relative_to(team.parent).as_posix() + "/")
        p.mkdir(parents=True, exist_ok=True)

    def write(p, text, overwrite=False):
        rel = p.relative_to(team.parent).as_posix()
        if p.exists() and not overwrite:
            skipped.append(rel)
            return
        created.append(rel + (" (refreshed)" if p.exists() else ""))
        p.write_text(text, encoding="utf-8", newline="\n")

    mkdir(team)
    for d in ("verdicts", "handoff", "examples", "seats", "templates"):
        mkdir(team / d)
    write(team / "board.md", board_text(a.variant, problem, today))
    write(team / "bank.md", bank_text(a.variant, problem, today))
    write(team / "locked.txt", locked_text(a.variant))
    write(team / "metrics.md", metrics_text(a.variant, problem, today))
    write(team / "hooks.settings.json", json.dumps(hooks_json(), indent=2) + "\n")
    write(team / "bulletin.md", bulletin_text(problem, today))
    write(team / "templates" / "templates.md", read("templates.md") + bank_formats(read("coding-team.md")),
          overwrite=a.refresh_seats)

    cards_src = read("role-cards.md")
    cards, fmt = parse_cards(cards_src), card_format(cards_src)
    laws = four_laws(read("laws.md"))
    roles = variant_roles(read("coding-team.md"))
    mlroles = ml_roles(read("coding-team.md"))
    missing = [s for s in SEATS if s not in cards and not seat_file(s)]
    for s in SEATS:
        write(team / "seats" / f"{s}.md", seat_prompt(s, a.variant, problem, cards, fmt, laws, roles, mlroles),
              overwrite=a.refresh_seats)

    for p in created:
        print("created ", p)
    for p in skipped:
        print("skipped ", p, "(exists)")
    if missing:
        print("warning: no role card parsed for seats", missing, file=sys.stderr)
    for s in ("guard_locked.py", "guard_sealed.py", "precompact_handoff.py", "log_event.py"):
        if not (SCRIPTS / s).exists():
            print(f"warning: hook script {s} not found in {SCRIPTS.as_posix()} (referenced anyway)", file=sys.stderr)
    print(f"next: merge {(team / 'hooks.settings.json').as_posix()} into the campaign's .claude/settings.json;"
          " then follow references/launcher.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
