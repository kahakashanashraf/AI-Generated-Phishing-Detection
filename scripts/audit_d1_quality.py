"""D1 full-file aggregate quality audit. Never prints or saves raw emails or URLs.

Usage:
python scripts/audit_d1_quality.py \
  --file data/datasets/D1_curated_emails/raw/Nazario.csv \
  --output data/audit/quality/D1_Nazario_full_quality.json

Even a successful run is NOT proof of source rights or phishing ground truth.
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

KNOWN_MD5 = {"Nazario.csv": "4022d055bb7cf8602f30f768f652e91e"}
REQUIRED_COLUMNS = {"subject", "body", "label"}
SUSPECT_ADMIN_PHRASES = ("don't delete this message", "folder internal data")


def _fingerprint(subject: str, body: str, normalize: bool) -> str:
    if normalize:
        subject = " ".join(subject.casefold().split())
        body = " ".join(body.casefold().split())
    payload = json.dumps((subject, body), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def inspect(path: Path) -> dict:
    path = Path(path)
    md5 = hashlib.md5()  # nosec: Zenodo checksum matching, not cryptographic trust
    sha256 = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            md5.update(part)
            sha256.update(part)
    actual_md5 = md5.hexdigest()
    expected_md5 = KNOWN_MD5.get(path.name)
    if expected_md5 is not None and actual_md5 != expected_md5:
        raise ValueError("MD5 CHECKSUM MISMATCH. Do not analyze this source.")

    raw_counts, norm_counts = Counter(), Counter()
    key_labels: dict[str, set[str]] = {}
    blanks, labels = Counter(), Counter()
    administrative_candidates = 0
    entirely_empty_text = 0
    rows = 0

    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        columns = reader.fieldnames or []
        if len(set(columns)) != len(columns) or not REQUIRED_COLUMNS.issubset(columns):
            raise ValueError("Missing/duplicate column headers or required subject/body/label")
        for row in reader:
            if None in row:
                raise ValueError("Unexpected additional CSV fields")
            if any(value is None for value in row.values()):
                raise ValueError("Incomplete CSV row")
            rows += 1
            for key, val in row.items():
                if not val.strip():
                    blanks[key] += 1
            subject, body, label = (
                row["subject"], row["body"], row["label"].strip()
            )
            if label not in {"0", "1"}:
                raise ValueError("Unknown or blank label; audit stopped")
            labels[label] += 1
            if not subject.strip() and not body.strip():
                entirely_empty_text += 1
            raw_key = _fingerprint(subject, body, normalize=False)
            norm_key = _fingerprint(subject, body, normalize=True)
            raw_counts[raw_key] += 1
            norm_counts[norm_key] += 1
            key_labels.setdefault(norm_key, set()).add(label)
            joined = (subject + " " + body).casefold()
            if any(phrase in joined for phrase in SUSPECT_ADMIN_PHRASES):
                administrative_candidates += 1

    if rows == 0:
        raise ValueError("Dataset has zero rows")
    exact_excess = sum(n - 1 for n in raw_counts.values() if n > 1)
    normalized_excess = sum(n - 1 for n in norm_counts.values() if n > 1)
    return {
        "status": "QUALITY_ONLY_NO_TRAINING_OR_LICENSE_GO",
        "file_name": path.name,
        "file_bytes": path.stat().st_size,
        "md5": actual_md5,
        "sha256": sha256.hexdigest(),
        "checksum_verified": expected_md5 is not None,
        "rows_full_scan": rows,
        "label_counts": dict(labels),
        "blank_counts": dict(blanks),
        "blank_subject_and_body": entirely_empty_text,
        "exact_duplicate_extra_rows_subject_body": exact_excess,
        "normalized_duplicate_extra_rows_subject_body": normalized_excess,
        "normalized_groups_with_conflicting_labels": sum(
            len(v) > 1 for v in key_labels.values()
        ),
        "heuristic_admin_record_candidates": administrative_candidates,
        "warnings": [
            "Duplicates are only within this file, not across other corpora.",
            "The admin record detector is a heuristic; no record has been removed.",
            "Labels are not independently validated phishing intent.",
            "Do not publicly commit raw data or per-record hashes.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = inspect(args.file)
        output = json.dumps(report, indent=2, ensure_ascii=False)
        print(output)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n", encoding="utf-8")
        return 0
    except (OSError, ValueError, csv.Error, UnicodeError) as err:
        print(f"QUALITY AUDIT STOP: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
