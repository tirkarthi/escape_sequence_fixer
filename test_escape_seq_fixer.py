import tempfile
import unittest

from escape_sequence_fixer import process_file


class TestFixer(unittest.TestCase):
    def test_cases(self):
        cases = [
            (r"a = '\d'", ["a = r'\\d'"]),
            (r"a = u'\d'", ["a = ru'\\d'"]),
            (r"a = r'\d'", ["a = r'\\d'"]),
        ]

        for code, expected in cases:
            with self.subTest(f"Testing with {code!r}"):
                with tempfile.NamedTemporaryFile("w+t") as source:
                    source.write(code)
                    source.seek(0)

                    _, patch = process_file(source)
                    self.assertEqual(patch, expected)


if __name__ == "__main__":
    unittest.main()
