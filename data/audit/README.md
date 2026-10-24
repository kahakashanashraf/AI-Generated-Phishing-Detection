# Audit Center (canonical, metadata-only)

Folders:
- `receipts/`: dated per-dataset intake, audit results and explicit GO/RESTRICTED/NO-GO, including template.
- `rights/`: legal source links, license evaluation and restrictions (no private correspondence).
- `schema/`: source-specific column meaning, label mapping and missingness.
- `quality/`: safely redacted aggregates, checksum metadata, executed test receipts. Raw JSON/CSV reports are ignored.
- `lineage/`: duplicate counts, parent ancestry, generator/corpus source overlap evidence. Never expose row text.
- `privacy/`: de-identification and governance; do not include actual PII.

Dataset approval is per **source and experimental purpose**, not a blanket GO. A source may be useful for robustness but invalid for held-out generator evaluation. All unused raw files remain private. Existing `reports/dataset_receipts/` paths are historical links; prefer this canonical location.
