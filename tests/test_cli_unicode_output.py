import io
import sys
import unittest

from lib import cliHandler


class Cp1252Stream(io.TextIOBase):
    def __init__(self):
        self._encoding = "cp1252"
        self.buffer = []

    @property
    def encoding(self):
        return self._encoding

    def write(self, s):
        s.encode(self.encoding)
        self.buffer.append(s)
        return len(s)

    def flush(self):
        pass

    def isatty(self):
        return False


class CliUnicodeOutputTests(unittest.TestCase):
    def test_safe_print_handles_cp1252_stdout(self):
        stream = Cp1252Stream()
        original_stdout = sys.stdout
        sys.stdout = stream
        try:
            cliHandler._safe_print("  ✔ Proyecto creado en: /tmp/demo")
        finally:
            sys.stdout = original_stdout

        output = "".join(stream.buffer)
        self.assertIn("Proyecto creado", output)
        self.assertNotIn("✔", output)


if __name__ == "__main__":
    unittest.main()
