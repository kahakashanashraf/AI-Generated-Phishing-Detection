"""Run before creating a GitHub release (which Zenodo archives).

Fails if any author is still a placeholder, or if the release metadata is malformed.
Usage: python scripts/check_release_metadata.py
"""
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
problems = []
zen = json.loads((R / ".zenodo.json").read_text(encoding="utf-8"))
for c in zen["creators"]:
    if "[AUTHOR" in c["name"] or "," not in c["name"]:
        problems.append(f".zenodo.json creator not filled or not 'Family, Given': {c['name']}")
cff = (R / "CITATION.cff").read_text(encoding="utf-8")
if "[AUTHOR" in cff:
    problems.append("CITATION.cff still has an author placeholder")
for f in ("LICENSE", "LICENSE-CC-BY-4.0.md"):
    if not (R / f).exists():
        problems.append(f"missing {f}")
if problems:
    print("NOT READY FOR RELEASE:")
    print("\n".join("  - " + p for p in problems))
    sys.exit(1)
print("Release metadata OK:", ", ".join(c["name"] for c in zen["creators"]))
