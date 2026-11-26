"""Deterministic MinHash + LSH near-duplicate linking and union-find grouping (pre-registration §3.3).

Shingles are 5-word windows of the normalised text. Hash values come from crc32, so they are
stable across processes and platforms; Python's salted hash() is never used. The LSH banding
(16 bands x 8 rows) proposes candidate pairs, and a candidate is accepted only if the
signature-estimated Jaccard similarity is at least the threshold (0.80 by default).
"""

from __future__ import annotations

import zlib
from collections import defaultdict

import numpy as np

from .textnorm import normalize

_MERSENNE = np.uint64((1 << 61) - 1)
_MAX32 = np.uint64(0xFFFFFFFF)


def shingles(text: str, k: int = 5) -> set[int]:
    toks = normalize(text).split()
    if not toks:
        return set()
    if len(toks) < k:
        return {zlib.crc32(" ".join(toks).encode("utf-8"))}
    return {zlib.crc32(" ".join(toks[i:i + k]).encode("utf-8")) for i in range(len(toks) - k + 1)}


class MinHasher:
    def __init__(self, num_perm: int = 128, seed: int = 2026):
        rng = np.random.default_rng(seed)
        self.num_perm = num_perm
        self.a = rng.integers(1, (1 << 61) - 1, size=num_perm, dtype=np.uint64)
        self.b = rng.integers(0, (1 << 61) - 1, size=num_perm, dtype=np.uint64)

    def signature(self, shingle_set: set[int]) -> np.ndarray:
        if not shingle_set:
            return np.full(self.num_perm, np.iinfo(np.uint64).max, dtype=np.uint64)
        x = np.fromiter(shingle_set, dtype=np.uint64, count=len(shingle_set))[:, None]
        # (a*x + b) mod p, computed modulo 2**64 and then reduced. This is a valid universal-style
        # hash family for MinHash, and it is deterministic.
        h = (x * self.a + self.b) % _MERSENNE
        return (h & _MAX32).min(axis=0)


def estimated_jaccard(s1: np.ndarray, s2: np.ndarray) -> float:
    return float(np.mean(s1 == s2))


class LSHIndex:
    """Banded LSH over MinHash signatures. Keys are arbitrary hashable ids."""

    def __init__(self, num_perm: int = 128, bands: int = 16, threshold: float = 0.80):
        if num_perm % bands:
            raise ValueError("num_perm must be divisible by bands")
        self.bands, self.rows, self.threshold = bands, num_perm // bands, threshold
        self.tables: list[dict[bytes, list]] = [defaultdict(list) for _ in range(bands)]
        self.sigs: dict = {}

    def _band_keys(self, sig: np.ndarray):
        for b in range(self.bands):
            yield b, sig[b * self.rows:(b + 1) * self.rows].tobytes()

    def add(self, key, sig: np.ndarray) -> None:
        self.sigs[key] = sig
        for b, bk in self._band_keys(sig):
            self.tables[b][bk].append(key)

    def query(self, sig: np.ndarray) -> list:
        cands = set()
        for b, bk in self._band_keys(sig):
            cands.update(self.tables[b].get(bk, ()))
        return sorted((c for c in cands if estimated_jaccard(sig, self.sigs[c]) >= self.threshold), key=str)


class UnionFind:
    def __init__(self):
        self.parent: dict = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            if str(ra) < str(rb):
                self.parent[rb] = ra
            else:
                self.parent[ra] = rb

    def groups(self) -> dict:
        out = defaultdict(list)
        for x in self.parent:
            out[self.find(x)].append(x)
        return out
