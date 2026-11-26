#!/usr/bin/env python3
"""Atheris fuzz harness for Verse reference and text handling.

Targets the code that touches untrusted input (the reference typed into the
URL or search box, and verse text read from the databases):
- web_app.parse_web_reference: "John 3:16" style input; only ValueError allowed
- web_app.split_database_reference: edition:Book:Chapter:Verse; only ValueError allowed
- verse.normalize_book / verse.clean_text: never raise, always return str
- core.db._reference_candidates: equivalent database spellings, never empty

Any other exception, or a broken invariant (asserted below), is a crash and
fails the fuzz job. Same pattern as the Lex CLI fuzz harnesses.

Run locally (Linux x86-64, Python 3.12+):
    python3 -m venv .fuzz-venv
    .fuzz-venv/bin/pip install --require-hashes --no-deps -r .github/requirements/fuzz-requirements.txt
    cp -R fuzz/corpus/refs /tmp/corpus-refs
    .fuzz-venv/bin/python fuzz/fuzz_refs.py /tmp/corpus-refs -max_total_time=60
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.db import _reference_candidates  # noqa: E402
from verse import clean_text, normalize_book  # noqa: E402
from web_app import parse_web_reference, split_database_reference  # noqa: E402

MAX_CHARS = 512


def require(condition, detail=None):
    """Raise on a broken fuzz invariant, including under optimized Python."""
    if not condition:
        raise AssertionError(detail)


def check_text(text):
    """Run every helper on one string and assert its invariants."""
    try:
        book, chapter, verse = parse_web_reference(text)
    except ValueError:
        pass
    else:
        require(isinstance(book, str) and book, text)
        require(chapter >= 1 and verse >= 1, text)

    try:
        edition, book, chapter, verse = split_database_reference(text)
    except ValueError:
        pass
    else:
        require(isinstance(edition, str) and isinstance(book, str), text)

    require(isinstance(normalize_book(text), str))
    require(isinstance(clean_text(text), str))
    candidates = _reference_candidates(text)
    require(candidates and text in candidates, (text, candidates))
    require(len(set(candidates)) == len(candidates), candidates)


def test_one_input(data):
    check_text(data.decode("utf-8", errors="replace")[:MAX_CHARS])


def main():
    import atheris

    atheris.instrument_all()
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
