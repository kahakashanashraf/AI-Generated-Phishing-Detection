"""Safe, synthetic fixture tests of D1 full-file quality summary."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_d1_quality import inspect


class QualityAuditTests(unittest.TestCase):
    def test_full_counts_and_no_raw_message_leak(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "synthetic.csv"
            file.write_text(
                "sender,receiver,date,subject,body,urls,label\n"
                'alice@example.test,,2026-01-01,"Alert","Never print https://bad.test",,1\n'
                'alice@example.test,,2026-01-02,"Alert","Never print https://bad.test",,1\n'
                'bob@example.test,,2026-01-03," ALERT "," never  print  https://bad.test ",,1\n'
                "bob@example.test,,2026-01-04,,, ,0\n",
                encoding="utf-8",
            )
            result = inspect(file)
            self.assertEqual(result["rows_full_scan"], 4)
            self.assertEqual(result["label_counts"], {"1": 3, "0": 1})
            self.assertEqual(result["exact_duplicate_extra_rows_subject_body"], 1)
            self.assertEqual(result["normalized_duplicate_extra_rows_subject_body"], 2)
            self.assertEqual(result["blank_subject_and_body"], 1)
            self.assertEqual(result["normalized_groups_with_conflicting_labels"], 0)
            output = json.dumps(result)
            self.assertNotIn("alice@example.test", output)
            self.assertNotIn("https://bad.test", output)
            self.assertNotIn("Never print", output)

    def test_conflicting_labels_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "synthetic.csv"
            file.write_text(
                "subject,body,label\nSame,text,0\nsame,TEXT,1\n",
                encoding="utf-8",
            )
            self.assertEqual(inspect(file)["normalized_groups_with_conflicting_labels"], 1)

    def test_nazario_checksum_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "Nazario.csv"
            file.write_text("subject,body,label\nA,B,1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "MD5 CHECKSUM MISMATCH"):
                inspect(file)


if __name__ == "__main__":
    unittest.main()
