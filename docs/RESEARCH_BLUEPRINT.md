# IEEE Access Research Blueprint — version 0.1 (2026-10-24)

> Status: **PLANNED, NOT VALIDATED.** Do not assert novelty, successful experiment, improved robustness, IEEE acceptance, or actual dataset readiness before evidence. This is a training-and-research roadmap for a first-time researcher using Kaggle free 2x Tesla T4.

## 0. North star
**Working title:** *Security-Sensitive Invariance Learning for Reliable Phishing Email Detection Under Unseen LLM Rewriting and Domain Shift*.

**Operational primary task:** Predict **phishing (1) vs legitimate (0)** for *emails*. Machine-generated vs human-written is a **stratification/provenance variable**, never the primary maliciousness target. Spam is distinct; keep a third class for exploratory analysis or explicitly exclude it from the binary task. Do NOT map all spam to phishing or legitimate without a justified preregistered policy.

**User-facing question:** Can a phishing detector maintain correct decisions when an unseen LLM changes wording, while changing its decision when defensible security evidence changes, and still control false alarms on AI-written legitimate emails?

## 1. Scientific research questions
- **RQ1 / invariance:** How often do fixed prediction and calibrated score change for validated, label-preserving rewrite pairs? Is that rate worse with unseen generators/corpora?
- **RQ2 / sensitivity:** Does an invariance-trained detector respond appropriately to **human-validated, label-changing security counterfactuals** rather than merely predicting the same class for every pair?
- **RQ3 / generalization:** Do the combined objectives improve performance vs strongest controls on pre-registered LO-generator, LO-family (where available), LO-corpus and *joint* generator+corpus held-out settings?
- **RQ4 / operational safety:** At a threshold fixed solely from seen validation, what are phishing recall, false-positive rate on legitimate human/AI mail and downstream human-review workload?

## 2. Falsifiable hypotheses (not facts)
- H1: Base phishing classifiers rely partly on linguistic/source shortcuts; same-intent edits trigger avoidable class flips.
- H2: Paired style-invariance alone can over-regularize sensitivity to changed security evidence.
- H3: A **bidirectional security-sensitive consistency objective** can reduce same-intent failures **without** decreasing verified security-change sensitivity compared to equal-compute augmentation and contrastive baselines.
- H4: Risk-aware abstention can improve accepted-set risk at a measured review cost under joint shift. No distribution-free guarantee under arbitrary shift is claimed.

## 3. Candidate learning method (NOT an established invention)
L_total = L_binary_classification + lambda * L_style_consistency(validated same-label pairs)
                         + mu * L_security_sensitivity(validated opposite-label pairs).
- L_style should compare calibrated logits/probabilities on parent + *verified* rewrite.
- L_security should enforce discriminative classification of *both labeled examples*; never reward unbounded prediction differences.
- Always compare against: classification only; ordinary independent augmentation; paired same-label consistency only; supervised contrastive where feasible; sensitivity-only; full combined; frozen-backbone LR/TF-IDF; transformer.
- If security-changing pairs fail annotation, **DO NOT train full method or make bidirectional novelty claims**. Fall back to rigorous shift/robustness audit if independently publishable.

## 4. Explicit novelty threat list
Prior work already exists on cross-model origin attribution/recalibration, LLM-rephrased phishing, style/linguistic cues, fuzzer variants, contrastive training, and confidence measures. Novelty must be (a) a validated task+counterfactual protocol AND/OR (b) demonstrated security-sensitive generalization improvement beyond strong controls. A combination of known losses alone is insufficient.
Review: https://doi.org/10.3389/fdata.2026.1883452
IEEE CARS: https://doi.org/10.1109/CARS67163.2025.11337548
Paired benchmark: https://github.com/DataPhish/PhishFuzzer
Authorship-only data: https://zenodo.org/records/20250116
Further reading: https://doi.org/10.1016/j.eswa.2025.127044

## 5. Data and protocol
Read **docs/DATASET_PLAYBOOK.md** before downloading, labeling or training.
Manifest minimum: `sample_id,source_corpus,source_revision,original_id,group_id,variant_id,language,label,origin,generator,generator_family,edit_type,verification_status,split,text_hash`. Additional subject/body/sender/URL fields only when source offers and licenses them. Use null for genuinely missing fields; do NOT infer exact generator or family from generic provider labels.
- Same original/group/campaign/template => one partition. Known cross-corpus mirrors must be deduplicated globally.
- Train/validation/test on **source group**, not individual rewrite row; freeze split seed and hashes.
- Calibrate/choose thresholds solely on seen-origin validation. New target labels **never** used in zero-shot method selection; target-adaptation experiments must be separately named and independently tested.
- Do not simultaneously claim 'unseen LLM' and include any data from the held-out generator in feature selection, fine-tuning, editing, prompting, calibration or validation.
- If corpus only has labels with uncertain phishing semantics or generator fields missing, restrict the claims.
- DO NOT use the phishing-only stylometric 2026 corpus as negative samples for maliciousness detection.

