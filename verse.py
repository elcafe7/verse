#!/usr/bin/env python3
"""Verse: single-verse rich Bible reader (bundled English editions)."""

import argparse
import os
import re
import subprocess
import sys
import termios
import tty

import rich.box
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from core.db import EDITIONS, get_neighbor, get_source, get_verse, list_editions

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
    "ps": "Psalm", "psa": "Psalm", "psalm": "Psalm",
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
})


def normalize_book(book: str) -> str:
    compact = NORM_RE.sub("", book.lower())
    return BOOK_ALIASES.get(compact, book.title())

CONFIG_DIR = os.path.expanduser("~/.config/verse")
DEFAULT_FILE = os.path.join(CONFIG_DIR, "default.txt")
THEME_FILE = os.path.join(CONFIG_DIR, "theme.txt")


def load_saved_theme() -> str | None:
    try:
        with open(THEME_FILE, encoding="utf-8") as theme_file:
            theme = theme_file.read().strip()
        return theme if theme in {"light", "dark"} else None
    except OSError:
        return None


def save_theme_preference(theme_mode: str | None) -> None:
    try:
        if theme_mode is None:
            try:
                os.remove(THEME_FILE)
            except OSError:
                pass
        else:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(THEME_FILE, "w", encoding="utf-8") as theme_file:
                theme_file.write(theme_mode + "\n")
    except OSError:
        pass


def detect_terminal_theme() -> str:
    colorfgbg = os.environ.get("COLORFGBG", "")
    if colorfgbg:
        try:
            background = int(colorfgbg.split(";")[-1])
            return "light" if background in range(7, 16) else "dark"
        except ValueError:
            pass

    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=0.5,
                check=False,
            )
            return (
                "dark"
                if result.returncode == 0 and result.stdout.strip().lower() == "dark"
                else "light"
            )
        except (OSError, subprocess.SubprocessError):
            pass
    return "dark"


def resolve_theme_mode(raw_arguments: list[str]) -> str:
    if "-light" in raw_arguments:
        return "light"
    if "-dark" in raw_arguments:
        return "dark"
    if "-auto" in raw_arguments:
        return detect_terminal_theme()
    environment_theme = os.environ.get("LEX_THEME", "").strip().lower()
    if environment_theme in {"light", "dark"}:
        return environment_theme
    saved_theme = load_saved_theme()
    if saved_theme in {"light", "dark"}:
        return saved_theme
    return detect_terminal_theme()


def build_theme(theme_mode: str) -> Theme:
    if theme_mode == "light":
        text_style = "rgb(31,31,31)"
        strong_text_style = "bold rgb(31,31,31)"
        muted_text_style = "rgb(100,100,100)"
        accent_style = "rgb(180,30,40)"
        accent_strong_style = "bold rgb(180,30,40)"
        warning_style = "rgb(160,100,0)"
        border_style = "rgb(200,190,170)"
        reference_style = accent_strong_style
    else:
        text_style = "grey93"
        strong_text_style = "bold white"
        muted_text_style = "grey50"
        accent_style = "dark_orange"
        accent_strong_style = "bold dark_orange"
        warning_style = "bold sandy_brown"
        border_style = "grey27"
        reference_style = "bold orange3"

    return Theme(
        {
            "text": text_style,
            "text.strong": strong_text_style,
            "text.muted": muted_text_style,
            "ui.action": accent_style,
            "ui.action.key": accent_strong_style,
            "ui.border": border_style,
            "ui.meta": muted_text_style,
            "verse.ref": reference_style,
            "verse.text": text_style,
            "verse.border": border_style,
            "warning": warning_style,
        }
    )


class BackgroundFillWriter:
    def __init__(self, stream, fill_sequence: str):
        self.stream = stream
        self.fill_sequence = fill_sequence

    def write(self, data: str):
        if self.fill_sequence:
            data = data.replace("\n", f"{self.fill_sequence}\n")
        return self.stream.write(data)

    def flush(self):
        return self.stream.flush()

    def isatty(self):
        return self.stream.isatty()

    def __getattr__(self, name):
        return getattr(self.stream, name)


