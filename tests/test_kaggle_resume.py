"""No-network, synthetic tests of idempotent Kaggle resume and checksum gates."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import kaggle_resume as kr


class KaggleResumeTests(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory()
        self.root = Path(self.context.name)
        self.repo = self.root / "repo"
        self.input_root = self.root / "input"
        self.input_root.mkdir(parents=True)

    def tearDown(self):
        self.context.cleanup()

    def _private_input(self, content=b"synthetic,not,a,real,email\n"):
        p = self.input_root / "my-private-d1" / "Nazario.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return p

    def test_missing_input_is_non_destructive(self):
        result = kr.resume(self.repo, self.input_root)
        self.assertIn("No checksum-matching", result["Nazario"])
        self.assertFalse(
            (self.repo / "data/datasets/D1_curated_emails/raw/Nazario.csv").exists()
        )

    def test_mount_verified_input_and_skip_same_sha_audits(self):
        private = self._private_input()
        sha = hashlib.sha256(private.read_bytes()).hexdigest()
        md5 = hashlib.md5(private.read_bytes()).hexdigest()
        dummy_preview = {
            "status": "PREVIEW_ONLY_NOT_LICENSE_OR_LABEL_APPROVAL",
            "checksums": {"sha256": sha},
            "zenodo_md5_match": True,
            "rows_examined": 1,
        }
        dummy_quality = {
            "status": "QUALITY_ONLY_NO_TRAINING_OR_LICENSE_GO",
            "sha256": sha,
            "rows_full_scan": 1,
            "exact_duplicate_extra_rows_subject_body": 0,
            "normalized_duplicate_extra_rows_subject_body": 0,
        }
        with patch.object(kr, "NAZARIO_MD5", md5), \
             patch.object(kr, "analyze", return_value=dummy_preview) as preview_fn, \
             patch.object(kr, "inspect", return_value=dummy_quality) as quality_fn:
            first = kr.resume(self.repo, self.input_root)
            target = self.repo / "data/datasets/D1_curated_emails/raw/Nazario.csv"
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), private.resolve())
            self.assertIn("EXECUTED", first["preview"])
            self.assertIn("EXECUTED", first["quality"])
            again = kr.resume(self.repo, self.input_root)
            self.assertIn("REUSED", again["preview"])
            self.assertIn("REUSED", again["quality"])
            self.assertEqual(preview_fn.call_count, 1)
            self.assertEqual(quality_fn.call_count, 1)
            self.assertEqual(private.read_bytes(), b"synthetic,not,a,real,email\n")

    def test_wrong_md5_does_not_mount_input(self):
        self._private_input()
        result = kr.resume(self.repo, self.input_root)
        self.assertIn("No checksum-matching", result["Nazario"])
        self.assertFalse(
            (self.repo / "data/datasets/D1_curated_emails/raw/Nazario.csv").exists()
        )

    def test_invalid_existing_local_file_rejected_not_overwritten(self):
        target = self.repo / "data/datasets/D1_curated_emails/raw/Nazario.csv"
        target.parent.mkdir(parents=True)
        target.write_text("private-invalid", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            kr.resume(self.repo, self.input_root)
        self.assertEqual(target.read_text(encoding="utf-8"), "private-invalid")

    def test_private_dataset_not_auto_downloaded_or_modified(self):
        self._private_input()
        result = kr.resume(self.repo, self.root / "nonexistent")
        self.assertIn("No attached Kaggle input", result["Nazario"])
        self.assertTrue((self.input_root / "my-private-d1/Nazario.csv").exists())


if __name__ == "__main__":
    unittest.main()
