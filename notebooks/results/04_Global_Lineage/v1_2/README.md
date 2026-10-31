# Notebook 04 v1.2 — verified global-lineage execution evidence

**Evidence source:** The researcher's executed Kaggle notebook `04-global-lineage-and-frozen-splits.ipynb` and `results (2)(2).zip`, uploaded 2026-10-31. All five `phishing_global_lineage_evidence/` files below have been **committed byte-identically** (Git blob SHA-1 checked against uploaded ZIP contents). No raw emails, addresses, URLs, parent keys or private per-row hashes were committed.

| Original safe artifact | File | SHA256 from uploaded ZIP |
|---|---|---|
| Full 13-source / 78 source-pair report | [lineage_audit.json](lineage_audit.json) | `9a77fffd69a21bdf45122ad37fac9bca272c95dfdb5c183799b66c2a25c27245` |
| Environment | [environment.json](environment.json) | `5c61c0f0deada7586cc87a7e6fd2eb746575a939caefe58a62dcbe8c0c93b8c5` |
| Resource | [resource_usage.json](resource_usage.json) | `c2a68c5f4461806fcd0d6bd685e2d97983e932c88868dfdefc420935eacdc9f1` |
| Run manifest | [run_manifest.json](run_manifest.json) | `52b35de4869ac32d8e83c3114bab7560ceb1fe801ad62830cf2fde8b92f945c1` |
| Summary | [summary.txt](summary.txt) | `49e587562f6e298ab98cd13a51503c376cfd5e1e7a5d0916691d1aa7291a6e17` |

**Original uploaded notebook SHA256:** `0a61e5bb37884e6a935c01c203f8b24c85c9fbb0951dc3a7d68f402d6ab0bcbc`.

**Original uploaded ZIP SHA256:** `5d3174d711b78e48d5bdb4bbe73dee31f14c9dac7e1e444860c28f3704e7fc67`.

## Reproducible observations

- **13/13 SHA256-pinned sources passed**, 121,536 source-file rows scanned; synthetic self-test PASS.
- **85,721** reported exact normalized-text + structural-parent connected components; **4,838** across multiple named source files; **3,018** across D1/D2/D3/D4 families; **40,111** rows in multi-file connected components. These are *candidate lineage/contamination components*, not independently established email campaign/true-parent ground truth.
- **D2_original ↔ D3_seeds: 2,896 shared unique subject/body keys** out of 3,000 unique keys in D2_original (**96.53%**). There are **2,971 rows on each side** in these shared keys; do **not** use D3 as an independent held-out corpus after training on D2 without cross-family lineage/overlap exclusion. High overlap may be due to reused source corpora, not merely chance, but its precise upstream provenance needs verification.
- D1_Nazario ↔ D1_Nazario5: **1,552 shared keys** / 1,565 rows on each side.
- D1_CEAS08 ↔ D2_original: **688 keys**; ↔ D3_seeds: **688 keys**. D1_Nazario5 ↔ D3_seeds: **577**; ↔ D2_original: **474**.
- **One** candidate incompatible three-class label per strict text key was detected within D2/D3. It is not a gold-standard adjudication and not safely resolvable from the public aggregate report; resolve privately.
- Body-only and coarse-template intersections are only *candidate* review signals. This audit does not cover semantic duplicates, prompt lineage or known campaign relationships exhaustively.
- D2 categorized mirror deliberately excluded; D5 authorship-feature archive deliberately excluded.

## Environment/resource

- Kaggle, Python 3.13.15, four logical CPUs, **GPU 0**; observed peak process RSS **653.22 MB**.
- **174.18 seconds**, **242,291,702 downloaded bytes**; no GPU training.
- No hidden/private record-level data were included in the shared artifacts.

## GO / NO-GO

- **GO:** Global descriptive cross-source overlap / candidate lineage evidence.
- **NO-GO:** Frozen splits and model training. Source-grounded phishing label meanings, underlying rights/privacy and redistribution, independent D2/D3 lineage, source-family holdout design, and human security-intent annotation are still incomplete.
- **Notebook 04 v1.3** (source-only fail-closed robustness patch) distinguishes expected vs observed file hashes in the manifest and prevents invalid *partial* component totals if a future file scan fails. This does **not** change the observed complete v1.2 run. No re-run is required just for the v1.3 patch.
- Never claim that these 121,536 rows are independently sampled emails or that an unseen-corpus test is valid before global overlap and lineage exclusions.

**Notebook source:** https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/04_Global_Lineage_and_Frozen_Splits.ipynb

**Study roadmap:** https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/ROADMAP.md
