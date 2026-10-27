"""Resume a Kaggle research session with no duplicate download or audit runs.

Run from a cloned repository:
    python scripts/kaggle_resume.py
    python scripts/kaggle_resume.py --input-root /kaggle/input --repo /kaggle/working/AI-Generated-Phishing-Detection

Behavior:
- Creates/verifies the canonical data/ directories.
- Reuses an existing Nazario.csv in private working storage.
- Otherwise mounts a checksum-verified /kaggle/input/**/Nazario.csv with a
  read-only symlink into data/datasets/D1_curated_emails/raw/.
- Runs metadata and quality scans ONCE per local SHA256, skipping cached
  reports with matching SHA256.
- Never downloads, uploads, commits, prints raw emails, visits links or trains.
- A source's cryptographic identity is not license/ground-truth approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from audit_d1_preview import analyze
from audit_d1_quality import inspect
from init_data_workspace import ensure_workspace

NAZARIO_MD5 = "4022d055bb7cf8602f30f768f652e91e"


def hashes(path: Path) -> tuple[str, str]:
    md5, sha = hashlib.md5(), hashlib.sha256()  # nosec: MD5 Zenodo source identity
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            md5.update(chunk)
            sha.update(chunk)
    return md5.hexdigest(), sha.hexdigest()


def select_nazario(target: Path, input_root: Path) -> tuple[Path | None, str]:
    """Don't overwrite existing files. Link only exact known-MD5 Kaggle inputs."""
    if target.exists():
        if not target.is_file():
            raise ValueError("Nazario destination exists but is not a file")
        actual, _ = hashes(target)
        if actual != NAZARIO_MD5:
            raise ValueError("Existing Nazario.csv checksum mismatch. STOP; do not overwrite it.")
        return target, "existing verified local file or input mount"

    if target.is_symlink():
        raise ValueError("Existing Nazario.csv symlink is broken. STOP; remove manually after verification.")

    if not input_root.is_dir():
        return None, "No attached Kaggle input folder"

    # Deterministic lookup. Strict hash verification prevents linking the
    # wrong file if several different datasets use the same filename.
    matches = sorted(p for p in input_root.rglob("Nazario.csv") if p.is_file())
    for candidate in matches:
        if candidate.resolve() == target.resolve():
            continue
        md5, _ = hashes(candidate)
        if md5 != NAZARIO_MD5:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(candidate.resolve())
        return target, "mounted existing Kaggle input (verified MD5)"
    return None, "No checksum-matching Nazario.csv in attached Kaggle inputs"


def _cached_report(path: Path, source_sha256: str, key: str) -> bool:
    if not path.is_file():
        return False
    try:
        r = json.loads(path.read_text(encoding="utf-8"))
        return (isinstance(r, dict) and r.get(key) == source_sha256
                and r.get("status") in (
                    "PREVIEW_ONLY_NOT_LICENSE_OR_LABEL_APPROVAL",
                    "QUALITY_ONLY_NO_TRAINING_OR_LICENSE_GO",
                ))
    except (ValueError, OSError, UnicodeError):
        return False


def resume(repo: Path, input_root: Path) -> dict[str, str]:
    data = repo / "data"
    ensure_workspace(data)
    raw = data / "datasets/D1_curated_emails/raw/Nazario.csv"
    source, mode = select_nazario(raw, input_root)
    report = {"workspace": "READY", "Nazario": mode}
    if source is None:
        report["next_action"] = (
            "Use your existing Nazario.csv in the private local raw/ folder, "
            "or attach a lawful private Kaggle input with Nazario.csv. "
            "No download was attempted."
        )
        return report

    _, sha = hashes(source)
    preview = data / "audit/quality/D1_Nazario_preview.json"
    quality = data / "audit/quality/D1_Nazario_full_quality.json"

    # Unlike the quality report, the preview report nests SHA256.
    preview_cached = False
    if preview.is_file():
        try:
            contents = json.loads(preview.read_text(encoding="utf-8"))
            preview_cached = (
                contents.get("status") == "PREVIEW_ONLY_NOT_LICENSE_OR_LABEL_APPROVAL"
                and contents.get("checksums", {}).get("sha256") == sha
                and contents.get("zenodo_md5_match") is True
                and contents.get("rows_examined", 0) > 0
            )
        except (ValueError, OSError, AttributeError, UnicodeError):
            preview_cached = False

    if preview_cached:
        report["preview"] = "REUSED existing checksum-matched result"
    else:
        value = analyze(source, max_rows=2000)
        preview.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        report["preview"] = f"EXECUTED ({value['rows_examined']} rows, metadata only)"

    if _cached_report(quality, sha, "sha256"):
        report["quality"] = "REUSED existing checksum-matched result"
    else:
        value = inspect(source)
        quality.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        report["quality"] = (
            f"EXECUTED ({value['rows_full_scan']} rows; "
            f"{value['exact_duplicate_extra_rows_subject_body']} exact, "
            f"{value['normalized_duplicate_extra_rows_subject_body']} normalized extra duplicates)"
        )
    report["SHA256"] = sha
    report["status"] = "AUDITS_NOT_LABEL_OR_LICENSE_APPROVAL"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--input-root", type=Path,
                        default=Path("/kaggle/input"))
    args = parser.parse_args()
    try:
        result = resume(args.repo, args.input_root)
    except (OSError, ValueError) as ex:
        print(f"KAGGLE RESUME STOP: {ex}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
