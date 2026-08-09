#!/usr/bin/env python3
"""Build verse's self-contained Greek (NT) and Hebrew (OT) source DBs.

Extracts per-verse original-language text from the Lex ESV interlinear JSON
(build-time source only; runtime verse never reads Lex data).
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

NT_BOOKS = {
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
    "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation",
}

LEX_INTERLINEAR = Path(
    "/Users/nate3/lex/runtime-data/esv-data/data/esv/esv-interlinear.json"
)
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "source"


def main() -> int:
    if not LEX_INTERLINEAR.is_file():
        print(f"missing source: {LEX_INTERLINEAR}", file=sys.stderr)
        return 1

    with open(LEX_INTERLINEAR, encoding="utf-8") as f:
        verses = json.load(f)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    greek_db = sqlite3.connect(OUT_DIR / "greek.db")
    hebrew_db = sqlite3.connect(OUT_DIR / "hebrew.db")
    for db in (greek_db, hebrew_db):
        db.execute("DROP TABLE IF EXISTS verses")
        db.execute(
            """CREATE TABLE verses (
                book TEXT NOT NULL,
                chapter INTEGER NOT NULL,
                verse INTEGER NOT NULL,
                text TEXT NOT NULL,
                translit TEXT NOT NULL DEFAULT '',
                strongs TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (book, chapter, verse)
            )"""
        )

    counts = {"greek": 0, "hebrew": 0}

    for entry in verses:
        ref = entry.get("r", "")
        parts = ref.split(":")
        if len(parts) != 4:
            continue
        book = parts[1]
        if book not in NT_BOOKS and not re.match(r"^(Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|1 Samuel|2 Samuel|1 Kings|2 Kings|1 Chronicles|2 Chronicles|Ezra|Nehemiah|Esther|Job|Psalm|Proverbs|Ecclesiastes|Song of Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi)$", book):
            continue
        chapter, verse = int(parts[2]), int(parts[3])
        if verse == 0:
            continue

        words = []
        translit = []
        strongs = []
        for token in entry.get("p", []):
            fields = token.split("|")
            while len(fields) < 11:
                fields.append("")
            surface = fields[6]
            if surface in {"", "→", "←", "•"}:
                continue
            words.append(surface)
            if fields[7]:
                translit.append(fields[7])
            if fields[3]:
                strongs.append(fields[3].upper())

        language = "hebrew" if book not in NT_BOOKS else "greek"
        if not words:
            continue
        db = greek_db if language == "greek" else hebrew_db
        db.execute(
            """INSERT OR REPLACE INTO verses (book, chapter, verse, text, translit, strongs)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                book,
                chapter,
                verse,
                " ".join(words),
                " ".join(translit),
                " ".join(strongs),
            ),
        )
        counts[language] += 1

    for db in (greek_db, hebrew_db):
        db.commit()
        db.close()

    print(
        f"greek.db: {counts['greek']} verses, "
        f"hebrew.db: {counts['hebrew']} verses -> {OUT_DIR}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
