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


def tempo_rules():
    """The 'Rules for every seat' section of references/tempo.md (appended to every seat prompt)."""
    text = read("tempo.md")
    i = text.find("## Rules for every seat")
    return text[text.index("\n", i) + 1:].strip() if i >= 0 else ""


# Model tier per seat (references/tempo.md, rule 6.2) and the Claude Code `model` value for it.
TIERS = {"fast": "sonnet", "strong": "opus", "strongest": "opus"}
KICKOFF_TIER = {"10a": "fast", "10b": "fast", "14a": "fast", "14b": "fast", "3s": "fast", "7a": "strong", "4a": "strong"}
TIME_BOX = "10 minutes or 40 tool calls"
BRIEF_SECTIONS = ("## What you do", "## What you hand over", "## Done when", "## Never")


def brief_text(seat, full):
    """Short context pack: the sections a spawn needs to act, plus the tempo rules (references/tempo.md, rule 6.1)."""
    keep, on = [], False
    for line in full.splitlines():
        if line.startswith("## "):
            on = line.strip() in BRIEF_SECTIONS
        if on:
            keep.append(line)
    head = (f"# No. {seat} {NAMES[seat]} — brief (read this first; the full prompt is .team/seats/{seat}.md, open it"
            " only when this brief does not settle a question)")
    return "\n".join([head, "", *keep, "", "## Tempo rules (from references/tempo.md)", tempo_rules()]) + "\n"


# The kickoff wave (references/tempo.md, rule 1): (agent id, seat, task). Spawned in ONE message right after setup.
KICKOFF = [
    ("10a", 10, "Literature review, classic sources: where does the coach's idea already live (named papers, books),"
                " what is known, what is open. Write .team/examples/lit-10a.md."
                " Done when the three questions are answered (five nearest papers with what they do; methods to beat; what is open) and the last two search rounds found nothing new; at most 3 rounds."),
    ("10b", 10, "Literature review, the last three years: recent papers on the coach's idea and its nearest"
                " neighbours; what is open. Write .team/examples/lit-10b.md."
                " Done when the three questions are answered (five nearest papers with what they do; methods to beat; what is open) and the last two search rounds found nothing new; at most 3 rounds."),
    ("14a", 14, "Smallest meaningful instance of the coach's problem: state it, compute it A to Z with a rerunnable"
                " script in .team/examples/, label every value."),
    ("14b", 14, "One realistic instance of the coach's problem: state it, the measurable quantity, a simple baseline,"
                " and compute it with a rerunnable script in .team/examples/."),
    ("3s", 3, "Quick novelty scan (not a verdict): is the coach's claim already known? List the five nearest papers"
              " with one line each on what they already do. Write .team/examples/novelty-scan.md."
              " Done when the last two search rounds found no nearer paper; at most 3 rounds."),
    ("7a", 7, "Far-analogy cards on the obstacle as the coach stated it: one or two cards, each recorded in the graph"
              " (add_connection.py) and sent to No. 14's inbox for a kill test."),
    ("4a", 4, "Edges of the coach's claim: where it must fail, and the simple baseline any proposal must beat. Write"
              " .team/examples/edges-4a.md and pass the baseline to No. 14 and No. 10."),
]