ACTIVE_THEME_MODE = resolve_theme_mode(sys.argv[1:])

def _build_style(mode: str) -> str:
    return (
        "rgb(31,31,31) on rgb(249,247,242)"
        if mode == "light"
        else "grey93 on grey11"
    )

def _build_fill(mode: str) -> str:
    if os.environ.get("LEX_NO_COLOR") or not sys.stdout.isatty():
        return ""
    return "\033[48;5;231m\033[K" if mode == "light" else "\033[40m\033[K"

BASE_STYLE = _build_style(ACTIVE_THEME_MODE)
FILL_SEQUENCE = _build_fill(ACTIVE_THEME_MODE)
console = Console(
    color_system="256",
    theme=build_theme(ACTIVE_THEME_MODE),
    style=BASE_STYLE,
    no_color=bool(os.environ.get("LEX_NO_COLOR")),
    file=BackgroundFillWriter(sys.stdout, FILL_SEQUENCE),
)

def rebuild_console(mode: str):
    global ACTIVE_THEME_MODE, BASE_STYLE, FILL_SEQUENCE, console
    ACTIVE_THEME_MODE = mode
    BASE_STYLE = _build_style(mode)
    FILL_SEQUENCE = _build_fill(mode)
    console = Console(
        color_system="256",
        theme=build_theme(mode),
        style=BASE_STYLE,
        no_color=bool(os.environ.get("LEX_NO_COLOR")),
        file=BackgroundFillWriter(sys.stdout, FILL_SEQUENCE),
    )

def get_default_edition() -> str | None:
    if os.path.exists(DEFAULT_FILE):
        with open(DEFAULT_FILE) as f:
            edition = f.read().strip()
            if edition in EDITIONS:
                return edition
    return None

def set_default_edition(edition: str):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(DEFAULT_FILE, "w") as f:
        f.write(edition)

def choose_edition() -> str:
    editions = list_editions()
    table = Table(
        title=Text("Select Bible Edition", style="verse.ref"),
        box=rich.box.SIMPLE_HEAVY,
        border_style="ui.border",
    )
    table.add_column("#", style="ui.meta")
    table.add_column("Edition", style="ui.action.key")
    table.add_column("Name", style="text")
    for i, ed in enumerate(editions, 1):
        table.add_row(str(i), ed.upper(), EDITIONS[ed])
    console.print(table)

    choice = IntPrompt.ask("Select edition (number)", default=1)
    if 1 <= choice <= len(editions):
        return editions[choice - 1]
    console.print("[warning]Invalid choice[/]")
    sys.exit(1)


def parse_reference(raw_reference: str, requested_edition: str | None) -> tuple[str, str]:
    """Normalize reference to edition:Book:Chapter:Verse."""
    raw_reference = raw_reference.strip()
    if requested_edition is None:
        raise ValueError("no Bible edition selected")
    if requested_edition not in EDITIONS:
        raise ValueError(
            f"unknown edition '{requested_edition}' (choose from: {', '.join(EDITIONS)})"
        )

    match = re.fullmatch(r"(.+?)\s+(\d+)(?:[:.\s]+)(\d+)", raw_reference)
    if not match:
        raise ValueError("reference must look like 'John 3:16', 'gen 1.1', or 'gen 1 1'")
    book, chapter, verse = match.groups()
    book = normalize_book(book.strip())
    return requested_edition, f"{requested_edition}:{book}:{chapter}:{verse}"


def read_navigation_key() -> str:
    """Read one navigation command without requiring Enter."""
    file_descriptor = sys.stdin.fileno()
    previous_settings = termios.tcgetattr(file_descriptor)
    try:
        tty.setraw(file_descriptor)
        key = sys.stdin.read(1)
        if key == "\x1b":
            key += sys.stdin.read(2)
        return key
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, previous_settings)


