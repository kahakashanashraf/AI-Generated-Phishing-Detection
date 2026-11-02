# N11 — Parent-safe benign rewrite augmentation: verified GitHub experiment (2026-11-02)

## Execution
- GitHub Actions: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/actions/runs/41472196787
- Source: `notebooks/11_Parent_Safe_LLM_Rewrite_Augmentation.ipynb` at source-hardening commit `4764a6b`.
- Pinned HarmJ0y D2 originals/rewrite providers, original N05 parent split and E-PhishLLM external synthetic English corpus.
- Data integrity: original source pinned; training augment excluded val/test originals **and all val/test rewrite-provider texts** by normalized SHA256. Removed 419 exact duplicated training augment candidate texts. No external source tuning.
- Four configured training strategies: original-only, source-labeled benign-only rewrites, all rewrites, GPT-4o only; identical TF-IDF LR model and validation-FPR threshold policy. Each parent receives equal total effective training weight.

## External E-PhishLLM English (5,506 synthetic legitimate, 5,996 synthetic phishing)
| Training strategy | Extra train rewrites | External legitimate FPR | External phishing recall | External AP |
|---|---:|---:|---:|---:|
| Original only (frozen baseline) | 0 | 88.87% | 99.30% | 94.74% |
| **Benign rewrites only** | 1,669 | **66.35%** | **98.25%** | 95.53% |
| All rewrites | 3,835 | 85.43% | 99.18% | 95.23% |
| GPT-4o only | 1,384 | 82.76% | 98.97% | 95.21% |

**Interpretation:** Benign-only train augmentation improved external FPR by 22.52 percentage points, with phishing recall decreasing by 1.05 percentage points (42 to 105 phishing false negatives). It remains unacceptably high and is **not an operationally safe deployed detector**. This is source-mismatched and post-exploration evidence, not a fresh blind holdout or causal effect of AI authorship.

## D2 held-out originals
| Strategy | FPR on 142 legitimate | Recall on 162 phishing |
|---|---:|---:|
| Original only | 16/142 = 11.27% | 161/162 = 99.38% |
| Benign rewrites only | 18/142 = 12.68% | 157/162 = 96.91% |
| All rewrites | 16/142 = 11.27% | 161/162 = 99.38% |
| GPT-4o only | 16/142 = 11.27% | 161/162 = 99.38% |

**Tradeoff:** Benign-only augmentation reduces external false alarms but hurts *both* FPR and phishing recall on D2 held-out originals. Therefore it **fails a strict across-source safety claim**.

## Scientific judgment
- GO: reproducible exploratory data-augmentation ablation, grounded source-derived labels, train-only parent controls, frozen validation threshold, privacy-safe aggregate output.
- NO-GO: publication-ready novel algorithm, causal AI-authorship bias, independent blinded generalization, safe deployment.
- Prior art already includes rewritten safe email and cross-corpus/uncertainty evaluation; simple augmentation is NOT novel. See `docs/SEQUENTIAL_JOURNAL_EXECUTION_SOTA_GATE_2026-11-02.md`.
- Next: run pinned DistilBERT comparator (`notebooks/12_DistilBERT_Fine_Tune_External_Reliability.ipynb`) on Kaggle GPU, add truly **new, blinded source-held-out** evaluation, semantic provenance/rights checks, confidence-interval comparisons, and reject or refine any proposed mitigation that worsens phishing recall or source-specific false alarms.

## Privacy
Only four aggregate output files committed under `phishing_n11_safe/`: `augmentation_metrics.csv`, `paired_benign_rewrite_effects.csv`, `support_and_training_counts.csv`, `run_manifest.json`. No raw email, per-row labels, personal sender details, active phishing URLs, or private reviewer aid.
