"""Thresholds, intervals and paired tests used by every Study 2 endpoint (pre-registration §4, §6)."""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np


def threshold_at_fpr(y, scores, target: float = 0.05) -> float:
    """Smallest threshold whose validation FPR is <= target (higher score means phishing).

    This is identical to the N05 rule, so Study 1 and Study 2 thresholds are comparable.
    """
    y = np.asarray(y)
    s = np.asarray(scores, dtype=float)
    neg = s[y == 0]
    if len(neg) < 20:
        raise ValueError("Insufficient validation legitimate controls")
    candidates = np.unique(np.r_[np.nextafter(s.max(), np.inf), s])
    for t in candidates:
        if float(np.mean(neg >= t)) <= target:
            return float(t)
    return float(s.max() + 1.0)


def wilson_ci(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(n01: int, n10: int) -> float:
    """Two-sided exact McNemar p-value: a binomial test on the discordant pairs."""
    n = n01 + n10
    if n == 0:
        return 1.0
    k = min(n01, n10)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired_discordance(a, b) -> tuple[int, int]:
    """For paired binary decisions a (reference) and b (comparison): (n_a0_b1, n_a1_b0)."""
    a = np.asarray(a, dtype=int)
    b = np.asarray(b, dtype=int)
    return int(np.sum((a == 0) & (b == 1))), int(np.sum((a == 1) & (b == 0)))


def cluster_bootstrap_delta(clusters, ref, cmp, iterations: int = 10_000, seed: int = 2026,
                            levels=(0.90, 0.95)) -> dict:
    """Cluster (parent) bootstrap of mean(cmp) - mean(ref).

    clusters: cluster id per paired row. ref/cmp: 0/1 outcomes per row (for example
    false-positive indicators). Rows that share a cluster are resampled together.
    """
    clusters = np.asarray(clusters)
    ref = np.asarray(ref, dtype=float)
    cmp = np.asarray(cmp, dtype=float)
    idx_by = defaultdict(list)
    for i, c in enumerate(clusters):
        idx_by[c].append(i)
    keys = sorted(idx_by, key=str)
    sums = np.array([[ref[idx_by[k]].sum(), cmp[idx_by[k]].sum(), len(idx_by[k])] for k in keys])
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(keys), size=(iterations, len(keys)))
    tot = sums[draws].sum(axis=1)
    deltas = tot[:, 1] / tot[:, 2] - tot[:, 0] / tot[:, 2]
    point = float(cmp.mean() - ref.mean())
    out = {"delta": point, "iterations": iterations, "clusters": len(keys)}
    for lv in levels:
        lo, hi = np.quantile(deltas, [(1 - lv) / 2, 1 - (1 - lv) / 2])
        out[f"ci{int(lv * 100)}"] = (float(lo), float(hi))
    return out


def tost_equivalent(boot: dict, margin: float = 0.03) -> bool:
    """TOST at alpha = 0.05: equivalence holds if the 90% CI lies inside (-margin, +margin)."""
    lo, hi = boot["ci90"]
    return (lo > -margin) and (hi < margin)


def holm(pvalues: dict) -> dict:
    """Holm-Bonferroni adjusted p-values (monotone), keyed like the input."""
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, running = {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        adj[k] = running
    return adj
