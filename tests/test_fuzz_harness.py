"""Replay the Atheris seed corpus through the fuzz harness checks.

Atheris itself only runs in .github/workflows/fuzz.yml; this test needs no
fuzzer. It imports fuzz/fuzz_refs.py (its `main` is not called) and feeds
every seed in fuzz/corpus/refs to the same invariant checks the fuzzer uses.

Run: python3 -m unittest tests.test_fuzz_harness
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUZZ_DIR = os.path.join(ROOT, "fuzz")
CORPUS = os.path.join(FUZZ_DIR, "corpus", "refs")


def load_harness():
    spec = importlib.util.spec_from_file_location(
        "fuzz_refs_under_test", os.path.join(FUZZ_DIR, "fuzz_refs.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FuzzRefsSeeds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.harness = load_harness()

    def test_every_seed_passes_the_invariants(self):
        names = sorted(os.listdir(CORPUS))
        self.assertTrue(names)
        for name in names:
            with open(os.path.join(CORPUS, name), "rb") as handle:
                self.harness.test_one_input(handle.read())

    def test_odd_inputs(self):
        for text in ["", ":", "::::", "a:b:c", "John 99999999999999999999:1", "\x00", "\u00e9 1:1"]:
            self.harness.check_text(text)


if __name__ == "__main__":
    unittest.main()
