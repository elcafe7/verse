#!/usr/bin/env python3
"""Verse: single-verse rich Bible reader (English editions from Lex)."""

import argparse
import os
import re
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.text import Text
import rich.box
from core.db import list_editions, get_verse, EDITIONS

CONFIG_DIR = os.path.expanduser("~/.config/verse")
DEFAULT_FILE = os.path.join(CONFIG_DIR, "default.txt")
console = Console()

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
    table = Table(title="[bold magenta]Select Bible Edition[/bold magenta]", box=rich.box.DOUBLE_EDGE, title_style="italic")
    table.add_column("#", style="cyan")
    table.add_column("Edition", style="green")
    table.add_column("File", style="dim")
    for i, ed in enumerate(editions, 1):
        table.add_row(str(i), ed.upper(), EDITIONS[ed])
    console.print(table)

    choice = IntPrompt.ask("Select edition (number)", default=1)
    if 1 <= choice <= len(editions):
        return editions[choice - 1]
    console.print("[red]Invalid choice[/]")
    sys.exit(1)


def parse_reference(raw_reference: str, requested_edition: str | None) -> tuple[str, str]:
    """Normalize common reference forms to edition:Book:Chapter:Verse."""
    raw_reference = raw_reference.strip()
    prefixed = re.fullmatch(r"([A-Za-z0-9]+):(.+):(\d+):(\d+)", raw_reference)
    if prefixed:
        embedded_edition, book, chapter, verse = prefixed.groups()
        embedded_edition = embedded_edition.lower()
        if requested_edition and requested_edition != embedded_edition:
            raise ValueError(
                f"reference uses {embedded_edition}, but --bible specifies {requested_edition}"
            )
        edition = embedded_edition
    else:
        plain = re.fullmatch(r"(.+?)\s+(\d+)(?::|\s+)(\d+)", raw_reference)
        if not plain:
            raise ValueError("reference must look like 'John 3:16'")
        book, chapter, verse = plain.groups()
        if requested_edition is None:
            raise ValueError("no Bible edition selected")
        edition = requested_edition

    if edition not in EDITIONS:
        raise ValueError(
            f"unknown edition '{edition}' (choose from: {', '.join(EDITIONS)})"
        )
    return edition, f"{edition}:{book.strip()}:{chapter}:{verse}"

def main():
    parser = argparse.ArgumentParser(description="Single-verse Bible reader")
    parser.add_argument("reference", nargs="*", help="Reference e.g. John 3:16 or esv:John:3:16")
    parser.add_argument("-B", "--bible", help="Edition (esv,nasb,kjv,gen,kj16)")
    args = parser.parse_args()

    requested_edition = args.bible.lower() if args.bible else None
    if requested_edition and requested_edition not in EDITIONS:
        parser.error(
            f"unknown edition '{requested_edition}' (choose from: {', '.join(EDITIONS)})"
        )

    edition = requested_edition or get_default_edition()
    if edition is None:
        edition = choose_edition()
        set_default_edition(edition)
        console.print(f"[green]Default saved: {edition}[/]")

    ref_input = None
    if not args.reference:
        ref_input = Prompt.ask(f"Enter reference (e.g. John 3:16, using {edition.upper()} as default edition)")
        if not ref_input:
            console.print("[red]No reference provided. Exiting.[/]")
            sys.exit(1)
        ref = ref_input
    else:
        ref = " ".join(args.reference)

    try:
        edition, ref = parse_reference(ref, requested_edition or edition)
    except ValueError as error:
        parser.error(str(error))

    text = get_verse(edition, ref)
    if text:
        panel = Panel(Text(text, style="italic yellow"), title=ref, border_style="blue")
        console.print(panel)
    else:
        console.print(f"[red]Verse not found: {ref}[/]")
        sys.exit(1)

if __name__ == "__main__":
    main()
