"""Synthetic-only tests for private D1 candidate indexing."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.review_d1_candidates import find_candidates, save_private_review


class D1CandidateReviewTests(unittest.TestCase):
    def _file(self, folder: str, rows: list[list[str]]) -> Path:
        p = Path(folder) / "synthetic.csv"
        with p.open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(["sender", "subject", "body", "label"])
            writer.writerows(rows)
        return p

    def test_groups_indexes_and_admin_separate_without_raw_text(self):
        with tempfile.TemporaryDirectory() as folder:
            p = self._file(folder, [
                ["private@example.org", "NOTICE", "Hello confidential@example.org", "1"],
                ["private@example.org", " notice ", " hello  CONFIDENTIAL@example.org ", "1"],
                ["private@example.org", "Report", "folder internal data", "1"],
                ["private@example.org", "Normal", "Normal body", "1"],
                ["private@example.org", "Follow up", "don't delete this message", "1"],
            ])
            r = find_candidates(p)
            self.assertEqual(r["rows_full_scan"], 5)
            self.assertEqual(r["normalized_duplicate_extra_rows"], 1)
            self.assertEqual(r["duplicate_group_count"], 1)
            self.assertEqual(r["duplicate_groups"][0]["row_numbers"], [1, 2])
            self.assertEqual(r["heuristic_admin_candidate_count"], 2)
            self.assertEqual([a["row_number"] for a in r["admin_candidates"]], [3, 5])
            a, b = save_private_review(r, Path(folder) / "quality")
            all_metadata = json.dumps(r) + a.read_text() + b.read_text()
            self.assertNotIn("private@example.org", all_metadata)
            self.assertNotIn("confidential@example.org", all_metadata)
            self.assertNotIn("folder internal data", all_metadata)
            self.assertNotIn("don't delete this message", all_metadata)
            self.assertEqual(r["duplicate_groups"][0]["human_verdict"], "PENDING")

    def test_multiple_in_one_normalized_group_counts_extra_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            p = self._file(folder, [
                ["a", "subject", "content", "1"],
                ["b", "SUBJECT", "CONTENT", "1"],
                ["c", " Subject ", " Content ", "1"],
            ])
            r = find_candidates(p)
            self.assertEqual(r["duplicate_group_count"], 1)
            self.assertEqual(r["normalized_duplicate_extra_rows"], 2)
            self.assertEqual(r["duplicate_groups"][0]["group_size"], 3)

    def test_empty_input_no_fabricated_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            p = self._file(folder, [])
            with self.assertRaisesRegex(ValueError, "zero rows"):
                find_candidates(p)


if __name__ == "__main__":
    unittest.main()
