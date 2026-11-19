<div align="center">

# Verse

**Read the Bible one verse at a time.**
One verse on the screen, nothing else in the way, with the Hebrew or Greek beneath it if you want.

<!-- Maintainers: the offline file name carries its date. After a new offline-* release, update verse-offline-20261023 everywhere in this file. -->
### [⬇ Download for offline use](https://github.com/elcafe7/verse/releases/latest/download/verse-offline-20261023.zip)

<sub>verse-offline-20261023.zip · about 8 MB · free · <a href="https://github.com/elcafe7/verse/releases/latest">release page</a></sub>

[**Read online**](https://apocalypse.press/verse/) · [Word](https://apocalypse.press/word/) · [Scroll](https://apocalypse.press/scroll/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/elcafe7/verse/badge)](https://scorecard.dev/viewer/?uri=github.com/elcafe7/verse)
<!-- OpenSSF Best Practices badge slot: set PROJECT_ID and uncomment (security/MANUAL-STEPS.md)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/PROJECT_ID/badge)](https://www.bestpractices.dev/projects/PROJECT_ID)
-->
<!-- Socket.dev badge slot: set SOCKET_URL and uncomment (security/MANUAL-STEPS.md)
[![Socket](https://img.shields.io/badge/Socket.dev-monitored-blue)](SOCKET_URL)
-->

<sub>A project of <a href="https://jesuspeoplesf.com">Jesus People SF</a> &amp; <a href="https://apocalypse.press">Apocalypse Press</a> · <a href="https://jesuspeoplesf.com/donate/">Donate</a></sub>

<img src="readme-assets/verse-phone.png" alt="Verse on a phone showing John 3:16 in the Geneva Bible, with Previous and Next buttons below" width="300">

</div>

---

## What it is

Verse shows one Bible verse at a time, large and quiet, so you can slow down and take it in. Type a reference like **John 3:16** or **Ps 23:1**, or step forward and back one verse at a time.

- **Three Bibles:** Geneva Bible (1599), King James Version (1611 original), and King James Version (Oxford 1769). The Geneva and 1611 editions include the Apocrypha.
- **The original languages:** show the Hebrew (Old Testament) or Greek (New Testament) under the English, with a pronunciation guide.
- **Minimalist mode:** hide everything except the verse.
- **Light or dark**, and it remembers your choices.

## Read online

Open **[apocalypse.press/verse](https://apocalypse.press/verse/)** in any browser, on a computer or a phone. Nothing to install.

## Download for offline use

Want to read with no internet, or with fewer distractions? Download Verse once and keep it.

1. **Download** [verse-offline-20261023.zip](https://github.com/elcafe7/verse/releases/latest/download/verse-offline-20261023.zip) (about 8 MB).
2. **Unzip it.** You get one folder called `dist`.
3. **Open `index.html`** inside that folder by double-clicking it. It opens in Chrome, Edge, Safari, or Firefox.
4. **That's it.** It works with no internet connection. Keep `index.html` in the folder with its `data` folder and other files.

Your place and settings are saved in your browser on your own device. No account, no sign-up.

**On a phone?** The easiest way is to read online at [apocalypse.press/verse](https://apocalypse.press/verse/). You can add it to your home screen from your browser's Share or menu button, like any web page.

<sub>Prefer a .tar.gz? [verse-offline-20261023.tar.gz](https://github.com/elcafe7/verse/releases/latest/download/verse-offline-20261023.tar.gz). Every file and its checksum is on the [release page](https://github.com/elcafe7/verse/releases/latest).</sub>

## How to use it

1. Type a verse in the box (for example **John 3:16** or **Ps 23:1**) and press **Read**.
2. Choose a Bible from the menu at the top.
3. Use **Previous** and **Next**, the arrow keys, or swipe, to move one verse at a time.

| Action | Keyboard | Touch |
|---|---|---|
| Previous / next verse | <kbd>←</kbd> / <kbd>→</kbd> | Swipe, or tap **Previous** / **Next** |
| Show or hide the Hebrew / Greek | <kbd>S</kbd> | **Source text** button |
| Minimalist mode | <kbd>M</kbd> | **Minimalist mode** button |
| Light / dark | <kbd>T</kbd> | **Sun** button |
| Find a verse | <kbd>/</kbd> | Tap the verse box |

## Texts

Bible text: Geneva Bible (1599), King James Version (1611 original, with Apocrypha), King James Version (Oxford 1769). Hebrew and Greek source text with transliteration. All public domain.

## More from us

- [Word](https://apocalypse.press/word/): Scripture one word at a time
- [Scroll](https://apocalypse.press/scroll/): the Bible rolling gently up your screen
- [Apocalypse Press](https://apocalypse.press) · [Jesus People SF](https://jesuspeoplesf.com) · [Donate](https://jesuspeoplesf.com/donate/)

## Issues and contributing

- **Questions, bugs and ideas:** open an issue in the [issue tracker](https://github.com/elcafe7/verse/issues). Add the `question` label for questions.
- **Code and docs:** pull requests against `main` are welcome. [CONTRIBUTING.md](CONTRIBUTING.md) has the steps, the checks to run, and what's needed for a change to be accepted.
- **Security problems:** please don't open a public issue. See [SECURITY.md](SECURITY.md) to report privately.

## License

The code is under the [MIT License](LICENSE). The Bible texts are public domain.

---

## For developers

You only need this to run or change the code. To read, use the download above.

This repo also has a terminal Bible reader and a small Flask web app over the same bundled texts, backed by local SQLite databases. No runtime dependency on Lex or any other project.

```sh
verse -v kjv "John 3:16"
verse -v gen "Psalm 23:1"
```

The offline download is built from the private `verse_web` repo (`offline/build_offline.py`, standard library only). To open it from a terminal:

```sh
tar -xzf verse-offline-20261023.tar.gz
xdg-open dist/index.html   # works over file://, USB stick, airplane mode
```

### Terminal reader features

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

### Data

All data ships inside the repo (no download step):

| Path | Contents |
|------|----------|
| `data/bible_versions/*.db` | English editions (`metadata` + `bible` tables) |
| `data/source/greek.db` | NT Greek source text, 7,941 verses |
| `data/source/hebrew.db` | OT Hebrew source text, 23,145 verses |

The source DBs are built with `scripts/build_source_db.py` (build-time only;
runtime reads only verse data).

### Install

Requires Python 3. Install the shared CLI and web dependencies:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
ln -s "$PWD/verse.py" ~/.local/bin/verse   # or your own launcher
```

### Usage

```sh
verse -v kjv "John 3:16"    # one-shot read
verse                       # interactive: prompts for edition + reference
verse -v kj16 "Romans 8:28" -dark
```

Interactive keys: `←` `→` navigate · `t` theme · `v` version · `s` source ·
`q` quit

### Web app

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

### Tests

```sh
. .venv/bin/activate
python -m unittest discover -s tests -v
```

### Release verification

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

### Security reports

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
