"""Verify arXiv citations against the arXiv API (needs internet access to export.arxiv.org).
Usage: python scripts/check_arxiv.py data/graph_vi.yaml [sample_size=all] > report.tsv
For each edge citing an arXiv id: fetch title/authors, compare with the surname(s) in the citation.
Output columns: id, arxiv_id, verdict (exists+authors-match / exists-authors-differ / not-found), title.
'exists' is not 'content-matches': a human still checks that the paper states the correspondence."""
import sys, re, time, random, yaml, urllib.request, xml.etree.ElementTree as ET
E = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
RX = re.compile(r"(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})")
rows = [(e["id"], m.group(1), str(e.get("source") or e.get("nguon") or ""))
        for e in E for m in [RX.search(str(e.get("source") or e.get("nguon") or ""))] if m]
if len(sys.argv) > 2: random.seed(0); rows = random.sample(rows, min(int(sys.argv[2]), len(rows)))
NS = {"a": "http://www.w3.org/2005/Atom"}
for i in range(0, len(rows), 50):
    batch = rows[i:i + 50]
    url = "http://export.arxiv.org/api/query?max_results=100&id_list=" + ",".join(r[1] for r in batch)
    root = ET.fromstring(urllib.request.urlopen(url, timeout=60).read())
    found = {}
    for en in root.findall("a:entry", NS):
        aid = re.sub(r"v\d+$", "", en.find("a:id", NS).text.split("/abs/")[-1])
        found[aid] = (" ".join(en.find("a:title", NS).text.split()), [x.find("a:name", NS).text for x in en.findall("a:author", NS)])
    for eid, aid, cit in batch:
        if aid not in found or not found[aid][0] or found[aid][0].lower() == "error": print(f"{eid}\t{aid}\tnot-found\t"); continue
        title, authors = found[aid]
        sur = {a.split()[-1].lower() for a in authors}
        ok = any(s in cit.lower() for s in sur)
        print(f"{eid}\t{aid}\t{'exists+authors-match' if ok else 'exists-authors-differ'}\t{title}")
    time.sleep(3)
