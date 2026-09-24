"""Tests for the CLI's output formatting, in particular --json mode."""

import contextlib
import io
import json
import os
import tempfile
import unittest

from emoji_census import cli


def _write_temp_file(text):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w", encoding="utf-8") as fileobj:
        fileobj.write(text)
    return path


class JsonOutputTests(unittest.TestCase):
    def _run(self, args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cli.main(args)
        return out.getvalue()

    def test_json_output_is_parseable_and_shaped(self):
        path = _write_temp_file("hi \U0001F600 there \U0001F600 again")
        try:
            output = self._run(["--json", path])
        finally:
            os.remove(path)

        rows = json.loads(output)
        self.assertEqual(rows, [
            {
                "sequence": "\U0001F600",
                "count": 2,
                "codepoints": ["U+1F600"],
            }
        ])

    def test_json_output_respects_top_n(self):
        path = _write_temp_file("\U0001F600\U0001F601\U0001F601")
        try:
            output = self._run(["--json", "-n", "1", path])
        finally:
            os.remove(path)

        rows = json.loads(output)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sequence"], "\U0001F601")
        self.assertEqual(rows[0]["count"], 2)

    def test_json_output_on_empty_input_is_an_empty_array(self):
        path = _write_temp_file("no emoji here")
        try:
            output = self._run(["--json", path])
        finally:
            os.remove(path)

        self.assertEqual(json.loads(output), [])


if __name__ == "__main__":
    unittest.main()
