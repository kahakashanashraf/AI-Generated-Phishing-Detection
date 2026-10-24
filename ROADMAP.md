# MASTER ROADMAP — PLOS ONE Phishing Research

**Version:** 0.2, 2026-10-24. **Current journal:** [PLOS ONE](docs/PLOS_ONE_TARGET.md); previous target IEEE Access retained in decision history. **This document is the task entrypoint.** We are learning research from first principles while enforcing reproducible, journal-grade evidence.

**Working problem:** *Security-Sensitive Invariance Learning for Reliable Phishing Email Detection Under Unseen LLM Rewriting and Domain Shift.*

**Primary label:** phishing vs legitimate. AI/human author is a **subgroup attribute**; don't mistakenly interpret the original `src/baseline.py` origin classifier as solving phishing detection. Treat spam separately.

**Canonical D1–D5 workspace:** [data/README.md](data/README.md) — source directories, audit receipts, split storage, annotations and safe releases. All actual dataset downloads are still pending.

**Main docs:** [Research Blueprint](docs/RESEARCH_BLUEPRINT.md) | [Dataset Playbook](docs/DATASET_PLAYBOOK.md) | [Beginner's Guide](docs/BEGINNERS_GUIDE.md) | [Decision Log](docs/DECISION_LOG.md) | [Existing Literature and Gaps](docs/LITERATURE_AND_GAPS.md).

## One step at a time — master checklist

- [ ] **M0** — [Novelty and problem freeze (#1)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/1). Literature matrix, explicit RQs, gap/overlap review. **START HERE.**
- [ ] **M1** — [Dataset rights, provenance and label/schema audit (#2)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/2). D1–D5 receipts; viable sources selected.
- [ ] **M2** — [Original↔rewrite pairs and counterfactual label checks (#3)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/3). Two kinds of vetted edits and annotation rubric.
- [ ] **M3** — [Leakage-proof, versioned evaluation splits (#4)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/4). Parent-safe, generator-safe, source-safe; hash receipts.
- [ ] **M4** — [Strong baselines before any new method (#5)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/5). TF-IDF/LR, SVM, DistilBERT, negative controls.
- [ ] **M5** — [Security-sensitive style consistency method (#6)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/6). Properly validated style and security-change objectives; ablations.
- [ ] **M6** — [Unseen LLM + corpus generalization and risk (#7)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/7). LO-generator, LO-corpus, conditional joint shift; fixed-FPR/review.
- [ ] **M7** — [Multiple seeds, statistics, error analysis (#8)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/8). Parent-bootstrap 95% CI, compute cost.
- [ ] **M8** — [Paper writing and scientific integrity audit (#9)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/9). PLOS ONE structure, Vancouver references, Data Availability and ethics, clear claims, figures, citations.
- [ ] **M9** — [Final reproducibility/submission package (#10)](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/10). Clean notebook, open code and minimal dataset/access plan, artifact checks, manuscript deliverables.

**Important:** This master list is NOT automatically synchronized with Issue checkboxes. Each time an entire milestone is verified, close the issue and manually replace `[ ]` with `[x]` here **in the same update**. Individual issue tasks get checked **only with evidence**. Until then all above remain unchecked.

## Dataset timing at a glance
| ID | Data source | Used when | Planned research function |
|---|---|---|---|
| D1 | [Curated email corpora (Zenodo 8339691)](https://zenodo.org/records/8339691) | M1, M3, M4, M6 | Original human email baseline; cross-corpus holdouts |
| D2 | [HarmJ0y PhishingSpamDataSet](https://github.com/HarmJ0y/PhishingSpamDataSet) | M1–M6 IF audited | Human/AI phishing/valid, rewritten examples, conditional held-out generators |
| D3 | [PhishFuzzer](https://github.com/DataPhish/PhishFuzzer) | M1, M2, M3, M6 | Parent-linked paired fuzzing and security metadata robustness |
| D4 | [LLMGen Phishing Email Dataset](https://huggingface.co/datasets/Dizzzy0x00/LLMGen-Phishing-Email-Dataset) | M1, M6 auxiliary | LLM synthetic phishing/valid check; no clean generator holdout due language confound |
| D5 | [Gutierrez cross-model dataset](https://zenodo.org/records/20250116) | M0, M4 auxiliary | Origin-attribution related-work reproduction ONLY |

All dataset candidates require license, provenance, overlapping-corpus and row-schema inspection **before approval**. See the [full dataset playbook](docs/DATASET_PLAYBOOK.md) for exact file names, risks and intake forms.

## Gates; no skipping
- G0 (research gap) -> G1 (rights + dataset provenance) -> G2 (pair validity) -> G3 (split integrity) -> G4 (reproducible baseline) -> G5 (real method value) -> G6 (scientific manuscript integrity).
- If G1 fails: change source/claims, **do not train anyway**.
- If G2 fails: remove 'bidirectional security-change' novelty and reconsider alternative paper hypothesis.
- If G4 finds no meaningful baseline weakness: reassess novelty before GPU-intensive training.
- If G5 fails: don't hide negative results or claim new SOTA.
- GitHub Issues are research notebooks: append dated evidence link, SHA256, command, result and reviewer GO/NO-GO before ticking.

## What is already actually done (infrastructure only)
- [x] GitHub repository created and connected; code pushed.
- [x] Kaggle clone/dependencies/GPU environment smoke test **reported by user** (2x T4), but no actual training.
- [x] Existing GitHub Actions workflow completed successfully once for origin-attribution baseline tests.
- [x] This research plan, learning guide, source shortlist and 10 milestone issues committed.
- [ ] All dataset-specific audits, primary phishing experiments and manuscript results: **NOT YET DONE.**

## First exercise
1. Read [Beginner's Guide](docs/BEGINNERS_GUIDE.md) and [M0 Issue #1](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/1).
2. Confirm in writing the distinction between origin attribution and phishing detection.
3. Build the 2024–2026 literature-overlap matrix (no models yet).
4. Then start [M1 Issue #2](https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/2): inspect D1 rights/schema and create the first intake receipt.
5. Send a run artifact or notebook link after each step; test it before clicking the checkbox.

## Progress reports
For every completed verified item, record:
`UTC time | Issue/checklist item | dataset revision/SHA256 | code commit | notebook/run | test | evidence | GO/NO-GO`.

Do not publish raw messages, active phishing URLs, passwords or private details.
