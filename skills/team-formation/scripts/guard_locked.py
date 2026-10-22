"""PreToolUse hook: block file edits to locked paths ("do not move the goalposts").
Locked paths: one glob per line in <project>/.team/locked.txt, relative to the project root
(e.g. tests/**, lean/Statement.lean, .team/bank.md). Lines starting with # are ignored.
Exit 2 blocks the tool call and shows the reason to the agent; exit 0 allows it.
Seat identity comes from TEAM_SEAT, which subagents inherit: run No. 1 in its own session.
Does not see shell commands: restrict Bash separately for seats that must not write locked files."""
import json, os, sys, fnmatch, pathlib

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path") or (data.get("tool_input") or {}).get("notebook_path")
if not path:
    sys.exit(0)
root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
locked = root / ".team" / "locked.txt"
if not locked.exists():
    sys.exit(0)
target = pathlib.Path(path)
target = (target if target.is_absolute() else root / target).resolve()
try:
    rel = target.relative_to(root).as_posix()
except ValueError:
    sys.exit(0)
patterns = [l.strip() for l in locked.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
# No. 1 (TEAM_SEAT=1) is the sole writer of the bank and the locked files; the lock list itself is locked for everyone
seat = os.environ.get("TEAM_SEAT", "").replace("No.", "").strip()
if seat == "1":
    patterns = []
for p in patterns + [".team/locked.txt"]:
    if fnmatch.fnmatch(rel, p) or rel == p.rstrip("/") or rel.startswith(p.rstrip("/*") + "/") and p.endswith(("/", "/**")):
        print(f"Blocked: {rel} is locked (pattern '{p}'). The attack only submits; ask No. 1.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
