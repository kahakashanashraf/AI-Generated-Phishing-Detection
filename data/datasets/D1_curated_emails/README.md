# D1: Champa et al. curated email corpora

- **Source:** https://zenodo.org/records/8339691
- **Status (2026-10-27):** RESEARCHER DOWNLOADED AND AUDITED NAZARIO ONLY. Checksum PASS, 1,565 all-positive rows, 0 exact duplicate extras, 13 normalized duplicate extras and 2 heuristic admin candidates. **NO GO** for training or public raw redistribution; other D1 constituent corpora remain unaudited.
- **Planned role:** Original human email sources; baseline and corpus-holdout candidates. Examine Nazario, SpamAssasin, Enron and CEAS_08 first.
- **Critical limitation:** Constituent corpus overlap, spam/phishing label semantics and redistribution rights are unverified.
- **Canonical evidence:** [D1 receipt](../../audit/receipts/D1.md) (if present); [receipt template](../../audit/receipts/_TEMPLATE.md).
- **Data flow:** original files in `raw/` → locally audited `interim/` → only verified inputs in `processed/`.
- **Privacy:** raw email, attachments, URLs, identifiers and per-row derived content stay private and are ignored by Git.
- **Approval gates:** source and constituent licenses, SHA256/size, label semantics, row counts, origin/parent metadata, duplicates and legitimate controls, train/test leakage and personal information review.

## Executed evidence
The researcher provided an executed five-cell Kaggle Notebook (`ai-generated-phishing-detection.ipynb`) whose Nazario quality JSON shows 1,565 rows, all label=1, no exact extras, **13** whitespace/case-normalized extra duplicate rows, no label conflicts and **2** unconfirmed heuristic admin candidate rows. See [canonical D1.2 receipt](../../audit/receipts/D1.md). Do not merge Nazario and Nazario_5 before cross-source identity verification. Existing exact/normalized counts are summaries, **not instructions to delete rows**.
