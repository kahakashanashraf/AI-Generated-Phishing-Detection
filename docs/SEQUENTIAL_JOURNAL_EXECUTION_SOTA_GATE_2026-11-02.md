# Sequential notebook execution and Q1-oriented SOTA gate — 2026-11-02

## What is committed and verified
1. N01–N04: historical executed audit reports in repo. Do not confuse executed audit notebooks with completed paper experiments.
2. N05: full source `notebooks/05_AI_Written_Legitimate_False_Alarm_Benchmark.ipynb` now committed from the researcher's uploaded notebook; privacy-safe executed E01 outputs in `notebooks/results/05_E01/`.
3. N06: standalone `notebooks/06_Paired_Inference_and_Selective_Reliability.ipynb` now committed. It reuses frozen N05 split, original models and validation-only thresholds. Extra stage: exact McNemar, 10,000 parent bootstrap draws, exact binomial CIs, risk–coverage. Its statistics code was subjected to local synthetic test cases including ties, one false-positive increase, and invalid-input failures. **Actual N06 data-dependent run not yet executed.**
4. Output rule: upload privacy-safe aggregates to this repository with exact hashes, but never public raw emails, private annotation panels, identifiers, URL payloads or row-level predictions.

## Confirmed high-overlap prior art: novelty danger
- **CARS 2025 / IEEE Jan 2026** specifically rephrased both phishing **and safe emails** with three LLMs, showing accuracy drops and retraining improvements. This is **not** a unique claim available to our paper.
  https://doi.org/10.1109/CARS67163.2025.11337548
- **E-PhishGEN / ACM AISec 2025** addresses high in-domain scores and weak modern-dataset generalization.
  https://doi.org/10.1145/3733799.3762967
- **Classical-First Selective Cascades / Electronics 2026** already compares strong TF-IDF SVM vs transformer, four-corpus cross-transfer, calibration, selective cascade and style stress; therefore neither 'SVM beats transformer' nor 'add abstention' can stand alone as novelty.
  https://doi.org/10.3390/electronics15143051
- **Cross-model evaluation / Frontiers 2026** addresses generator shift and calibration in a *phishing-only AI-vs-human authorship* task, not binary benign false-alarm analysis.
  https://doi.org/10.3389/fdata.2026.1883452
- **Opara et al. / ESWA 2025** studies stylometric features and email service spam filters against AI phishing.
  https://doi.org/10.1016/j.eswa.2025.127044

## Testable candidate journal contribution — not yet validated
1. Quantify **source-matched, label-checked AI-authored legitimate false alarm excess** separately from rewriting effects; report paired discordances, intervals, class-conditional calibration, operating thresholds and real review-load trade-offs.
2. Distinguish **style reliance vs security evidence** with pre-registered cue-suppression and evidence-preserving ablations, controlled matched benign and phishing samples, independent reader/label review of stratified edge cases. Avoid claiming a causal counterfactual without validated meaning preservation.
3. Build/test a **security-evidence conditioned confidence or abstention mechanism** against same-capacity and classical/transformer baselines, with a pre-specified allowable phishing recall loss. No novel architecture claim until tests show benefit on a truly independent held-out corpus.
4. External source holdout must be lineage-clean: D2 and D3 share ancestors and cannot form train-test independence. Freeze time/source campaigns and verify original label mappings.

## Q1 target is a quality bar, not a guaranteed quartile or publication acceptance
To target a *current* Q1 journal, verify the target journal's contemporary JCR/Scimago quartile and scope before submission; indexing and quartiles depend on edition/category. The article requires a literature-differentiated contribution, sufficient datasets, controlled baselines, robust statistics, reproducibility, ablations, failure taxonomy, limitations, and data/ethics safeguards. Do not present the proposed contribution as established novelty.

## Next sequential notebooks
N07 — strong model benchmarking with **group-aware inner CV** on the permitted train partition and primary endpoint fixed before test. No cherry-picking from N05 test. Include word/character TF-IDF, NB, LightGBM and at least one transformer if source suitability and compute allow.
N08 — independently sourced AI-authored benign controls, source-held-out and decontamination; fail closed if legitimacy/provenance unavailable.
N09 — security/style feature ablation and candidate evidence-aware method **only after** detecting a robust failure mode.
N10 — full paper figures, statistical tests, and reproducibility audit.

## Progress gate
N05 is **executed GO (exploratory source-assigned benchmark)**.
N06 is **source committed + local synthetic tests GO; Kaggle real-data execution PENDING**.
N07–N10 are planned, **not built or run**.
