# Tools per seat
| Seat | Existing | Still to write |
|---|---|---|
| 1 | lean4-skills (github.com/cameronfreer/lean4-skills), lean-lsp-mcp (github.com/project-numina/lean-lsp-mcp), aristotle-lean (external API) | grader-hardening checks per team rules |
| 2 | lean4-skills | statement lock (two independent versions); notation/sign consistency |
| 4 | mcp-solver (github.com/szeider/mcp-solver), z3smt-mcp (pypi), mcp-sage (pypi) | counterexample hunt + Lakatos labels |
| 3 | arxiv-mcp-server (github.com/blazickjp/arxiv-mcp-server), alphaXiv MCP, papersflow-mcp | novelty and credit, negative results with scope |
| 10 | arxiv-mcp-server, academic-research-skills (github.com/Imbad0202/academic-research-skills) | systematic pairing of papers |
| 14 | mcp-sage, mcp-solver, Lipshitz workflow (plan → code → review) | experiment loop with re-evaluation against noise |
| 9 | lean4-skills, lean-lsp-mcp | proving along the blueprint, interface requests |
| 11, 7 | far-analogy skill (built) | — |
| 6 | — | claim graph and retraction; value-of-information allocation; pre-compact handoff hook |
| all | claude-for-researchers (CLAUDE.md, condensed notes) | board fragment; handoff |
| sparring | — | plant false variants, measure catch rate |
Skill rules: role card per seat, skill per procedure; grader skills read-only for generators; checks as scripts, not prose;
version skills and measure each change on/off against the baseline; short skills with explicit triggers.
Security: community skills run code; read before installing. Repository URLs above are unchecked.
Built here: `scripts/guard_locked.py` (seat 1's "do not move the goalposts" check for file edits).
