# Verse

A single-verse terminal Bible reader with original-language source text,
backed entirely by local SQLite databases. Self-contained — no runtime
dependency on Lex or any other project.

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

Requires Python 3 with `rich`.

```sh
pip3 install rich
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
