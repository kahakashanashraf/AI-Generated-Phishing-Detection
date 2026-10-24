"""Dataset workspace layout regression tests, using empty temporary directories."""
import tempfile
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
