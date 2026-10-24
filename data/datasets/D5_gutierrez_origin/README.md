# D5: Gutierrez et al. cross-model corpus

- **Source:** https://zenodo.org/records/20250116
- **Status:** CANDIDATE / NOT DOWNLOADED OR ROW-AUDITED BY THIS REPOSITORY UPDATE.
- **Planned role:** Auxiliary AI-vs-human authorship replication only.
- **Critical limitation:** Both authored categories are phishing; not a phishing-vs-legitimate classifier dataset.
- **Canonical evidence:** [D5 receipt](../../audit/receipts/D5.md) (if present); [receipt template](../../audit/receipts/_TEMPLATE.md).
- **Data flow:** original files in `raw/` → locally audited `interim/` → only verified inputs in `processed/`.
- **Privacy:** raw email, attachments, URLs, identifiers and per-row derived content stay private and are ignored by Git.
- **Approval gates:** source and constituent licenses, SHA256/size, label semantics, row counts, origin/parent metadata, duplicates and legitimate controls, train/test leakage and personal information review.
