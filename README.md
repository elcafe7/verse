# Verse

A single-verse terminal Bible reader with original-language source text,
backed entirely by local SQLite databases. Self-contained — no runtime
dependency on Lex or any other project.

Verse now includes two interfaces over the same bundled corpus:

- a responsive browser reader with shareable URLs, keyboard navigation,
  theme and edition controls, and Hebrew/Greek source panels;
- the original focused terminal reader.

```sh
verse -v kjv "John 3:16"
verse -v nasb "Psalm 23:1"
```

## Features

- **Five English editions** bundled: KJV, KJ1611 (`kj16`), Geneva 1587
  (`gen`), ESV, NASB — exact verse lookup with tolerant book aliases
  (`verse -v kjv "Psalm 23:1"`).
- **Original-language toggle** (`s` in interactive mode): shows the Hebrew
  (Old Testament) or Greek (New Testament) source verse with transliteration
  below the English text, aligned by chapter/verse.
- **Interactive navigation**: `←`/`→` previous/next verse, `t` light/dark
  theme, `v` edition picker, `s` source toggle, `q` quit. `s source on` is
  shown in the nav bar while active.
- Source output is stripped of markup (`[G1063]` Strong's markers, `<em>`,
  `[[ ]]` tituli, RTF tokens) for clean reading; KJV psalm superscriptions
  keep their printed brackets.

## Data

All data ships inside the repo (no download step):

| Path | Contents |
|------|----------|
| `data/bible_versions/*.db` | English editions (`metadata` + `bible` tables) |
| `data/source/greek.db` | NT Greek source text, 7,941 verses |
| `data/source/hebrew.db` | OT Hebrew source text, 23,145 verses |

The source DBs are extracted from the OpenScriptures ESV interlinear with
`scripts/build_source_db.py` (build-time only; runtime reads only verse data).

## Install

Requires Python 3. Install the shared CLI and web dependencies:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
ln -s "$PWD/verse.py" ~/.local/bin/verse   # or your own launcher
```

## Usage

```sh
verse -v kjv "John 3:16"    # one-shot read
verse                       # interactive: prompts for edition + reference
verse -v esv "Romans 8:28" -dark
```

Interactive keys: `←` `→` navigate · `t` theme · `v` version · `s` source ·
`q` quit

## Web app

Start the development server:

```sh
. .venv/bin/activate
flask --app web_app run --port 5050
```

Open `http://127.0.0.1:5050`. The browser UI supports the same five editions,
reference aliases, AJAX book-name suggestions, adjacent-verse navigation,
light/dark themes, persistent Minimalist Mode (`M`), and direct Hebrew or Greek
source display. Minimalist Mode leaves only the verse, floating navigation,
source control, and its own exit control. Geneva 1587 is the default web
edition. URLs retain the current edition, reference, and source-panel state so
a reading can be bookmarked or shared.

The production instance is mounted at `https://poeta.icu/verse/`. Reverse
proxies should strip the `/verse/` prefix before forwarding and send
`X-Forwarded-Prefix: /verse`; the application uses that header when generating
asset and navigation URLs.

For a production WSGI server:

```sh
gunicorn --workers 2 --bind 127.0.0.1:5050 web_app:app
```

The SQLite files are read-only at runtime. Place a reverse proxy in front of
Gunicorn for TLS and public deployment.

## Tests

```sh
. .venv/bin/activate
python -m unittest discover -s tests -v
```

## Offline HTML build

Going off-grid? Grab the offline HTML build (KJV + Geneva 1587 with
Apocrypha + Hebrew/Greek sources, no dependencies, no internet needed):

**[Download verse-offline-20260927.tar.gz](https://github.com/elcafe7/verse/releases/download/offline-20260927/verse-offline-20260927.tar.gz)**

```sh
tar -xzf verse-offline-20260927.tar.gz
xdg-open dist/index.html   # works over file://, USB stick, airplane mode
```

Built from the private `verse_web` repo (`offline/build_offline.py`, stdlib
only) and attached to the
[offline-20260927 release](https://github.com/elcafe7/verse/releases/tag/offline-20260927).
