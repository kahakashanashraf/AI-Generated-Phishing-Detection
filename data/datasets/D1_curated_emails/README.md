# D1: Champa et al. curated email corpora

- **Source:** https://zenodo.org/records/8339691
- **Status:** CANDIDATE / NOT DOWNLOADED OR ROW-AUDITED BY THIS REPOSITORY UPDATE.
- **Planned role:** Original human email sources; baseline and corpus-holdout candidates. Examine Nazario, SpamAssasin, Enron and CEAS_08 first.
- **Critical limitation:** Constituent corpus overlap, spam/phishing label semantics and redistribution rights are unverified.
- **Canonical evidence:** [D1 receipt](../../audit/receipts/D1.md) (if present); [receipt template](../../audit/receipts/_TEMPLATE.md).
- **Data flow:** original files in `raw/` → locally audited `interim/` → only verified inputs in `processed/`.
- **Privacy:** raw email, attachments, URLs, identifiers and per-row derived content stay private and are ignored by Git.
- **Approval gates:** source and constituent licenses, SHA256/size, label semantics, row counts, origin/parent metadata, duplicates and legitimate controls, train/test leakage and personal information review.
