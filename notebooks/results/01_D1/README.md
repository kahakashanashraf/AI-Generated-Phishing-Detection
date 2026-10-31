# Notebook 01 — D1 v1.1 results (aggregate only)

**Source:** The researcher's executed Kaggle notebook and uploaded `results (2)(1).zip` (2026-10-31). Only aggregate statistics are stored here. These results have **not** been recomputed by downloading/reprocessing restricted emails in ChatGPT. They are derived from the verified uploaded result archive. The JSON here has been serialized from the uploaded safe fields, so it is semantically equivalent, not promised byte-for-byte identical to the original JSON.

**Validated from supplied run**
- Release: `D1-N01-v1.1-2026-10-31`.
- 5 of 5 D1 files: `PASS_DESCRIPTIVE`; 79,360 source rows scanned; synthetic self-test PASS.
- Nazario ↔ Nazario_5: 1,552 shared normalized subject/body keys, covering 1,565 rows on each side.
- Nazario_5 ↔ SpamAssasin: 239 shared keys; ↔ CEAS_08: 298; SpamAssasin ↔ Enron: 2.
- Manual review candidate **entries**: 1,031, not yet adjudicated.
- Training: **NO-GO**. Checksum match is **not** proof of rights, privacy clearance, phishing-label ground truth, parent/campaign-disjoint splits or robust deduplication.

**Provenance SHA256 (original user attachments)**

| Artifact | SHA256 |
|---|---|
| Executed notebook 01 v1.1 | `133fc513db82bd710afdccfd300f7ddb2d681c2d5e6f8b6f55498d7314a9691e` |
| Uploaded results ZIP | `fdd301efdee9faf577892735c32bf5f31e5d682375c9ecb274bc11a7c9f15fa4` |
| Original aggregate JSON inside ZIP | `71fc63aea2d8663344b9f78e8c40190a3a61d6400c788b2782619e3ca4cb6c56` |
| Original aggregate TXT inside ZIP | `f5353732a27ecb95d16d2e7eb768d09093d9dd2e76c439cf7e3e320bde3e299b` |

The version-controlled, clean code-only notebook is at:
https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/01_D1_Source_Intake_and_Overlap.ipynb

The subsequent notebook is:
https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/02_D2_D5_Provenance_and_Schema.ipynb

**Do not commit** raw third-party emails, senders, suspicious URLs, per-record text hashes, private manual-review indices, or Kaggle credentials.
