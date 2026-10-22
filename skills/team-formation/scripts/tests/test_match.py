"""Tests for scripts/log_event.py and scripts/view_match.py. Run: python -m unittest discover -s scripts/tests"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
LOG, VIEW = SCRIPTS / "log_event.py", SCRIPTS / "view_match.py"


def cli(camp, *args):
    r = subprocess.run([sys.executable, str(LOG), *args, "--campaign", str(camp)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def hook(camp, payload, seat):
    env = dict(os.environ, TEAM_SEAT=seat, CLAUDE_PROJECT_DIR=str(camp))
    r = subprocess.run([sys.executable, str(LOG)], input=json.dumps(payload), capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr


class MatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.camp = pathlib.Path(self.tmp.name)
        (self.camp / ".team").mkdir()
        self.log = self.camp / ".team" / "events.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def events(self):
        return [json.loads(l) for l in self.log.read_text(encoding="utf-8").splitlines()]

    def test_cli_events(self):
        cli(self.camp, "start", "--seat", "No. 14", "--agent", "a1", "--time", "2026-10-22T10:00:00")
        cli(self.camp, "pass", "--from", "14", "--to", "no.9", "--what", "example", "--time", "2026-10-22T10:05:00")
        ev = self.events()
        self.assertEqual(ev[0]["seat"], "14")
        self.assertEqual((ev[1]["from"], ev[1]["to"]), ("14", "9"))

    def test_hook_logs_inside_campaign_only(self):
        inside = (self.camp / "work" / "a.md").as_posix()
        hook(self.camp, {"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": inside}}, "14")
        hook(self.camp, {"hook_event_name": "PostToolUse", "tool_name": "Read",
                         "tool_input": {"file_path": str(pathlib.Path(self.tmp.name).parent / "elsewhere.md")}}, "9")
        hook(self.camp, {"hook_event_name": "PostToolUse", "tool_name": "Read",
                         "tool_input": {"file_path": str(self.log)}}, "9")
        hook(self.camp, {"hook_event_name": "SubagentStop"}, "9")
        ev = self.events()
        self.assertEqual([e["kind"] for e in ev], ["write", "stop"])
        self.assertEqual(ev[0]["path"], "work/a.md")

    def test_hook_never_fails_on_bad_input(self):
        r = subprocess.run([sys.executable, str(LOG)], input="not json", capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)

    def test_viewer_derives_passes_and_load(self):
        cli(self.camp, "start", "--seat", "14", "--agent", "a1", "--time", "2026-10-22T10:00:00")
        cli(self.camp, "stop", "--seat", "14", "--time", "2026-10-22T10:10:00")
        cli(self.camp, "start", "--seat", "9", "--agent", "b1", "--time", "2026-10-22T10:10:00")
        cli(self.camp, "start", "--seat", "4", "--agent", "c1", "--time", "2026-10-22T10:30:00")
        cli(self.camp, "stop", "--seat", "4", "--time", "2026-10-22T10:35:00")
        cli(self.camp, "stop", "--seat", "9", "--time", "2026-10-22T10:40:00")
        with self.log.open("a", encoding="utf-8") as fh:  # 14 writes the example, 9 reads it twice: one derived pass
            for t, k, s in (("10:09:00", "write", "14"), ("10:11:00", "read", "9"), ("10:11:30", "read", "9")):
                fh.write(json.dumps({"t": f"2026-10-22T{t}", "kind": k, "seat": s, "path": ".team/examples/E1.md"}) + "\n")
        sys.path.insert(0, str(SCRIPTS))
        import view_match
        out, spells, passes, load = view_match.build(self.camp)
        self.assertEqual(passes, 1)
        rows = {r["seat"]: r for r in load}
        self.assertEqual(rows["9"]["busy"], 1800)
        self.assertTrue(rows["9"]["hot"])          # 30 of 40 minutes
        self.assertFalse(rows["4"]["hot"])
        self.assertEqual((rows["14"]["out"], rows["9"]["in"]), (1, 1))
        page = out.read_text(encoding="utf-8")
        self.assertIn("Workload per seat", page)
        self.assertNotIn("__DATA__", page)


if __name__ == "__main__":
    unittest.main()