def pick_edition_interactive(current: str) -> str | None:
    """Arrow-key navigable edition picker. Returns new edition or None."""
    editions = list_editions()
    if not editions:
        return None
    idx = 0
    for i, ed in enumerate(editions):
        if ed == current:
            idx = i
            break

    while True:
        console.clear()
        lines = []
        for i, ed in enumerate(editions):
            name = EDITIONS[ed]
            prefix = " \u25b6 " if i == idx else "   "
            row = f"{prefix} {ed.upper():6s} {name}"
            lines.append(row)
        panel = Panel(
            "\n".join(lines),
            title="Select Bible Version",
            border_style="ui.action.key",
            padding=(1, 2),
        )
        console.print(Align.center(panel))
        console.print(
            "\n[ui.meta]\u2191\u2193 navigate  Enter select  Esc/q cancel[/]",
            justify="center",
        )

        key = read_navigation_key()
        if key in ("q", "\x1b", "\x03"):
            return None
        if key == "\x1b[A":  # up
            idx = (idx - 1) % len(editions)
        elif key == "\x1b[B":  # down
            idx = (idx + 1) % len(editions)
        elif key in ("\r", "\n"):
            return editions[idx]


def source_ref(ref: str) -> tuple[str, int, int] | None:
    """Extract (book, chapter, verse) from an edition-prefixed reference."""
    parts = ref.split(":")
    if len(parts) != 4:
        return None
    return parts[1], int(parts[2]), int(parts[3])


def source_panel(book: str, chapter: int, verse: int) -> Panel | None:
    source = get_source(book, chapter, verse)
    if not source:
        return None
    text, translit, language = source
    parts = [Align.center(Text(f"\u2500 {language.title()} \u2500", style="ui.meta"))]
    parts.append(Text(text, style="verse.text", justify="center"))
    if translit:
        parts.append(Text("", style="text"))
        parts.append(Text(translit, style="text.muted", justify="center"))
    panel_width = max(1, min(88, console.width - 4))
    return Panel(
        Group(*parts),
        border_style="verse.border",
        padding=(1, 3),
        width=panel_width,
    )


def render_verse(ref: str, verse_text: str, show_source_on: bool) -> None:
    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    if show_source_on:
        src = source_ref(ref)
        source = source_panel(*src) if src else None
        if source:
            stack = Group(verse_panel(ref, verse_text), source)
            if interactive:
                stack = Align.center(stack, vertical="middle", height=max(1, console.height - 2))
            console.print(stack)
            return
        console.print("[warning]No source data for this reference.[/]")
    show_verse(ref, verse_text, centered=interactive)


def format_ref(reference: str) -> str:
    parts = reference.split(":", 2)
    if len(parts) == 3:
        edition, book, chap_verse = parts
        return f"{book} {chap_verse} ({edition.upper()})"
    return reference

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

def verse_panel(reference: str, text: str) -> Panel:
    text = clean_text(text)
    verse = Text(text, style="verse.text", justify="center")
    panel_width = max(1, min(88, console.width - 4))
    return Panel(
        verse,
        title=Text(format_ref(reference), style="verse.ref"),
        border_style="verse.border",
        padding=(1, 3),
        width=panel_width,
    )

def show_verse(reference: str, text: str, *, centered: bool = False) -> None:
    panel = verse_panel(reference, text)
    if centered:
        viewport = Align.center(
            panel,
            vertical="middle",
            height=max(1, console.height - 2),
        )
        console.print(viewport)
    else:
        console.print(Align.center(panel))

