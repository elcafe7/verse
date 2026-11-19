import random
import re
import time
import unittest

from verse import split_reference
from web_app import parse_web_reference

# The pattern split_reference() replaced. It is only used here, on generated
# strings, to prove the new parser accepts the same input with the same parts.
OLD_REFERENCE_RE = re.compile(r"(.+?)\s+(\d+)(?:[:.\s]+)(\d+)")


class SplitReferenceTests(unittest.TestCase):
    def test_common_references(self):
        self.assertEqual(split_reference("John 3:16"), ("John", "3", "16"))
        self.assertEqual(split_reference("gen 1.1"), ("gen", "1", "1"))
        self.assertEqual(split_reference("gen 1 1"), ("gen", "1", "1"))
        self.assertEqual(split_reference("1 John 3:16"), ("1 John", "3", "16"))
        self.assertEqual(split_reference("Song of Solomon 2 : 1"), ("Song of Solomon", "2", "1"))
        self.assertIsNone(split_reference("John 3"))
        self.assertIsNone(split_reference("John3:16"))
        self.assertIsNone(split_reference(""))

    def test_matches_old_pattern(self):
        alphabet = list("ab1 2:.\n\t\u0663\u00a0J")
        rnd = random.Random(20261112)
        for _ in range(20000):
            text = "".join(rnd.choice(alphabet) for _ in range(rnd.randint(0, 9)))
            match = OLD_REFERENCE_RE.fullmatch(text)
            expected = match.groups() if match else None
            self.assertEqual(split_reference(text), expected, repr(text))

    def test_long_input_is_fast(self):
        start = time.perf_counter()
        for text in ("a" + " " * 100_000 + "a", "a" * 100_000, "a " + "1 " * 50_000 + "x"):
            split_reference(text)
            with self.assertRaises(ValueError):
                parse_web_reference(text)
        self.assertLess(time.perf_counter() - start, 2.0)


if __name__ == "__main__":
    unittest.main()
