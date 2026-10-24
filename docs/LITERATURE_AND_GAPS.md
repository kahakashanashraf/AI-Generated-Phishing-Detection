# Evidence-based related work and gap audit (2026-10-24)

## Verified papers
1. Gutierrez, Villegas-Ch & Govea (2026), *Cross-model evaluation of phishing detectors against LLM-generated emails*. Frontiers in Big Data. https://doi.org/10.3389/fdata.2026.1883452
   - 9,986 phishing-only samples, three generators (GPT-4.1, DeepSeek 3.2, Llama 3.3 70B). Human-phishing vs LLM-phishing **origin attribution**, not safe-vs-phishing detection.
   - Reported 28-point cross-generator F1 gap and substantial gains from target-threshold recalibration. Repeating leave-one-generator-out or calibration alone is NOT novel.
   - Released data/scripts: https://zenodo.org/records/20250116 ; check license, raw text availability, provenance, and splits before importing.
2. *CuePhish: Interpretable Detection of Large Language Model-Generated Phishing Emails via Linguistic and Stylometric Cues*, IEEE LCN 2026. https://doi.org/10.1109/LCN67947.2026.11660775
   - Linguistic/stylometric features and adversarial hardening for origin attribution; explanation alone is not a novel contribution.
3. *Detecting AI-Generated Phishing Campaigns Using Linguistic Forensics and Machine Learning*, IEEE ICCSDFAI 2026. https://doi.org/10.1109/ICCSDFAI70505.2026.11648017
   - 28 features on human-vs-GPT-4 phishing; low-cost inference and feature ablations reported.
4. Alhuzali et al., *Phishing-Email-Detection-Dataset*, Zenodo v2 (2025-10-10). https://zenodo.org/records/17314806
   - Large merged binary phishing dataset. May contain overlapping source corpora; cannot assume independence or AI provenance.

## Critical problems / evidence to collect
P0. **Target confusion**: authorship (AI vs human among phishing) is not maliciousness (phishing vs benign). A 2-class dataset with only phishing messages CANNOT support claims of detecting phishing vs safe emails. Define target explicitly.
P0. **Same-source or template leakage**: overlapping human corpora, reused templates, paraphrases or generators can inflate test performance. Audit exact duplicates and near duplicates; group by ancestor/template **before split**.
P0. **Label-source confounding**: if all AI samples come from one collection and human samples from another, a model may learn dataset artifacts. Evaluate source-held-out and matched topic/length subsets where possible.
P0. **Target calibration leakage**: tuning an unseen-generator threshold with its test labels invalidates zero-shot claims. Separate zero-shot from few-shot calibration, freeze thresholds using *validation only*.
P1. **Unseen family vs unseen checkpoint**: generator identity and model family are different. Group an entire family for stronger holdout; never use the held-out generator for training or feature selection.
P1. **Operational false positives**: phishing-only AI-attribution benchmarks cannot estimate false positives on legitimate emails. Build a four-way provenance × intent evaluation if trustworthy data exists.
P1. **Data rights and privacy**: check license, personal information, synthetic prompt provenance and permitted reuse. Do not commit email bodies or credentials.
P1. **Robustness**: deterministic controlled paraphrase, lexical perturbation and campaign shift; count any generated augmentation as belonging to its parent split.
P1. **Metrics**: AUROC alone obscures operating thresholds; show PR-AUC, recall at fixed FPR, calibration ECE/Brier, subgroup counts, and confidence intervals.
P2. **Efficiency**: report training wall time, RAM, GPU/CPU inference and energy only if directly measured.

## Falsifiable contribution hypothesis (NOT a result)
Risk-controlled selective classification may reduce erroneous high-confidence origin attribution under unseen generators without using target labels. Compare against simple LR/TF-IDF, stylometric and threshold-only baselines. Do not assert novel architecture or superiority until experiments show it.

## Claims NOT warranted yet
- The repo has not reproduced any paper or trained a validated model.
- The proposed benchmark does not currently include vetted four-way data.
- No source-audited zero-shot result, confidence interval, or SOTA claim exists.
