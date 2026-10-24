# Related-work comparison worksheet — 2026-10-24

**Fill evidence first.** A claimed gap is valid only after comparing directly overlapping publications. Details below are a starting reading checklist, **not completed full-text verification**.

| Study | Stable source | Primary task | Existing contribution | Our exact non-overlap hypothesis | What to verify in full text | Status |
|---|---|---|---|---|---|---|
| Gutierrez, Villegas-Ch & Govea (2026) | https://doi.org/10.3389/fdata.2026.1883452 | AI vs human origin *among phishing* | Cross-generator transfer + target-slice recalibration, stylometric features | Phishing *vs legitimate* paired security-intent study with target-free threshold | Are benign controls used? Was target calibration permitted? Splits grouped? | ABSTRACT+METHODS read; extract full matrix |
| Evaluating Effectiveness of Existing Phishing Detectors (IEEE CARS 2025) | https://doi.org/10.1109/CARS67163.2025.11337548 | Phishing vs safe under LLM rephrase | Cross-LLM rephrasing degrades BERT and simpler methods; retraining helps | Matched security-change sensitivity AND joint source+generator held-outs at frozen false alarm budget | Exact generators, paired validity, source overlap, thresholds and robustness metrics | ABSTRACT checked; full-method audit pending |
| Opara, Modesti & Golightly (2025) | https://doi.org/10.1016/j.eswa.2025.127044 | Detect AI-phishing / spam filter challenges | Stylometric features and AI email evaluations | Do not overclaim stylistic features as novel | Dataset composition and threat model | ABSTRACT checked |
| PhishFuzzer | https://github.com/DataPhish/PhishFuzzer | 3-class LLM email robustness | 3,300 original + 19,800 linked variants and confidence/template success | Verified *label-changing* vs *label-preserving* distinction (conditional), plus risk control | Actual variant fields, origin model, labels, license | README checked; rows pending |
| HarmJ0y dataset | https://github.com/HarmJ0y/PhishingSpamDataSet | 3-class provenance and rephrase | Human/AI corpus and multiple pipelines | Conditional generator×corpus controlled study | Exact model metadata, parent IDs, train overlap and usage rights | README checked; rows pending |
| Gutierrez dataset archive | https://zenodo.org/records/20250116 | Authorship feature analysis | 17 stylometric features on phishing-only examples | Auxiliary replication, NOT primary task | Contents, raw text fields, license, split | Descriptor checked |
| More 2025–2026 consistency/contrastive work | To be added via verified DOI | Phishing generalization | Must compare existing invariance learning | Is any proposed combined objective already directly covered? | Read full papers and ablations | TODO |

## How to fill each new row
1. DOI, publication date and PDF availability.
2. Threat model and exact task label.
3. Dataset names, source overlap, number of generators.
4. Train/validation/test split method and leakage controls.
5. Whether rephrasing preserves labels, and whether label-changing counterfactuals are considered.
6. Calibration: same-domain validation vs held-out target-label tuning.
7. Metrics: FPR, recall, AUROC/PR-AUC, paired flip, uncertainty.
8. Compute constraints, code and reproducibility.
9. EXACT difference from our method; novelty claim marked SUPPORTED/OVERLAP/UNKNOWN.

Before G0 GO: at least ~15 directly relevant scholarly works reviewed, with strongest 5–8 in full methodological detail, rather than merely citing titles. Number is a depth guideline, not a publication requirement.
