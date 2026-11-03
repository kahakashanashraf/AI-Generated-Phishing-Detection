# SOTA-grounded model-development decisions — 2026-11-03

**Goal.** Reduce false alarms on AI-authored legitimate email **without** sacrificing phishing recall. Results on E-PhishLLM are exploratory: multiple earlier experiments have already inspected its labels and observed outcomes. It must not be called a fresh blind test or used for hyperparameter selection.

## 1. Prior art (what is NOT novel)

1. **Pajola et al., E-PhishGEN (ACM AISec 2025)**: same-corpus near-perfect performance masks out-of-corpus failure; E-PhishLLM synthetic corpus contains 16,616 emails in three languages. This is an explicit precedent for cross-source evaluation. https://doi.org/10.1145/3733799.3762967 ; https://github.com/pajola/e-phishGen
2. **Adversarially Robust Phishing Detection via Contrastive Learning and Generative Attacks**: already proposes dual-encoder text/URL contrastive robustness and generative perturbations. Plain “contrastive + rewrites” is **not** a novelty claim. https://doi.org/10.1109/ITT69610.2025.11352920
3. **Enhanced phishing detection using multimodal data**: combines textual/technical security signals and persuasion cues, so “evidence fusion” alone is **not** new. https://doi.org/10.1016/j.knosys.2025.115105
4. **EdgeGuard (2026-11-02)**: source-aware TF–IDF/LR/SVM tests across LLM phishing variants with lightweight edge-resource analysis. Its own paper explicitly describes its contribution as protocol, not a new classifier. https://doi.org/10.1007/s44443-026-01351-9
5. **Classical-First Selective Cascades (Electronics 2026)**: calibrating/deferring borderline cases already has prior art, and multi-source email corpora reveal substantial overlap. https://www.mdpi.com/2079-9292/15/14/3051
6. **Cross-model stylometric phishing study (Frontiers in Big Data 2026)**: source-specific calibration and pooled training are prior art, not evidence of calibrated generalization without target labels. https://doi.org/10.3389/fdata.2026.1883452
7. **Intent-Based Phishing Detection (code and hybrid LLM/regex intent inference)**: hybrid rule + LLM and robust attack variants are already explored. Repository-level results are author claims pending independent reproduction. https://github.com/OU-GC/Intent-Based-Phishing-Detection

## 2. What N05–N13 actually prove

- Frozen D2-original-trained text models cannot guarantee cross-source legitimate reliability.
- N11 benign-rewrite augmentation reduces E-PhishLLM legitimate FPR (88.87% to 66.35%) but reduces D2 phishing recall and increases D2 FPR: **not a safe successful mitigation**.
- N09 evidence proxy dramatically changes the FPR/recall tradeoff but harms phishing recall. The features are mere string patterns, not DNS/URL authentication.
- N12 fine-tuned DistilBERT did not consistently fix external legitimate false positives across seeds.
- N13 demonstrates class-conditional source shift and low character n-gram similarity to original training. It is **descriptive**, not proof of causation by AI-writing style.

## 3. Experiment queue, with concrete decision rules

**P0 / N14 (implemented and launched).** Compare original+rewrites with fixed penalties on original-vs-rewrite *logit disagreement*, while jointly encoding word/character TF–IDF and 12 lexical security proxies. Explicit smooth objective, balanced per-parent supervised loss, fixed L2, fixed lambda 0 / 0.2 / 1, and predeclared benign-only ablation. Train only N05 source-original training parents and their rewrites. Select decision threshold *only* from D2 validation at max 5% FPR. Publish full D2-original, three held-out provider variants, and E-PhishLLM class-specific metrics, no cherry-picked winner. A variant passes only if phishing recall stays >=98% on both D2 and existing external comparison **and** legitimate FPR improves meaningfully; this is exploratory, not final paper evidence.

**P0 / N15. Acquire an independent source, lock it before viewing scores.** Candidate: MeAJOR corpus (108,685 multi-source, source labels; inspect overlap with Nazario/TREC/Enron and label semantics), https://doi.org/10.1016/j.dib.2026.112595 and https://zenodo.org/records/18471483. Alternative: seven-phishing-email-datasets with explicit dataset_name, noted at https://www.mdpi.com/2079-9292/15/14/3051 . Neither is automatically a genuine *AI-authored legitimate* blind benchmark. Need original legitimate/LLM-rewrite parent linkage, permissions, per-email source stratification, semantic label adjudication and campaign disjointness. Pre-register and SHA-pin the holdout before comparing N14 methods.

**P1 / N16. Stronger teacher and actual verified evidence.** Larger encoder or LoRA model on GPU (DeBERTa-v3, ModernBERT, or equivalent only after verifying supported checkpoint/license), trained on source-disjoint multi-source emails rather than just 1,418 originals. Feed authenticated URL and header evidence only if supplied by the dataset; do NOT fabricate sender alignment from email text. Compare equal-data encoder, augmented encoder, encoder+evidence, and calibrated selective mechanism at matched sensitivity. Budget is secondary to credible generalization.

**P1 / N17. Hard negative and hard positive controls.** Construct held-out source-disjoint legitimate AI-authored rewrites and malicious phishing rewrites with parent-level semantic review. Contrast matched `legitimate original vs legitimate rewritten` with `phishing original vs phishing rewritten`, not E-PhishLLM's synthetic generator source versus D2 historical emails. Report paired error effects with confidence intervals and test a source-level evaluation where generator, topic, temporal origin, and label source are not conflated.

**P2 / N18. Scientific novelty gate.** Comparison against TF–IDF LR/SVM, XGBoost/LightGBM, N11 augmentation, N12 DistilBERT, classical-first routing, and available prior intent-/evidence-aware baselines under identical source partitions and fixed operating points. Ablate consistency loss, paired rewrite choice, metadata channels, evidence reliability, domain/source partition and abstention cost. Report FPR, FNR, recall, AUPRC, ECE, review fraction, calibration, 95% paired/source-cluster bootstrap intervals and data rights.

## 4. No-go conditions

- External E-PhishLLM was used indirectly to choose architecture; **do not advertise it as untouched generalization**.
- Decrease in FPR that hides phishing in the legitimate class is **failure**.
- Unsupported “Q1-ready”, “SOTA”, “world-first”, or causal AI-bias claims are **failure**.
- Only lexical proxies (URL existence, keyword urgency) cannot substantiate a full security-evidence engine.
- Existing corpus source membership and campaign leaks need audited grouping before any public performance claim.

**Execution evidence:** https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/actions
