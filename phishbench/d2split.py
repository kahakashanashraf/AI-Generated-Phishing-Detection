"""Exact reproduction of the frozen N05 D2 parent split (Study 1), so Study 2 reuses the same IN test.

The logic is copied rule for rule from notebooks/05_AI_Written_Legitimate_False_Alarm_Benchmark.ipynb.
The expected sizes are asserted: train 1,418, validation 304, test 304 (142 legitimate, 162 phishing).
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

D2_REV = "d13e9bb73d03f458e6d5b6cb6c7b0a708ea47e3d"
D2_FILES = {
    "original": ("1_DataSet/cleaned_emails.json", 7370034, "b9d6dd2ac3d6e2d337b9b9d79fc8f1f4377ea4f9"),
    "deepseek": ("3_RePhrase/DeepSeek/emails_rephrased_clean_deepseek.json", 7528880,
                 "11cc02aeb03b5a318f3107a71a20f2406b8f790a"),
    "gpt4o": ("3_RePhrase/GPT4/emails_rephrased_clean_openai4o.json", 7079916,
              "d0cf5fe3bdf0a3dd962492720c3cb10381f9e313"),
    "randomapi": ("3_RePhrase/RandomAPI/emails_rephrased_openrouter_clean.json", 7124691,
                  "2febaf0e74ac23689889164bfe5b8e538b706140"),
}
SEED = 2026
EXPECTED = {"train": 1418, "val": 304, "test": 304, "test_legit": 142, "test_phish": 162}


def d2_url(rel: str) -> str:
    from urllib.parse import quote
    return f"https://raw.githubusercontent.com/HarmJ0y/PhishingSpamDataSet/{D2_REV}/{quote(rel, safe='/')}"


def get(row: dict, *keys):
    normalized = {re.sub("[^a-z0-9]", "", str(k).lower()): v for k, v in row.items()}
    for k in keys:
        x = normalized.get(re.sub("[^a-z0-9]", "", k.lower()))
        if x is not None:
            return x
    return None


def load_json_list(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig") as f:
        d = json.load(f)
    if isinstance(d, dict):
        d = next((d[k] for k in ("emails", "data", "records", "items", "dataset", "results")
                  if isinstance(d.get(k), list)), None)
    if not isinstance(d, list) or not all(isinstance(x, dict) for x in d):
        raise ValueError("Invalid JSON list")
    return d


def ident(x):
    if x is None or isinstance(x, (dict, list, bool)):
        return None
    s = str(x).strip()
    if not s or s.casefold() in ("none", "null", "nan"):
        return None
    if re.fullmatch(r"\d+\.0", s):
        s = s[:-2]
    return s


def label(r: dict):
    return {"Phishing": 1, "Valid": 0}.get(get(r, "Type"))


def subject_body(r: dict) -> tuple[str, str]:
    return str(get(r, "Subject") or ""), str(get(r, "Body") or "")


def n05_text(r: dict) -> str:
    s, b = subject_body(r)
    return s + "\n" + b


def _digest(s: str) -> str:
    return hashlib.sha256(" ".join(s.casefold().split()).encode("utf-8")).hexdigest()


def index_by_no(rows: list[dict]) -> dict:
    out = {}
    for r in rows:
        key = ident(get(r, "No."))
        if key is None or key in out:
            raise ValueError("Missing/duplicate original parent ID")
        out[key] = r
    return out


def n05_split(original_rows: list[dict]) -> dict:
    """Return {'train','val','test'} lists of D2 'No.' ids, plus 'valid' (id -> row) and 'excluded'."""
    from sklearn.model_selection import train_test_split

    orig = index_by_no(original_rows)
    if len(orig) != 3075:
        raise ValueError("Source revision/row count changed")
    counts = Counter(str(get(r, "Type")) for r in orig.values())
    if counts != {"Phishing": 1090, "Spam": 1000, "Valid": 950, "Phishing Simulation": 35}:
        raise ValueError("Original class taxonomy changed")
    valid = {k: r for k, r in orig.items() if label(r) is not None and n05_text(r).strip()}
    text_to_groups, text_to_classes = defaultdict(set), defaultdict(set)
    for k, r in valid.items():
        h = _digest(n05_text(r))
        text_to_groups[h].add(k)
        text_to_classes[h].add(label(r))
    excluded = {k for h, ids in text_to_groups.items()
                if len(ids) > 1 or len(text_to_classes[h]) > 1 for k in ids}
    valid = {k: r for k, r in valid.items() if k not in excluded}
    keys = sorted(valid)
    y = [label(valid[k]) for k in keys]
    train, tmp = train_test_split(keys, test_size=.3, random_state=SEED, stratify=y)
    val, test = train_test_split(tmp, test_size=.5, random_state=SEED, stratify=[label(valid[k]) for k in tmp])
    got = {"train": len(train), "val": len(val), "test": len(test),
           "test_legit": sum(label(valid[k]) == 0 for k in test),
           "test_phish": sum(label(valid[k]) == 1 for k in test)}
    if got != EXPECTED:
        raise ValueError(f"N05 split not reproduced: {got} != {EXPECTED}")
    return {"train": train, "val": val, "test": test, "valid": valid, "excluded": sorted(excluded), "orig": orig}
