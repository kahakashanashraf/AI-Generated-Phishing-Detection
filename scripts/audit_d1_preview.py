"""Privacy-conscious FIRST PASS intake for D1, not an approval of labels or licenses.

Usage:
    python scripts/audit_d1_preview.py --file /kaggle/working/Nazario.csv
Only metadata, checksums, and candidate label counts are printed.
Never print or publish source email bodies, sender addresses, or URLs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ZENODO_MD5 = {
    "Nazario.csv": "4022d055bb7cf8602f30f768f652e91e",
    "SpamAssasin.csv": "d921e0b2333bfaa058bd38193e6b3fbd",
    "Enron.csv": "10489e0fdcc8af6fe62135c689367d40",
    "CEAS_08.csv": "1f0d59191eec892a709995d48cd8decb",
}
LABEL_NAMES = {
    "label", "labels", "class", "category", "type",
    "is_phishing", "phishing", "is_spam", "spam",
}
SAFE_VALUE = re.compile(r"^[a-zA-Z0-9 _.-]{1,40}$")


def hash_file(path: Path) -> dict[str, str]:
    md5 = hashlib.md5()  # nosec: used to verify Zenodo file identity, not cryptography
    sha256 = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            md5.update(block)
            sha256.update(block)
    return {"md5": md5.hexdigest(), "sha256": sha256.hexdigest()}


def analyze(path: Path, max_rows: int = 2000) -> dict:
    if max_rows < 1:
        raise ValueError("max_rows must be >= 1")
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    checksums = hash_file(path)
    expected = ZENODO_MD5.get(path.name)
    if expected and expected != checksums["md5"]:
        raise ValueError(
            f"MD5 CHECKSUM MISMATCH for {path.name}: expected {expected}, "
            f"actual {checksums['md5']}; do not analyze/release this file."
        )
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    missing = Counter()
    class_counts: dict[str, Counter] = {}
    count = 0
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, strict=True)
        columns = reader.fieldnames or []
        if not columns or len(set(columns)) != len(columns):
            raise ValueError("Missing CSV header or duplicate column names; stop for audit")
        likely_labels = [
            col for col in columns if col.strip().lower() in LABEL_NAMES
        ]
        class_counts = {col: Counter() for col in likely_labels}
        for row in reader:
            if count >= max_rows:
                break
            if None in row:
                raise ValueError("Row has more fields than the CSV header")
            count += 1
            for key in columns:
                value = row.get(key)
                if value is None or not str(value).strip():
                    missing[key] += 1
            for key in likely_labels:
                value = (row.get(key) or "").strip()
                # Only print safe short class literals, never email-like / URL text.
                safe = value if SAFE_VALUE.fullmatch(value) else "<redacted-or-unusual>"
                class_counts[key][safe] += 1
    return {
        "status": "PREVIEW_ONLY_NOT_LICENSE_OR_LABEL_APPROVAL",
        "filename": path.name,
        "file_bytes": path.stat().st_size,
        "checksums": checksums,
        "zenodo_md5_match": expected is not None and checksums["md5"] == expected,
        "rows_examined": count,
        "sample_limit": max_rows,
        "columns": columns,
        "missing_in_sample": dict(missing),
        "candidate_label_counts_in_sample": {
            key: dict(counter.most_common(20)) for key, counter in class_counts.items()
        },
        "warnings": [
            "Counts are sample-only, not full-file prevalence.",
            "Candidate label columns are not validated phishing ground truth.",
            "No license, origin, parent IDs, overlap, or privacy checks are inferred.",
            "Do not commit raw emails, URLs or personal information to GitHub.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--sample-rows", type=int, default=2000)
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional path for metadata-only JSON receipt")
    args = parser.parse_args()
    try:
        result = analyze(args.file, max_rows=args.sample_rows)
    except (OSError, ValueError, UnicodeError, csv.Error) as err:
        print(f"DATA AUDIT STOP: {err}", file=sys.stderr)
        return 2
    report = json.dumps(result, indent=2, ensure_ascii=False)
    print(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
