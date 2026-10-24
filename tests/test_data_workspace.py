"""Dataset workspace layout regression tests, using empty temporary directories."""
import tempfile
import subprocess
import unittest
from pathlib import Path

from scripts.init_data_workspace import (
    SOURCE_FOLDERS, WORKSPACE_DIRS, ensure_workspace
)


class DatasetWorkspaceTests(unittest.TestCase):
    def test_create_all_directories_idempotently(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            self.assertTrue(ensure_workspace(root, check=True))
            self.assertEqual(ensure_workspace(root), [])
            self.assertEqual(ensure_workspace(root), [])
            self.assertEqual(ensure_workspace(root, check=True), [])
            self.assertEqual(len(SOURCE_FOLDERS), 5)
            for rel in WORKSPACE_DIRS:
                self.assertTrue((root / rel).is_dir())

    def test_does_not_modify_existing_private_content(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            ensure_workspace(root)
            secret = root / "datasets/D1_curated_emails/raw/private.eml"
            secret.write_text("sensitive-only-local\n", encoding="utf-8")
            ensure_workspace(root)
            self.assertEqual(secret.read_text(encoding="utf-8"),
                             "sensitive-only-local\n")

    def test_gitingore_blocks_private_data_but_not_receipts(self):
        repo = Path(__file__).resolve().parents[1]
        private_paths = [
            "data/datasets/D1_curated_emails/raw/Nazario.csv",
            "data/datasets/D2_harmj0y/processed/samples.jsonl",
            "data/audit/quality/D1_Nazario_preview.json",
            "data/splits/private/split_assignment.csv",
        ]
        for private_path in private_paths:
            with self.subTest(private_path=private_path):
                result = subprocess.run(
                    ["git", "check-ignore", "--no-index", "--quiet", private_path],
                    cwd=repo, check=False, capture_output=True
                )
                self.assertEqual(result.returncode, 0, f"Private path not ignored: {private_path}")
        for public_path in ("data/README.md", "data/audit/receipts/D1.md"):
            with self.subTest(public_path=public_path):
                result = subprocess.run(
                    ["git", "check-ignore", "--no-index", "--quiet", public_path],
                    cwd=repo, check=False, capture_output=True
                )
                self.assertEqual(result.returncode, 1, f"Public metadata unexpectedly ignored: {public_path}")


if __name__ == "__main__":
    unittest.main()
