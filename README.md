# AI-Generated Phishing Detection — IEEE Access Research Project

**Status: RESEARCH PLANNING / PRE-DATA AUDIT. No phishing model has been scientifically validated yet.**

## START HERE — one checkbox at a time
- **[MASTER ROADMAP](ROADMAP.md)** — 10 milestones, each with a linked GitHub Issue and evidence-only checkbox.
- **[BEGINNER'S GUIDE](docs/BEGINNERS_GUIDE.md)** — step-by-step lessons, plain-language concepts and what output to show after each task.
- **[DATASET PLAYBOOK](docs/DATASET_PLAYBOOK.md)** — D1–D5 sources: exactly which data, when, why and constraints.
- **[RESEARCH BLUEPRINT](docs/RESEARCH_BLUEPRINT.md)** — title, gap, hypotheses, method, experiments, metrics, GO/NO-GO.
- [RELATED WORK MATRIX](docs/RELATED_WORK_MATRIX.md) — 2025–2026 closest competitor papers and novelty checks.
- [PAIR ANNOTATION RUBRIC](docs/ANNOTATION_RUBRIC.md) — tell harmless rewrites from security-changing edits.
- [DECISION LOG](docs/DECISION_LOG.md) — append-only history of scientific decisions and uncertainties.
- [DATASET AUDIT RECEIPT](reports/dataset_receipts/_TEMPLATE.md) — template to copy to D1.md, D2.md, etc.

### Project question
Can a detector classify **phishing vs legitimate** accurately under unseen LLM rewriting **while remaining stable for verified same-intent edits and sensitive to verified security-changing edits**, without excessive false alarms on legitimate AI-written email?

**Caution:** Existing `src/baseline.py` is an **auxiliary authorship classifier** (AI vs human *among phishing-only* samples). It is NOT the main phishing detector. Do not use its metrics to claim maliciousness detection. Our proposed security-sensitive objective is a **hypothesis, not proven novelty**.

## Datasets (candidates only; must pass rights+provenance checks)
- D1: https://zenodo.org/records/8339691 — human originals / baseline and corpus shift.
- D2: https://github.com/HarmJ0y/PhishingSpamDataSet — human/AI original and rewritten email, conditional generator holdout.
- D3: https://github.com/DataPhish/PhishFuzzer — 3,300 seeds + 19,800 variants, paired testing; mutations may alter security cues.
- D4: https://huggingface.co/datasets/Dizzzy0x00/LLMGen-Phishing-Email-Dataset — auxiliary synthetic/language-stratified evaluation, not clean LO-generator.
- D5: https://zenodo.org/records/20250116 — phishing-only AI-origin replication, not primary classification.

See **Dataset Playbook** for file-level intake order, licenses, potential source leakage and expected columns. No raw email data should be committed to this public repository.

## Kaggle (free GPU / CPU) quick start
You already successfully cloned the repository and saw 2x Tesla T4 in your environment check. If **already inside repo**, use `!git pull --ff-only` in Kaggle to update to these new planning docs. For a new notebook:

```python
!git clone https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git
%cd AI-Generated-Phishing-Detection
!pip install -r requirements.txt
!python -m unittest discover -s tests -v
!python scripts/check_kaggle.py
```

GPU is not required for the initial literature review, data audit or TF-IDF classifier. Do not waste free GPU quota until **M4**.

## Evidence-only progress marking
**[Issue #1 — start literature/problem gate](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/1)**. For each checkbox: show dated artifact + dataset/code versions/hashes + executed test/log + GO/NO-GO. Once a milestone is complete, close its issue and tick the corresponding ROADMAP item. Never tick for unrun code, a paper citation alone, or an unaudited dataset.

Security: do not publish private messages, credentials, live-looking phishing links or copyrighted/raw restricted corpora.
