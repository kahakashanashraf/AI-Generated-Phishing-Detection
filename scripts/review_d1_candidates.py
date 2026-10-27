"""Locate D1 Nazario QA review candidates without exposing email text.

The only outputs are local, gitignored metadata:
    data/audit/quality/D1_Nazario_review_index.json
    data/audit/quality/D1_Nazario_review_sheet.csv

These contain row indices, not email bodies/subjects/addresses/URLs.
A human must privately inspect the original source to adjudicate them.
No automatic deletion, relabeling or model training is performed.

Usage:
 python scripts/review_d1_candidates.py \
   --file data/datasets/D1_curated_emails/raw/Nazario.csv \
   --output-dir data/audit/quality
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

try:
    from .audit_d1_quality import _fingerprint, inspect, SUSPECT_ADMIN_PHRASES
except ImportError:
    from audit_d1_quality import _fingerprint, inspect, SUSPECT_ADMIN_PHRASES


def find_candidates(path: Path) -> dict:
    path = Path(path)
    quality = inspect(path)  # checks checksum, column/label consistency
    fingerprints: dict[str, list[int]] = defaultdict(list)
    admin_rows: dict[int, list[str]] = {}
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        for row_number, row in enumerate(reader, start=1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError("Malformed CSV row; do not generate review artifact")
            subject, body = row["subject"], row["body"]
            key = _fingerprint(subject, body, normalize=True)
            fingerprints[key].append(row_number)
            joined = (subject + " " + body).casefold()
            reasons = [
                f"admin_phrase_{i+1}"
                for i, phrase in enumerate(SUSPECT_ADMIN_PHRASES)
                if phrase in joined
            ]
            if reasons:
                admin_rows[row_number] = reasons

    duplicate_groups = [
        rows for rows in fingerprints.values() if len(rows) > 1
    ]
    duplicate_groups.sort(key=lambda rows: rows[0])
    duplicates = [
        {
            "group_id": f"NORM-{i:03d}",
            "row_numbers": rows,
            "group_size": len(rows),
            "extra_rows": len(rows) - 1,
            "human_verdict": "PENDING",
        }
        for i, rows in enumerate(duplicate_groups, 1)
    ]
    administrative = [
        {
            "row_number": row,
            "reason_codes": reasons,
            "human_verdict": "PENDING",
        }
        for row, reasons in sorted(admin_rows.items())
    ]
    extra_count = sum(group["extra_rows"] for group in duplicates)
    if (
        extra_count != quality["normalized_duplicate_extra_rows_subject_body"]
        or len(administrative) != quality["heuristic_admin_record_candidates"]
    ):
        raise AssertionError("Candidate indexing disagrees with the quality audit")

    return {
        "status": "PRIVATE_REVIEW_INDEX_NOT_ADJUDICATED",
        "filename": path.name,
        "source_sha256": quality["sha256"],
        "rows_full_scan": quality["rows_full_scan"],
        "duplicate_group_count": len(duplicates),
        "normalized_duplicate_extra_rows": extra_count,
        "heuristic_admin_candidate_count": len(administrative),
        "duplicate_groups": duplicates,
        "admin_candidates": administrative,
        "disclosure_warning": (
            "Indices are private research metadata. No raw emails were emitted. "
            "Review privately; do not post row text, sender, URLs or files publicly."
        ),
    }


def save_private_review(report: dict, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "D1_Nazario_review_index.json"
    sheet_path = output_dir / "D1_Nazario_review_sheet.csv"
    index_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with sheet_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["candidate_type", "group_id", "data_row_number",
                         "reason_code", "human_decision", "reviewer_notes"])
        for group in report["duplicate_groups"]:
            for row in group["row_numbers"]:
                writer.writerow(["normalized_duplicate", group["group_id"],
                                 row, "same_casefolded_subject_body", "", ""])
        for item in report["admin_candidates"]:
            writer.writerow(["possible_admin", "", item["row_number"],
                             "+".join(item["reason_codes"]), "", ""])
    return index_path, sheet_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path,
                        default=Path("data/audit/quality"))
    args = parser.parse_args()
    try:
        report = find_candidates(args.file)
        idx, sheet = save_private_review(report, args.output_dir)
    except (OSError, ValueError, AssertionError, csv.Error, UnicodeError) as exc:
        print(f"D1 REVIEW STOP: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": report["status"],
        "source_sha256": report["source_sha256"],
        "duplicate_groups_needing_review": report["duplicate_group_count"],
        "duplicate_extra_rows": report["normalized_duplicate_extra_rows"],
        "administrative_rows_needing_review": report["heuristic_admin_candidate_count"],
        "private_review_index": str(idx),
        "private_review_sheet": str(sheet),
        "action": "Manual adjudication ONLY; no rows removed",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
