"""Tests for scripts/init_team.py. Run: python -m unittest discover -s scripts/tests  (or python test_init.py)."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

INIT = pathlib.Path(__file__).resolve().parent.parent / "init_team.py"
SKILL = INIT.parent.parent
SEATS = [6, 14, 10, 8, 4, 9, 2, 3, 1, 11, 7]
WINGS = {11}


def run(camp, variant="math", problem="Prove the bound", *extra):
    r = subprocess.run([sys.executable, str(INIT), str(camp), "--variant", variant, "--problem", problem, *extra],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return r.stdout


class InitTeam(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.camp = pathlib.Path(self.tmp.name) / "campaign"
        self.team = self.camp / ".team"

    def tearDown(self):
        self.tmp.cleanup()

    def test_structure(self):
        out = run(self.camp)
        for d in ("verdicts", "handoff", "examples", "seats"):
            self.assertTrue((self.team / d).is_dir(), d)
        for f in ("board.md", "bank.md", "locked.txt", "metrics.md", "hooks.settings.json"):
            self.assertTrue((self.team / f).is_file(), f)
            self.assertIn(f".team/{f}", out)
        board = (self.team / "board.md").read_text(encoding="utf-8")
        for sec in ("## Phase", "## Directions", "## Fragments", "## Tabu", "## Dependencies"):
            self.assertIn(sec, board)
        self.assertIn("Prove the bound", board)
        self.assertIn("Baseline", (self.team / "metrics.md").read_text(encoding="utf-8"))
        locked = (self.team / "locked.txt").read_text(encoding="utf-8")
        self.assertTrue(all(l.startswith("#") or not l.strip() or "/" in l for l in locked.splitlines()))
        hooks = json.loads((self.team / "hooks.settings.json").read_text(encoding="utf-8"))["hooks"]
        cmds = json.dumps(hooks)
        for s in ("guard_locked.py", "guard_sealed.py", "precompact_handoff.py", "log_event.py"):
            self.assertIn(s, cmds)
        self.assertIn("PreToolUse", hooks)
        self.assertIn("PreCompact", hooks)
        for entry in hooks["PreToolUse"] + hooks["PreCompact"]:
            for h in entry["hooks"]:
                script = h["command"].split('"')[-2]
                self.assertTrue(pathlib.Path(script).is_absolute(), script)

    def test_seats(self):
        run(self.camp)
        files = sorted(p.name for p in (self.team / "seats").glob("*.md"))
        self.assertEqual(files, sorted(f"{s}.md" for s in SEATS))
        for s in SEATS:
            text = (self.team / "seats" / f"{s}.md").read_text(encoding="utf-8")
            seat_lines = [l for l in text.splitlines() if l.startswith("TEAM_SEAT=")]
            self.assertEqual(seat_lines, [f"TEAM_SEAT={s}"], s)
            self.assertIn(f"No. {s}", text)
            full = (SKILL / "references" / "seats" / f"{s}.md").exists()
            self.assertIn("## What you do" if full else "**No.", text, f"seat prompt missing for {s}")
            self.assertIn("bulletin.md", text, s)
            self.assertNotIn("no card found", text, s)
            self.assertIn("1. **", text)  # the four laws
            self.assertIn("4. **", text)
            self.assertEqual("switched on per problem" in text, s in WINGS, s)

    def test_idempotent(self):
        run(self.camp)
        board, bank = self.team / "board.md", self.team / "bank.md"
        with board.open("a", encoding="utf-8") as f:
            f.write("\nFRAGMENT added by a seat\n")
        with bank.open("a", encoding="utf-8") as f:
            f.write("\nENTRY added by No. 1\n")
        before = {p: p.read_bytes() for p in self.team.rglob("*") if p.is_file()}
        out = run(self.camp, "software", "A different problem")
        after = {p: p.read_bytes() for p in self.team.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertIn("FRAGMENT added by a seat", board.read_text(encoding="utf-8"))
        self.assertIn("ENTRY added by No. 1", bank.read_text(encoding="utf-8"))
        self.assertNotIn("created  .team/board.md", out)
        self.assertIn("skipped  .team/board.md", out)
        self.assertIn("skipped  .team/bank.md", out)

    def test_refresh_seats_keeps_board_and_bank(self):
        run(self.camp)
        bank = self.team / "bank.md"
        with bank.open("a", encoding="utf-8") as f:
            f.write("\nENTRY\n")
        run(self.camp, "software", "Build the service", "--refresh-seats")
        self.assertIn("ENTRY", bank.read_text(encoding="utf-8"))
        self.assertIn("software variant", (self.team / "seats" / "9.md").read_text(encoding="utf-8"))
        self.assertIn("Prove the bound", (self.team / "board.md").read_text(encoding="utf-8"))

    def test_bad_variant(self):
        r = subprocess.run([sys.executable, str(INIT), str(self.camp), "--variant", "chess", "--problem", "x"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.team.exists())


if __name__ == "__main__":
    unittest.main()
