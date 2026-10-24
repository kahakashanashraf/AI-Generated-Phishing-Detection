# AI-Generated Phishing Detection

Research project: generalizable phishing-email detection across unseen LLM generators, with careful leakage prevention, calibration, and evaluation.

## Kaggle (free GPU) quick start

1. Create a new notebook at https://www.kaggle.com/code and select **GPU** in notebook settings.
2. Enable **Internet** (if available). Run:

```python
!git clone https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git
%cd AI-Generated-Phishing-Detection
!pip install -r requirements.txt
!python scripts/check_kaggle.py
```

3. For offline sessions, add this repository as a Kaggle notebook input or attach a Kaggle Dataset containing the source code; cloning requires Internet.
4. Save notebook versions and, if available in your Kaggle UI, use **File > Link to GitHub** to authorize GitHub sync. This authorization step must be performed in your Kaggle account; adding this README does **not** establish the account-level link.

## Research guardrails

- Split by source email / template family **before** augmentation or paraphrase.
- Keep generator identity for **leave-one-LLM-out** tests; never train on the held-out generator.
- Track both phishing status and human-vs-AI provenance; AI-generated does not inherently mean malicious.
- Report false-positive rate, phishing recall at fixed FPR, PR-AUC, ECE and risk-coverage curves.
- Do not commit Kaggle API tokens, private emails, personal information, or large raw datasets.
- This initial repository setup is a smoke test, **not** a trained phishing detector.

## Contents

- `scripts/check_kaggle.py`: quick runtime/dependency/GPU verification.
- `requirements.txt`: starter dependencies.
- `.gitignore`: excludes credentials, private data and checkpoints.
