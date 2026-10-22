"""Match viewer: replay .team/events.jsonl on the pitch as a self-contained HTML page.
A seat glows while its agent is running (start -> stop); a ball flies from seat A to seat B when information passes
(explicit "pass" events, plus derived ones: a read of a file last written by another seat).
Usage:  python view_match.py [<campaign-dir>] [-o match.html] [--title "..."]      one replay, written once
        python view_match.py [<campaign-dir>] --live [--port 8765]                   live view while the team plays
Writes <campaign>/.team/match.html by default; open it in a browser. --live serves .team/ on
http://127.0.0.1:<port>/match.html and rebuilds the data every 2 s, so the page follows the match as events arrive
(seats glow while running, open spells run up to now). Python 3 standard library only."""
import argparse, datetime, html, json, pathlib, sys

# position in metres on a 105 x 68 pitch, attacking to the right (as on the formation slide), role colour, wing?
SEATS = {
    "1": ("Final verifier", 6, 34, "#A86C0E", False), "3": ("Novelty", 20, 19, "#C93A2A", False),
    "2": ("Proof-checker", 20, 49, "#C93A2A", False), "6": ("Coordinator", 34, 34, "#1C2333", False),
    "11": ("Adjacent field", 50, 10, "#2B59D9", True), "10": ("In-field", 50, 34, "#2B59D9", False),
    "7": ("Far field", 50, 58, "#2B59D9", False), "8": ("Blueprint", 65, 34, "#2B59D9", False),
    "14": ("Examples", 83, 13, "#2B59D9", False), "9": ("Prover", 87, 34, "#2B59D9", False),
    "4": ("Breaker", 83, 55, "#C93A2A", False),
    "coach": ("Coach", 40, -7, "#5B6472", False), "referee": ("Referee", 70, -7, "#5B6472", False),
}
PASS_WINDOW = 60  # seconds: the same (from, to, path) read again within this window is one pass


def parse_t(s):
    return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00")).replace(tzinfo=None)


def load(path):
    evs = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
            e["_t"] = parse_t(e["t"])
            evs.append(e)
        except (ValueError, KeyError):
            print(f"skipped bad line {n}", file=sys.stderr)
    evs.sort(key=lambda e: e["_t"])
    return evs


def derive(evs, now=None):
    """Return (intervals, passes, log). Times in seconds from the first event; open spells end at `now` if given."""
    t0 = evs[0]["_t"]
    sec = lambda e: (e["_t"] - t0).total_seconds()
    end = max(sec(evs[-1]), (now - t0).total_seconds() if now else 0)
    open_, intervals, passes, log, last_writer, seen = {}, [], [], [], {}, {}
    for e in evs:
        s, k, seat = sec(e), e.get("kind"), str(e.get("seat", ""))
        if k == "start":
            open_[(seat, e.get("agent", ""))] = (s, e.get("note", ""), e.get("agent", ""))
        elif k == "stop":
            key = (seat, e.get("agent", ""))
            if key not in open_:  # stop without agent id: close the seat's oldest open spell
                key = next((q for q in open_ if q[0] == seat), None)
            if key in open_:
                st, note, agent = open_.pop(key)
                intervals.append({"seat": seat, "a": st, "b": s, "note": note, "agent": agent or e.get("agent", "")})
            else:  # a stop with no start (hook only): a short burst of activity
                intervals.append({"seat": seat, "a": max(0, s - 30), "b": s, "note": "", "agent": e.get("agent", "")})
        elif k in ("read", "write") and e.get("path"):
            p = e["path"]
            if k == "write":
                last_writer[p] = seat
                if not any(q[0] == seat for q in open_):
                    intervals.append({"seat": seat, "a": max(0, s - 5), "b": s + 5, "note": "", "agent": e.get("agent", "")})
            elif p in last_writer and last_writer[p] != seat:
                key = (last_writer[p], seat, p)
                if s - seen.get(key, -1e9) > PASS_WINDOW:
                    passes.append({"from": last_writer[p], "to": seat, "t": s, "what": p.split("/")[-1]})
                seen[key] = s
        elif k == "pass":
            passes.append({"from": str(e.get("from")), "to": str(e.get("to")), "t": s, "what": e.get("what", "")})
        label = {"start": "starts", "stop": "hands back", "read": "reads", "write": "writes", "pass": "passes",
                 "note": "note"}.get(k, k)
        who = f"{e.get('from')} → {e.get('to')}" if k == "pass" else f"No. {seat}" if seat.isdigit() else seat
        detail = e.get("what") or e.get("path") or e.get("note") or ""
        log.append({"t": s, "clock": e["_t"].strftime("%H:%M:%S"), "text": f"{who} {label} {detail}".strip()})
    for (seat, _), (st, note, agent) in open_.items():
        intervals.append({"seat": seat, "a": st, "b": end, "note": note, "agent": agent})
    return t0, end, intervals, passes, log


