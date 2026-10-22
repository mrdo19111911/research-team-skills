# Worked examples (all six steps)

## 1. Annealing: statistical physics → combinatorial optimization
Obstacle: local search stops at a local minimum. Table: energy ↔ objective; state ↔ solution;
thermal fluctuation ↔ accepted bad move; cooling ↔ decreasing acceptance probability.
Break: no true thermal equilibrium; the schedule must be chosen. Prediction: slower cooling → better
solutions on the same instance. Kill: no difference when changing cooling rate.

## 2. Football formation → agent-team organization
Obstacle: several agents produce and judge results; producers are tempted to game the score.
Table: striker ↔ generator; defender ↔ breaker; goalkeeper ↔ final verifier; offside ↔ ban on editing
the grader; substitution ↔ replacing an agent at full context; phase-dependent shape ↔ phase-dependent organization.
Break: "11 players" says nothing about how many agents to use. Prediction: banning generators from
editing tests lowers "reported done but wrong". Kill: no drop in an on/off measurement.

## 3. Power systems → software architecture (coach's example)
Obstacle: interdependent blocks; one failure cascades.
| Power systems | Software |
|---|---|
| fuse, breaker | circuit breaker |
| selective protection (nearest breaker trips first) | nested timeouts: inner shorter than outer |
| N-1 criterion | no single point of failure; kill each service in turn |
| grid frequency drops when load > supply | queue length as system-wide health signal |
| load shedding | drop low-priority requests |
| spinning reserve | warm standby, autoscaling headroom |
| islanding | cell-based architecture |
| ordered black start | restart order along the dependency graph |
| oscillation, resonance; damping | retry storms; exponential backoff with jitter |
| transformer | adapter, protocol gateway |
| Kirchhoff current law | message conservation: in = out + queued |
| SCADA | observability |
Breaks: electricity is hardly storable, software can queue (queues both save and hide overload);
current follows physics, software routes explicitly; Kirchhoff is exact, messages can be lost or duplicated;
power faults are mostly independent, software bugs are correlated (same code everywhere).
Predictions: (1) inner timeout ≥ outer → wasted work and retry storms under a slow dependency;
kill: inject latency, compare. (2) queue-based shedding is more stable than latency-based; kill: ramp load,
compare. (3) N-1 drill: kill each service in turn; full outages must be 0.
