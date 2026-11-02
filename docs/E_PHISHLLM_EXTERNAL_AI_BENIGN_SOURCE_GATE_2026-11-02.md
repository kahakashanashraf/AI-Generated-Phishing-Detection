# External AI-authored legitimate candidate — E-PhishLLM (2026-11-02)

## Primary evidence
- ACM AISec 2025 paper: https://doi.org/10.1145/3733799.3762967
- Official public repository: https://github.com/pajola/e-phishGen
- Dataset path: https://github.com/pajola/e-phishGen/blob/main/ephishLLM.json
- Official source README: https://github.com/pajola/e-phishGen/blob/main/README.md
- Hugging Face mirror/source description: https://huggingface.co/datasets/pajola/e-phishGen

The paper describes **16,616 synthetic emails** balanced phishing versus benign, created with an LLM, and three languages. Repository README confirms per-record Subject, Body, type (0 legitimate, 1 phishing), and Language, but its text emphasizes English/Italian even though the paper describes English/Italian/German. **Language distribution and released version need direct inspection before recording precise per-language counts.** GitHub browser reports about 11.7 MB for `ephishLLM.json`.

## Why this matters
This is a candidate **independently generated AI-authored legitimate** source, distinct from our D2 *rewritten* legitimate examples. It may permit external false-positive evaluation of the N05/N07 detectors **without treating its synthetic benign semantics as human-validated real-world legitimacy**. Different topic, language, organization style and generator are confounds; cross-source failures alone do not establish causal AI-style bias.

## Required gates BEFORE enabling final N08 results
1. Download specific immutable commit/file revision to private storage, compute SHA256/byte count and save pin. Do not use mutable `main` in final reproducibility manifests.
2. Confirm dataset dimensions, actual languages, label semantics, non-empty text, and whether there are parent/campaign or company/person profiles; deduplicate within source and across full training source originals/rewrites using normalized exact match and near-duplicate check.
3. Fix primary analysis to source-compatible English-only subset **before looking at outcomes**; report other languages separately as cross-language stress if tokenizer is appropriate.
4. Freeze N05/N07 chosen models/thresholds: no tuning on E-PhishLLM, no fitting vectorizers on its emails, and no using its labels in training.
5. Verify repository license/terms and any generator-output reuse conditions; if unclear, cite public paper and do not redistribute raw text.
6. Flag this as **synthetic AI-authored legitimate external-source evaluation**; it still lacks matching independently sourced human-authored benign emails under a randomized controlled topic/source design. Pairwise D2 rewriting is a separate experiment.
7. Require external phishing recall along with benign FPR and Wilson/exact confidence intervals, coverage and prevalence stress; compare to any available human-source test as contextual (not causal) contrast.

## SOTA/novelty warning
Because E-PhishGEN itself already benchmarked detectors on this exact corpus, merely reproducing cross-dataset failures **cannot be claimed novel**. Novelty must be a demonstrable, statistically validated false-alarm mechanism/mitigation and matched operational trade-off beyond existing work. The 2025 IEEE CARS paper already evaluates LLM-rewritten *safe* email, so that task is not novel by itself:
https://doi.org/10.1109/CARS67163.2025.11337548

## Status
**Candidate located and documented only. No real data downloaded or trained on locally.** The user needs only one final Kaggle run after fully validated notebooks are ready.
