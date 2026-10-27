# Research Dataset Catalog (metadata-only; 2026-10-24)

| ID | Source | Role in study | Primary task? | Gate |
|---|---|---|---|---|
| D1 | [Champa et al. curated email corpora](https://zenodo.org/records/8339691) | Nazario subset: 1,565 all label=1; full-file scan found 13 normalized duplicate extras and 2 unconfirmed admin candidates. Other corpora pending. | NOT APPROVED: candidate positive slice only | [Nazario receipt](audit/receipts/D1.md); source label truth, rights, cross-corpus overlap pending |
| D2 | [HarmJ0y PhishingSpamDataSet](https://github.com/HarmJ0y/PhishingSpamDataSet) | Candidate original/rewrite human/AI email and legitimate-AI control; conditional generator holdout. | Candidate subject to audit | license, labels, provenance, overlap |
| D3 | [PhishFuzzer](https://github.com/DataPhish/PhishFuzzer) | Parent-linked phishing/spam/valid variants for robustness analysis. | Candidate subject to audit | license, labels, provenance, overlap |
| D4 | [LLMGen Phishing Email Dataset](https://huggingface.co/datasets/Dizzzy0x00/LLMGen-Phishing-Email-Dataset) | Auxiliary synthetic and AI-written legitimate stratum if labels verified. | Auxiliary only | license, labels, provenance, overlap |
| D5 | [Gutierrez et al. cross-model corpus](https://zenodo.org/records/20250116) | Auxiliary AI-vs-human authorship replication only. | NO — authorship only | license, labels, provenance, overlap |

Never blindly merge these sources; they differ in acquisition period, taxonomy, model provenance and parent linkage. The combined binary task is **phishing vs legitimate**; spam remains separate until a documented decision. Conditions involving unseen generators or joint generator×corpus shifts are CONDITIONAL on verified per-record origin/generator labels.

Each source directory has `raw/`, `interim/` and `processed/`. `raw/` files stay **unchanged and private**; processed files are created only after schema/label/rights GO. Parent- and source-disjoint split evidence lives under `audit/lineage/` and `splits/`.

**Canonical receipts:** [audit/receipts/](audit/receipts/) rather than historical `reports/dataset_receipts/` (legacy paths retained as redirects).
