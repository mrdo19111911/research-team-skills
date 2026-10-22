# Research team skills for Claude Code

Three Claude Code skills for running a multi-agent research campaign on a hard problem
(mathematical proofs, algorithm research, or software) and writing the verified results up as a paper.

| Skill | What it does |
|---|---|
| [`team-formation`](skills/team-formation/SKILL.md) | An 11-seat agent team laid out as a football formation; the far-field seat (No. 7) is always on. The attack generates ideas freely; nothing counts until two independent defenders and a final verifier pass it. Includes hooks that stop the attack from editing the locked statement and stop judges from reading each other's verdicts before they are sealed. |
| [`far-analogy`](skills/far-analogy/SKILL.md) | Gets past a concrete obstacle by borrowing a tool from a distant field, through a structured analogy that ends in a testable prediction. Ships a graph of mathematical correspondences (`data/`); every card found is recorded in `data/found.yaml` by `scripts/add_connection.py`, alive or dead. |
| [`paper-editor`](skills/paper-editor/SKILL.md) | The goalkeeper's (No. 1) write-up skill: turns the bank of verified results into a paper, one bank entry per claim, checked by fresh defenders before release. |

## Install

Windows (PowerShell), from the repository root:

```powershell
./install.ps1
```

macOS / Linux:

```bash
./install.sh
```

Each script links every folder in `skills/` into `~/.claude/skills/`, so edits in this repository take effect
at once. A skill folder that already exists there is left alone and reported.

## Start a campaign

```bash
python ~/.claude/skills/team-formation/scripts/init_team.py <campaign-dir> --variant math --problem "<one line>"
```

Then merge `<campaign-dir>/.team/hooks.settings.json` into `<campaign-dir>/.claude/settings.json` and follow
[`launcher.md`](skills/team-formation/references/launcher.md).

## Tests

```bash
python skills/team-formation/scripts/tests/test_hooks.py
python skills/team-formation/scripts/tests/test_init.py
python skills/far-analogy/scripts/tests/test_add_connection.py
```

## Status and known limits

- The team has not yet been run on a real problem, and not yet compared with a single agent on the same budget.
  The laws in `references/laws.md` are design hypotheses; `references/evidence.md` lists which sources are unchecked.
- Hooks identify a seat by the `TEAM_SEAT` environment variable, which subagents inherit: run No. 1, No. 2 and
  No. 3 in their own sessions. The shell check in `guard_sealed.py` only matches paths written in the command.
- `paper-editor` reads the paper project's own `CLAUDE.md` and `WRITING_GUIDELINE.md` (if present) and uses the
  optional `my_revive_paper` readability skill, which is not part of this repository.
- `far-analogy/data/graph_vi.yaml` is machine-generated (in Vietnamese) and its sources are not yet verified.

`docs/slides-doi-hinh.pptx` is a slide deck (in Vietnamese) explaining the formation.
