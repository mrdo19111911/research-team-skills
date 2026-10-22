"""Find paths in the dictionary graph and compose status and hypotheses.
Usage:
  python scripts/find_path.py "<start>" "<goal>" [maxlen=4]      # correspondences only
  python scripts/find_path.py --families "<start>" "<goal>" [maxlen=4]  # also hop through families
  python scripts/find_path.py --edges "<node>"     python scripts/find_path.py --find "<keyword>"
  python scripts/find_path.py --family-of "<node>" python scripts/find_path.py --stats
Data: every *.yaml in data/ except families.yaml (or env GRAPH=file1,file2). Reads English
(name/status/hyp) and Vietnamese (ten/trang_thai/gia_thiet) schemas.
A family hop is NOT a correspondence: any path using one is downgraded to heuristic.
Edges with small_test: dead (killed connections in data/found.yaml) are skipped."""
import os, sys, re, glob, unicodedata, collections, signal, yaml
from collections import deque
if hasattr(signal, "SIGPIPE"): signal.signal(signal.SIGPIPE, signal.SIG_DFL)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = os.environ["GRAPH"].split(",") if os.environ.get("GRAPH") else \
    [f for f in sorted(glob.glob(os.path.join(ROOT, "data", "*.yaml"))) if not f.endswith("families.yaml")]
VI = {"dinh_ly": "theorem", "co_dieu_kien": "conditional", "heuristic": "heuristic", "phong_doan": "conjecture"}
ORDER = ["theorem", "conditional", "heuristic", "conjecture"]
def g(e, *k): return next((e[x] for x in k if e.get(x)), "")
E = []
for f in files:
    for e in yaml.safe_load(open(f, encoding="utf-8")) or []:
        if e.get("small_test") == "dead": continue  # killed connections are kept on record, never used as paths
        st = g(e, "status", "trang_thai"); E.append(dict(id=e["id"], name=g(e, "name", "ten"), a=e["a"], b=e["b"],
            status=VI.get(st, st) if VI.get(st, st) in ORDER else "heuristic", hyp=g(e, "hyp", "gia_thiet")))
FP = os.path.join(ROOT, "data", "families.yaml")
FAM = yaml.safe_load(open(FP, encoding="utf-8")) if os.path.exists(FP) else []
def norm(s):
    s = unicodedata.normalize("NFD", str(s)).replace("đ", "d").replace("Đ", "d")
    return re.sub(r"[^a-z0-9*]+", "", "".join(c for c in s if unicodedata.category(c) != "Mn").lower())
def families(name):
    p = " " + re.sub(r"\s+", " ", name.lower()) + " "
    return [h["family"] for h in FAM if any((k in p) if len(k) > 4 else
            re.search(r"(?<![\wà-ỹ])" + re.escape(k.strip()) + r"(?![\wà-ỹ])", p) for k in h["keywords"])]
adj, label = collections.defaultdict(list), {}
for e in E:
    for x, y in ((e["a"], e["b"]), (e["b"], e["a"])):
        adj[norm(x)].append((norm(y), e)); label[norm(x)] = x
members = collections.defaultdict(list)
for k, t in label.items():
    for h in families(t): members[h].append(k)
def resolve(q):
    k = norm(q)
    if k in label: return k
    near = [label[t] for t in label if k in t][:8]
    sys.exit(f"No node '{q}'." + (f" Closest: {near}" if near else " Use --find."))
def search(start, goal, maxlen, fam):
    q, out = deque([(start, [])]), []
    while q and len(out) < 50:
        n, p = q.popleft()
        if n == goal and p:
            if sum(x[0] == "E" for x in p) >= sum(x[0] == "F" for x in p): out.append(p)
            continue
        if sum(2 if x[0] == "F" else 1 for x in p) >= maxlen: continue
        seen = {start} | {x[2] for x in p}
        for s, e in adj.get(n, []):
            if s not in seen: q.append((s, p + [("E", e, s)]))
        if fam and not (p and p[-1][0] == "F"):
            for h in families(label[n]):
                for s in members[h]:
                    if s not in seen and s != n: q.append((s, p + [("F", h, s)]))
    return out
def level(p):
    m = max([ORDER.index(x[1]["status"]) for x in p if x[0] == "E"] or [0])
    return max(m, 2) if any(x[0] == "F" for x in p) else m
if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "--find":
        k = norm(a[1]); print("\n".join(v for t, v in sorted(label.items()) if k in t) or "(none)")
    elif a[0] == "--edges":
        for s, e in adj.get(resolve(a[1]), []): print(f"{e['id']} {e['name']} ({e['status']}) -> {label[s]}")
    elif a[0] == "--family-of":
        print(families(label[resolve(a[1])]) or "(no family)")
    elif a[0] == "--stats":
        par = {}
        def f(x):
            par.setdefault(x, x)
            while par[x] != x: par[x] = par[par[x]]; x = par[x]
            return x
        for e in E: par[f(norm(e["a"]))] = f(norm(e["b"]))
        c = sorted(collections.Counter(f(k) for k in label).values(), reverse=True)
        print(f"{len(E)} edges from {len(files)} files, {len(label)} nodes, {len(c)} components "
              f"(largest {c[:3]}); nodes in a family: {sum(1 for t in label.values() if families(t))}")
        print(dict(collections.Counter(e["status"] for e in E)))
    else:
        fam = a[0] == "--families"; a = a[1:] if fam else a
        s, t, n = resolve(a[0]), resolve(a[1]), int(a[2]) if len(a) > 2 else 4
        ps = search(s, t, n, fam)
        if not ps and not fam:
            print("No path through correspondences only. Retrying with family hops (heuristic)...")
            ps = search(s, t, n + 2, True)
        ps.sort(key=lambda p: (level(p), sum(x[0] == "F" for x in p), len(p)))
        print(f"{len(ps)} paths (most certain first).")
        for p in ps[:8]:
            print(f"\nWhole path: {ORDER[level(p)]}"); cur = label[s]
            for x in p:
                if x[0] == "E":
                    e = x[1]; h = f"\n      hyp: {e['hyp']}" if e["hyp"] else ""
                    print(f"  {cur} --[{e['id']} {e['name']}, {e['status']}]--> {label[x[2]]}{h}")
                else: print(f"  {cur} ~~[same family: {x[1]}]~~> {label[x[2]]}")
                cur = label[x[2]]