BUSY = 0.6  # a seat busy more than this share of the match is a candidate for a second agent next time


def load_table(intervals, passes, end):
    """Workload per seat: busy time (union of its spells), spells, distinct agents, passes received and sent."""
    rows = {}
    for x in sorted(intervals, key=lambda x: x["a"]):
        r = rows.setdefault(x["seat"], {"seat": x["seat"], "busy": 0.0, "spells": 0, "agents": set(), "in": 0,
                                        "out": 0, "_hi": -1.0})
        r["spells"] += 1
        if x.get("agent"):
            r["agents"].add(x["agent"])
        a, b = max(x["a"], r["_hi"]), x["b"]
        if b > a:
            r["busy"] += b - a
        r["_hi"] = max(r["_hi"], b)
    for p in passes:
        for k, s in (("out", p["from"]), ("in", p["to"])):
            rows.setdefault(s, {"seat": s, "busy": 0.0, "spells": 0, "agents": set(), "in": 0, "out": 0, "_hi": -1.0})
            rows[s][k] += 1
    out = []
    for r in rows.values():
        share = r["busy"] / end if end > 0 else 0.0
        out.append({"seat": r["seat"], "busy": round(r["busy"]), "share": round(share, 3), "spells": r["spells"],
                    "agents": max(1, len(r["agents"])) if r["spells"] else 0, "in": r["in"], "out": r["out"],
                    "hot": share > BUSY})
    return sorted(out, key=lambda r: -r["busy"])


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#f6f7f9;--ink:#1c2333;--muted:#5b6472;--panel:#fff;--line:#d9dde3}
@media (prefers-color-scheme:dark){:root{--bg:#12151b;--ink:#e8ebf0;--muted:#9aa3b2;--panel:#1b2029;--line:#2c3340}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,Segoe UI,Arial,sans-serif}
main{max-width:1180px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:0 0 4px}.sub{color:var(--muted);margin:0 0 12px}
.wrap{display:grid;grid-template-columns:1fr 300px;gap:14px}@media(max-width:860px){.wrap{grid-template-columns:1fr}}
svg{width:100%;height:auto;display:block;border-radius:10px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px}
.ctrl{display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap}
button,select{font:inherit;padding:5px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);cursor:pointer}
input[type=range]{flex:1;min-width:160px}
#live.on{background:#C93A2A;color:#fff;border-color:#C93A2A}#clock{font-variant-numeric:tabular-nums;font-weight:600;min-width:76px}
#log{list-style:none;margin:0;padding:0;max-height:520px;overflow:auto;font-size:13px}
#log li{padding:3px 0;border-bottom:1px solid var(--line);color:var(--muted)}#log li.on{color:var(--ink);font-weight:600}
#load{width:100%;border-collapse:collapse;margin-top:8px;font-size:13px}#load th,#load td{text-align:left;padding:4px 6px;border-bottom:1px solid var(--line)}
#load .bar{height:12px;border-radius:6px;background:#2B59D9;display:inline-block;vertical-align:middle}#load tr.hot .bar{background:#C93A2A}
#log .c{font-variant-numeric:tabular-nums;margin-right:6px}
.player circle.body{transition:opacity .25s}.player.off{opacity:.38}
.player.on .halo{opacity:1}.halo{opacity:0;transition:opacity .25s}
.lbl{font:600 15px system-ui,Arial;fill:#fff}.num{font:700 22px system-ui,Arial;fill:#fff}
</style></head><body><main>
<h1>__TITLE__</h1><p class="sub">A seat glows while its agent runs; a ball flies when information passes. <span id="span">__SPAN__</span></p>
<div class="wrap"><div>
<svg id="pitch" viewBox="-30 -140 1110 860" role="img" aria-label="pitch replay">
<defs><filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="9" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="hl"><stop offset="0" stop-color="#fff6b0" stop-opacity=".95"/><stop offset="1" stop-color="#ffd84a" stop-opacity="0"/></radialGradient></defs>
<rect x="-30" y="-30" width="1110" height="740" fill="#2F7D3A"/>
<g id="stripes"></g>
<g fill="none" stroke="#fff" stroke-width="3">
<rect x="0" y="0" width="1050" height="680"/><line x1="525" y1="0" x2="525" y2="680"/><circle cx="525" cy="340" r="91.5"/>
<rect x="0" y="138.4" width="165" height="403.2"/><rect x="0" y="248.4" width="55" height="183.2"/>
<rect x="885" y="138.4" width="165" height="403.2"/><rect x="995" y="248.4" width="55" height="183.2"/></g>
<rect x="-16" y="303" width="16" height="73" fill="#dde3ea"/><rect x="1050" y="303" width="16" height="73" fill="#dde3ea"/>
<text x="1040" y="-48" text-anchor="end" style="font:600 18px system-ui;fill:var(--ink)">attack →</text>
<g id="trails"></g><g id="players"></g><g id="balls"></g></svg>
<div class="ctrl"><button id="play">▶ Play</button><span id="clock">00:00:00</span>
<input id="scrub" type="range" min="0" max="1000" value="0" aria-label="time">
<select id="speed" aria-label="speed"></select><button id="live" hidden>● Live</button></div></div>
<div class="panel"><b>Events</b><ul id="log"></ul></div></div>
<div class="panel" style="margin-top:14px"><b>Workload per seat</b> <span class="sub">— busy share of the match; a seat
busy most of the time (marked ▲) is where a second agent helps next time; a seat that never runs can be switched off.</span>
<table id="load"><thead><tr><th>Seat</th><th style="width:45%">Busy</th><th>Spells</th><th>Agents</th><th>Received</th><th>Sent</th></tr></thead><tbody></tbody></table></div>
</main><script>
let D=__DATA__;
const S=D.seats;let I=D.intervals, P=D.passes, L=D.log, END=Math.max(D.end,1), live=false;
const NS="http://www.w3.org/2000/svg", el=(n,a,p)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e};
const st=document.getElementById("stripes");for(let i=0;i<10;i++)el("rect",{x:i*105,y:0,width:105,height:680,fill:i%2?"#36873F":"#2F7D3A"},st);
const pos=s=>{const q=S[s];return q?[q[1]*10,q[2]*10]:[525,-90]};
const G={};
for(const s in S){const [name,x,y,col,wing]=S[s];if(!(s in S))continue;
 const g=el("g",{class:"player off",transform:`translate(${x*10},${y*10})`},document.getElementById("players"));
 el("circle",{class:"halo",r:62,fill:"url(#hl)"},g);
 el("circle",{class:"body",r:30,fill:col,stroke:"#fff","stroke-width":4,"stroke-dasharray":wing?"10 7":"none",filter:""},g);
 const t=el("text",{class:"num","text-anchor":"middle",y:8},g);t.textContent=/^\d+$/.test(s)?s:(s==="coach"?"C":"R");
 const w=Math.max(70,name.length*8.6+20);el("rect",{x:-w/2,y:38,width:w,height:26,rx:6,fill:"#1C2333","fill-opacity":.78},g);
 const lb=el("text",{class:"lbl","text-anchor":"middle",y:57},g);lb.textContent=name;
 G[s]=g;}
function markUsed(){const used=new Set([...I.map(x=>x.seat),...P.flatMap(x=>[x.from,x.to])]);for(const s in G)G[s].style.opacity=used.has(s)?"":.18}
const speeds=[10,30,60,120,300,600];const sp=document.getElementById("speed");
const auto=speeds.find(v=>END/v<=90)||600;for(const v of speeds){const o=document.createElement("option");o.value=v;o.textContent="×"+v;if(v===auto)o.selected=true;sp.appendChild(o)}
const logEl=document.getElementById("log");
function renderLog(){logEl.innerHTML="";L.forEach((e,i)=>{const li=document.createElement("li");li.innerHTML=`<span class="c">${e.clock}</span>`;li.appendChild(document.createTextNode(e.text));li.dataset.i=i;logEl.appendChild(li)})}
const BALL=()=>live?3:Math.max(4, Number(sp.value)*1.6); // seconds of match time a ball is in the air
let t=0,playing=false,last=null;const clock=document.getElementById("clock"),scrub=document.getElementById("scrub");
const t0=new Date(D.t0);
function draw(){
 for(const s in G){const on=I.some(x=>x.seat===s&&x.a<=t&&t<=x.b);G[s].classList.toggle("on",on);G[s].classList.toggle("off",!on);
  G[s].querySelector(".body").setAttribute("filter",on?"url(#glow)":"")}
 const bl=document.getElementById("balls"),tr=document.getElementById("trails");bl.innerHTML="";tr.innerHTML="";
 for(const p of P){const u=(t-p.t)/BALL();
  if(u>=-0.02&&u<=1.6){const [ax,ay]=pos(p.from),[bx,by]=pos(p.to);
   el("line",{x1:ax,y1:ay,x2:bx,y2:by,stroke:"#fff","stroke-width":3,"stroke-dasharray":"8 8",opacity:Math.max(0,.75-.45*Math.max(0,u-1))},tr);
   if(u<=1){const k=Math.max(0,u),e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2,x=ax+(bx-ax)*e,y=ay+(by-ay)*e-Math.sin(Math.PI*e)*60;
    el("circle",{cx:x,cy:y,r:13,fill:"#fff",stroke:"#111","stroke-width":3},bl);
    el("circle",{cx:x,cy:y,r:4.5,fill:"#111"},bl);
    const tx=el("text",{x:x,y:y-22,"text-anchor":"middle",style:"font:600 16px system-ui;fill:#fff;paint-order:stroke;stroke:#1c2333;stroke-width:4px"},bl);tx.textContent=p.what||""}}}
 const d=new Date(t0.getTime()+t*1000);clock.textContent=d.toTimeString().slice(0,8);scrub.value=Math.round(1000*t/END);
 let cur=-1;L.forEach((e,i)=>{if(e.t<=t)cur=i});[...logEl.children].forEach((li,i)=>li.classList.toggle("on",i===cur));
 if(cur>=0&&playing){const li=logEl.children[cur];if(li)li.scrollIntoView({block:"nearest"})}}
function frame(ts){if(!playing)return;if(last!==null)t=Math.min(END,t+(ts-last)/1000*Number(sp.value));last=ts;draw();
 if(t>=END){playing=false;document.getElementById("play").textContent="▶ Play";return}requestAnimationFrame(frame)}
document.getElementById("play").onclick=()=>{playing=!playing;document.getElementById("play").textContent=playing?"❚❚ Pause":"▶ Play";
 if(playing){if(t>=END)t=0;last=null;requestAnimationFrame(frame)}};
scrub.oninput=()=>{t=END*scrub.value/1000;draw()};
logEl.onclick=ev=>{const li=ev.target.closest("li");if(li){t=L[li.dataset.i].t;draw()}};
const fmt=s=>s>=3600?(s/3600).toFixed(1)+" h":s>=60?Math.round(s/60)+" min":s+" s";
const tb=document.querySelector("#load tbody");
function renderLoad(){tb.innerHTML="";for(const r of D.load){const tr=document.createElement("tr");if(r.hot)tr.className="hot";
 const nm=(S[r.seat]||[r.seat])[0];
 tr.innerHTML=`<td>${/^\d+$/.test(r.seat)?"No. "+r.seat:r.seat} · ${nm}${r.hot?" ▲":""}</td><td><span class="bar" style="width:${Math.max(2,r.share*85)}%"></span> ${fmt(r.busy)} (${Math.round(r.share*100)}%)</td><td>${r.spells}</td><td>${r.agents}</td><td>${r.in}</td><td>${r.out}</td>`;
 tr.onclick=()=>{const x=I.find(v=>v.seat===r.seat);if(x){t=x.a;draw()}};tb.appendChild(tr)}}
let fetched=Date.now();
function apply(nd){D=nd;I=nd.intervals;P=nd.passes;L=nd.log;END=Math.max(nd.end,1);fetched=Date.now();markUsed();renderLog();renderLoad();
 if(nd.span)document.getElementById("span").textContent=nd.span;if(live)t=END;draw()}
apply(D);
// live mode (view_match.py --live serves the page over http): poll the data file, follow the newest moment
const lv=document.getElementById("live");
if(location.protocol.startsWith("http")){lv.hidden=false;live=true;lv.classList.add("on");
 lv.onclick=()=>{live=!live;lv.classList.toggle("on",live);if(live){playing=false;t=END;draw()}};
 scrub.addEventListener("input",()=>{live=false;lv.classList.remove("on")});
 setInterval(async()=>{try{const r=await fetch("match_data.json?"+Date.now());if(r.ok)apply(await r.json())}catch(e){}},2000);
 setInterval(()=>{if(live){t=END+(Date.now()-fetched)/1000;draw()}},100)}
</script></body></html>"""


def match_data(root, now=None):
    evs = load(root / ".team" / "events.jsonl")
    if not evs:
        raise SystemExit("no events in .team/events.jsonl")
    t0, end, intervals, passes, log = derive(evs, now)
    load_ = load_table(intervals, passes, end)
    span = (f"{t0:%Y-%m-%d %H:%M} – {(t0 + datetime.timedelta(seconds=end)):%H:%M}, {len(intervals)} spells, "
            f"{len(passes)} passes.")
    return {"seats": SEATS, "intervals": intervals, "passes": passes, "log": log, "end": end, "t0": t0.isoformat(),
            "load": load_, "span": span}


def build(campaign, out=None, title=None, now=None):
    root = pathlib.Path(campaign).resolve()
    data = match_data(root, now)
    intervals, passes, load_, span = data["intervals"], data["passes"], data["load"], data["span"]
    title = title or f"Match replay — {root.name}"
    page = (PAGE.replace("__TITLE__", html.escape(title)).replace("__SPAN__", html.escape(span))
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    out = pathlib.Path(out) if out else root / ".team" / "match.html"
    out.write_text(page, encoding="utf-8", newline="\n")
    return out, len(intervals), len(passes), load_


def serve_live(campaign, port, title=None):
    """Serve .team/ over http and rewrite match_data.json every 2 s; the page polls it."""
    import functools, http.server, threading, time
    root = pathlib.Path(campaign).resolve()
    team, log = root / ".team", root / ".team" / "events.jsonl"
    while not log.exists() or not log.read_text(encoding="utf-8").strip():
        print("waiting for the first event in", log)
        time.sleep(2)
    title = title or f"Live match — {root.name}"
    build(root, title=title, now=datetime.datetime.now())
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(team))
    handler.func.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"live view: http://127.0.0.1:{port}/match.html  (Ctrl+C to stop)", flush=True)
    while True:
        try:
            tmp = team / "match_data.json.tmp"
            tmp.write_text(json.dumps(match_data(root, datetime.datetime.now()), ensure_ascii=False), encoding="utf-8")
            tmp.replace(team / "match_data.json")
        except (OSError, SystemExit) as e:
            print("rebuild skipped:", e, file=sys.stderr)
        time.sleep(2)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("campaign", nargs="?", default=".")
    ap.add_argument("-o", "--out"); ap.add_argument("--title")
    ap.add_argument("--live", action="store_true", help="serve a live view that follows events as they arrive")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args(argv)
    if a.live:
        try:
            serve_live(a.campaign, a.port, a.title)
        except KeyboardInterrupt:
            return 0
    out, ni, np_, load_ = build(a.campaign, a.out, a.title)
    print(f"wrote {out} ({ni} spells, {np_} passes)")
    print(f"{'seat':>8} {'busy':>8} {'share':>6} {'spells':>6} {'agents':>6} {'in':>4} {'out':>4}")
    for r in load_:
        print(f"{r['seat']:>8} {r['busy']:>7}s {r['share']:>6.0%} {r['spells']:>6} {r['agents']:>6} {r['in']:>4} {r['out']:>4}"
              + ("  <- busy most of the match: candidate for a second agent" if r["hot"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