def kickoff_text(problem, today):
    log = (SCRIPTS / "log_event.py").as_posix()
    out = [f"# Kickoff wave ({today}) — spawn ALL of these in ONE message, in parallel, before anything else",
           f"Problem (coach): {problem}",
           "Rule (references/tempo.md): no planning first; board details and budget are written while the wave runs.",
           "Default wave budget: one task per agent; stop at the first verified-looking result or when the task is done.",
           "For each agent: `log_event.py start` before the spawn, `stop` when it returns. Also start the coordinators:"
           " head No. 6 and lane coordinators 6a (scouting), 6b (build), 6c (verification).",
           "Tell the coach at once which agents started and give the live view: "
           "`view_match.py <campaign> --live` (references/tempo.md, rule 5).", ""]
    for aid, seat, task in KICKOFF:
        tier = KICKOFF_TIER.get(aid, "strong")
        out += [f"## Agent {aid} — No. {seat}",
                f"Model tier: {tier} (Claude Code Agent tool: model \"{TIERS[tier]}\") · time box: {TIME_BOX}",
                f"Command before spawning: `python \"{log}\" start --seat {seat} --agent {aid}`",
                "Prompt:", "```",
                f"You are No. {seat}, agent {aid}, of a research team. TEAM_SEAT={seat}.",
                f"Read your brief .team/seats/brief/{seat}.md first (the full prompt .team/seats/{seat}.md only if"
                f" needed), then .team/bulletin.md, your inbox .team/inbox/{seat}/ and .team/cache/index.md.",
                f"Problem (coach): {problem}",
                f"Your task: {task}",
                f"Progress at once: within your first minute write your plan in one line to"
                f" .team/progress/{seat}-{aid}.md and run `python \"{log}\" note --seat {seat} --agent {aid} --note \"plan: ...\"`;"
                " then one line after each partial result, with its label.",
                "Pass directly along the open lanes (inbox file + log_event.py pass); never to a judge.",
                "Run independent searches, scripts and reads as parallel tool calls. Add what you fetch or compute to"
                " .team/cache/ with one line in .team/cache/index.md.",
                f"Time box: {TIME_BOX}. At the box return what you have, labelled, and one line `NEXT: <the rest>`.",
                "Return a board fragment (template in .team/templates/templates.md).",
                "```", ""]
    return "\n".join(out) + "\n"


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
        out += [full.replace("<far-analogy skill>", (SKILL.parent / "far-analogy").as_posix()), "", "## The four laws (from references/laws.md)", laws, "",
                "## Tempo rules (from references/tempo.md)", tempo_rules(), ""]
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
            "", "## Tempo rules (from references/tempo.md)", tempo_rules(),
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
    ap.add_argument("--install", action="store_true", help="pip-install the libraries the variant needs, if missing")
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
    for d in ("verdicts", "handoff", "examples", "seats", "seats/brief", "templates", "progress", "board", "inbox",
              "cache"):
        mkdir(team / d)
    for s_ in SEATS:
        mkdir(team / "inbox" / str(s_))
    for lane, seats_ in (("scouting", "14, 10, 7, 11, kickoff No. 3"), ("build", "8, 4, 9"),
                         ("verify", "verdict flow, No. 1 hand-offs")):
        write(team / "board" / f"lane-{lane}.md", f"# Lane {lane} (seats {seats_}); written only by its lane"
              f" coordinator; one summary line per return (references/tempo.md, rule 3)\n")
    write(team / "board.md", board_text(a.variant, problem, today))
    write(team / "bank.md", bank_text(a.variant, problem, today))
    write(team / "locked.txt", locked_text(a.variant))
    write(team / "metrics.md", metrics_text(a.variant, problem, today))
    write(team / "hooks.settings.json", json.dumps(hooks_json(), indent=2) + "\n")
    write(team / "bulletin.md", bulletin_text(problem, today))
    write(team / "kickoff.md", kickoff_text(problem, today))
    write(team / "cache" / "index.md", "# Cache index: one line per item (what, file, who, label). Read before"
          " searching or computing; add what you fetch (references/tempo.md, rule 6.5)\n")
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
        full = seat_file(s)
        if full:
            write(team / "seats" / "brief" / f"{s}.md", brief_text(s, full), overwrite=a.refresh_seats)

    for p in created:
        print("created ", p)
    for p in skipped:
        print("skipped ", p, "(exists)")
    if missing:
        print("warning: no role card parsed for seats", missing, file=sys.stderr)
    for s in ("guard_locked.py", "guard_sealed.py", "precompact_handoff.py", "log_event.py"):
        if not (SCRIPTS / s).exists():
            print(f"warning: hook script {s} not found in {SCRIPTS.as_posix()} (referenced anyway)", file=sys.stderr)
    sys.path.insert(0, str(SCRIPTS))
    import check_env
    miss = check_env.check(a.variant, a.install)
    print("environment:", "ok" if not miss else "MISSING " + " ".join(miss) +
          f' -> "{sys.executable}" -m pip install ' + " ".join(miss) + " (or rerun with --install)")
    print(f"next: merge {(team / 'hooks.settings.json').as_posix()} into the campaign's .claude/settings.json;"
          f" then spawn every agent in {(team / 'kickoff.md').as_posix()} in ONE message (references/tempo.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
