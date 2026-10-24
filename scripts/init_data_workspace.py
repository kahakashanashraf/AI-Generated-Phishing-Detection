"""Create/verify local dataset-workspace directories without downloading any data.

Usage: python scripts/init_data_workspace.py
       python scripts/init_data_workspace.py --root /some/repo
       python scripts/init_data_workspace.py --check
No data reads, deletes, transfers or network access.
"""
from __future__ import annotations

import argparse
from pathlib import Path

SOURCE_FOLDERS = (
    "D1_curated_emails", "D2_harmj0y", "D3_phishfuzzer",
    "D4_llmgen", "D5_gutierrez_origin",
)
PARTS = ("raw", "interim", "processed")
WORKSPACE_DIRS = tuple(
    f"datasets/{dataset}/{part}" for dataset in SOURCE_FOLDERS for part in PARTS
) + (
    "audit/receipts", "audit/rights", "audit/schema", "audit/quality",
    "audit/lineage", "audit/privacy", "splits/private",
    "annotations/private", "combined/private", "releases",
)


def ensure_workspace(data_root: Path, check: bool = False) -> list[str]:
    """Create empty folders idempotently; --check fails for any missing folder."""
    root = Path(data_root)
    missing = []
    for relative in WORKSPACE_DIRS:
        path = root / relative
        if not path.is_dir():
            if check:
                missing.append(relative)
            else:
                path.mkdir(parents=True, exist_ok=True)
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "data",
                        help="Location of the data/ workspace root")
    parser.add_argument("--check", action="store_true",
                        help="Read-only check that directory structure already exists")
    args = parser.parse_args()
    missing = ensure_workspace(args.root, check=args.check)
    if missing:
        print("MISSING workspace directories: " + ", ".join(missing))
        return 2
    print(f"Dataset workspace {'verified' if args.check else 'ready'}: {args.root}")
    print("No dataset contents were downloaded, changed or approved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
