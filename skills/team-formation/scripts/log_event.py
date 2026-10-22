"""Match log: append one event per line to <campaign>/.team/events.jsonl (append-only; read by view_match.py).

Two ways in.
1. Hook (no arguments; Claude Code passes the hook input as JSON on stdin). Register it for PostToolUse on
   Read|Write|Edit|MultiEdit|NotebookEdit and for Stop / SubagentStop. It records, with the seat from TEAM_SEAT:
     read  - a file inside the campaign was read      write - a file inside the campaign was written
     stop  - the agent ended its turn
   Files outside the campaign, and .team/events.jsonl itself, are ignored. Never blocks: always exits 0.
2. Orchestrator CLI (the reliable source for who runs when, and for agents the hooks cannot see):
     log_event.py start --seat 9 [--agent ID] [--note "..."]      an agent takes the seat
     log_event.py stop  --seat 9 [--agent ID] [--note "..."]      it hands back
     log_event.py pass  --from 14 --to 9 --what "worked example"  information handed from one seat to another
     log_event.py note  --seat 6 --note "phase 0 -> 1"
   Options: --campaign DIR (default: the current directory), --time ISO (default: now; for rebuilding a past run).

Event fields: t (ISO time), kind, seat, agent, path, from, to, what, note. Seats are "1".."14", "coach", "referee".
view_match.py derives the remaining passes: a read of a file last written by another seat is a pass writer -> reader."""
import argparse, datetime, json, os, pathlib, sys


def norm_seat(s):
    s = str(s or "").strip().lower().replace("no.", "").replace("no", "").strip()
    return s or "unknown"


def campaign_root(start):
    p = pathlib.Path(start).resolve()
    for q in [p, *p.parents]:
        if (q / ".team").is_dir():
            return q
    return None


def append(root, ev):
    ev = {k: v for k, v in ev.items() if v not in (None, "")}
    with open(root / ".team" / "events.jsonl", "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


READ_TOOLS = {"Read", "NotebookRead"}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def from_hook(raw):
    data = json.loads(raw)
    root = campaign_root(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")
    if root is None:
        return
    seat = norm_seat(os.environ.get("TEAM_SEAT"))
    agent = data.get("agent_id") or data.get("session_id")
    event = data.get("hook_event_name", "")
    if event in ("Stop", "SubagentStop"):
        append(root, {"t": now(), "kind": "stop", "seat": seat, "agent": agent, "note": event})
        return
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path")
    if not path or tool not in READ_TOOLS | WRITE_TOOLS:
        return
    target = pathlib.Path(path)
    target = (target if target.is_absolute() else root / target).resolve()
    try:
        rel = target.relative_to(root).as_posix()
    except ValueError:
        return
    if rel == ".team/events.jsonl":
        return
    append(root, {"t": now(), "kind": "read" if tool in READ_TOOLS else "write", "seat": seat, "agent": agent,
                  "path": rel})


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        try:
            from_hook(sys.stdin.read())
        except Exception:
            pass
        return 0
    ap = argparse.ArgumentParser(description="Append an event to .team/events.jsonl")
    ap.add_argument("kind", choices=["start", "stop", "pass", "note"])
    ap.add_argument("--seat"); ap.add_argument("--agent")
    ap.add_argument("--from", dest="src"); ap.add_argument("--to", dest="dst"); ap.add_argument("--what")
    ap.add_argument("--note"); ap.add_argument("--time"); ap.add_argument("--campaign", default=".")
    a = ap.parse_args(argv)
    root = campaign_root(a.campaign)
    if root is None:
        sys.exit(f"no .team/ found at or above {a.campaign}")
    if a.kind == "pass":
        if not (a.src and a.dst):
            sys.exit("pass needs --from and --to")
        ev = {"from": norm_seat(a.src), "to": norm_seat(a.dst), "what": a.what}
    else:
        if not a.seat:
            sys.exit(f"{a.kind} needs --seat")
        ev = {"seat": norm_seat(a.seat), "agent": a.agent}
    if a.time:
        datetime.datetime.fromisoformat(a.time)
    append(root, {"t": a.time or now(), "kind": a.kind, **ev, "note": a.note})
    return 0


if __name__ == "__main__":
    sys.exit(main())
