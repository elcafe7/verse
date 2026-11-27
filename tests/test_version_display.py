"""Prominent offline version: VERSION, README, and the stamped shell."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_build():
    path = ROOT / "offline" / "build_offline.py"
    spec = importlib.util.spec_from_file_location("verse_build_offline", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


build = _load_build()


class VersionDisplayTests(unittest.TestCase):
    def test_version_file_is_an_offline_tag(self):
        tag = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(tag, build.TAG_RE)

    def test_readme_shows_the_current_tag_prominently(self):
        tag = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            f"**Current offline release: [{tag}](https://github.com/elcafe7/verse/releases/tag/{tag})**",
            readme,
        )
        self.assertIn(f"<sub>{tag} · verse-offline-", readme)

    def test_env_overrides_version_file(self):
        self.assertEqual(
            build.read_version(env={"VERSE_OFFLINE_TAG": "offline-20260101"}),
            "offline-20260101",
        )

    def test_stamp_shell_fills_header_title_and_footer(self):
        raw = (ROOT / "offline" / "shell.html").read_text(encoding="utf-8")
        self.assertGreaterEqual(raw.count(build.VERSION_TOKEN), 3)
        out = build.stamp_shell(raw, "offline-20261125-1")
        self.assertNotIn(build.VERSION_TOKEN, out)
        self.assertIn('data-testid="app-version">offline-20261125-1</span>', out)
        self.assertIn(
            'data-testid="footer-version">Verse offline-20261125-1 · KJV · Geneva 1599 · no internet needed',
            out,
        )
        self.assertIn("<title>Verse Offline offline-20261125-1 — A focused Bible reader</title>", out)
        self.assertIn('<meta name="verse-version" content="offline-20261125-1">', out)

    def test_rejects_a_bad_tag(self):
        with self.assertRaises(SystemExit):
            build.read_version(env={"VERSE_OFFLINE_TAG": "v1.0.0"})


if __name__ == "__main__":
    unittest.main()
