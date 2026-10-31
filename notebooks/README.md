# End-to-end Kaggle notebook program (2026-10-31)

One notebook = one research milestone. Start with Notebook 01 and do not proceed to a downstream notebook when its scientific gate fails. Notebooks produce aggregate shareable evidence, and leave raw third-party email data in private storage. The research target is phishing (1) vs legitimate (0), not AI/human authorship. Spam must not be silently mapped to either class. No result is considered executed until the user returns the Kaggle output.

| Order | Notebook | Full milestone | Gate |
|---|---|---|---|
| 01 | 01_D1_Source_Intake_and_Overlap.ipynb | Official Zenodo D1: Nazario, Nazario_5, SpamAssasin, Enron, CEAS_08; integrity, schema, class counts, duplicates, cross-file exact/normalized overlap, redacted audit report | Dataset intake only. Rights, labels, human adjudication unresolved |
| 02 | 02_D2_D5_Provenance_and_Schema.ipynb | D2 HarmJ0y, D3 PhishFuzzer, D4 LLMGen, D5 authorship-only source; schema, source rights, provenance and generator metadata audits | No invented parent or generator claims |
| 03 | 03_Pair_and_Security_Counterfactual_Review.ipynb | Original/rewrite parent verification, style-invariant vs security-changing human review panels and agreement | Human-adjudicated paired evidence required |
| 04 | 04_Global_Lineage_and_Frozen_Splits.ipynb | Global deduplication, parent/campaign-safe groups, corpus and generator coverage checks, frozen manifests and split hashes | No split if unresolved lineage or labels |
| 05 | 05_Classical_and_Transformer_Baselines.ipynb | TF-IDF/LR/SVM and compact transformer, matched splits, multiple seeds, validation-only thresholds and checkpoint receipts | Approved binary data and leakage-safe splits |
| 06 | 06_Security_Sensitive_Method_and_Ablations.ipynb | Ordinary augmentation, same-label consistency, verified opposite-label sensitivity, equal-budget ablations | Pair quality and baseline controls must pass |
| 07 | 07_Unseen_Shift_Risk_and_Statistics.ipynb | Leave-one-generator/corpus and conditional joint shifts, AI-written legitimate errors, grouped bootstrap and calibrated review-load analysis | Frozen models/thresholds only; honest conditional claims |
| 08 | 08_Paper_Tables_Figures_and_Release_Audit.ipynb | Final figures/tables, seed and CI reporting, evidence hashes, efficiency, privacy/data availability checklist | No invented paper results or unauthorized redistribution |

## Kaggle usage
1. Upload/open the current numbered notebook in Kaggle, use CPU for 01–04, and choose **Run All**. A single code cell performs the automated work.
2. Share **only** the generated aggregate JSON/text report or safe notebook console summary, not raw emails, per-record hashes, live phishing URLs, or private adjudication contents.
3. The next notebook is prepared only after the current output is reviewed; revise the current one when the evidence requires it.
4. If a private Kaggle Input is attached, its checksum is verified and reused. If no input is present, Notebook 01 may download only the five listed official Zenodo files to temporary runtime storage.
5. Data-intake or integrity PASS never implies license approval, trustworthy labels, or binary-model training approval.

Research controls: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/ROADMAP.md
Primary dataset source: https://zenodo.org/records/8339691
