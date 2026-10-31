# D1–D4 Global Cross-Source Lineage Audit — 2026-10-31

**Status: descriptive audit GO; split freeze and binary training NO-GO.** This is a research receipt, not a declaration that source labels/rights have been approved. Evidence: [Notebook 04 v1.2 executed source report](../../../notebooks/results/04_Global_Lineage/v1_2/lineage_audit.json) and [execution receipt](../../../notebooks/results/04_Global_Lineage/v1_2/README.md).

- 13/13 SHA256-verified input files; 121,536 total source-file rows (not unique independent examples).
- 85,721 candidate global connected components: unions of verified D2 `No.` and D3 `Original_ID` identifiers, plus exact normalized subject/body duplicates. Components are not verified semantic clusters.
- 4,838 multi-file components, 3,018 cross-D1/D2/D3/D4-family components, 40,111 rows in multi-file components.
- **D2 original vs D3 seeds: 2,896 overlapping normalized unique text keys.** This represents 96.53% of the 3,000 unique normalized D2 original texts and 2,971 rows on each side. D3 is therefore **not an independent held-out test set relative to D2 training** without strict overlap/lineage exclusion.
- D1 Nazario vs Nazario_5: 1,552 common normalized keys (all 1,565 Nazario rows); D1 CEAS_08 vs D2 original: 688, CEAS_08 vs D3 seeds: 688; Nazario_5 vs D2 original: 474, Nazario_5 vs D3 seeds: 577.
- One strict-text conflict candidate between D2/D3 three-class annotations. Needs private human/source-grounded adjudication; do not reveal raw source text or per-record hashes.
- Weaker body-only and coarse-template overlap counts in full JSON identify candidates, not validated campaign/semantic duplicates.
- Kaggle CPU run 174.18 seconds; max process RSS 653.22 MB; download 242,291,702 bytes; Python 3.13.15, four CPUs, no GPU.

## Blockers to frozen splits and baseline training

1. Document exact source license, third-party copyright/redistribution, privacy and permissible data-access route **per constituent source**.
2. Adjudicate the 35 D2 unexpected category values per 3,075-row pipeline; distinguish spam vs phishing vs legitimate across D1/D4/D2/D3. Do not silently force binary.
3. Resolve cross-family identity and group duplicates (especially D2/D3); agree how to protect one locked independent holdout when unique support is small.
4. Complete two-reviewer private pilot of N03's 142 sampled pairs, assess disagreement, explicit sender/URL/attachment changes, and map same-intent vs security-changing true classes.
5. Pre-register split policy, set data version and group/overlap hash receipts, and freeze before any baseline tuning.
6. The 2026-10-31 global aggregate report **does not include private per-row group assignments** or model-ready split manifests; never fabricate them from aggregate counts.

## Experiment implications

- **E01:** in-corpus baseline can eventually be attempted on label/rights-approved, parent-group-safe independent partitions; do not score from aggregate class counts.
- **E03:** only adjudicated security-changing counterparts may be used as genuine label-changing evidence.
- **E04/E06/E07:** clean unseen generator / unseen corpus / joint shift claims are conditional on demonstrably independent source and generator ancestry. Because D2/D3 reuse nearly all D2 original texts, naive leave-D3-out is invalid.
- **E08:** AI-written legitimate false-positive rate requires grounded AI-origin AND legitimate ground truth; source category alone may be insufficient.

**Code:** https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/04_Global_Lineage_and_Frozen_Splits.ipynb

**Dataset structure/data controls:** https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/docs/DATASET_PLAYBOOK.md

No raw emails, URLs, sender identifiers or private reviewer content are stored in GitHub.
