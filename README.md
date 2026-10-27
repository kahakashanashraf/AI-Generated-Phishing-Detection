# AI-Generated Phishing Detection — PLOS ONE Research Project

**Primary target: [PLOS ONE](docs/PLOS_ONE_TARGET.md) (journal switch recorded 2026-10-24).**

**Status: RESEARCH PLANNING / PRE-DATA AUDIT. No phishing model has been scientifically validated yet.**

## M0 manuscript literature outputs (2026-10-24)
- **[Related Work — 30-paper draft (adapt to PLOS template)](paper/related_work.tex)** — 6 thematic subsections, 30 in-text citations, double-column comparison table.
- **[BibTeX references](paper/references.bib)** — 30 entries with journal/conference DOI or authoritative URL.
- **[Evidence/access audit](paper/LITERATURE_EVIDENCE_AUDIT.md)** — which papers were read as full text vs abstract only, exact novelty overlaps and pending papers.
- **[30-study detailed analysis matrix](paper/STUDY_MATRIX_30.md)** — each study's actual task, method, relevance, source link and full-text access status.
- **[PLOS ONE target and compliance](docs/PLOS_ONE_TARGET.md)** — rigor, reproducibility, data rights, fees and exact submission steps.
- **[Manuscript integration instructions](paper/README.md)** — required packages, `\\input`, BibTeX and publication QA.

Research gate M0 remains **IN PROGRESS**, even though the first draft is committed. Source limitations and still-unverified novelty are documented, and no results are invented.

## Kaggle one-cell resume / prevent repeated setup
- [Session persistence and reusable one-cell setup](docs/KAGGLE_PERSISTENCE.md) — restores GitHub workspace, mounts approved private Kaggle inputs, skips unchanged metadata audits; no dataset re-download by default. Save notebook and use Persistence > Files only when available.

## Single data workspace (new)
- **[data/ — datasets, audits, splits and annotations](data/README.md)** is now the canonical home for **all five** research datasets. Raw/processed files stay private and are ignored; dataset receipts are centralized under [data/audit/receipts](data/audit/receipts).
- Create/verify local folders with `python scripts/init_data_workspace.py` (safe and idempotent). No data are downloaded by this command.

## START HERE — one checkbox at a time
- **[MASTER ROADMAP](ROADMAP.md)** — 10 milestones, each with a linked GitHub Issue and evidence-only checkbox.
- **[BEGINNER'S GUIDE](docs/BEGINNERS_GUIDE.md)** — step-by-step lessons, plain-language concepts and what output to show after each task.
- **[DATASET PLAYBOOK](docs/DATASET_PLAYBOOK.md)** — D1–D5 sources: exactly which data, when, why and constraints.
- **[RESEARCH BLUEPRINT](docs/RESEARCH_BLUEPRINT.md)** — title, gap, hypotheses, method, experiments, metrics, GO/NO-GO.
- [RELATED WORK MATRIX](docs/RELATED_WORK_MATRIX.md) — 2025–2026 closest competitor papers and novelty checks.
- [PAIR ANNOTATION RUBRIC](docs/ANNOTATION_RUBRIC.md) — tell harmless rewrites from security-changing edits.
- [DECISION LOG](docs/DECISION_LOG.md) — append-only history of scientific decisions and uncertainties.
- [DATASET AUDIT RECEIPT](data/audit/receipts/_TEMPLATE.md) — template to copy to D1.md, D2.md, etc.

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
