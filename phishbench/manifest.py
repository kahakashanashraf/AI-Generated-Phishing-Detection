"""Hashing, JSON writing and environment capture for run manifests."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git_blob_sha1(path: Path) -> str:
    p = Path(path)
    h = hashlib.sha1(b"blob " + str(p.stat().st_size).encode() + b"\x00")
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha256_of_ids(ids) -> str:
    """Fingerprint of a set of sample IDs: sha256 over the sorted, newline-joined list."""
    return hashlib.sha256("\n".join(sorted(map(str, ids))).encode("utf-8")).hexdigest()


def write_json(path: Path, obj) -> None:
    """Write strict JSON with a real trailing newline. (The N05–N10 bug wrote a literal backslash-n.)"""
    text = json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False, default=str)
    json.loads(text)  # fail loudly if the payload is not valid JSON
    # Written as bytes so the file (and its hash) is identical on Linux (Kaggle) and Windows.
    Path(path).write_bytes((text + "\n").encode("utf-8"))


def environment(repo_dir: Path | None = None) -> dict:
    env = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    for mod in ("numpy", "pandas", "sklearn", "torch", "transformers", "vllm", "langdetect"):
        try:
            env[f"pkg_{mod}"] = getattr(__import__(mod), "__version__", "present")
        except Exception:
            env[f"pkg_{mod}"] = None
    if repo_dir is not None:
        try:
            env["git_commit"] = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
                                               capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception:
            env["git_commit"] = None
    return env


def file_hashes(folder: Path) -> dict:
    folder = Path(folder)
    return {str(p.relative_to(folder)).replace("\\", "/"): sha256_file(p)
            for p in sorted(folder.rglob("*")) if p.is_file() and p.name != "run_manifest.json"}
