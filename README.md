# Verse

A small terminal Bible verse reader backed by local SQLite editions.

```sh
verse -B kjv "John 3:16"
verse -B gen "1 John 1:1"
```

The launcher expects Python with `rich` installed. Place edition databases in
`data/bible_versions/`; each database must contain `metadata` and `bible`
tables. Bible database files are intentionally excluded from this repository.
