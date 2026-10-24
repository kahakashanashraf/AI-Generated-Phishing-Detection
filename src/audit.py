"""Basic manifest integrity audit. No text is transmitted."""
import argparse
import hashlib
import re
import pandas as pd

COLUMNS = {"text", "label", "generator", "source", "group_id"}

def normalize(text):
    return re.sub(r"\\s+", " ", str(text).strip().lower())

def audit(frame):
    missing = COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Empty dataset")
    if frame[list(COLUMNS)].isna().any().any():
        raise ValueError("Null required fields")
    if not set(frame.label.unique()).issubset({0, 1}):
        raise ValueError("label must be 0 or 1")
    if (frame.text.astype(str).str.strip() == "").any():
        raise ValueError("Blank text")
    if (frame.group_id.astype(str).str.strip() == "").any():
        raise ValueError("Blank group_id")
    ai = frame[frame.label == 1]
    human = frame[frame.label == 0]
    if ai.empty or human.empty:
        raise ValueError("Both classes needed")
    if (ai.generator.astype(str).str.lower() == "human").any():
        raise ValueError("AI label paired with human generator")
    if (human.generator.astype(str).str.lower() != "human").any():
        raise ValueError("Human label must use generator=human")
    x = frame.copy()
    x["text_hash"] = x.text.map(lambda v: hashlib.sha256(normalize(v).encode()).hexdigest())
    conflicting = x.groupby("text_hash").agg(n_labels=("label", "nunique"), n_groups=("group_id", "nunique"))
    collisions = conflicting[(conflicting.n_labels > 1) | (conflicting.n_groups > 1)]
    if not collisions.empty:
        raise ValueError(f"Exact normalized text duplicate spans different groups/labels: {len(collisions)}")
    conflicting_groups = x.groupby("group_id").label.nunique()
    if (conflicting_groups > 1).any():
        raise ValueError("Same ancestor group has multiple labels; investigate provenance")
    return {"rows": len(frame), "groups": frame.group_id.nunique(),
            "generators": ai.generator.value_counts().to_dict(),
            "sources": frame.source.value_counts().to_dict(),
            "classes": frame.label.value_counts().to_dict(),
            "duplicate_rows": int(x.text_hash.duplicated().sum())}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    args = parser.parse_args()
    print(audit(pd.read_csv(args.csv)))
