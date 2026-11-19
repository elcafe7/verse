# Fuzzing

[Atheris](https://github.com/google/atheris) (libFuzzer for Python) harness for
the code that handles untrusted input. It satisfies the OpenSSF Scorecard
Fuzzing check and runs in `.github/workflows/fuzz.yml`.

| Harness | What it fuzzes | Invariants |
|---|---|---|
| `fuzz_refs.py` | `parse_web_reference`, `split_database_reference` (web_app.py), `normalize_book`, `clean_text` (verse.py), `_reference_candidates` (core/db.py) | only `ValueError` from the two parsers; chapter and verse are at least 1; the text helpers return `str`; candidates always include the input |

Seed inputs live in `corpus/refs/`. `tests/test_fuzz_harness.py` replays them in
the normal test suite, without Atheris.

Run locally (Linux x86-64, Python 3.12+):

```bash
python3 -m venv .fuzz-venv
.fuzz-venv/bin/pip install --require-hashes --no-deps -r .github/requirements/fuzz-requirements.txt
cp -R fuzz/corpus/refs /tmp/corpus-refs
.fuzz-venv/bin/python fuzz/fuzz_refs.py /tmp/corpus-refs -max_total_time=60
```

A crash writes `crash-<sha1>` with the input; re-run the harness with that file
as its only argument to reproduce it, then add a minimised copy to the corpus
once fixed.
