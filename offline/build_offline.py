#!/usr/bin/env python3
"""Build the fully-offline Verse reader (stdlib only, no dependencies).

Reads the bundled SQLite editions and emits dist/:
  index.html, app.js, styles.css, favicon.svg,
  data/index.js                    (editions, book order, chapter sizes, src langs)
  data/<ed>/<book-slug>.js         (one file per book per edition)
  data/src/<book-slug>.js          (Hebrew/Greek source + transliteration)

Data shards are .js (not .json) so they load over file:// via <script> tags,
where fetch() is blocked. Usage:
    python3 offline/build_offline.py            # writes offline/dist/
    tar -czf verse-offline.tar.gz -C offline dist
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.refs import clean_text  # noqa: E402

OFFLINE_DIR = os.path.join(ROOT, "offline")
DIST_DIR = os.path.join(OFFLINE_DIR, "dist")

EDITIONS = {
    "kjv": "King James Version (Oxford 1769)",
    "kj16": "King James Version (1611 Original)",
    "gen": "Geneva Bible (1599)",
}

# Geneva abbreviated tokens -> full canonical names.
GEN_ABBR_TO_FULL = {
    "1Chr": "1 Chronicles", "1Cor": "1 Corinthians", "1John": "1 John",
    "1Kgs": "1 Kings", "1Pet": "1 Peter", "1Sam": "1 Samuel",
    "1Thess": "1 Thessalonians", "1Tim": "1 Timothy",
    "2Chr": "2 Chronicles", "2Cor": "2 Corinthians", "2John": "2 John",
    "2Kgs": "2 Kings", "2Pet": "2 Peter", "2Sam": "2 Samuel",
    "2Thess": "2 Thessalonians", "2Tim": "2 Timothy", "3John": "3 John",
    "Acts": "Acts", "Amos": "Amos", "Col": "Colossians", "Dan": "Daniel",
    "Deut": "Deuteronomy", "Eccl": "Ecclesiastes", "Eph": "Ephesians",
    "Esth": "Esther", "Exod": "Exodus", "Ezek": "Ezekiel", "Ezra": "Ezra",
    "Gal": "Galatians", "Gen": "Genesis", "Hab": "Habakkuk", "Hag": "Haggai",
    "Heb": "Hebrews", "Hos": "Hosea", "Isa": "Isaiah", "Jas": "James",
    "Jer": "Jeremiah", "Job": "Job", "Joel": "Joel", "John": "John",
    "Jonah": "Jonah", "Josh": "Joshua", "Jude": "Jude", "Judg": "Judges",
    "Lam": "Lamentations", "Lev": "Leviticus", "Luke": "Luke", "Mal": "Malachi",
    "Mark": "Mark", "Matt": "Matthew", "Mic": "Micah", "Nah": "Nahum",
    "Neh": "Nehemiah", "Num": "Numbers", "Obad": "Obadiah",
    "Phil": "Philippians", "Phlm": "Philemon", "Prov": "Proverbs",
    "Ps": "Psalm", "Rev": "Revelation", "Rom": "Romans", "Ruth": "Ruth",
    "Song": "Song of Solomon", "Titus": "Titus",
    "Zech": "Zechariah", "Zeph": "Zephaniah",
    # Geneva Apocrypha subset in this corpus:
    "1Macc": "1 Maccabees", "2Macc": "2 Maccabees", "Bar": "Baruch",
    "Jdt": "Judith", "Sir": "Ecclesiasticus", "Tob": "Tobit",
    "Wis": "Wisdom of Solomon",
}


def slug(book: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", book.lower()).strip("-")


def connect_ro(path: str) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)


def js_assign(target: str, payload: object) -> str:
    return f"{target}={json.dumps(payload, ensure_ascii=False, separators=(',', ':'))};"


def main() -> None:
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(os.path.join(DIST_DIR, "data"))

    index: dict = {"editions": {}, "srcLang": {}}

    for ed, name in EDITIONS.items():
        db_path = os.path.join(ROOT, "data", "bible_versions", f"{ed}.db")
        con = connect_ro(db_path)
        rows = con.execute("SELECT reference, text FROM bible ORDER BY id").fetchall()
        con.close()

        books: dict[str, dict[str, dict[str, str]]] = {}
        order: list[str] = []
        for reference, text in rows:
            parts = reference.split(":")
            if len(parts) != 4:
                continue
            _, book, chapter, verse = parts
            if ed == "gen":
                book = GEN_ABBR_TO_FULL.get(book, book)
            elif book == "Psalms":
                # KJV and KJ1611 store "Psalms"; canonical key is "Psalm"
                # (matches the source DBs and the hosted reader).
                book = "Psalm"
            cleaned = clean_text(text)
            if not cleaned:
                continue
            if book not in books:
                books[book] = {}
                order.append(book)
            books[book].setdefault(chapter, {})[verse] = cleaned

        ed_dir = os.path.join(DIST_DIR, "data", ed)
        os.makedirs(ed_dir)
        chapters: dict[str, dict[str, int]] = {}
        for book in order:
            with open(os.path.join(ed_dir, slug(book) + ".js"), "w", encoding="utf-8") as f:
                f.write(f"window.VERSE_DATA=window.VERSE_DATA||{{}};VERSE_DATA.{ed}=VERSE_DATA.{ed}||{{}};")
                f.write(js_assign(f'VERSE_DATA.{ed}[{json.dumps(book)}]', books[book]))
                f.write("\n")
            chapters[book] = {
                ch: max(int(v) for v in verses) for ch, verses in books[book].items()
            }
        index["editions"][ed] = {"name": name, "order": order, "books": chapters}
        print(f"{ed}: {len(order)} books, {sum(len(v) for b in books.values() for v in b.values())} verses")

    # Original-language source shards (shared by both editions).
    src_dir = os.path.join(DIST_DIR, "data", "src")
    os.makedirs(src_dir)
    for language in ("hebrew", "greek"):
        db_path = os.path.join(ROOT, "data", "source", f"{language}.db")
        con = connect_ro(db_path)
        rows = con.execute("SELECT book, chapter, verse, text, translit FROM verses").fetchall()
        con.close()
        per_book: dict[str, dict] = {}
        for book, chapter, verse, text, translit in rows:
            cleaned = clean_text(text or "")
            if not cleaned:
                continue
            per_book.setdefault(book, {}).setdefault(str(chapter), {})[str(verse)] = [
                cleaned, clean_text(translit or ""),
            ]
        for book, verses in per_book.items():
            path = os.path.join(src_dir, slug(book) + ".js")
            if os.path.exists(path):
                continue  # a book lives in exactly one source language
            with open(path, "w", encoding="utf-8") as f:
                f.write("window.VERSE_DATA=window.VERSE_DATA||{};VERSE_DATA.src=VERSE_DATA.src||{};")
                f.write(js_assign(f"VERSE_DATA.src[{json.dumps(book)}]", {"lang": language, "v": verses}))
                f.write("\n")
            index["srcLang"][book] = language
        print(f"{language}: {len(per_book)} books")

    with open(os.path.join(DIST_DIR, "data", "index.js"), "w", encoding="utf-8") as f:
        f.write("window.VERSE_INDEX=")
        f.write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")

    # Shell assets.
    shutil.copy(os.path.join(OFFLINE_DIR, "shell.html"), os.path.join(DIST_DIR, "index.html"))
    shutil.copy(os.path.join(OFFLINE_DIR, "app.js"), os.path.join(DIST_DIR, "app.js"))
    shutil.copy(os.path.join(ROOT, "static", "styles.css"), os.path.join(DIST_DIR, "styles.css"))
    shutil.copy(os.path.join(ROOT, "static", "favicon.svg"), os.path.join(DIST_DIR, "favicon.svg"))

    total = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, _, fns in os.walk(DIST_DIR) for f in fns
    )
    nfiles = sum(len(fns) for _, _, fns in os.walk(DIST_DIR))
    print(f"dist/: {nfiles} files, {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