## 6. Main experimental matrix
| Exp | Train/eval | Question |
|---|---|---|
| E00 | Schema, duplicates, license, parent-link audit | Can data support claims? |
| E01 | Original-only in-corpus split | Reference baseline, not novelty |
| E02 | Original vs verified same-intent rewrite pairs | Invariance/flip rate |
| E03 | Security-changing adjudicated paired edits | Sensitivity/control |
| E04 | Hold out entire rewrite generator | LO-G only if provenance known |
| E05 | Hold out generator family | LO-F when feasible |
| E06 | Independent source held out | LO-C |
| E07 | Held-out generator + corpus | Joint shift, only if factorial coverage permits |
| E08 | Human vs AI **legitimate** strata | AI-benign false alarms |
| E09 | Calibrated+selective decisions (frozen validation) | Review cost, risk |
| E10 | 3+ seeds, paired bootstrap grouped by parent, ablations | Statistical credibility |
| E11 | CPU inference latency and peak RAM, Kaggle GPU training log | Reproducibility/feasibility |

## 7. Metrics and statistical reporting
Primary: phishing recall at fixed **validation-selected** FPR budget (1% and 5% if enough legitimate controls), realized test FPR, PR-AUC, worst-source performance. Never assume test FPR is guaranteed under shift.
Paired: prediction disagreement (flip) rate on *verified same-label pairs*, parent-level full-correct rate, sensitivity on verified label-change pairs, per-generator support.
Secondary: precision, recall, F1, MCC, AUROC, AUPRC, Brier, ECE (define bins), risk-coverage with abstention/review rate. Use parent-group bootstrap 95% CI and report actual counts. Avoid treating correlated rewrites as independent.
Low prevalence: scenario-adjust precision / alerts per 10k emails with explicitly stated assumptions. Resource: batch size, model size, speed and RAM.

## 8. Staged decisions
- **G0 literature GO:** unique RQ with defensible differentiation, related-paper table.
- **G1 data GO:** licenses, provenance, labels, parent links, sufficient human+AI legitimate and phishing coverage.
- **G2 paired GO:** audited meaning-preserving pairs + verified changed-security labels.
- **G3 split GO:** overlap, leakage, stratification, group logic pass.
- **G4 baseline GO:** reproducible and convincing failure, not artifacts.
- **G5 method GO:** full method beats equal-budget strong alternatives on multiple shifts without sacrificing sensitivity.
- **G6 paper GO:** ablations, statistical evidence, error analysis, reproducibility, ethics, consistent claims.
Each gate is NO-GO unless its **issue checklist and attached evidence** are complete. Failed hypotheses must be reported, not concealed.

## 9. Free GPU plan
- Stage A: Dataset auditing, TF-IDF/LR/SVM primarily CPU.
- Stage B: DistilBERT/MiniLM 256–384 token input; 8–16 batch, fp16/gradient accumulation as needed, one T4 first. Measure truncated-email fraction before accepting max length.
- Stage C: Paired fine-tuning with controlled groups; use cached outputs, checkpoint and Kaggle dataset input if internet restricted.
- Do NOT train huge LLMs; original/rewrite data is the primary research ingredient. A second T4 is optional, not a reason to require distributed training.

## 10. Publication outline
1 Introduction: impact, gap, exact RQs, contributions.
2 Related work: LLM phishing, domain shift, paired consistency, risk control.
3 Threat model and task: email field availability, adversary assumptions and label definitions.
4 Datasets, rights, audit, protocol, split/independent test.
5 Method and training details incl. baselines.
6 Results RQ1–RQ4 with paired CI, multiple seeds, strongest controls.
7 Ablation/error/shortcut/privacy/deployment analysis.
8 Limitations and responsible disclosure.
9 Conclusion.
Appendix: manifest/split hashes, hyperparameters, templates, rubric, negative results.

**Review rule**: No checkmark without (1) artifact, (2) executable tests or reproducible inspection, (3) result including failures, (4) written GO/NO-GO decision.
