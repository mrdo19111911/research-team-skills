# Match log and replay

Why: after a campaign you want to see, at a glance, who played when, who passed to whom, and which seat was busy all
match. That last view decides the next campaign's shape: a seat busy most of the time gets a second agent (a squad,
squads.md); a seat that never ran is switched off; a seat that receives many passes and sends few is a bottleneck.

## The log: `.team/events.jsonl`
Append-only, one JSON object per line. Fields: `t` (ISO time), `kind`, `seat`, `agent`, `path`, `from`, `to`, `what`,
`note`. Seats are `"1"`..`"14"`, `"coach"`, `"referee"`. Kinds:

| kind | written by | meaning |
|---|---|---|
| start / stop | orchestrator (No. 6) | an agent takes the seat / hands back (stop also comes from the Stop hooks) |
| pass | orchestrator | information handed from one seat to another (`what`: "worked example", "verdict S2") |
| read / write | hook `log_event.py` | a file inside the campaign was read / written by the seat in `TEAM_SEAT` |
| note | orchestrator | anything else ("phase 0 -> 1") |

Passes are also derived: a read of a file whose last writer is a different seat is a pass writer → reader (repeat reads
of the same file within 60 s count once).

## Two sources
1. **Hook** (`scripts/log_event.py` with no arguments), registered by `init_team.py` in `hooks.settings.json` for
   PostToolUse (Read|NotebookRead|Write|Edit|MultiEdit|NotebookEdit) and Stop / SubagentStop. It only knows `TEAM_SEAT`,
   so Agent-tool subagents (which inherit the orchestrator's environment) all log as the orchestrator's seat.
2. **Orchestrator CLI** — the reliable source; No. 6 calls it around every spawn and hand-over:
```bash
python <skill>/scripts/log_event.py start --seat 14 --agent a1 --note "worked examples N=1,2"
python <skill>/scripts/log_event.py pass --from 14 --to 9 --what "worked example N=1"
python <skill>/scripts/log_event.py stop --seat 14 --agent a1
```
   `--campaign DIR` (default: current directory), `--time ISO` to rebuild a past run from file times.

## The replay: `scripts/view_match.py`
```bash
python <skill>/scripts/view_match.py <campaign-dir>
```
Writes `.team/match.html` (one self-contained file, no network) and prints the workload table. In the page:
- the pitch of the formation slide; a seat **glows** while its agent runs; unused seats are faded;
- a **ball** flies from seat to seat for each pass, labelled with what was passed;
- play / pause, a time slider, speed; the event list (click a line to jump there);
- **Workload per seat**: busy share of the match (union of its spells), spells, distinct agents, passes received and
  sent, sorted busiest first. ▲ marks a seat busy more than 60% of the match: candidate for a second agent.

## Reading the workload table
- ▲ seat with one agent → next campaign, give it a squad of 2–3 (squads.md) or split its task.
- Seat with 0 spells → switch it off, or ask why No. 6 never gave it a task.
- Many received, few sent → the seat is a bottleneck; others waited on it.
- Judges (2, 3, 1) are busy only after submissions; a low share there is normal.
The table measures wall-clock activity, not tokens; put token use per seat in `.team/metrics.md` beside it.
