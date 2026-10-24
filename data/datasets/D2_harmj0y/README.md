# D2: HarmJ0y PhishingSpamDataSet

- **Source:** https://github.com/HarmJ0y/PhishingSpamDataSet
- **Status:** CANDIDATE / NOT DOWNLOADED OR ROW-AUDITED BY THIS REPOSITORY UPDATE.
- **Planned role:** Candidate original/rewrite human/AI email and legitimate-AI control; conditional generator holdout.
- **Critical limitation:** Verify per-row rewriting model, parent linkage, true-versus-predicted labels and original license.
- **Canonical evidence:** [D2 receipt](../../audit/receipts/D2.md) (if present); [receipt template](../../audit/receipts/_TEMPLATE.md).
- **Data flow:** original files in `raw/` → locally audited `interim/` → only verified inputs in `processed/`.
- **Privacy:** raw email, attachments, URLs, identifiers and per-row derived content stay private and are ignored by Git.
- **Approval gates:** source and constituent licenses, SHA256/size, label semantics, row counts, origin/parent metadata, duplicates and legitimate controls, train/test leakage and personal information review.
