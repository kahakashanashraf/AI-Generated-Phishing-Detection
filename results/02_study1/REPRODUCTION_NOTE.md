# Study 1 re-execution in the unified Kaggle image: reproduction note

**Run:** Kaggle kernel `ddipra/02-study1-exploratory-reproduction`, version 3, notebook `kaggle_kernels/02/`, runtime 1,438 s.
**Run status:** `COMPLETED_WITH_GATE_FAILURES`. Gate `no_shape_or_column_changes` = False; the other two gates PASS.
**Reference:** the original GitHub Actions outputs at commit `0705745`.
**Decision:** DECISION_LOG D016. In line with D013, these re-executed outputs are the canonical Study 1 numbers.

## What differs, and why

| Tables | Status in `reproduction_report.csv` | Explanation |
|---|---|---|
| N05, N09, N10 (N05/N09 tables), N13, N14 metrics | IDENTICAL or WITHIN_TOLERANCE (max abs diff ≤ 1.5e-8, mostly ≤ 4e-16) | Exact reproduction across environments |
| N07 `inner_cv_scores`, `model_comparison`, `paired_effects`; N08 `external_*`; N10 `table03`, `table04` | SHAPE_OR_COLUMNS_DIFFER, which made the gate fail | **Extra rows only.** The original N07 recorded `"lightgbm": "not-installed: SKIPPED"` on GitHub Actions. The Kaggle image ships LightGBM, so the optional `word_lgb` family now runs. Every original row is reproduced with max abs diff ≤ 6e-16 (checked row by row against `0705745`). |
| N11 augmentation tables | DIFFERENT | Identical training sets and row counts, and the `orig_only` threshold is identical. Logistic-regression fits on the augmented sets differ slightly across CPU/BLAS platforms. Largest change: 0.71 pp FPR and 0.62 pp recall, AUC and AP ≤ 0.0002. Conclusions unchanged. |
| N12 DistilBERT tables | DIFFERENT | Fine-tuned on a T4 GPU here, against CPU on GitHub Actions, with a single seed. Largest change: 3.5 pp FPR on D2 GPT-4o and 1.9 pp external AUC. Study 1 transformer results are exploratory and single-seed. Study 2 uses five seeds (D5). |
| N14 `training_objective_diagnostics` | DIFFERENT, through a text column only | Numeric values within 3e-15. |

## Consequence
- Study 1 numbers in the paper come from this folder.
- The paper reports the GitHub Actions-to-Kaggle differences above in the reproducibility section, and treats the LightGBM rows as an additional exploratory comparator.
- No Study 2 (confirmatory) result depends on 02.
