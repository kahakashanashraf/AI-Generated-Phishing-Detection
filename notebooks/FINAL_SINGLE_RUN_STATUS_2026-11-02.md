# Cumulative experiment runner — 2026-11-02

**Single Kaggle notebook:** `notebooks/10_Paper_Tables_Figures_and_Manifest.ipynb`

The N10 notebook includes all code cells of the earlier N05, N06, N07, N08 and N09 stages, followed by N10 aggregate-only figures/tables. It is designed for **one complete sequential Run All** after this research build has been reviewed. It is not the same as independent end-to-end verification.

## Frozen experiment sequence

| Notebook | Scope | Current evidence |
|---|---|---|
| N01–N04 | Dataset source, schema, pair, lineage audits | Earlier real Kaggle reports supplied by researcher |
| N05 | Two frozen TF-IDF baselines, parent-held-out D2 original vs rewrite | **Real Kaggle executed**; E01 aggregate results committed |
| N06 | Exact McNemar, parent bootstrap 95% CI, risk–coverage | Source committed, local synthetic tests PASS, **real data pending** |
| N07 | Train-only nested within-fold TF-IDF tuning: word/char/ngram, NB, optional LightGBM | Source committed; local synthetic tests PASS, **real data pending** |
| N08 | Official ACM E-PhishLLM source with Git blob pin `7a0e74ecebc1f3f5b21f42deccfb716b14bba46b`; English external AI-authored benign FPR | Source committed; real data **pending**, source paper verified |
| N09 | Style-only vs security-cue lexical proxies vs train-only selected fusion | Source committed; synthetic pipeline checks PASS, **real data pending** |
| N10 | Aggregate-only publication-draft tables, four PNG + four PDF figures and content hashes | Source committed, **real data pending** |

## Preconditions
- Use a **private Kaggle notebook**, CPU sufficient for N05–N10 classical experiments; Internet ON for first verified source download, or upload *exact pinned* source files to a private Kaggle Input.
- Requires Python, scikit-learn, scipy, numpy, matplotlib, optional lightgbm. No installation from network is silently performed. No mandatory GPU models are included yet; a transformer SOTA comparator is **still missing** and must be added before Q1-target model comparison is called complete.
- Download/report ONLY safe `/kaggle/working/phishing_n05_safe` through `phishing_n10_safe` directories, after privacy checks.
- Private raw text is staged in `/kaggle/temp/phishing_n05_private`, not published.
- Because source `ephishLLM.json` is from an official *mutable main URL*, the notebook checks the immutable Git **blob SHA-1** before use and stops on a mismatch.

## Required research steps before *final manuscript* claims
- Independently verify privacy, usage rights, class provenance, semantics and controlled AI-authored legitimate-vs-human comparator.
- Independent corpus source overlap checks beyond exact text: campaign/template/near-duplicate decontamination.
- Freeze/execute the corpus-held-out evaluation, paired statistics, style/evidence ablation and any claimed method.
- Add strong transformer comparison (fine-tuned compact transformer, identical source and threshold policy) rather than only classical algorithms.
- Recheck literature: prior work already includes safe-email LLM rewriting, cross-corpus/transformer comparisons and calibrated selective cascades.
- Choose and verify a current Q1 journal's scope and quartile by edition/category; quartile is not guaranteed or verified here.
- Results must not be selected/tuned after viewing the E-PhishLLM test. Negative findings should be retained.

## GitHub key paths
- N05: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/05_AI_Written_Legitimate_False_Alarm_Benchmark.ipynb
- N06: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/06_Paired_Inference_and_Selective_Reliability.ipynb
- N07: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/07_Train_Only_CV_Classical_Benchmark.ipynb
- N08: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/08_External_AI_Authored_Benign_EPhishLLM.ipynb
- N09: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/09_Style_vs_Evidence_Proxy_Ablation.ipynb
- N10: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/10_Paper_Tables_Figures_and_Manifest.ipynb

## Honest status
**Notebook code staged and synthetic smoke tested; real dataset results beyond N05 are unverified.** Do not describe N06–N10 as Kaggle-executed or Q1 publication ready. Do not claim a newly trained transformer or a validated security-evidence method.
