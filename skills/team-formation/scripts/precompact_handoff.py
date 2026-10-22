"""PreCompact hook: write a handoff note before context compaction (references/substitution.md, trigger 1).
Writes <project>/.team/handoff/<seat>-<YYYYmmdd-HHMMSS>.md in the handoff template of references/templates.md.
The seat is env TEAM_SEAT (default "unknown"). A hook cannot ask the model, so the note is a skeleton filled
mechanically from the transcript (hook input "transcript_path", JSONL): recent messages, recent tool calls
(errors flagged), files edited and files read. STUCK AT / DO NOT RETRY / NEXT STEP are left for the bench agent.
Never blocks compaction: every error is caught and the hook exits 0."""
import json, os, re, sys, datetime, pathlib, collections

N_MSG, N_TOOLS, CLIP = 8, 20, 400
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "NotebookRead"}


def clip(s, n=CLIP):
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= n else s[: n - 3] + "..."


def summarize_input(name, ti):
    if not isinstance(ti, dict):
        return clip(ti, 160)
    for k in ("file_path", "notebook_path", "command", "pattern", "path", "url", "description", "prompt"):
        if ti.get(k):
            return clip(f"{k}={ti[k]}", 160)
    return clip(json.dumps(ti, ensure_ascii=False), 160)


def parse_transcript(path):
    msgs = collections.deque(maxlen=N_MSG)
    tools = collections.deque(maxlen=N_TOOLS)
    edited, read = [], []
    by_id = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not isinstance(e, dict):
                continue
            m = e.get("message") if isinstance(e.get("message"), dict) else {}
            role = m.get("role") or e.get("type")
            content = m.get("content")
            if isinstance(content, str):
                if role in ("user", "assistant") and content.strip():
                    msgs.append((role, clip(content)))
                continue
            if not isinstance(content, list):
                continue
            for b in content:
                if not isinstance(b, dict):
                    continue
                t = b.get("type")
                if t == "text" and role in ("user", "assistant") and (b.get("text") or "").strip():
                    msgs.append((role, clip(b["text"])))
                elif t == "tool_use":
                    name, ti = b.get("name") or "?", b.get("input") or {}
                    rec = {"name": name, "input": summarize_input(name, ti), "error": False}
                    tools.append(rec)
                    if b.get("id"):
                        by_id[b["id"]] = rec
                    fp = isinstance(ti, dict) and (ti.get("file_path") or ti.get("notebook_path"))
                    if fp:
                        lst = edited if name in EDIT_TOOLS else read if name in READ_TOOLS else None
                        if lst is not None and fp not in lst:
                            lst.append(fp)
                elif t == "tool_result" and b.get("is_error"):
                    rec = by_id.get(b.get("tool_use_id"))
                    if rec:
                        rec["error"] = True
                        rec["result"] = clip(b.get("content"), 160)
    return list(msgs), list(tools), edited, read


def render(seat, data, parsed, err):
    now = datetime.datetime.now().isoformat(timespec="seconds")
    msgs, tools, edited, read = parsed
    last_user = next((t for r, t in reversed(msgs) if r == "user"), "")
    last_asst = next((t for r, t in reversed(msgs) if r == "assistant"), "")
    L = [f"# Handoff note (automatic, PreCompact) - seat {seat} - {now}",
         f"session: {data.get('session_id', '?')} | trigger: {data.get('trigger', '?')} | "
         f"transcript: {data.get('transcript_path', '?')}"]
    if err:
        L.append(f"NOTE: transcript not parsed ({err}); fields below are empty skeletons.")
    L += ["", "Template: SEAT: | DOING: | TRIED (and result): | STUCK AT: | DO NOT RETRY: | NEXT STEP I WOULD TAKE: | FILES:",
          "", f"SEAT: {seat}", "",
          "DOING: (mechanical guess: last request and last reply)",
          f"- last user message: {last_user or '(none found)'}",
          f"- last assistant message: {last_asst or '(none found)'}", "",
          f"TRIED (and result): last {len(tools)} tool calls, oldest first; ERROR = tool reported an error"]
    L += [f"- {t['name']}: {t['input']}" + (f"  -> ERROR: {t.get('result', '')}" if t["error"] else "") for t in tools] or ["- (none found)"]
    L += ["", "STUCK AT: fill in: where stuck (bench agent: read the messages below and the board)", "",
          "DO NOT RETRY: fill in (check the tabu log; tool calls marked ERROR above are candidates)", "",
          "NEXT STEP I WOULD TAKE: fill in: next step", "",
          "FILES:", "- edited (Edit/Write/MultiEdit/NotebookEdit):"]
    L += [f"  - {p}" for p in edited] or ["  - (none)"]
    L += ["- read:"] + ([f"  - {p}" for p in read[-30:]] or ["  - (none)"])
    L += ["", f"RECENT MESSAGES (last {len(msgs)}, clipped to {CLIP} chars):"]
    L += [f"- [{r}] {t}" for r, t in msgs] or ["- (none found)"]
    return "\n".join(L) + "\n"


def main():
    data, err = {}, None
    try:
        data = json.loads(sys.stdin.read() or "{}")
        if not isinstance(data, dict):
            data = {}
    except Exception as e:
        err = f"bad hook input: {type(e).__name__}"
    seat = os.environ.get("TEAM_SEAT") or "unknown"
    parsed = ([], [], [], [])
    tp = data.get("transcript_path")
    if not err:
        try:
            if not tp:
                err = "no transcript_path in hook input"
            else:
                parsed = parse_transcript(os.path.expanduser(tp))
        except Exception as e:
            err = f"{type(e).__name__}: {clip(e, 120)}"
    root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")
    out_dir = root / ".team" / "handoff"
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{re.sub(r'[^A-Za-z0-9._-]+', '_', seat)}-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    out, i = out_dir / f"{stem}.md", 1
    while out.exists():
        out, i = out_dir / f"{stem}-{i}.md", i + 1
    out.write_text(render(seat, data, parsed, err), encoding="utf-8")
    print(f"Handoff note written: {out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"precompact_handoff: could not write handoff note ({type(e).__name__}: {e})", file=sys.stderr)
    sys.exit(0)
