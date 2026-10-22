# Substitution
Outgoing agent writes a handoff note (templates.md). Bench agent reads: handoff note → board summary ("match map") → tabu log, then plays.
Research state lives in files (board, notes), never in model memory.

## Trigger (operational, in order of preference)
1. **PreCompact hook** (preferred): writes the handoff note automatically before context compaction. Document the hook in the seat's CLAUDE.md; hooks are invisible otherwise.
2. **Token estimate** from the transcript, checked by No. 6 between tasks: hand off at 50% of the context window.
3. **Visible fatigue**, at any context level: repeating itself, re-entering tabu directions, losing locked definitions → hand off early.
The 50% figure is a tunable default, not a measured optimum. Record handoffs on the board so the threshold can be tuned per seat.
