"""SQLite-backed access to the Bible editions bundled with Verse."""

from pathlib import Path
import sqlite3


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "bible_versions"
SOURCE_DIR = Path(__file__).resolve().parent.parent / "data" / "source"


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    """Open a bundled database without creating journal or shared-memory files."""
    return sqlite3.connect(f"{db_path.as_uri()}?mode=ro&immutable=1", uri=True)


def _load_editions() -> dict[str, str]:
    editions = {}
    for db_path in sorted(DATA_DIR.glob("*.db")):
        edition = db_path.stem.lower()
        try:
            with _connect_readonly(db_path) as connection:
                row = connection.execute(
                    "SELECT value FROM metadata WHERE key = 'edition_name'"
                ).fetchone()
        except sqlite3.Error:
            continue
        editions[edition] = row[0] if row else edition.upper()
    return editions


EDITIONS = _load_editions()


def list_editions() -> list[str]:
    return list(EDITIONS)


BOOK_TO_ABBR = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
    "Deuteronomy": "Deut", "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth",
    "1 Samuel": "1Sam", "2 Samuel": "2Sam", "1 Kings": "1Kgs", "2 Kings": "2Kgs",
    "1 Chronicles": "1Chr", "2 Chronicles": "2Chr", "Ezra": "Ezra", "Nehemiah": "Neh",
    "Esther": "Esth", "Job": "Job", "Psalm": "Ps", "Proverbs": "Prov",
    "Ecclesiastes": "Eccl", "Song of Solomon": "Song", "Isaiah": "Isa", "Jeremiah": "Jer",
    "Lamentations": "Lam", "Ezekiel": "Ezek", "Daniel": "Dan", "Hosea": "Hos",
    "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad", "Jonah": "Jonah",
    "Micah": "Mic", "Nahum": "Nah", "Habakkuk": "Hab", "Zephaniah": "Zeph",
    "Haggai": "Hag", "Zechariah": "Zech", "Malachi": "Mal",
    "Matthew": "Matt", "Mark": "Mark", "Luke": "Luke", "John": "John",
    "Acts": "Acts", "Romans": "Rom",
    "1 Corinthians": "1Cor", "2 Corinthians": "2Cor", "Galatians": "Gal",
    "Ephesians": "Eph", "Philippians": "Phil", "Colossians": "Col",
    "1 Thessalonians": "1Thess", "2 Thessalonians": "2Thess",
    "1 Timothy": "1Tim", "2 Timothy": "2Tim", "Titus": "Titus",
    "Philemon": "Phlm", "Hebrews": "Heb",
    "James": "Jas", "1 Peter": "1Pet", "2 Peter": "2Pet",
    "1 John": "1John", "2 John": "2John", "3 John": "3John",
    "Jude": "Jude", "Revelation": "Rev",
}


def _try_reference(connection, reference: str) -> tuple | None:
    row = connection.execute(
        "SELECT text FROM bible WHERE reference = ?", (reference,)
    ).fetchone()
    if row is None:
        row = connection.execute(
            """SELECT text FROM bible
               WHERE replace(reference, ' ', '') = replace(?, ' ', '')
                     COLLATE NOCASE
               LIMIT 1""",
            (reference,),
        ).fetchone()
    return row


def _abbreviate_ref(reference: str) -> str:
    parts = reference.split(":", 2)
    if len(parts) != 3:
        return reference
    edition, book, rest = parts
    abbr = BOOK_TO_ABBR.get(book)
    if abbr:
        return f"{edition}:{abbr}:{rest}"
    return reference


def _reference_candidates(reference: str) -> list[str]:
    """Return equivalent database spellings for a canonical reference."""
    candidates: list[str] = []
    for candidate in (reference, _abbreviate_ref(reference)):
        candidates.extend(
            (
                candidate,
                candidate.replace(":Psalm:", ":Psalms:"),
                candidate.replace(":Psalms:", ":Psalm:"),
            )
        )
    return list(dict.fromkeys(candidates))


def get_verse(edition: str, reference: str) -> str | None:
    """Return an exact verse, tolerating case and spacing differences."""
    db_path = DATA_DIR / f"{edition}.db"
    if edition not in EDITIONS or not db_path.is_file():
        return None

    row = None
    with _connect_readonly(db_path) as connection:
        for candidate in _reference_candidates(reference):
            row = _try_reference(connection, candidate)
            if row is not None:
                break
    return row[0] if row else None


def get_source(book: str, chapter: int, verse: int) -> tuple[str, str, str] | None:
    """Return (text, translit, language) for the original-language verse, or None.

    Hebrew is used for the Old Testament and Greek for the New Testament.
    """
    if book == "Psalms":
        book = "Psalm"
    for language in ("hebrew", "greek"):
        db_path = SOURCE_DIR / f"{language}.db"
        if not db_path.is_file():
            continue
        with _connect_readonly(db_path) as connection:
            row = connection.execute(
                "SELECT text, translit FROM verses"
                " WHERE book = ? AND chapter = ? AND verse = ?",
                (book, chapter, verse),
            ).fetchone()
        if row:
            return (row[0], row[1], language)
    return None


def get_neighbor(
    edition: str, reference: str, direction: int
) -> tuple[str, str] | None:
    """Return the previous or next verse in database order."""
    db_path = DATA_DIR / f"{edition}.db"
    if edition not in EDITIONS or direction not in (-1, 1):
        return None

    with _connect_readonly(db_path) as connection:
        current = None
        for candidate in _reference_candidates(reference):
            current = connection.execute(
                """SELECT id FROM bible
                   WHERE replace(reference, ' ', '') = replace(?, ' ', '')
                         COLLATE NOCASE
                   LIMIT 1""",
                (candidate,),
            ).fetchone()
            if current is not None:
                break
        if current is None:
            return None

        operator, ordering = (">", "ASC") if direction > 0 else ("<", "DESC")
        row = connection.execute(
            f"""SELECT reference, text FROM bible
                WHERE id {operator} ? AND reference NOT LIKE '%:0'
                ORDER BY id {ordering}
                LIMIT 1""",
            (current[0],),
        ).fetchone()
    return (row[0], row[1]) if row else None