def main():
    parser = argparse.ArgumentParser(description="Single-verse Bible reader")
    parser.add_argument("reference", nargs="*", help="Reference e.g. John 3:16 or esv:John:3:16")
    parser.add_argument("-v", "--version", help="Edition (esv,nasb,kjv,gen,kj16)")
    theme_group = parser.add_mutually_exclusive_group()
    theme_group.add_argument("-light", dest="theme_mode", action="store_const", const="light")
    theme_group.add_argument("-dark", dest="theme_mode", action="store_const", const="dark")
    theme_group.add_argument("-auto", dest="theme_mode", action="store_const", const="auto")
    args = parser.parse_args()

    if args.theme_mode == "auto":
        save_theme_preference(None)
    elif args.theme_mode:
        save_theme_preference(args.theme_mode)

    requested_edition = args.version.lower() if args.version else None
    if requested_edition and requested_edition not in EDITIONS:
        parser.error(
            f"unknown edition '{requested_edition}' (choose from: {', '.join(EDITIONS)})"
        )

    edition = requested_edition or get_default_edition()
    if edition is None:
        edition = choose_edition()
        set_default_edition(edition)
        console.print(f"[ui.action]Default saved: {edition}[/]")

    ref_input = None
    if not args.reference:
        ref_input = Prompt.ask(f"Enter reference (e.g. John 3:16, using {edition.upper()} as default edition)")
        if not ref_input:
            console.print("[warning]No reference provided. Exiting.[/]")
            sys.exit(1)
        ref = ref_input
    else:
        ref = " ".join(args.reference)

    try:
        edition, ref = parse_reference(ref, requested_edition or edition)
    except ValueError as error:
        parser.error(str(error))

    verse_text = get_verse(edition, ref)
    if not verse_text:
        console.print(f"[warning]Verse not found: {ref}[/]")
        sys.exit(1)

    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    source_on = False
    render_verse(ref, verse_text, source_on)
    if not interactive:
        return

    while True:
        current_theme = "light" if ACTIVE_THEME_MODE == "light" else "dark"
        other_theme = "dark" if current_theme == "light" else "light"
        source_hint = (
            "[ui.action.key]s[/] [ui.action.key]source on[/]"
            if source_on
            else "[ui.action.key]s[/] [ui.meta]source[/]"
        )
        console.print(
            "[ui.action.key]\u2190[/] [ui.meta]previous[/]  "
            "[ui.action.key]\u2192[/] [ui.meta]next[/]  "
            "[ui.action.key]t[/] [ui.meta]"
            + other_theme
            + "[/]  "
            "[ui.action.key]v[/] [ui.meta]version[/]  "
            + source_hint
            + "  "
            "[ui.action.key]q[/] [ui.meta]quit[/]",
            justify="center",
        )
        key = read_navigation_key()
        if key.lower() == "q" or key == "\x03":
            console.print()
            return
        if key.lower() == "t":
            new_mode = "light" if ACTIVE_THEME_MODE == "dark" else "dark"
            rebuild_console(new_mode)
            save_theme_preference(new_mode)
            console.clear()
            render_verse(ref, verse_text, source_on)
            continue
        if key.lower() == "s":
            source_on = not source_on
            console.clear()
            render_verse(ref, verse_text, source_on)
            continue
        if key.lower() == "v":
            new_edition = pick_edition_interactive(edition)
            if new_edition and new_edition != edition:
                edition = new_edition
                set_default_edition(edition)
                _, _, rest = ref.partition(":")
                ref = f"{edition}:{rest}"
                verse_text = get_verse(edition, ref)
                if not verse_text:
                    console.clear()
                    console.print("[warning]Verse not found in that edition.[/]")
                    continue
                console.clear()
                render_verse(ref, verse_text, source_on)
            else:
                console.clear()
                render_verse(ref, verse_text, source_on)
            continue
        direction = -1 if key in ("\x1b[D", "h") else 1 if key in ("\x1b[C", "l") else 0
        if not direction:
            continue

        neighbor = get_neighbor(edition, ref, direction)
        if neighbor is None:
            console.print("[warning]No more verses in that direction.[/]")
            continue
        ref, verse_text = neighbor
        console.clear()
        render_verse(ref, verse_text, source_on)

if __name__ == "__main__":
    main()
