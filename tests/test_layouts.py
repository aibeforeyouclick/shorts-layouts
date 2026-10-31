"""Tests for the layout tools and the script checker. Standard library only; no TTS, no rendering.

Each test copies an example video into a temp folder, so the repo is never modified.
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_script  # noqa: E402
import layoutlib  # noqa: E402
import ranking_list  # noqa: E402
import split_screen  # noqa: E402
import storytelling  # noqa: E402
import trial_reels  # noqa: E402


def run(fn, path):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = fn(path)
    return code, out.getvalue()


class ExampleCase(unittest.TestCase):
    example = "layout-check"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / self.example
        shutil.copytree(ROOT / "examples" / self.example, self.dir)

    def tearDown(self):
        self.tmp.cleanup()

    def edit_script(self, change):
        p = self.dir / "script.json"
        s = json.loads(p.read_text(encoding="utf-8-sig"))
        change(s)
        p.write_text(json.dumps(s), encoding="utf-8")


class TestLayoutlib(unittest.TestCase):
    def test_norm(self):
        self.assertEqual(layoutlib.norm("Short,"), "short")
        self.assertEqual(layoutlib.norm("Don't!"), "don't")

    def test_check_file_rejects_paths_outside_the_folder(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(layoutlib.check_file("x", "../secret.png", Path(d)))
            self.assertTrue(layoutlib.check_file("x", str(Path(d).resolve() / "a.png"), Path(d)))
            self.assertTrue(layoutlib.check_file("x", "missing.png", Path(d)))

    def test_check_anchor_counts_inside_the_phase(self):
        words = [{"word": "go", "phase": "p1"}, {"word": "go", "phase": "p2"}]
        self.assertEqual(layoutlib.check_anchor("a", "go", 1, "p2", words), [])
        self.assertTrue(layoutlib.check_anchor("a", "go", 2, "p2", words))
        self.assertTrue(layoutlib.check_anchor("a", "go", 1, "p2", None))


class TestTrialReels(ExampleCase):
    def test_ok_and_idempotent(self):
        self.assertEqual(run(trial_reels.main, self.dir)[0], 0)
        first = (self.dir / "index.html").read_text(encoding="utf-8")
        self.assertEqual(run(trial_reels.main, self.dir)[0], 0)
        second = (self.dir / "index.html").read_text(encoding="utf-8")
        self.assertEqual(first, second)
        self.assertEqual(second.count('src="vendor/trial-hook.js"'), 1)
        self.assertEqual(second.count('"id":"trial"'), 1)

    def test_rules(self):
        data_js = (self.dir / "data.js").read_text(encoding="utf-8")
        good = json.loads((self.dir / "script.json").read_text(encoding="utf-8-sig"))["trials"]
        self.assertEqual(trial_reels.check(good, data_js), [])
        self.assertTrue(trial_reels.check(good[:2], data_js))
        dup = [dict(t, style="post") for t in good]
        self.assertTrue(any("differ" in e for e in trial_reels.check(dup, data_js)))
        long = [dict(good[0], text="one two three four five six seven eight nine ten eleven twelve thirteen")] + good[1:]
        self.assertTrue(any("12 words" in e for e in trial_reels.check(long, data_js)))
        self.assertTrue(any("p1" in e for e in trial_reels.check(good, "")))


class TestRankingList(ExampleCase):
    def test_ok(self):
        code, out = run(ranking_list.main, self.dir)
        self.assertEqual(code, 0, out)
        self.assertIn("window.RANKING", (self.dir / "ranking-list.data.js").read_text(encoding="utf-8"))

    def test_unspoken_anchor_is_refused(self):
        self.edit_script(lambda s: s["ranking"]["items"][0].update(anchor="banana"))
        code, out = run(ranking_list.main, self.dir)
        self.assertEqual(code, 1)
        self.assertIn("banana", out)

    def test_bad_tier_is_refused(self):
        self.edit_script(lambda s: s["ranking"]["items"][0].update(tier="Z"))
        self.assertEqual(run(ranking_list.main, self.dir)[0], 1)


class TestStorytellingAndSplit(ExampleCase):
    example = "layout-check-2"

    def test_story_ok(self):
        code, out = run(storytelling.main, self.dir)
        self.assertEqual(code, 0, out)

    def test_story_needs_three_images(self):
        self.edit_script(lambda s: s["story"]["images"].pop())
        self.assertEqual(run(storytelling.main, self.dir)[0], 1)

    def test_split_ok(self):
        code, out = run(split_screen.main, self.dir)
        self.assertEqual(code, 0, out)

    def test_split_refuses_path_outside_folder(self):
        self.edit_script(lambda s: s["split"].update(host="../../README.md"))
        code, out = run(split_screen.main, self.dir)
        self.assertEqual(code, 1)
        self.assertIn("relative path inside", out)

    def test_split_phases_must_be_consecutive(self):
        self.edit_script(lambda s: s["split"].update(phases=["p1", "p3"]))
        self.assertEqual(run(split_screen.main, self.dir)[0], 1)


class TestCheckScript(ExampleCase):
    def test_examples_pass(self):
        for ex in ["layout-check", "layout-check-2"]:
            code, out = run(check_script.main, ROOT / "examples" / ex)
            self.assertEqual(code, 0, out)

    def test_unspoken_privacy_line_fails(self):
        self.edit_script(lambda s: s.update(privacy="We sell nothing"))
        self.assertEqual(run(check_script.main, self.dir)[0], 1)


if __name__ == "__main__":
    unittest.main()
