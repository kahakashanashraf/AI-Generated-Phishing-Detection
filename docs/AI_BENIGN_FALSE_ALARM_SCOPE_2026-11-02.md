# Research scope freeze — 2026-11-02

## Primary question
Does a phishing detector incorrectly flag legitimate AI-written email as phishing more often than legitimate human-written email?

## Supporting questions
- Can it recognize phishing after GPT-4o/DeepSeek/other LLM rewriting without relying on superficial style?
- Does performance hold on genuinely independent source corpora and defensible held-out generators?
- How does calibration and selective abstention change false-positive rates and manual-review burden?

## Target and strata
- Main label: phishing versus legitimate. Preserve **spam** as a separate source category rather than silently equating it with phishing.
- Provenance variable: AI versus human **only where supported by record-level source evidence**.
- Negative control: verified AI-written legitimate email. Report false-positive rate for AI-written and human-written legitimate strata separately, including support and uncertainty intervals.
- Primary emphasis: false alarm disparity and generalization, not AI-vs-human authorship classification.
- Never claim source-assigned human/AI labels are individually adjudicated ground truth unless verified.

## Source constraints established by prior executed audits
- D2 originals and D3 PhishFuzzer seeds are **not independent**: all 3,075 D2 IDs reappear in D3; 2,896/3,000 D2 unique normalized texts overlap with D3 (96.53%). Enforce shared ancestry group and cross-source text decontamination.
- D2 has an explicit fourth type `Phishing Simulation` (35 originals), plus one D2 `Valid` to D3 `Phishing` ID conflict. Quarantine these for the binary target unless separately justified.
- D1 curated spam/ham source labels cannot universally be treated as strictly phishing/legitimate.
- D4 LLMGen's language and generator are confounded; use for stratified exploratory synthetic evaluation, not unqualified leave-one-generator-out claims.
- D5 is phishing-only AI/human authorship context; exclude from primary phishing-vs-legitimate binary evaluation.
- N03 structural pairing is not semantic gold. AI-assisted triage is not independent human adjudication.

## Ten-day research execution order
1. Freeze a small, source-documented binary benchmark with explicit label policy. Rights and privacy review is obligatory for each included source; exclude unsupported sources instead of forcing a label.
2. Generate row-level ancestry/duplicate-safe partitions from approved sources, preserving a locked external source test (do not infer assignments from aggregate N04 counts).
3. Run TF-IDF + Logistic Regression and Linear SVM first; add LightGBM and a compact transformer only if budget permits.
4. Measure legitimate human vs legitimate AI false-positive rates at fixed validation-selected thresholds (1%/5% FPR targets if adequate controls).
5. Evaluate original vs LLM-rewritten phishing on ancestry-safe paired samples, reporting metadata/semantic uncertainty.
6. Evaluate held-out source generalization, calibration (Brier/ECE), risk–coverage, and confidence intervals. Never tune on final test.
7. Write paper from verified results. Negative results are acceptable; do not invent metrics or claim novelty in deduplication alone.

## Data safety and output retention
Commit to public GitHub: notebook source when output-stripped, executed **aggregate-only** reports, input/output SHA256 manifests, experimental protocol, limitations, synthetic tests, and reproducible decisions.
Never commit: raw messages, live links, private 142-pair panel, full-text reviewer-aid CSV, per-row judgment joined to raw text, personal addresses or other restricted derivatives. Keep these in authorized private storage. GitHub .gitignore alone does not sanitize a file.

## Previous baseline distinction
Legacy `src/baseline.py` predicts AI-vs-human **within phishing-only data** and cannot establish AI-written benign false-positive rates.

## Evidence pointers
- https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/docs/RESEARCH_BLUEPRINT.md
- https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/data/audit/readiness/D1_D5_rights_labels_D2_D3_lineage_2026-10-31.md
- https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/results/04_Global_Lineage/v1_2/README.md

This is a preregistered *plan*, not a report of executed phishing model experiments.
