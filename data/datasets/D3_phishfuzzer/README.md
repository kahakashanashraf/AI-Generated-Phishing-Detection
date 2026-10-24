# D3: PhishFuzzer

- **Source:** https://github.com/DataPhish/PhishFuzzer
- **Status:** CANDIDATE / NOT DOWNLOADED OR ROW-AUDITED BY THIS REPOSITORY UPDATE.
- **Planned role:** Parent-linked phishing/spam/valid variants for robustness analysis.
- **Critical limitation:** Variants may change URL, sender, requested action; do not assume security intent is preserved.
- **Canonical evidence:** [D3 receipt](../../audit/receipts/D3.md) (if present); [receipt template](../../audit/receipts/_TEMPLATE.md).
- **Data flow:** original files in `raw/` → locally audited `interim/` → only verified inputs in `processed/`.
- **Privacy:** raw email, attachments, URLs, identifiers and per-row derived content stay private and are ignored by Git.
- **Approval gates:** source and constituent licenses, SHA256/size, label semantics, row counts, origin/parent metadata, duplicates and legitimate controls, train/test leakage and personal information review.
