"""SQLite-backed access to the Bible editions bundled with Verse."""

from pathlib import Path
import sqlite3


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "bible_versions"


def _load_editions() -> dict[str, str]:
    editions = {}
    for db_path in sorted(DATA_DIR.glob("*.db")):
        edition = db_path.stem.lower()
        try:
            with sqlite3.connect(db_path) as connection:
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


def get_verse(edition: str, reference: str) -> str | None:
    """Return an exact verse, tolerating case and spacing differences."""
    db_path = DATA_DIR / f"{edition}.db"
    if edition not in EDITIONS or not db_path.is_file():
        return None

    with sqlite3.connect(db_path) as connection:
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
    return row[0] if row else None
