#!/usr/bin/env python3
"""Shared book-name and text helpers for the Verse web reader.

Extracted from the `verse` CLI so this repo stays web-only.
"""

from __future__ import annotations

import re


NORM_RE = re.compile(r"[^a-z0-9]+")

TSK_BOOK_ABBR = {
    "Genesis": "Ge.", "Exodus": "Ex.", "Leviticus": "Le.", "Numbers": "Nu.",
    "Deuteronomy": "De.", "Joshua": "Jos.", "Judges": "Jdg.", "Ruth": "Ru.",
    "1 Samuel": "1Sa.", "2 Samuel": "2Sa.", "1 Kings": "1Ki.", "2 Kings": "2Ki.",
    "1 Chronicles": "1Ch.", "2 Chronicles": "2Ch.", "Ezra": "Ezr.", "Nehemiah": "Neh.",
    "Esther": "Est.", "Job": "Job.", "Psalm": "Ps.", "Proverbs": "Pr.",
    "Ecclesiastes": "Ec.", "Song of Solomon": "So.", "Isaiah": "Is.", "Jeremiah": "Jer.",
    "Lamentations": "La.", "Ezekiel": "Eze.", "Daniel": "Da.", "Hosea": "Hos.",
    "Joel": "Joe.", "Amos": "Am.", "Obadiah": "Ob.", "Jonah": "Jon.",
    "Micah": "Mic.", "Nahum": "Nah.", "Habakkuk": "Hab.", "Zephaniah": "Zep.",
    "Haggai": "Hag.", "Zechariah": "Zec.", "Malachi": "Mal.",
    "Matthew": "Mt.", "Mark": "Mk.", "Luke": "Lk.", "John": "Jn.",
    "Acts": "Ac.", "Romans": "Ro.", "1 Corinthians": "1Co.", "2 Corinthians": "2Co.",
    "Galatians": "Ga.", "Ephesians": "Eph.", "Philippians": "Php.", "Colossians": "Col.",
    "1 Thessalonians": "1Th.", "2 Thessalonians": "2Th.",
    "1 Timothy": "1Ti.", "2 Timothy": "2Ti.", "Titus": "Tit.", "Philemon": "Phm.",
    "Hebrews": "Heb.", "James": "Jas.", "1 Peter": "1Pe.", "2 Peter": "2Pe.",
    "1 John": "1Jn.", "2 John": "2Jn.", "3 John": "3Jn.", "Jude": "Jude.",
    "Revelation": "Re.",
}

BIBLE_BOOKS = list(TSK_BOOK_ABBR)

BOOK_ALIASES = {}
for book in BIBLE_BOOKS:
    low = book.lower()
    book_key = NORM_RE.sub("-", low).strip("-")
    compact_key = NORM_RE.sub("", low)
    BOOK_ALIASES[book_key] = book
    BOOK_ALIASES[compact_key] = book
    abbr = TSK_BOOK_ABBR.get(book, "").rstrip(".").lower()
    if abbr:
        BOOK_ALIASES[NORM_RE.sub("-", abbr).strip("-")] = book
        BOOK_ALIASES[NORM_RE.sub("", abbr)] = book

