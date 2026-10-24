# Preregistered benchmark protocol v0.1

**Primary benchmark:** among *known phishing emails*, distinguish machine-generated (origin=ai) versus human-written (origin=human). This is **authorship attribution**, NOT phishing-vs-benign detection. The first runnable baseline implements only this task.

**Secondary benchmark (blocked):** phishing-vs-legitimate detection across human/AI provenance requires genuinely labeled legitimate AI emails; do not re-label arbitrary AI prose as legitimate email.

## Required manifest
CSV fields: `text,label,generator,source,group_id`.
- label: 1=AI-generated phishing, 0=human-written phishing.
- generator: exact generator/checkpoint for AI samples; `human` for human samples.
- source: original corpus/source ID.
- group_id: shared ancestor/template/campaign ID; every derivative and paraphrase uses its parent's ID.
- Deidentify raw bodies. Never place raw private messages in Git.

## Train/validation/test
- Declare held-out generator BEFORE fitting or selecting hyperparameters.
- Remove all held-out generator samples from training and validation.
- Group split remaining seen-generator and human samples into train/validation and *human control test*. Held-out generator forms AI test. Ensure no group_id crosses any boundary.
- Tune TF-IDF vectorizer, model, threshold, calibration only on train or validation. Never on held-out generator.
- Compare (a) frozen global threshold from validation, (b) 0.5 default, (c) explicitly labeled few-shot target recalibration as a **separate** adaptation experiment with disjoint target test.
- For group-held-out evaluation, measure class balance carefully; split count and source composition must be printed. Do not silently choose a seed that yields favorable results.
- Never claim source-independent robustness unless entire source corpora are held out.

## Reporting
At minimum: support per class; confusion matrix; precision, recall, F1, balanced accuracy, AUROC, average precision; false positive rate at the frozen threshold; generator-wise breakdown; bootstrap grouped 95% CI where sufficient groups exist; calibration ECE and Brier with class prevalence. Compare training + inference resource demands on actual hardware.

## Ablations
TF-IDF+LR baseline -> stylometry-only -> optional lightweight transformer -> optional combination -> calibration/abstention. Feature extraction and selection MUST be fit on training fold alone.

## GO / NO-GO
NO-GO for paper claim if duplicate or parent leakage, unverifiable labels, unknown provenance, unseen-generator test labels used for calibration, or missing human-control test.
