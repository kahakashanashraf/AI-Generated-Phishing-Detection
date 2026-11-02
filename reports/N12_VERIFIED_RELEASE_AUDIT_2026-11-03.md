# N12 verified-release audit — 2026-11-03

## Provenance and status
GitHub Actions run 41497439164 completed SUCCESS, including real CPU training, notebook protocol guardrails, aggregate checksum validation, artifact upload, and commit of safe aggregates. Run URL: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/actions/runs/41497439164

Repository release: phishing_n12_safe/run_manifest.json, transformer_metrics.csv, train_validation_history.csv. Manifest identifies distilbert/distilbert-base-uncased at immutable revision 12040accade4e8a0f71eabdb258fecc2e7e948be, seeds 2026/2027, at most 2 epochs, 1418 original training examples, 304 validation examples, and selection by validation AP with threshold from D2 validation at nominal <=5% FPR. Both seeds were trained on CPU. The workflow's checksum verification passed; this report does not claim an independent bytewise checksum recomputation.

## Matched D2 original (142 legitimate, 162 phishing)
| Comparator | FPR (FP/142) | Phishing recall (TP/162) |
|---|---:|---:|
| N05 TF-IDF logistic | 11.27% (16) | 99.38% (161) |
| N05 calibrated linear SVM | 9.86% (14) | 100.00% (162) |
| N11 benign_rewrites | 12.68% (18) | 96.91% (157) |
| N12 DistilBERT seed 2026 | 11.27% (16) | 99.38% (161) |
| N12 DistilBERT seed 2027 | 14.08% (20) | 99.38% (161) |

These are descriptive model-level comparisons, NOT paired significance tests; individual per-example prediction agreement is unavailable in privacy-safe aggregate CSVs. Note: nominal 5% FPR threshold is selected on validation, not guaranteed on held-out data.

## External E-PhishLLM English (5506 legitimate, 5996 phishing)
| Comparator | FPR (FP/5506) | Recall (TP/5996) |
|---|---:|---:|
| N05 TF-IDF logistic | 88.87% (4893) | 99.30% (5954) |
| N05 calibrated linear SVM | 86.43% (4759) | 99.50% (5966) |
| N11 benign_rewrites | 66.35% (3653) | 98.25% (5891) |
| N12 DistilBERT seed 2026 | 87.05% (4793) | 98.33% (5896) |
| N12 DistilBERT seed 2027 | 93.59% (5153) | 98.88% (5929) |

N12 is not a consistent improvement on N05/N11. N11 benign_rewrites reduces external FPR relative to both N12 seeds but also has a recall trade-off relative to N05. No superiority, causal AI-authorship effect, or Q1 novelty is established.

## Critical validity gates
- The external E-PhishLLM test is **exploratory, not fresh blind**: manifest explicitly says it was examined before design.
- Verify independent source/campaign and normalized near-duplicate overlaps before interpreting generalization; check labels independently where feasible.
- Next experiment should freeze code/hypotheses and choose a genuinely unexamined independent test; never retune threshold using the external test.
- Do not publish raw email or row-level sensitive predictions. Report confidence intervals and paired inference only when legally and methodologically supported by matched predictions.
- No new training run is warranted solely to repeat a successful checksum-verified release.
