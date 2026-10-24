"""Leakage-conscious zero-shot held-out-generator TF-IDF + LR baseline.

Usage: python -m src.baseline --csv manifest.csv --held-out MODEL --out outputs/metrics.json
The manifest represents only *phishing* messages. Labels refer to AI vs human origin.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from .audit import audit

def run(frame, held_out, seed=42):
    report = audit(frame)
    ai_held = frame[(frame.label == 1) & (frame.generator == held_out)]
    seen = frame[~((frame.label == 1) & (frame.generator == held_out))]
    if ai_held.empty:
        raise ValueError(f"No AI examples for generator={held_out!r}")
    if (seen.group_id.isin(ai_held.group_id)).any():
        raise ValueError("Held-out generator shares ancestor groups with seen data")
    if seen.generator.eq(held_out).any():
        raise ValueError("Held-out generator present in training pool")
    # Independent train, val and human-control test groups from seen data.
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.4, random_state=seed)
    tr_idx, temp_idx = next(splitter.split(seen, seen.label, seen.group_id))
    train, temp = seen.iloc[tr_idx], seen.iloc[temp_idx]
    split2 = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=seed + 1)
    va_idx, te_idx = next(split2.split(temp, temp.label, temp.group_id))
    val, ctrl = temp.iloc[va_idx], temp.iloc[te_idx]
    for name, part in [("train", train), ("validation", val)]:
        if part.label.nunique() != 2:
            raise ValueError(f"{name} must contain both classes; need more independent groups")
    human_control = ctrl[ctrl.label == 0]
    if human_control.empty:
        raise ValueError("No human control samples in test split")
    segments = [train, val, ctrl, ai_held]
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            if set(segments[i].group_id) & set(segments[j].group_id):
                raise ValueError("Group leakage across split boundaries")
    model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=30000),
                          LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed))
    model.fit(train.text.astype(str), train.label.astype(int))
    # Choose threshold using validation only; never look at target generator labels.
    val_prob = model.predict_proba(val.text.astype(str))[:, 1]
    y_val = val.label.to_numpy(dtype=int)
    grid = np.linspace(0.01, 0.99, 99)
    scores = [f1_score(y_val, val_prob >= t, zero_division=0) for t in grid]
    threshold = float(grid[int(np.argmax(scores))])
    test = pd.concat([human_control, ai_held], ignore_index=True)
    y = test.label.to_numpy(dtype=int)
    probs = model.predict_proba(test.text.astype(str))[:, 1]
    pred = (probs >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    results = {
        "task": "ai_vs_human_origin_among_phishing_only",
        "held_out_generator": held_out,
        "seed": seed, "threshold_source": "seen_validation_only",
        "threshold": threshold,
        "train_n": len(train), "validation_n": len(val),
        "human_test_n": len(human_control), "unseen_ai_test_n": len(ai_held),
        "seen_train_generators": sorted(train.loc[train.label == 1, "generator"].unique().tolist()),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "auroc": float(roc_auc_score(y, probs)),
        "average_precision": float(average_precision_score(y, probs)),
        "false_positive_rate": float(fp / (fp + tn)),
        "confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "manifest_audit": report,
        "WARNING": "This is origin attribution among phishing emails, not phishing-vs-benign evaluation."
    }
    return results

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--held-out", required=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="outputs/baseline_metrics.json")
    args = p.parse_args()
    output = run(pd.read_csv(args.csv), args.held_out, args.seed)
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k not in {"manifest_audit"}}, indent=2))

if __name__ == "__main__":
    main()
