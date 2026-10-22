"""Tests for guard_sealed.py and precompact_handoff.py. Run: python scripts/tests/test_hooks.py"""
import json, os, subprocess, sys, tempfile, unittest, pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
SEALED_HOOK = HERE / "guard_sealed.py"
HANDOFF_HOOK = HERE / "precompact_handoff.py"


def run(script, payload, seat=None, root=None, raw=None):
    env = dict(os.environ)
    env.pop("TEAM_SEAT", None)
    if seat is not None:
        env["TEAM_SEAT"] = seat
    if root is not None:
        env["CLAUDE_PROJECT_DIR"] = str(root)
    stdin = raw if raw is not None else json.dumps(payload)
    p = subprocess.run([sys.executable, str(script)], input=stdin, capture_output=True, text=True, env=env, timeout=30)
    return p.returncode, p.stderr


class SealedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.sub = self.root / ".team" / "verdicts" / "S1"
        self.sub.mkdir(parents=True)
        (self.sub / "2.md").write_text("SEAT: 2 | VERDICT: fail", encoding="utf-8")
        (self.root / "notes.md").write_text("x", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def hook(self, tool, ti, seat):
        return run(SEALED_HOOK, {"tool_name": tool, "tool_input": ti, "cwd": str(self.root)}, seat, self.root)[0]

    def seal(self):
        (self.sub / "SEALED").write_text("", encoding="utf-8")

    def test_own_write_allowed(self):
        self.assertEqual(self.hook("Write", {"file_path": str(self.sub / "3.md"), "content": "v"}, "3"), 0)
        self.assertEqual(self.hook("Write", {"file_path": ".team/verdicts/S1/3.md", "content": "v"}, "No. 3"), 0)

    def test_other_write_blocked(self):
        self.assertEqual(self.hook("Edit", {"file_path": str(self.sub / "2.md")}, "3"), 2)

    def test_read_other_blocked_then_allowed(self):
        ti = {"file_path": str(self.sub / "2.md")}
        self.assertEqual(self.hook("Read", ti, "3"), 2)
        self.assertEqual(self.hook("Read", ti, "2"), 0)  # own
        self.seal()
        self.assertEqual(self.hook("Read", ti, "3"), 0)

    def test_sealed_verdicts_immutable(self):
        self.seal()
        self.assertEqual(self.hook("Write", {"file_path": str(self.sub / "2.md")}, "2"), 2)

    def test_no6_list_allowed_read_blocked(self):
        self.assertEqual(self.hook("Glob", {"pattern": "*", "path": str(self.sub)}, "6"), 0)
        self.assertEqual(self.hook("Glob", {"pattern": ".team/verdicts/S1/*.md"}, "6"), 0)
        self.assertEqual(self.hook("Bash", {"command": "ls .team/verdicts/S1"}, "6"), 0)
        self.assertEqual(self.hook("Read", {"file_path": str(self.sub / "2.md")}, "6"), 2)
        self.assertEqual(self.hook("Bash", {"command": "cat .team/verdicts/S1/2.md"}, "6"), 2)
        self.assertEqual(self.hook("Grep", {"pattern": "fail", "path": str(self.sub)}, "6"), 2)

    def test_glob_by_defender_blocked(self):
        self.assertEqual(self.hook("Glob", {"pattern": "*", "path": str(self.sub)}, "3"), 2)

    def test_bash(self):
        self.assertEqual(self.hook("Bash", {"command": "cat .team/verdicts/S1/2.md"}, "3"), 2)
        self.assertEqual(self.hook("Bash", {"command": r"type .team\verdicts\S1\2.md"}, "3"), 2)
        self.assertEqual(self.hook("Bash", {"command": "cat .team/verdicts/S1/*"}, "3"), 2)
        self.assertEqual(self.hook("Bash", {"command": "grep -r fail .team/verdicts"}, "3"), 2)
        self.assertEqual(self.hook("Bash", {"command": "echo pass > .team/verdicts/S1/3.md"}, "3"), 0)
        self.assertEqual(self.hook("Bash", {"command": "ls .team/verdicts/S1 && cat .team/verdicts/S1/2.md"}, "6"), 2)
        self.assertEqual(self.hook("Bash", {"command": "touch .team/verdicts/S1/SEALED"}, "3"), 2)
        self.assertEqual(self.hook("Bash", {"command": "python run.py"}, "3"), 0)
        self.seal()
        self.assertEqual(self.hook("Bash", {"command": "cat .team/verdicts/S1/2.md"}, "3"), 0)

    def test_grep_ancestor(self):
        self.assertEqual(self.hook("Grep", {"pattern": "fail"}, "3"), 2)
        self.assertEqual(self.hook("Grep", {"pattern": "fail", "glob": "*.py"}, "3"), 0)
        self.assertEqual(self.hook("Grep", {"pattern": "fail", "path": str(self.root / "src")}, "3"), 0)
        self.seal()
        self.assertEqual(self.hook("Grep", {"pattern": "fail"}, "3"), 0)

    def test_sealed_file_creation(self):
        self.assertEqual(self.hook("Write", {"file_path": str(self.sub / "SEALED")}, "3"), 2)
        self.assertEqual(self.hook("Write", {"file_path": str(self.sub / "SEALED")}, "6"), 0)

    def test_unrelated_and_malformed(self):
        self.assertEqual(self.hook("Read", {"file_path": str(self.root / "notes.md")}, "3"), 0)
        self.assertEqual(run(SEALED_HOOK, None, "3", self.root, raw="{not json .team/verdicts/S1/2.md")[0], 2)
        self.assertEqual(run(SEALED_HOOK, None, "3", self.root, raw="{not json")[0], 0)

    def test_unset_seat_cannot_read(self):
        self.assertEqual(self.hook("Read", {"file_path": str(self.sub / "2.md")}, None), 2)


class HandoffTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def notes(self):
        return list((self.root / ".team" / "handoff").glob("*.md"))

    def test_missing_transcript(self):
        code, _ = run(HANDOFF_HOOK, {"hook_event_name": "PreCompact", "transcript_path": str(self.root / "nope.jsonl"),
                                      "cwd": str(self.root), "trigger": "auto"}, "9", self.root)
        self.assertEqual(code, 0)
        n = self.notes()
        self.assertEqual(len(n), 1)
        self.assertTrue(n[0].name.startswith("9-"))
        self.assertIn("fill in: next step", n[0].read_text(encoding="utf-8"))

    def test_garbage_input(self):
        self.assertEqual(run(HANDOFF_HOOK, None, None, self.root, raw="<<garbage")[0], 0)
        self.assertTrue(self.notes()[0].name.startswith("unknown-"))

    def test_transcript_parsed(self):
        tp = self.root / "t.jsonl"
        lines = [
            {"type": "user", "message": {"role": "user", "content": "Prove lemma L3 for N = 1."}},
            {"type": "assistant", "message": {"role": "assistant", "content": [
                {"type": "text", "text": "Trying the potential function."},
                {"type": "tool_use", "id": "a", "name": "Edit", "input": {"file_path": "proofs/L3.md"}},
                {"type": "tool_use", "id": "b", "name": "Bash", "input": {"command": "lake build"}}]}},
            {"type": "user", "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "b", "is_error": True, "content": "error: unsolved goals"}]}},
        ]
        tp.write_text("\n".join(json.dumps(l) for l in lines) + "\nnot json\n", encoding="utf-8")
        code, _ = run(HANDOFF_HOOK, {"transcript_path": str(tp), "cwd": str(self.root)}, "9", self.root)
        self.assertEqual(code, 0)
        txt = self.notes()[0].read_text(encoding="utf-8")
        for s in ("proofs/L3.md", "lake build", "ERROR: error: unsolved goals", "Prove lemma L3", "fill in: where stuck"):
            self.assertIn(s, txt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
