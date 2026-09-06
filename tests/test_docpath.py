import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
import docpath


class CheckTests(unittest.TestCase):
    def run_check(self, files):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')
            return docpath.check(root)

    def test_missing_path_line_number(self):
        report = self.run_check({'README.md': '# Test\n\n[bad](lost.md)'})
        self.assertEqual(report['issues'][0]['line'], 3)
        self.assertEqual(report['issues'][0]['reason'], 'path does not exist')

    def test_relative_root_image_encoded_and_headings(self):
        report = self.run_check({'README.md': '[x](docs/a%20b.md#你好-world)\n![x](/img/icon.svg)', 'docs/a b.md': '# 你好 World\n[back](../README.md)', 'img/icon.svg': '<svg/>'})
        self.assertEqual(report['issues'], [])

    def test_duplicate_and_missing_anchors(self):
        report = self.run_check({'a.md': '# Hello\n# Hello\n[x](#hello-1)\n[y](#hello-2)'})
        self.assertEqual(len(report['issues']), 1)
        self.assertEqual(report['issues'][0]['target'], '#hello-2')

    def test_ignore_code_comments_and_remote(self):
        report = self.run_check({'a.md': '```md\n[x](missing)\n```\n`[x](missing)`\n<!--\n[x](missing)\n-->\n[x](https://example.com)\n[x](mailto:a@example.com)'})
        self.assertEqual(report['issues'], [])

    def test_root_escape(self):
        report = self.run_check({'a.md': '[x](../private.md)'})
        self.assertEqual(report['issues'][0]['reason'], 'target is outside the project root')

    def test_ignored_directories(self):
        report = self.run_check({'a.md': '# OK', 'node_modules/a.md': '[x](bad)'})
        self.assertEqual(report['files_scanned'], 1)

    def test_setext(self):
        self.assertIn('hello-world', docpath.headings('Hello World\n===\n'))

    def test_json_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'a.md').write_text('[x](bad)', encoding='utf-8')
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(docpath.main([directory, '--json']), 1)
            self.assertEqual(len(json.loads(output.getvalue())['issues']), 1)

    def test_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'a.md').write_bytes(b'\xff')
            self.assertIn('cannot read Markdown', docpath.check(Path(directory))['issues'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