BOOK_ALIASES.update({
    "ge": "Genesis", "gn": "Genesis", "gen": "Genesis",
    "ex": "Exodus", "exo": "Exodus", "exod": "Exodus",
    "le": "Leviticus", "lev": "Leviticus",
    "nu": "Numbers", "num": "Numbers",
    "de": "Deuteronomy", "dt": "Deuteronomy", "deut": "Deuteronomy",
    "jos": "Joshua", "josh": "Joshua",
    "jdg": "Judges", "judg": "Judges",
    "ru": "Ruth",
    "1sa": "1 Samuel", "1sam": "1 Samuel",
    "2sa": "2 Samuel", "2sam": "2 Samuel",
    "1ki": "1 Kings", "1kgs": "1 Kings",
    "2ki": "2 Kings", "2kgs": "2 Kings",
    "1ch": "1 Chronicles", "1chr": "1 Chronicles",
    "2ch": "2 Chronicles", "2chr": "2 Chronicles",
    "ezr": "Ezra", "neh": "Nehemiah", "est": "Esther",
    "ps": "Psalm", "psa": "Psalm", "psalm": "Psalm", "psalms": "Psalm",
    "pr": "Proverbs", "pro": "Proverbs", "prov": "Proverbs",
    "ec": "Ecclesiastes", "ecc": "Ecclesiastes", "eccl": "Ecclesiastes",
    "song": "Song of Solomon", "sos": "Song of Solomon", "canticles": "Song of Solomon",
    "is": "Isaiah", "isa": "Isaiah",
    "jr": "Jeremiah", "jer": "Jeremiah",
    "lam": "Lamentations",
    "eze": "Ezekiel", "ezek": "Ezekiel", "ezk": "Ezekiel",
    "da": "Daniel", "dn": "Daniel", "dan": "Daniel",
    "hos": "Hosea",
    "jl": "Joel",
    "am": "Amos",
    "ob": "Obadiah", "obad": "Obadiah",
    "jon": "Jonah",
    "mi": "Micah", "mic": "Micah",
    "na": "Nahum", "nah": "Nahum",
    "hab": "Habakkuk",
    "zep": "Zephaniah", "zeph": "Zephaniah",
    "hag": "Haggai",
    "zec": "Zechariah", "zech": "Zechariah",
    "mal": "Malachi",
    "mt": "Matthew", "mat": "Matthew", "matt": "Matthew",
    "mk": "Mark", "mrk": "Mark",
    "lk": "Luke", "lu": "Luke",
    "jn": "John", "jhn": "John", "joh": "John",
    "ac": "Acts",
    "ro": "Romans", "rom": "Romans",
    "1co": "1 Corinthians", "1cor": "1 Corinthians",
    "2co": "2 Corinthians", "2cor": "2 Corinthians",
    "gal": "Galatians",
    "eph": "Ephesians",
    "php": "Philippians", "phil": "Philippians",
    "col": "Colossians",
    "1th": "1 Thessalonians", "1thess": "1 Thessalonians",
    "2th": "2 Thessalonians", "2thess": "2 Thessalonians",
    "1ti": "1 Timothy", "1tim": "1 Timothy",
    "2ti": "2 Timothy", "2tim": "2 Timothy",
    "tit": "Titus",
    "phm": "Philemon", "phlm": "Philemon",
    "heb": "Hebrews",
    "jas": "James", "jam": "James",
    "1pe": "1 Peter", "1pet": "1 Peter",
    "2pe": "2 Peter", "2pet": "2 Peter",
    "1jn": "1 John", "1jhn": "1 John",
    "2jn": "2 John", "2jhn": "2 John",
    "3jn": "3 John", "3jhn": "3 John",
    "rev": "Revelation", "rv": "Revelation", "re": "Revelation", "revelations": "Revelation",
    # Apocrypha present in the Geneva 1587 and KJ1611 corpora.
    "tob": "Tobit", "tobit": "Tobit",
    "jdt": "Judith", "judith": "Judith",
    "wis": "Wisdom of Solomon", "wisdomofsolomon": "Wisdom of Solomon",
    "sir": "Ecclesiasticus", "ecclesiasticus": "Ecclesiasticus", "sirach": "Ecclesiasticus",
    "bar": "Baruch", "baruch": "Baruch",
    "1macc": "1 Maccabees", "1maccabees": "1 Maccabees",
    "2macc": "2 Maccabees", "2maccabees": "2 Maccabees",
})


def normalize_book(book: str) -> str:
    compact = NORM_RE.sub("", book.lower())
    return BOOK_ALIASES.get(compact, book.title())


def clean_text(text: str) -> str:
    text = re.sub(r"\\par\b", " ", text)
    text = re.sub(r"\{\\cf\d+\s+([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+\d*\s?", "", text)
    text = re.sub(r"[\[<][GH]\d+[>\]]", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[\[", "[", text)
    text = re.sub(r"\]\]", "]", text)
    text = re.sub(r"\*[a-z]+", "", text)
    text = re.sub(r"\byourln\b", "your", text, flags=re.IGNORECASE)
    text = re.sub(r"\bonld\b", "on", text, flags=re.IGNORECASE)
    text = re.sub(r"\[/?[a-z]+\]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()
