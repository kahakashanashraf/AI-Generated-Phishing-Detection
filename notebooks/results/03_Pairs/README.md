# Notebook 03 — audited execution evidence (v1.1)

**Original user-provided evidence:** Executed `03-pair-and-security-counterfactual-review.ipynb` and `results (2).zip`, uploaded October 31, 2026. All five **privacy-safe aggregate files** below are committed and were checked for **byte-for-byte** correspondence to the uploaded ZIP using Git blob identity, not just a copied summary.

- [pair_audit.json](pair_audit.json) — 29,025 candidate pairs, per-family flags, 142 pilot review candidates; **NOT** human-verified label preservation.
- [environment.json](environment.json) — Kaggle CPU / Python 3.13.15, four logical CPUs, packages, no observed GPU.
- [resource_usage.json](resource_usage.json) — 23.018 s, 609.84 MB process peak RSS, 85,481,663 bytes input downloaded, no training.
- [run_manifest.json](run_manifest.json) — pinned source revisions and all six SHA256 identities.
- [summary.txt](summary.txt) — console-equivalent safe final status.

## Findings and gate

- D2 DeepSeek/GPT-4o/RandomAPI: 3,075 candidate parent matches each, zero unmatched.
- D3: 19,800 variants, 3,300 distinct parent IDs, six variants per parent.
- Total **29,025 structural pairs**, with **19,997** pairs flagged for changed sender/URL/attachment/embedded URL cue. These are NOT 19,997 verified security-label changes.
- No source labels contradict their inherited variant categories according to the scanner; 35 D2 class values per pipeline remain unrecognized. Structural `No.`-matching does not prove semantic parent identity.
- The deterministic 142-row private human-review panel was generated but **no two-reviewer decisions or agreement were provided**. Source permissions, semantic equivalence, pair-gold, maliciousness labels and downstream training remain **NO-GO / PENDING**.

## Original attachment SHA256 values

| Artifact | SHA256 |
|---|---|
| Executed notebook v1.1 | `999e27b67b9da960de3590b5a3cab67f397654a2dc8feb83bba1bf4c8671cd7d` |
| Uploaded results ZIP | `51eee4ebb65560ef7d92420ac698aa7da505e842ac68592b4fda0572c36b6457` |
| pair_audit.json | `6551fe1f8ec542cb982af3e0e329cebe74686fe9f4f70138a0ef9f825855428b` |
| environment.json | `57fb5e435cb826e747c150e8cf00c1702f6848c226a01dc709327a4ee86bd118` |
| resource_usage.json | `e3df55af58b98510e8efd3914def0dcc29a8cb9503698127127e8ac25fb14f05` |
| run_manifest.json | `11d2b9186984ef333d33bf89b6cb4628cd09803cb2f0d40ef8968c09c2d405c7` |
| summary.txt | `b8ac05fd29ff1329d0c83fc5cbf34d1f77d0031eaca83444a67738a38e7e4a43` |

## Reviewer-blocking problem discovered

The v1.1 **private** 142-pair review sheet omitted original/variant explicit URL, sender and attachment fields although changes in those fields generated the `security_cue_changed` flag. This **does not invalidate the source audit**, but it prevents adequate human adjudication of security-significant changes.

**Fix:** [Notebook 03 v1.2](../../03_Pair_and_Security_Counterfactual_Review.ipynb) adds original/variant sender, explicit URL, attachment, source, and year fields to the *private-only* reviewer panel; preserves prior reviewer IDs; does not overwrite an existing completed/partially completed private decision template; and validates independent two-reviewer decisions, adjudication, observed agreement and Cohen's kappa when provided.

**Execution distinction:** The numbers and files committed here belong to **v1.1**, NOT a Kaggle execution of v1.2. The v1.2 code has been reviewed and synthetic tests exercised locally but still requires a researcher-run evidence artifact.

**Do not commit/publish** the private review panel, raw emails, active phishing URLs, sender addresses, private annotations, or personal data.
