"""Owner-side helpers for the 04 human validation (run locally; see docs/HUMAN_VALIDATION_PROTOCOL.md).

  python scripts/human_validation.py extract A path/to/rater_A.xlsx
      Reads ONLY item IDs and answers from a completed workbook. Writes
      results/04_human_validation/ratings/rater_A.csv, which contains no email text and is safe to commit.

  python scripts/human_validation.py disagreements
      Once both raters are extracted, writes results/04_human_validation/ratings/adjudication.csv. That file has one
      row per item and question where the raters differ. Fill its 'resolved' column after discussion. Keep the
      'note' column short, and never put email text in it.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from phishbench import human_validation as hv  # noqa: E402

RATINGS = REPO / "results" / "04_human_validation" / "ratings"
FIELDS = ["item_id", "task", *hv.ANSWER_COLUMNS]


def _write(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in fields} for r in rows)


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main(argv: list[str]) -> int:
    if argv[:1] == ["extract"] and len(argv) == 3:
        rater, xlsx = argv[1].upper(), Path(argv[2])
        rows = sorted(hv.read_workbook(xlsx), key=lambda r: r["item_id"])
        out = RATINGS / f"rater_{rater}.csv"
        _write(out, rows, FIELDS)
        print(f"{len(rows)} items -> {out}")
        return 0
    if argv[:1] == ["disagreements"]:
        a, b = _read(RATINGS / "rater_A.csv"), _read(RATINGS / "rater_B.csv")
        out = RATINGS / "adjudication.csv"
        if out.exists():
            print(f"{out} already exists; not overwritten")
            return 1
        rows = hv.disagreements(a, b)
        _write(out, rows, ["item_id", "question", "rater_A", "rater_B", "resolved", "note"])
        print(f"{len(rows)} disagreements -> {out} (fill the 'resolved' column after discussion)")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
