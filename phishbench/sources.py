"""Pinned source registry and verified downloads for Study 2 (pre-registration §2–§3).

Each source carries the strongest pin available:
- Zenodo: MD5 published by Zenodo.
- GitHub: Git blob SHA-1.
- Hugging Face: immutable revision plus SHA-256.
- monkey.org Nazario mboxes: no hash is published, so the SHA-256 is recorded on first download
  (trust on first use) and must match on every later run.
"""

from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from .manifest import git_blob_sha1, md5_file, sha256_file

ZENODO_D1 = "https://zenodo.org/api/records/8339691/files/{name}/content"
NAZARIO = "https://monkey.org/~jose/phishing/phishing-{year}"
LLMGEN_REV = "d717e5457b71cb44dd038dafe6a81cea5e0badab"
EPHISH_BLOB = "7a0e74ecebc1f3f5b21f42deccfb716b14bba46b"


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    licence: str
    role: str
    size: int | None = None
    md5: str | None = None
    sha256: str | None = None
    git_blob: str | None = None
    notes: str = ""


D1 = {
    "Enron.csv": (44837129, "10489e0fdcc8af6fe62135c689367d40"),
    "SpamAssasin.csv": (14879195, "d921e0b2333bfaa058bd38193e6b3fbd"),
    "CEAS_08.csv": (67902056, "1f0d59191eec892a709995d48cd8decb"),
    "Nigerian_Fraud.csv": (9192393, "65fd47ae7cb4ae762e4be42b11905d63"),
}


def registry() -> dict[str, Source]:
    reg: dict[str, Source] = {}
    for name, (size, md5) in D1.items():
        reg[f"d1/{name}"] = Source(f"d1/{name}", ZENODO_D1.format(name=name), "CC-BY-4.0 (collection; constituent rights noted)",
                                   "R2 train pool / EXT legitimate", size=size, md5=md5)
    for year in range(2015, 2026):
        role = "R2 train (phishing)" if year <= 2021 else ("EXT-phish-H" if year == 2022 else "MODERN-phish")
        reg[f"nazario/{year}"] = Source(f"nazario/{year}", NAZARIO.format(year=year), "CC-BY-4.0 (monkey.org README)", role)
    reg["llmgen/GPT_Phishing_Email_dataset.csv"] = Source(
        "llmgen/GPT_Phishing_Email_dataset.csv",
        f"https://huggingface.co/datasets/Dizzzy0x00/LLMGen-Phishing-Email-Dataset/resolve/{LLMGEN_REV}/GPT_Phishing_Email_dataset.csv",
        "Apache-2.0", "LOCKED AI-authored", size=5690445,
        sha256="e3a335c8acacec09afaa4b9a14c7010195063310e4dcfbae38c1fa50b8d48dc3")
    reg["d3/PhishFuzzer_emails_original_seed_v1.json"] = Source(
        "d3/PhishFuzzer_emails_original_seed_v1.json",
        "https://raw.githubusercontent.com/DataPhish/PhishFuzzer/1e21dd4edbe5c64694f156bf5318c97c7c80681c/"
        "PhishFuzzer_emails_original_seed_v1.json",
        "no licence declared (lineage audit only; excluded from Study 2)", "D2->D3 lineage audit",
        size=8218997, git_blob="294e84ed06957ab64b3a6fe4dfc05a6afda7f7de")
    reg["ephish/ephishLLM.json"] = Source(
        "ephish/ephishLLM.json", "https://raw.githubusercontent.com/pajola/e-phishGen/main/ephishLLM.json",
        "MIT", "DEV AI-authored", git_blob=EPHISH_BLOB)
    return reg


def download(src: Source, dest_dir: Path, tofu: dict | None = None, max_bytes: int = 400_000_000,
             retries: int = 3) -> dict:
    """Download (or reuse a cached copy of) a source, verify every available pin, return a receipt.

    tofu: mapping of source name to recorded sha256, used for sources without a published hash.
    It raises if a recorded hash no longer matches.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dst = dest_dir / src.name.replace("/", "__")

    def verify(path: Path) -> dict:
        rec = {"name": src.name, "url": src.url, "licence": src.licence, "role": src.role,
               "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        if src.size is not None and rec["bytes"] != src.size:
            raise ValueError(f"{src.name}: size {rec['bytes']} != pinned {src.size}")
        if src.md5 is not None:
            rec["md5"] = md5_file(path)
            if rec["md5"] != src.md5:
                raise ValueError(f"{src.name}: MD5 mismatch")
        if src.sha256 is not None and rec["sha256"] != src.sha256:
            raise ValueError(f"{src.name}: SHA-256 mismatch")
        if src.git_blob is not None:
            rec["git_blob"] = git_blob_sha1(path)
            if rec["git_blob"] != src.git_blob:
                raise ValueError(f"{src.name}: Git blob mismatch (content changed upstream)")
        if tofu and src.name in tofu and tofu[src.name] != rec["sha256"]:
            raise ValueError(f"{src.name}: recorded SHA-256 (trust on first use) no longer matches")
        rec["pin"] = ("md5" if src.md5 else "sha256" if src.sha256 else "git_blob" if src.git_blob
                      else "tofu-recorded" if tofu and src.name in tofu else "tofu-first-use")
        return rec

    if dst.is_file():
        try:
            rec = verify(dst)
            rec["origin"] = "verified_cache"
            return rec
        except ValueError:
            dst.unlink()

    last_err = None
    for attempt in range(retries):
        part = dst.with_suffix(dst.suffix + ".part")
        try:
            req = urllib.request.Request(src.url, headers={"User-Agent": "phishbench-research/2.1"})
            with urllib.request.urlopen(req, timeout=180) as r, part.open("wb") as f:
                total = 0
                for block in iter(lambda: r.read(1 << 20), b""):
                    total += len(block)
                    if total > max_bytes:
                        raise ValueError(f"{src.name}: exceeds {max_bytes} bytes")
                    f.write(block)
            part.replace(dst)
            rec = verify(dst)
            rec["origin"] = "pinned_download"
            return rec
        except Exception as e:  # retry network errors; verification errors also retry once more
            last_err = e
            if part.exists():
                part.unlink()
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Download failed for {src.name}: {last_err}")
