"""offline/pack_archives.py: verse-<tag>/ root, deterministic zip and tar.gz."""

import hashlib
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "offline"))
from pack_archives import (  # noqa: E402
    TAG_RE,
    archive_stem,
    build,
    date_from_tag,
    folder_name,
    read_tag,
    safe_under,
)

TAG = "offline-20261125-1"
DATE = "20261125"
FOLDER = folder_name(TAG)
STEM = archive_stem(DATE)
FIXED_MTIME = 1795564800  # 2026-11-25 00:00:00 UTC


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class PackArchivesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = Path(self.tmp.name) / "dist"
        (self.src / "data" / "kjv").mkdir(parents=True)
        (self.src / "index.html").write_text("<!doctype html><title>Verse</title>\n", encoding="utf-8")
        (self.src / "app.js").write_text("console.log('ok');\n", encoding="utf-8")
        (self.src / "data" / "kjv" / "john.js").write_text("/* john */\n", encoding="utf-8")
        self.out = Path(self.tmp.name) / "out"

    def test_tag_helpers(self):
        self.assertRegex("offline-20261125-1", TAG_RE)
        self.assertEqual(date_from_tag("offline-20261125-1"), "20261125")
        self.assertEqual(folder_name("offline-20261125-1"), "verse-offline-20261125-1")
        self.assertEqual(read_tag("offline-20261125-1"), "offline-20261125-1")
        with self.assertRaises(SystemExit):
            read_tag("v1.0.0")

    def test_contents_and_root(self):
        z, t, members, root = build(self.src, self.out, TAG, DATE)
        self.assertEqual(root, FOLDER)
        self.assertEqual(z.name, f"{STEM}.zip")
        self.assertEqual(t.name, f"{STEM}.tar.gz")
        want = sorted(f"{FOLDER}/{n}" for n in members)
        with zipfile.ZipFile(z) as zf:
            self.assertEqual(sorted(zf.namelist()), want)
            self.assertTrue(all(n.startswith(f"{FOLDER}/") for n in zf.namelist()))
            self.assertFalse(any(n == "dist" or n.startswith("dist/") for n in zf.namelist()))
            self.assertEqual(zf.read(f"{FOLDER}/index.html"), (self.src / "index.html").read_bytes())
        with tarfile.open(t, "r:gz") as tf:
            self.assertEqual(sorted(tf.getnames()), want)
            for m in tf.getmembers():
                self.assertTrue(m.isfile())
                self.assertFalse(m.issym() or m.islnk())
                self.assertEqual((m.mtime, m.uid, m.gid, m.mode), (FIXED_MTIME, 0, 0, 0o644))

    def test_deterministic_and_gzip_header(self):
        z1, t1, _, _ = build(self.src, self.out, TAG, DATE)
        z2, t2, _, _ = build(self.src, Path(self.tmp.name) / "out2", TAG, DATE)
        self.assertEqual(sha(z1), sha(z2))
        self.assertEqual(sha(t1), sha(t2))
        raw = t1.read_bytes()
        self.assertEqual(raw[:3], b"\x1f\x8b\x08")
        self.assertEqual(raw[3] & 0x08, 0)
        self.assertEqual(raw[4:8], b"\0\0\0\0")


    def test_safe_under_stays_inside_and_rejects_escapes(self):
        dest = safe_under(self.out, "verse-offline-20261125.tar.gz", what="tar.gz path")
        self.assertTrue(dest.startswith(str(self.out.resolve()) + "/"))
        self.assertTrue(dest.endswith("verse-offline-20261125.tar.gz"))
        with self.assertRaises(SystemExit):
            safe_under(self.out, "../secret.tar.gz", what="tar.gz path")
        with self.assertRaises(SystemExit):
            safe_under(self.out, "/etc/passwd", what="tar.gz path")
        with self.assertRaises(SystemExit):
            safe_under(self.out, "foo\x00bar", what="tar.gz path")


if __name__ == "__main__":
    unittest.main()
