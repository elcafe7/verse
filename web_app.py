#!/usr/bin/env python3
"""Browser application for Verse's bundled SQLite Bible editions."""

from __future__ import annotations

import re
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from core.db import EDITIONS, get_neighbor, get_source, get_verse, list_editions
from verse import BIBLE_BOOKS, clean_text, normalize_book


REFERENCE_RE = re.compile(r"(.+?)\s+(\d+)(?:[:.\s]+)(\d+)")


def parse_web_reference(raw_reference: str) -> tuple[str, int, int]:
    """Return a canonical book, chapter, and verse from human input."""
    match = REFERENCE_RE.fullmatch(raw_reference.strip())
    if not match:
        raise ValueError("Use a reference such as John 3:16.")

    raw_book, raw_chapter, raw_verse = match.groups()
    book = normalize_book(raw_book.strip())
    chapter = int(raw_chapter)
    verse = int(raw_verse)
    if chapter < 1 or verse < 1:
        raise ValueError("Chapter and verse numbers must be greater than zero.")
    return book, chapter, verse


def split_database_reference(reference: str) -> tuple[str, str, int, int]:
    """Split an edition:Book:Chapter:Verse database reference."""
    edition, book, chapter, verse = reference.split(":", 3)
    return edition, book, int(chapter), int(verse)


def reference_payload(reference: str) -> dict[str, object]:
    edition, book, chapter, verse = split_database_reference(reference)
    display_book = normalize_book(book)
    return {
        "canonical": reference,
        "edition": edition,
        "book": display_book,
        "chapter": chapter,
        "verse": verse,
        "display": f"{display_book} {chapter}:{verse}",
    }


def neighbor_payload(edition: str, reference: str, direction: int) -> dict | None:
    neighbor = get_neighbor(edition, reference, direction)
    if neighbor is None:
        return None
    neighbor_reference, _ = neighbor
    return reference_payload(neighbor_reference)


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    asset_files = (Path(app.static_folder) / name for name in ("styles.css", "app.js", "favicon.svg"))
    app.config.from_mapping(
        JSON_SORT_KEYS=False,
        ASSET_VERSION=max(int(path.stat().st_mtime) for path in asset_files),
    )
    if test_config:
        app.config.update(test_config)

    @app.after_request
    def add_response_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; connect-src 'self'; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        if request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=3600"
        return response

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(status="ok", editions=len(EDITIONS))

    @app.get("/api/editions")
    def editions():
        return jsonify(
            editions=[
                {"id": edition, "name": EDITIONS[edition]}
                for edition in list_editions()
            ]
        )

    @app.get("/api/books")
    def books():
        query = request.args.get("q", "").strip().lower()
        if not query or len(query) > 40:
            return jsonify(books=[])

        normalized_query = re.sub(r"[^a-z0-9]+", "", query)
        if not normalized_query:
            return jsonify(books=[])

        def rank(book: str) -> tuple[int, int, str]:
            normalized_book = re.sub(r"[^a-z0-9]+", "", book.lower())
            if normalized_book.startswith(normalized_query):
                return (0, len(book), book)
            if normalized_query in normalized_book:
                return (1, len(book), book)
            return (2, len(book), book)

        matches = [book for book in BIBLE_BOOKS if rank(book)[0] < 2]
        matches.sort(key=rank)
        return jsonify(books=matches[:8])

    @app.get("/api/verse")
    def verse():
        edition = request.args.get("edition", "gen").strip().lower()
        raw_reference = request.args.get("reference", "John 3:16")
        include_source = request.args.get("source", "0").lower() in {
            "1",
            "true",
            "yes",
        }

        if edition not in EDITIONS:
            return (
                jsonify(
                    error=f"Unknown edition '{edition}'.",
                    editions=list_editions(),
                ),
                400,
            )

        try:
            book, chapter, verse_number = parse_web_reference(raw_reference)
        except ValueError as error:
            return jsonify(error=str(error)), 400

        database_reference = f"{edition}:{book}:{chapter}:{verse_number}"
        verse_text = get_verse(edition, database_reference)
        if verse_text is None:
            return (
                jsonify(
                    error=f"Verse not found in {edition.upper()}.",
                    reference=f"{book} {chapter}:{verse_number}",
                ),
                404,
            )

        payload: dict[str, object] = {
            "reference": reference_payload(database_reference),
            "edition": {"id": edition, "name": EDITIONS[edition]},
            "text": clean_text(verse_text),
            "neighbors": {
                "previous": neighbor_payload(edition, database_reference, -1),
                "next": neighbor_payload(edition, database_reference, 1),
            },
            "source": None,
        }

        if include_source:
            source = get_source(book, chapter, verse_number)
            if source:
                source_text, transliteration, language = source
                payload["source"] = {
                    "language": language,
                    "label": language.title(),
                    "text": clean_text(source_text),
                    "transliteration": clean_text(transliteration),
                }

        return jsonify(payload)

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify(error="API endpoint not found."), 404
        return render_template("index.html"), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
