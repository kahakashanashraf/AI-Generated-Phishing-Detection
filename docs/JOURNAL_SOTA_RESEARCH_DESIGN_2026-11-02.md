# Journal-grade research design and SOTA positioning (2026-11-02)

**Status:** literature-grounded experiment plan, not executed results. Preserve N05 Logistic Regression and calibrated Linear SVM **unchanged as frozen baselines**.

## Primary question
Do phishing detectors over-rely on AI-generated linguistic style, increasing false alarms on **legitimate** rewritten/AI-authored emails even when security-critical evidence is unchanged? Can a security-evidence-aware and calibrated prediction protocol mitigate that risk without materially losing phishing recall on unseen sources?

### Essential terminology
1. **AI-rewritten legitimate**: verified parent-original email transformed by LLM. This is what N05 tests.
2. **AI-authored legitimate**: newly composed benign mail with documented generator provenance; do not relabel rewrite data as independently AI-authored.
3. **Spam** != phishing. No undocumented class collapse.
4. All D2 classifications are source assigned; counterfactual intent preservation not human confirmed. N05 FPR rises 1/142 for GPT-4o on each baseline, not evidence of statistically significant AI discrimination.

## Related work positioning
- Opara, Modesti, Golightly (2025), Expert Systems with Applications: stylometric detection and commercial filtering of AI phishing. https://www.sciencedirect.com/science/article/pii/S0957417425006669
- Pajola et al. (ACM AISec 2025), E-PhishGEN/E-PhishLLM: 16,616 emails, three languages, previous benchmark ceiling critique. https://doi.org/10.1145/3733799.3762967
- Gutierrez et al. (Frontiers in Big Data, 2026): cross-model phishing-only authorship discrimination and calibration. Distinct task from phishing-vs-legitimate. https://www.frontiersin.org/journals/big-data/articles/10.3389/fdata.2026.1883452/full
- Bhuiyan and Bhuiyan (2026), fragility of phishing detectors under cross-corpus shift/prevalence shift and artifacts. https://www.mdpi.com/2504-2289/10/7/211
- Classical-First Selective Cascades (2026): cross-corpus selective phishing email detection. https://www.mdpi.com/2079-9292/15/14/3051
- HarmJ0y source README includes strict and relaxed 3-class/unwanted-vs-valid and LLM rewrites; do not claim simple rewrite experiment is novel. https://github.com/HarmJ0y/PhishingSpamDataSet
- Risk-coverage foundation: https://www.jmlr.org/papers/v11/el-yaniv10a.html

## Core controlled tests — pre-register
E1. Reproduce N05 unchanged as frozen exploratory baselines (single documented split; *do not retune it on its test*).
E2. Add distinct, verified data stratum of independently AI-authored benign mail, with human benign controls matched on topic, subject type, document length, security context, and source as possible. Never confound generator with labels or language. Pre-register source availability gate.
E3. Train strong comparable models on **the same allowed training fold**: word/char TF-IDF Logistic Regression and LinearSVC, multinomial NB, LightGBM/XGBoost over sparse or SVD embeddings, one compact transformer (e.g., DeBERTa-v3-small or DistilBERT). A second transformer only if useful. Benchmark a **3-class Phishing/Spam/Valid** sensitivity task separately; do not silently map spam to another class. Strongest baselines not picked on final external test.
E4. Signal ablation (controlled): raw subject+body; artifact-controlled subject/body; style-only linguistic/stylometric features; structural/security cues only; fusion of content embeddings and security cues; style-adversarial/regularized variant only after signal exploitation is observed. **Metadata-based sender/domain evidence only if consistently present and not fabricated**. Use masking on URL domains, named entities and unsubscribe/marketing cues as explicit ablation, not causal evidence in itself. Compare paired matched controls and assess leakage from generator fingerprints.
E5. Grouping by originals, all rewrites, normalized exact texts, near-duplicate templates/campaign where evidence permits; nested group-stratified CV inside train; locked validation for threshold and calibration; final parent-held-out test plus independently source-held-out test after decontamination. No shared D2/D3 as independent test. Repeated seeds / bootstrap units grouped by ancestor/source.
E6. Evaluate thresholded FPR on benign original, LLM rewrite, truly AI-authored benign, and external legitimate separately. Report recall at fixed *validation-selected* FPR, realistic class prevalence, PR-AUC, Brier, ECE, class-conditional calibration, risk–coverage and operational review load. Validation FPR is a goal not guarantee.
E7. Paired difference for 142 matched originals versus rewrites: discordance n01/n10, exact McNemar if binary decisions, paired bootstrap over ancestor IDs for delta FPR 95% CI. Need row-level decisions in *private* store; commit only aggregates and pseudonym-free numbers. Cluster bootstrap by source/campaign for external sets as appropriate. Report power/low sample limitations; one additional FP is not evidence of a general effect.
E8. Model comparison via same held-out examples, pre-registered primary endpoint, adjusted exploratory multiplicity, confidence intervals, leakage/label audits, error taxonomy and calibration/review tradeoff. Negative results and null findings remain publishable if rigorously documented.

## Paper contribution hierarchy
**Required contribution:** rigorously quantified false-alarm gap for LLM-rewritten and separately AI-authored benign communication, under fixed thresholds and source-safe evaluation.
**Second contribution:** security/style signal ablations with matched benign/attack controls and attribution/error study.
**Third contribution:** external transfer and selective prediction, including risk–coverage, cost, uncertainty and practical review trade-offs.
**Conditional (only after positive evidence):** simple style-invariance or evidence-aware fusion training. Compare to same-capacity model and no-fusion ablation; do not advertise an architecture before experiments.

## 10-day prioritization
P0: freeze N05, source/provenance and independent benign AI controls, grouped splits, leakage scans, private per-row predictions.
P1: model comparison + tuned hyperparameters within nested group-aware CV, 3-class sensitivity benchmark, original/rewrite paired statistics.
P2: external source evaluation, calibration, risk–coverage, ECE and prevalence stress.
P3: security/style feature ablation, failure explanations, manuscript tables, limitations and reproducibility package.
Optional P4: evidence fusion regularization and transformer extension if data/compute support.

## Hard scientific blockers to claims (not to the project)
- No verified independently AI-authored legitimate stratum: cannot claim general AI-authorship bias, only rewriting-associated false alarms.
- No independently vetted security-equivalent pair: cannot claim security invariant counterfactual robustness or label-flip sensitivity.
- No independent holdout: cannot claim cross-corpus generalization.
- No frozen validation or nested selection: cannot claim unbiased tuned-model test score.
- Training experiment on source-labeled text ≠ objective certification of phishing intent.
- Do not publicly commit raw/private emails, per-row predictions, sensitive URLs, or human annotation panel.

## Expected deliverables
A testable model matrix, statistical report with CIs and exact paired tests, source/lineage manifest, source-held-out transfer matrix, ablation table, calibration and risk-coverage plots, error taxonomy, manuscript with exact reproducible protocol.
