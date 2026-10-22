"""PreToolUse hook: sealed verdicts ("judge independently, before seeing any other verdict").
Verdicts: <project>/.team/verdicts/<submission-id>/<seat>.md ; the file SEALED in that directory means all are filed.
The seat is env TEAM_SEAT ("2", "3", "6", "3b" ...; "No. 2" is read as "2"). Unset -> seat "unknown", owns no file.
While a submission directory has no SEALED file:
  - Read/NotebookRead/Edit/Write/MultiEdit/NotebookEdit of another seat's verdict -> blocked; own verdict -> allowed.
  - Grep inside the directory, or over an ancestor that would search other seats' verdicts -> blocked.
  - Glob inside the directory -> allowed only for No. 6 (file names = "submitted / not yet").
  - Bash: best-effort string check of the command for paths under .team/verdicts/.
After SEALED: reads are allowed; edits of any verdict file are blocked (sealed = immutable).
SEALED itself may be created through Edit/Write only by No. 6 or No. 1.
Fail closed: unparseable input or an internal error blocks the call if it mentions "verdicts", otherwise allows it.
Exit 2 blocks the tool call and shows the reason to the agent; exit 0 allows it."""
import json, os, re, sys, fnmatch, pathlib

READ_TOOLS = {"Read", "NotebookRead"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SEALERS = {"6", "1"}
LIST_CMDS = {"ls", "dir", "gci", "get-childitem", "test", "[", "tree"}
WRITE_TOKENS = re.compile(r"(>|\btouch\b|\bnew-item\b|\bset-content\b|\bout-file\b|\badd-content\b|\bcp\b|\bmv\b|\bcopy\b|\bmove\b|\btee\b|\brm\b|\bdel\b|\bremove-item\b)", re.I)


def block(msg):
    print(f"Blocked (sealed verdicts): {msg}", file=sys.stderr)
    sys.exit(2)


def norm_seat(s):
    s = (s or "").strip().lower()
    s = re.sub(r"^no\.?\s*", "", s)
    return re.sub(r"\s+", "", s) or "unknown"


SEAT = norm_seat(os.environ.get("TEAM_SEAT") or "unknown")


def sealed(d):
    return (d / "SEALED").exists()


def others(d):
    """Verdict files in d not owned by SEAT."""
    try:
        return [p for p in d.iterdir() if p.is_file() and p.suffix.lower() == ".md" and norm_seat(p.stem) != SEAT]
    except OSError:
        return []


def rel_parts(root, path):
    """Path as lower-case parts relative to root, or None if outside root."""
    p = pathlib.Path(path)
    p = (p if p.is_absolute() else root / p).resolve()
    try:
        return [x.lower() for x in p.relative_to(root).parts]
    except ValueError:
        return None


def unsealed_dirs(vroot):
    try:
        return [d for d in vroot.iterdir() if d.is_dir() and not sealed(d)]
    except OSError:
        return []


def check_file(root, vroot, parts, tool):
    """parts: relative parts of a path. Decide Read/Edit on it."""
    if parts[:2] != [".team", "verdicts"] or len(parts) < 3:
        return
    d = vroot / parts[2]
    if len(parts) == 3:  # the submission directory itself
        if tool in READ_TOOLS and not sealed(d):
            block(f"{parts[2]} is not sealed; only No. 6 may list it (Glob), nobody reads it.")
        return
    name = parts[-1]
    if name == "sealed":
        if tool in EDIT_TOOLS and SEAT not in SEALERS:
            block("only No. 6 or No. 1 may create SEALED.")
        return
    own = len(parts) == 4 and norm_seat(pathlib.PurePath(name).stem) == SEAT and name.endswith(".md")
    if sealed(d):
        if tool in EDIT_TOOLS:
            block(f"submission {parts[2]} is sealed; verdicts are immutable (append a correction elsewhere).")
        return
    if not own:
        block(f"submission {parts[2]} is not sealed yet; seat {SEAT} may touch only its own verdict "
              f".team/verdicts/{parts[2]}/{SEAT}.md. Wait for SEALED.")


def check_grep(root, vroot, ti):
    target = ti.get("path") or str(root)
    parts = rel_parts(root, target)
    if parts is None:
        return
    if parts[:2] == [".team", "verdicts"] and len(parts) >= 3:
        if len(parts) >= 4:
            return check_file(root, vroot, parts, "Read")
        if not sealed(vroot / parts[2]):
            block(f"submission {parts[2]} is not sealed; do not search it.")
        return
    if parts != [".team", "verdicts"][:len(parts)]:
        return  # unrelated directory, not an ancestor of .team/verdicts
    gl, typ = ti.get("glob"), (ti.get("type") or "").lower()
    if typ and typ not in ("md", "markdown"):
        return
    for d in unsealed_dirs(vroot):
        for f in others(d):
            rel = f.relative_to(root).as_posix()
            if not gl or any(fnmatch.fnmatch(x, g) for x in (f.name, rel) for g in re.split(r"[ ,]", gl.strip("{}")) if g):
                block(f"this search would read unsealed verdicts in .team/verdicts/{d.name}/. "
                      f"Narrow 'path' or add a 'glob' that excludes .team/verdicts.")


def check_glob(root, vroot, ti):
    base = ti.get("path") or str(root)
    pat = (ti.get("pattern") or "").replace("\\", "/")
    joined = pat if pathlib.PurePath(pat).is_absolute() else base.rstrip("/\\") + "/" + pat
    # literal prefix of the pattern, before the first wildcard
    lit = re.split(r"[*?\[{]", joined.replace("\\", "/"))[0]
    parts = rel_parts(root, lit or base)
    if parts is None or parts[:2] != [".team", "verdicts"] or len(parts) < 3:
        return
    d = vroot / parts[2]
    if not sealed(d) and SEAT != "6":
        block(f"submission {parts[2]} is not sealed; only No. 6 may list it.")


PATH_RE = re.compile(r"\.team[\\/]+verdicts(?:[\\/]+([^\s\\/'\"`;|&<>)]*))?(?:[\\/]+([^\s'\"`;|&<>)]*))?", re.I)


def check_bash(root, vroot, cmd):
    hits = list(PATH_RE.finditer(cmd))
    if not hits:
        return
    first = (cmd.strip().split() or [""])[0].lower()
    listing = first in LIST_CMDS and not re.search(r"[;&|`$]", cmd)
    for m in hits:
        sid, rest = (m.group(1) or ""), (m.group(2) or "").replace("\\", "/").strip("/")
        dirs = [d for d in unsealed_dirs(vroot) if not sid or fnmatch.fnmatch(d.name.lower(), sid.lower())]
        for d in dirs:
            if rest.lower() == "sealed":
                if WRITE_TOKENS.search(cmd) and SEAT not in SEALERS:
                    block("only No. 6 or No. 1 may create SEALED.")
                continue
            if rest and "/" not in rest and norm_seat(pathlib.PurePath(rest).stem) == SEAT \
                    and not re.search(r"[*?\[]", rest):
                continue  # own verdict
            if not rest and listing and SEAT == "6":
                continue  # No. 6 lists "submitted / not yet"
            block(f"command touches unsealed .team/verdicts/{d.name}/ (seat {SEAT}). "
                  f"Only your own file {SEAT}.md is allowed until SEALED; No. 6 may only 'ls' the directory. "
                  f"(String check; rephrase only if the command does not read other verdicts.)")
        if sid and rest and not re.search(r"[*?\[]", sid):
            d = vroot / sid
            if d.is_dir() and sealed(d) and rest.lower().endswith(".md") and WRITE_TOKENS.search(cmd):
                block(f"submission {sid} is sealed; verdicts are immutable.")


def main(data):
    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}
    root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    vroot = root / ".team" / "verdicts"
    if not vroot.is_dir():
        return
    if tool in READ_TOOLS | EDIT_TOOLS:
        path = ti.get("file_path") or ti.get("notebook_path")
        if path:
            parts = rel_parts(root, path)
            if parts is not None:
                check_file(root, vroot, parts, tool)
    elif tool == "Grep":
        check_grep(root, vroot, ti)
    elif tool == "Glob":
        check_glob(root, vroot, ti)
    elif tool == "Bash" or tool == "PowerShell":
        check_bash(root, vroot, ti.get("command") or "")


if __name__ == "__main__":
    raw = sys.stdin.read()
    try:
        main(json.loads(raw))
    except SystemExit:
        raise
    except Exception as e:  # fail closed only when the call is about verdicts
        if "verdicts" in raw.lower():
            block(f"hook could not check this call ({type(e).__name__}); refusing because it mentions verdicts.")
    sys.exit(0)
