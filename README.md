# Verse

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/elcafe7/verse/badge)](https://scorecard.dev/viewer/?uri=github.com/elcafe7/verse)
<!-- OpenSSF Best Practices badge slot: set PROJECT_ID and uncomment (security/MANUAL-STEPS.md)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/PROJECT_ID/badge)](https://www.bestpractices.dev/projects/PROJECT_ID)
-->
<!-- Socket.dev badge slot: set SOCKET_URL and uncomment (security/MANUAL-STEPS.md)
[![Socket](https://img.shields.io/badge/Socket.dev-monitored-blue)](SOCKET_URL)
-->

A single-verse terminal Bible reader with original-language source text,
backed entirely by local SQLite databases. Self-contained — no runtime
dependency on Lex or any other project.

Verse now includes two interfaces over the same bundled corpus:

- a responsive browser reader with shareable URLs, swipe and keyboard
  navigation, theme and edition controls, and Hebrew/Greek source panels;
- the original focused terminal reader.

```sh
verse -v kjv "John 3:16"
verse -v gen "Psalm 23:1"
```

## Offline HTML build

Going off-grid? Grab the offline HTML build (KJV + KJ1611 with Apocrypha +
Geneva 1599 with Apocrypha + Hebrew/Greek sources, no dependencies, no
internet needed):

**[Download verse-offline-20261023.tar.gz](https://github.com/elcafe7/verse/releases/download/offline-20261023/verse-offline-20261023.tar.gz)**
(no tar handy? grab the
[.zip instead](https://github.com/elcafe7/verse/releases/download/offline-20261023/verse-offline-20261023.zip))

```sh
tar -xzf verse-offline-20261023.tar.gz
xdg-open dist/index.html   # works over file://, USB stick, airplane mode
```

Built with `offline/build_offline.py` (stdlib only) and attached to the
[offline-20261023 release](https://github.com/elcafe7/verse/releases/tag/offline-20261023).
To rebuild locally: `python3 offline/build_offline.py`, then
`tar -czf verse-offline.tar.gz -C offline dist`. New releases are built by
[`.github/workflows/release.yml`](.github/workflows/release.yml) when an
`offline-YYYYMMDD` tag is pushed.

## Verification

Releases built by [`.github/workflows/release.yml`](.github/workflows/release.yml)
are built, scanned, checksummed and attested by GitHub Actions. Each such
release on the [Releases page](https://github.com/elcafe7/verse/releases) has, next
to the downloads:

| File | What it is |
|---|---|
| `SHA256SUMS` | SHA-256 checksums for every file in the release |
| `<name>.cdx.json` | CycloneDX SBOM (software bill of materials) |
| `<name>-osv-scan.json` / `.md` | Dated OSV-Scanner report |
| `verification.json` | Scan summary (tool, date, result, report link) for download pages |

A release is only published when every check passes: OSV-Scanner finds no
known vulnerabilities (CVSS 7.0 or higher fails the release, and lower-rated
findings hold it too; advisories with no CVSS score are listed as warnings),
the checksums verify, and VirusTotal (when turned on) flags nothing. If any
check fails, nothing is published, and the findings with a suggested fix go
to a "Release blocked" issue instead. Details:
[docs/RELEASE_VERIFICATION.md](docs/RELEASE_VERIFICATION.md).

**Check the checksums** (download the files plus `SHA256SUMS` into one folder):

```bash
sha256sum -c --ignore-missing SHA256SUMS        # Linux
shasum -a 256 -c --ignore-missing SHA256SUMS    # macOS
```

**Check build provenance** with the [GitHub CLI](https://cli.github.com/).
This confirms the file was built from this repository by GitHub Actions:

```bash
gh attestation verify verse-offline-<YYYYMMDD>.tar.gz -R elcafe7/verse
```

**Re-scan against today's advisories** (the report is a dated record):

```bash
osv-scanner scan source -L verse-offline-<YYYYMMDD>.cdx.json
```

Releases published before the workflow existed have only `SHA256SUMS`.


## Security reports

Every clean release also opens a PR that adds a dated report folder,
`security/reports/<tag>_<UTC timestamp>/`, with a `summary.md` (each check,
its result, date and time in UTC) and one file per check: OSV-Scanner report,
SBOM, SHA256SUMS, attestation link, VirusTotal links (when turned on) and the
OpenSSF Scorecard JSON. Index of all runs, newest first:
[security/README.md](security/README.md) (machine-readable:
[security/latest.json](security/latest.json)).

<!-- security-reports:start -->
Latest: none yet. The first verified release adds its report here. All runs: [security/README.md](security/README.md).
<!-- security-reports:end -->

## Features

- **Three English editions** bundled: KJV, KJ1611 (`kj16`) and Geneva 1599
  (`gen`) — exact verse lookup with tolerant book aliases
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

The source DBs are built with `scripts/build_source_db.py` (build-time only;
runtime reads only verse data).

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
verse -v kj16 "Romans 8:28" -dark
```

Interactive keys: `←` `→` navigate · `t` theme · `v` version · `s` source ·
`q` quit

## Web app

Start the development server:

```sh
. .venv/bin/activate
flask --app web_app run --port 5050
```

Open `http://127.0.0.1:5050`. The browser UI supports the same three editions,
reference aliases, AJAX book-name suggestions, adjacent-verse navigation,
light/dark themes, persistent Minimalist Mode (`M`), and direct Hebrew or Greek
source display. Minimalist Mode leaves only the verse, floating navigation,
source control, and its own exit control. Geneva 1599 is the default web
edition. URLs retain the current edition, reference, and source-panel state so
a reading can be bookmarked or shared.

Reverse proxies should strip the `/verse/` prefix before forwarding and send
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

## License

The code is under the [MIT License](LICENSE). The Bible texts are public domain.
