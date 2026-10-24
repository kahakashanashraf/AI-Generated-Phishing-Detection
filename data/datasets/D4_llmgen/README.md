# D4: LLMGen Phishing Email Dataset

- **Source:** https://huggingface.co/datasets/Dizzzy0x00/LLMGen-Phishing-Email-Dataset
- **Status:** CANDIDATE / NOT DOWNLOADED OR ROW-AUDITED BY THIS REPOSITORY UPDATE.
- **Planned role:** Auxiliary synthetic and AI-written legitimate stratum if labels verified.
- **Critical limitation:** English/Chinese may be confounded with generator; not standalone evidence of unseen-generator generalization.
- **Canonical evidence:** [D4 receipt](../../audit/receipts/D4.md) (if present); [receipt template](../../audit/receipts/_TEMPLATE.md).
- **Data flow:** original files in `raw/` → locally audited `interim/` → only verified inputs in `processed/`.
- **Privacy:** raw email, attachments, URLs, identifiers and per-row derived content stay private and are ignored by Git.
- **Approval gates:** source and constituent licenses, SHA256/size, label semantics, row counts, origin/parent metadata, duplicates and legitimate controls, train/test leakage and personal information review.
