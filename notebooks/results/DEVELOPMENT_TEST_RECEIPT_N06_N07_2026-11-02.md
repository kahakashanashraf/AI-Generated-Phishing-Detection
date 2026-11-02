# N06–N07 development-stage validation receipt (2026-11-02)

This report records **assistant-side CPU-only synthetic tests**, not real Kaggle dataset execution or a full audit of journal readiness.

## Local tests run in Python
- **N06 paired statistics:** exact discordance counts, two-sided exact McNemar from `scipy.stats.binomtest`, 10,000 parent paired bootstrap examples, exact binomial bounds, selective risk coverage, input validation.
- Synthetic paired example of **one new false positive among 142**: delta `1/142=0.007042253521126761`; bootstrap 95% interval on the constructed toy example `[0.0,0.02112676056338028]`; exact McNemar p=1.0. **These are synthetic diagnostics, NOT measured N05 parent discordance, and MUST NOT appear as N05 inferential results.**
- **N07 classical CV:** executable 3-fold StratifiedKFold smoke checks on toy data for TF-IDF word LR, word MultinomialNB, and character n-gram LR. Each returned three finite average-precision scores; predict_proba output shapes matched. PASS.

## Source commitment
- N05 archived original researcher-uploaded notebook: `notebooks/05_AI_Written_Legitimate_False_Alarm_Benchmark.ipynb`.
- N06 standalone notebook: `notebooks/06_Paired_Inference_and_Selective_Reliability.ipynb`.
- N07 standalone notebook: `notebooks/07_Train_Only_CV_Classical_Benchmark.ipynb`.

## Execution gate
- N05 real data: previously executed on Kaggle, results already committed.
- N06 real data: **PENDING**. The earlier N05 aggregate tables are insufficient for exact paired disagreement; notebook recomputes private row-aligned scores from pinned sources and outputs only statistics.
- N07 real data: **PENDING**. Train-only model selection avoids test-set hyperparameter tuning, but the original N05 holdout is already seen; new independent cross-corpus test is essential before final results.
- Transformer fine-tuning / evidence ablation / independently AI-authored benign controls: **NOT YET IMPLEMENTED**.

## Important SOTA overlap and manuscript restriction
Existing studies already rephrase *safe email*, compare classical and transformer models, perform cross-corpus testing, and calibrate selective detectors. See `docs/SEQUENTIAL_JOURNAL_EXECUTION_SOTA_GATE_2026-11-02.md`. Consequently these operations alone are **not** unique novelty; Q1-target journal claims require a distinctly tested, evidence-linked contribution and a fresh independent holdout.
