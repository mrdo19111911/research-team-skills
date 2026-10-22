"""Tests for add_connection.py and its effect on find_path.py. Run: python scripts/tests/test_add_connection.py"""
import os, subprocess, sys, tempfile, unittest
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
ADD = os.path.join(SCRIPTS, "add_connection.py")
FIND = os.path.join(SCRIPTS, "find_path.py")
A, B = "compact Hausdorff spaces", "commutative rings"  # both exist in data/core_en.yaml


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.found = os.path.join(self.d, "found.yaml")
        self.env = dict(os.environ, FOUND=self.found, PYTHONIOENCODING="utf-8")

    def run_add(self, *args):
        return subprocess.run([sys.executable, ADD, *args], env=self.env, capture_output=True, text=True, encoding="utf-8")

    def base(self, test="alive", name="test link"):
        return self.run_add("--name", name, "--a", A, "--b", B, "--map", "point = prime ideal; map = ring map",
                            "--breaks", "non-affine case", "--small-test", test, "--problem", "unit test")

    def edges(self):
        with open(self.found, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_add_and_ids(self):
        self.assertEqual(self.base().returncode, 0)
        self.assertEqual(self.base(name="second").returncode, 0)
        e = self.edges()
        self.assertEqual([x["id"] for x in e], ["F001", "F002"])
        self.assertEqual(e[0]["status"], "heuristic")
        self.assertEqual(e[0]["source"], "none")
        self.assertEqual(e[0]["source_checked"], "no")
        self.assertEqual(e[0]["map"][0], ["point", "prime ideal"])

    def test_duplicate_becomes_seen(self):
        self.base()
        r = self.base(test="dead")
        self.assertIn("updated F001", r.stdout)
        e = self.edges()
        self.assertEqual(len(e), 1)
        self.assertEqual(len(e[0]["seen"]), 2)
        self.assertEqual(e[0]["small_test"], "dead")

    def test_reversed_pair_is_duplicate(self):
        self.base()
        self.run_add("--name", "test link", "--a", B, "--b", A, "--map", "x = y", "--breaks", "z", "--small-test", "alive")
        self.assertEqual(len(self.edges()), 1)

    def test_no_theorem_status(self):
        r = self.run_add("--name", "n", "--a", A, "--b", B, "--map", "x = y", "--breaks", "z",
                         "--small-test", "alive", "--status", "theorem")
        self.assertNotEqual(r.returncode, 0)

    def test_missing_fields_refused(self):
        r = self.run_add("--name", "n", "--a", A, "--b", B, "--small-test", "alive")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--map", r.stderr)
        self.assertFalse(os.path.exists(self.found))

    def test_unknown_world_refused_unless_new_node(self):
        args = ["--name", "n", "--a", "zzqq world", "--b", B, "--map", "x = y", "--breaks", "z", "--small-test", "alive"]
        self.assertNotEqual(self.run_add(*args).returncode, 0)
        self.assertEqual(self.run_add(*args, "--new-node").returncode, 0)

    def test_name_normalized_to_existing_node(self):
        self.run_add("--name", "n", "--a", "Compact  hausdorff spaces", "--b", B, "--map", "x = y", "--breaks", "z",
                     "--small-test", "alive")
        self.assertEqual(self.edges()[0]["a"], A)

    def test_update(self):
        self.base()
        r = self.run_add("--update", "F001", "--source", "arXiv:0000.00000", "--source-checked", "exists", "--note", "checked")
        self.assertEqual(r.returncode, 0)
        e = self.edges()[0]
        self.assertEqual(e["source_checked"], "exists")
        self.assertEqual(e["seen"][-1]["note"], "checked")

    def test_find_path_uses_alive_skips_dead(self):
        self.base(name="alive link")
        self.run_add("--name", "dead link", "--a", A, "--b", "Boolean algebras", "--map", "x = y", "--breaks", "z",
                     "--small-test", "dead")
        env = dict(self.env, GRAPH=self.found)
        out = subprocess.run([sys.executable, FIND, "--edges", A], env=env, capture_output=True, text=True, encoding="utf-8").stdout
        self.assertIn("alive link", out)
        self.assertNotIn("dead link", out)


if __name__ == "__main__":
    unittest.main()
