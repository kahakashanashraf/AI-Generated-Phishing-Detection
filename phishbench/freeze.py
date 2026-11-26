"""Decontamination and seeded cell selection for N15 (pre-registration §3.1 and §3.3)."""

from __future__ import annotations

from collections import Counter

import numpy as np

from .dedup import LSHIndex, MinHasher, shingles
from .textnorm import detect_language, text_key, word_count


class Decontaminator:
    """Exact-key plus MinHash/LSH membership test against a protected set of documents."""

    def __init__(self, hasher: MinHasher, threshold: float = 0.80, cache: dict | None = None):
        self.hasher = hasher
        self.keys: set[str] = set()
        self.lsh = LSHIndex(num_perm=hasher.num_perm, bands=16, threshold=threshold)
        self.cache = cache if cache is not None else {}
        self._n = 0

    def signature(self, rec: dict):
        sid = rec.get("sample_id")
        if sid is not None and sid in self.cache:
            return self.cache[sid]
        sig = self.hasher.signature(shingles(f"{rec['subject']}\n{rec['body']}"))
        if sid is not None:
            self.cache[sid] = sig
        return sig

    def add(self, rec: dict, sig=None) -> None:
        self.keys.add(text_key(rec["subject"], rec["body"]))
        self.lsh.add(self._n, self.signature(rec) if sig is None else sig)
        self._n += 1

    def linked(self, rec: dict, sig=None) -> bool:
        if text_key(rec["subject"], rec["body"]) in self.keys:
            return True
        return bool(self.lsh.query(self.signature(rec) if sig is None else sig))

    def __len__(self) -> int:
        return self._n


def basic_ok(rec: dict, min_words: int | None = None, max_words: int | None = None,
             require_english: bool = True) -> str | None:
    """Return None if the record passes, otherwise a short exclusion reason (counted in outputs)."""
    if not (rec["body"] or "").strip():
        return "empty_body"
    wc = word_count(rec["body"])
    if min_words is not None and wc < min_words:
        return "too_short"
    if max_words is not None and wc > max_words:
        return "too_long"
    if require_english and detect_language(f"{rec['subject']}\n{rec['body']}") != "en":
        return "not_english"
    return None


def seeded_order(records: list[dict], seed: int) -> list[dict]:
    """Deterministic shuffle that does not depend on input order (sorted by sample_id first)."""
    recs = sorted(records, key=lambda r: r["sample_id"])
    perm = np.random.default_rng(seed).permutation(len(recs))
    return [recs[i] for i in perm]


def select_cell(candidates: list[dict], n_max: int | None, seed: int, protected: Decontaminator,
                hasher: MinHasher, **filter_kw) -> tuple[list[dict], Counter]:
    """Walk candidates in seeded random order and keep a record only if it:
    passes the filters, is not linked to the protected (training/validation) set, and is not a
    near-duplicate of a record already kept in this cell. Stops at n_max.
    This is equivalent to uniform random sampling from the eligible, de-duplicated pool.
    """
    kept, reasons = [], Counter()
    local = Decontaminator(hasher, threshold=protected.lsh.threshold, cache=protected.cache)
    for rec in seeded_order(candidates, seed):
        if n_max is not None and len(kept) >= n_max:
            break
        why = basic_ok(rec, **filter_kw)
        if why:
            reasons[why] += 1
            continue
        sig = protected.signature(rec)
        if protected.linked(rec, sig):
            reasons["linked_to_train_or_val"] += 1
            continue
        if local.linked(rec, sig):
            reasons["near_duplicate_within_cell"] += 1
            continue
        local.add(rec, sig)
        kept.append(rec)
    reasons["kept"] = len(kept)
    return kept, reasons


def proportional_allocation(counts: dict, cap: int) -> dict:
    """Largest-remainder allocation of a total cap across strata, never exceeding stratum size."""
    total = sum(counts.values())
    if total <= cap:
        return dict(counts)
    raw = {k: cap * v / total for k, v in counts.items()}
    alloc = {k: min(counts[k], int(np.floor(x))) for k, x in raw.items()}
    rest = cap - sum(alloc.values())
    for k in sorted(raw, key=lambda k: (-(raw[k] - np.floor(raw[k])), str(k))):
        if rest <= 0:
            break
        if alloc[k] < counts[k]:
            alloc[k] += 1
            rest -= 1
    return alloc
