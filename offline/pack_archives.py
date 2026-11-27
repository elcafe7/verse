#!/usr/bin/env python3
"""Pack the Verse offline dist/ into zip and tar.gz with a verse-<tag>/ root.

Usage:
  python3 offline/pack_archives.py            # packs offline/dist/ into dist/
  python3 offline/pack_archives.py --src DIR --out-dir DIR --tag TAG --date YYYYMMDD

The download names stay verse-offline-<date>.zip and .tar.gz (date only).
Each archive unpacks to one folder, verse-<tag>/ (for example
verse-offline-20261125-1/). --tag defaults to VERSE_OFFLINE_TAG or VERSION.

Deterministic: sorted names, mtime fixed to <date> 00:00:00 UTC, uid/gid 0,
gzip has no filename or timestamp. No symlinks. Standard library only.
"""

from __future__ import annotations

import argparse
import calendar
import gzip
import io
import os
import re
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
TAG_RE = re.compile(r"^offline-[0-9]{8}(-[0-9]+)?$")
DATE_RE = re.compile(r"^[0-9]{8}$")


def fail(msg: str) -> None:
    print(f"pack_archives: {msg}", file=sys.stderr)
    raise SystemExit(1)


def read_tag(tag: str = "", version_file: Path = VERSION_FILE) -> str:
    raw = (tag or os.environ.get("VERSE_OFFLINE_TAG") or "").strip()
    if not raw:
        try:
            raw = version_file.read_text(encoding="utf-8").strip()
        except OSError as e:
            fail(f"VERSION file not found ({version_file}): {e}")
    if not TAG_RE.fullmatch(raw):
        fail(f"tag must look like offline-YYYYMMDD or offline-YYYYMMDD-N (got {raw!r})")
    return raw


def date_from_tag(tag: str) -> str:
    return TAG_RE.fullmatch(tag).group(0)[len("offline-"):][:8]


def folder_name(tag: str) -> str:
    return f"verse-{tag}"


def archive_stem(date: str) -> str:
    return f"verse-offline-{date}"


def safe_under(base, *parts, what: str = "path") -> str:
    """Resolve base/parts and require the result to stay under base.

    CodeQL py/path-injection: realpath + commonpath and startswith(base + sep).
    """
    base_s = os.fspath(base)
    if not isinstance(base_s, str) or not base_s or "\0" in base_s:
        fail(f"{what}: empty path or NUL byte")
    for part in parts:
        if not isinstance(part, str) or not part or "\0" in part:
            fail(f"{what}: empty path or NUL byte")
    base_real = os.path.realpath(os.path.normpath(base_s))
    resolved = os.path.realpath(os.path.normpath(os.path.join(base_real, *parts)))
    if (
        os.path.commonpath([resolved, base_real]) != base_real
        or not resolved.startswith(base_real + os.sep)
    ):
        fail(f"{what}: {os.path.join(*parts)!r} resolves outside {base_s}")
    return resolved


def collect(src: Path) -> dict[str, bytes]:
    if not (src / "index.html").is_file():
        fail(f"no index.html in {src} (run python3 offline/build_offline.py first)")
    members: dict[str, bytes] = {}
    for dirpath, dirnames, filenames in os.walk(src, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if not Path(dirpath, d).is_symlink())
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if p.is_symlink():
                fail(f"symlink not allowed: {p}")
            if not p.is_file():
                fail(f"non-file not allowed: {p}")
            rel = p.relative_to(src).as_posix()
            if rel.startswith("/") or ".." in rel.split("/"):
                fail(f"unsafe path: {rel}")
            members[rel] = p.read_bytes()
    if not members:
        fail(f"no files in {src}")
    return dict(sorted(members.items()))


def mtime_for(date: str) -> int:
    return calendar.timegm((int(date[:4]), int(date[4:6]), int(date[6:]), 0, 0, 0))


def build(src: Path, out_dir: Path, tag: str, date: str) -> tuple[Path, Path, dict[str, bytes], str]:
    if not DATE_RE.fullmatch(date):
        fail("--date must be YYYYMMDD")
    tag = read_tag(tag)
    members = collect(src)
    root = folder_name(tag)
    stem = archive_stem(date)
    mtime = mtime_for(date)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Filenames are built only from the DATE_RE-validated date (never the raw
    # tag / VERSE_OFFLINE_TAG / --out-dir string). Then the joined path is
    # resolved and required to stay under out_dir.
    zname, tname = f"{stem}.zip", f"{stem}.tar.gz"
    if not zname.startswith("verse-offline-") or not tname.startswith("verse-offline-"):
        fail("archive name must start with verse-offline-")
    zpath_s = safe_under(out_dir, zname, what="zip path")
    tpath_s = safe_under(out_dir, tname, what="tar.gz path")

    with zipfile.ZipFile(zpath_s, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name, data in members.items():
            zi = zipfile.ZipInfo(
                f"{root}/{name}",
                date_time=(int(date[:4]), int(date[4:6]), int(date[6:]), 0, 0, 0),
            )
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = (0o100644) << 16
            zi.create_system = 3
            zf.writestr(zi, data, compresslevel=9)

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for name, data in members.items():
            ti = tarfile.TarInfo(f"{root}/{name}")
            ti.size = len(data)
            ti.mtime = mtime
            ti.mode = 0o644
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = "root"
            tf.addfile(ti, io.BytesIO(data))
    with open(tpath_s, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as gz:
            gz.write(buf.getvalue())
    return Path(zpath_s), Path(tpath_s), members, root


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=str(ROOT / "offline" / "dist"), help="built offline folder (default: offline/dist)")
    ap.add_argument("--out-dir", default=str(ROOT / "dist"), help="where to write the archives (default: dist/)")
    ap.add_argument("--tag", default="", help="release tag; defaults to VERSE_OFFLINE_TAG or VERSION")
    ap.add_argument("--date", default="", help="YYYYMMDD for the archive filename and mtimes; defaults to the tag date")
    a = ap.parse_args(argv)
    tag = read_tag(a.tag)
    date = a.date or date_from_tag(tag)
    z, t, members, root = build(Path(a.src), Path(a.out_dir), tag, date)
    print(f"{z} {t}  ({len(members)} files, root {root}/)")


if __name__ == "__main__":
    main()
