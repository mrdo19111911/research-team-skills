"""Record a connection found by a far-analogy card in data/found.yaml (read by find_path.py).
Run it after every card, whatever the kill test said: live connections grow the graph, dead ones stop
the next agent from proposing them again.
Usage:
  python scripts/add_connection.py --name "<usual name>" --a "<world A>" --b "<world B>" \
      --map "obj A = obj B; op A = op B" --breaks "<where it fails>" --small-test alive|dead|"not run" \
      [--hyp ...] [--motif ...] [--source ... (default none)] [--status heuristic|conjecture|conditional] \
      [--problem "<obstacle or campaign>"] [--card <path>] [--new-node]
  python scripts/add_connection.py --update F003 [--small-test ...] [--source ...] [--source-checked exists|content-matches] [--note ...]
  python scripts/add_connection.py --list
New edges never get status "theorem": only the user upgrades an edge (edit the file by hand).
World names should match existing nodes exactly (that is what joins the graph); an unknown name is refused
with the closest existing names, unless --new-node is given.
The same pair of worlds with the same name is not added twice: the existing entry gets a new line in `seen`.
Data file: data/found.yaml next to this script's skill, or env FOUND=<file>."""
import argparse, datetime, glob, os, re, sys, unicodedata
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOUND = os.environ.get("FOUND") or os.path.join(ROOT, "data", "found.yaml")
STATUSES = ["conditional", "heuristic", "conjecture"]
TESTS = ["alive", "dead", "not run"]


def norm(s):
    s = unicodedata.normalize("NFD", str(s)).replace("đ", "d").replace("Đ", "d")
    return re.sub(r"[^a-z0-9*]+", "", "".join(c for c in s if unicodedata.category(c) != "Mn").lower())


def load(path):
    if not os.path.exists(path):
        return []
    return yaml.safe_load(open(path, encoding="utf-8")) or []


def save(edges):
    head = ("# Connections found by far-analogy cards (written by scripts/add_connection.py; append-only).\n"
            "# small_test: alive | dead | not run. Dead edges are kept on record and skipped by find_path.py.\n"
            "# status is never theorem here unless the user changed it by hand.\n")
    tmp = FOUND + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(head)
        yaml.safe_dump(edges, f, allow_unicode=True, sort_keys=False, width=110)
    os.replace(tmp, FOUND)


def nodes():
    names = {}
    files = [f for f in glob.glob(os.path.join(ROOT, "data", "*.yaml")) if not f.endswith("families.yaml")]
    if os.path.abspath(FOUND) not in map(os.path.abspath, files):
        files.append(FOUND)
    for f in files:
        for e in load(f):
            for k in ("a", "b"):
                if e.get(k):
                    names.setdefault(norm(e[k]), e[k])
    return names


def today():
    return datetime.date.today().isoformat()


def add(args):
    edges = load(FOUND)
    known = nodes()
    for w in (args.a, args.b):
        if norm(w) not in known and not args.new_node:
            k = norm(w)
            near = [v for t, v in known.items() if k[:6] and k[:6] in t][:8]
            sys.exit(f"Unknown world '{w}'. Reuse an existing node name"
                     + (f", e.g. {near}" if near else "") + " (find_path.py --find <kw>), or pass --new-node.")
    a = known.get(norm(args.a), args.a)
    b = known.get(norm(args.b), args.b)
    seen = {"date": today(), "small_test": args.small_test}
    if args.problem:
        seen["problem"] = args.problem
    if args.card:
        seen["card"] = args.card
    pair = {norm(a), norm(b)}
    for e in edges:
        if {norm(e["a"]), norm(e["b"])} == pair and norm(e["name"]) == norm(args.name):
            e.setdefault("seen", []).append(seen)
            e["small_test"] = args.small_test
            save(edges)
            print(f"updated {e['id']} (already recorded; seen {len(e['seen'])} times, small_test now {args.small_test})")
            return
    n = max([int(e["id"][1:]) for e in edges if re.fullmatch(r"F\d+", str(e.get("id", "")))] or [0]) + 1
    mp = [[x.strip() for x in pair_.split("=", 1)] for pair_ in args.map.split(";") if "=" in pair_]
    if not mp:
        sys.exit("--map needs at least one 'object in A = object in B' pair (relations or operations, not attributes).")
    e = {"id": f"F{n:03d}", "name": args.name, "a": a, "b": b, "status": args.status}
    if args.hyp:
        e["hyp"] = args.hyp
    e.update({"map": mp, "breaks": args.breaks})
    if args.motif:
        e["motif"] = args.motif
    e.update({"source": args.source, "source_checked": "no", "small_test": args.small_test,
              "found": today(), "seen": [seen]})
    edges.append(e)
    save(edges)
    print(f"added {e['id']}: {a} <-> {b} ({args.status}, small test {args.small_test})")


def update(args):
    edges = load(FOUND)
    for e in edges:
        if e["id"] == args.update:
            log = {"date": today()}
            if args.small_test:
                e["small_test"] = log["small_test"] = args.small_test
            if args.source:
                e["source"] = log["source"] = args.source
                e["source_checked"] = "no"
            if args.source_checked:
                e["source_checked"] = log["source_checked"] = args.source_checked
            if args.note:
                log["note"] = args.note
            e.setdefault("seen", []).append(log)
            save(edges)
            print(f"updated {e['id']}")
            return
    sys.exit(f"No edge {args.update} in {FOUND}.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--name"); p.add_argument("--a"); p.add_argument("--b")
    p.add_argument("--map"); p.add_argument("--breaks"); p.add_argument("--hyp"); p.add_argument("--motif")
    p.add_argument("--source"); p.add_argument("--status", default="heuristic", choices=STATUSES)
    p.add_argument("--small-test", choices=TESTS); p.add_argument("--problem"); p.add_argument("--card")
    p.add_argument("--new-node", action="store_true")
    p.add_argument("--update"); p.add_argument("--source-checked", choices=["exists", "content-matches"])
    p.add_argument("--note"); p.add_argument("--list", action="store_true")
    args = p.parse_args()
    if args.list:
        for e in load(FOUND):
            print(f"{e['id']} {e['name']}: {e['a']} <-> {e['b']} ({e['status']}, small test {e.get('small_test')}, "
                  f"seen {len(e.get('seen', []))})")
        return
    if args.update:
        return update(args)
    missing = [k for k in ("name", "a", "b", "map", "breaks", "small_test") if not getattr(args, k)]
    if missing:
        sys.exit("Missing: " + ", ".join("--" + m.replace("_", "-") for m in missing)
                 + ". A connection without its map, its breaks and its kill-test result is not recorded.")
    args.source = args.source or "none"
    add(args)


if __name__ == "__main__":
    main()
