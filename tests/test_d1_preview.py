"""Regression tests: D1 first-pass scanner must not expose raw email text."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_d1_preview import analyze


class D1PreviewTests(unittest.TestCase):
    def test_metadata_only_no_raw_email_leak(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.csv"
            path.write_text(
                'text,label,source\\n'
                '"Please email private@example.com and visit https://example.test",phishing,A\\n'
                '"Personal message for testing",legitimate,A\\n',
                encoding="utf-8"
            )
            report = analyze(path, max_rows=2)
            printed = json.dumps(report)
            self.assertEqual(report["rows_examined"], 2)
            self.assertEqual(report["candidate_label_counts_in_sample"]["label"],
                             {"phishing": 1, "legitimate": 1})
            self.assertNotIn("private@example.com", printed)
            self.assertNotIn("https://example.test", printed)
            self.assertNotIn("Personal message", printed)

    def test_checksum_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "Nazario.csv"
            path.write_text("text,label\\nbody,1\\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "MD5 CHECKSUM MISMATCH"):
                analyze(path)

    def test_unknown_label_values_redacted(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.csv"
            path.write_text('label,text\\n"john@domain.test",secret\\n', encoding="utf-8")
            report = analyze(path)
            self.assertNotIn("john@domain.test", json.dumps(report))
            self.assertIn("<redacted-or-unusual>",
                          report["candidate_label_counts_in_sample"]["label"])


if __name__ == "__main__":
    unittest.main()
