# End-to-end Kaggle notebook program (2026-10-31)

One notebook = one research milestone. Start with Notebook 01 and do not proceed to a downstream notebook when its scientific gate fails. Notebooks produce aggregate shareable evidence, and leave raw third-party email data in private storage. The research target is phishing (1) vs legitimate (0), not AI/human authorship. Spam must not be silently mapped to either class. No result is considered executed until the user returns the Kaggle output.

| Order | Notebook | Full milestone | Gate |
|---|---|---|---|
| 01 | 01_D1_Source_Intake_and_Overlap.ipynb | Official Zenodo D1: Nazario, Nazario_5, SpamAssasin, Enron, CEAS_08; integrity, schema, class counts, duplicates, cross-file exact/normalized overlap, redacted audit report | Dataset intake only. Rights, labels, human adjudication unresolved |
| 02 | 02_D2_D5_Provenance_and_Schema.ipynb | D2 HarmJ0y, D3 PhishFuzzer, D4 LLMGen, D5 authorship-only source; schema, source rights, provenance and generator metadata audits | No invented parent or generator claims |
| 03 | 03_Pair_and_Security_Counterfactual_Review.ipynb | Original/rewrite parent verification, style-invariant vs security-changing human review panels and agreement | Human-adjudicated paired evidence required |
| 04 | 04_Global_Lineage_and_Frozen_Splits.ipynb | Global deduplication, parent/campaign-safe groups, corpus and generator coverage checks, frozen manifests and split hashes | No split if unresolved lineage or labels |
| 05 | 05_Classical_and_Transformer_Baselines.ipynb | TF-IDF/LR/SVM and compact transformer, matched splits, multiple seeds, validation-only thresholds and checkpoint receipts | Approved binary data and leakage-safe splits |
| 06 | 06_Security_Sensitive_Method_and_Ablations.ipynb | Ordinary augmentation, same-label consistency, verified opposite-label sensitivity, equal-budget ablations | Pair quality and baseline controls must pass |
| 07 | 07_Unseen_Shift_Risk_and_Statistics.ipynb | Leave-one-generator/corpus and conditional joint shifts, AI-written legitimate errors, grouped bootstrap and calibrated review-load analysis | Frozen models/thresholds only; honest conditional claims |
| 08 | 08_Paper_Tables_Figures_and_Release_Audit.ipynb | Final figures/tables, seed and CI reporting, evidence hashes, efficiency, privacy/data availability checklist | No invented paper results or unauthorized redistribution |

## Mandatory environment and resource contract — Notebooks 02–08

Every remaining notebook must be a **self-contained end-to-end milestone** with a compact environment/resource preflight and a machine-readable safe execution receipt; do not ask the researcher to run isolated cells manually. Include the following, as applicable to the workload:

1. **Environment fingerprint:** UTC execution time; Kaggle/Colab/local runtime detection; OS and kernel; Python version; exact versions of imported core packages; PyTorch/CUDA/cuDNN and driver information when available; code revision / notebook version / relevant model and data revision. Record versions as observed, never assume a specific GPU or Kaggle image.
2. **Resource inventory and fit checks:** CPU logical core count, system RAM total/available, GPU model/count, compute capability, total/free GPU memory, GPU allocation status, free and used disk space, memory/GPU suitability for the proposed workload. CPU-only stages must run without an accelerator. If GPU-dependent work cannot fit, stop or use a clearly labeled, scientifically equivalent supported fallback, not a silent change of model/protocol.
3. **Resource budgets:** Before expensive work, estimate major input sizes, model/optimizer memory, peak batch size, planned training walltime, approximate disk/checkpoint footprint and relevant Kaggle session/quota constraints *where actually available*. Track actual per-phase elapsed time, peak RSS RAM, peak GPU VRAM, GPU-hours when observable, file sizes, cached artifacts, and measured throughput/latency where relevant. Do not invent quota remaining or GPU billing multiplier.
4. **Dependency/reproducibility checks:** verify imports and pinned requirements first; log platform/package versions, Python and model seeds, deterministic settings and limitations, dataset/source SHA256, split-manifest hash and source/code revision. Avoid unconditional `pip install -U`, `git pull` and unpinned package installs; do not silently switch models or data revisions. Declare any required internet access, credentials, model cache and optional libraries explicitly.
5. **Resumability:** idempotent reuse of SHA256-verified inputs and outputs, with cache invalidation on changes to scripts/config/model/transform revision; safe checkpoint writes and recovery after Kaggle session reset; never assume `/kaggle/working` survives an editing-session reset without a saved/attached controlled artifact.
6. **Integrity gates:** validate labels, schema, class coverage, split overlap, data rights/privacy and external-test isolation before model training. Fail closed on missing evidence or OOM; summarize exact reason and permitted next step. Keep results from partially completed runs clearly labeled and preserve negative outcomes.
7. **Privacy-safe reports:** create `run_manifest.json`, `environment.json`, `resource_usage.json`, `scientific_results.json` and a concise `summary.txt` as applicable. No raw private emails, active suspicious URLs, PII, passwords, tokens, per-row text hashes or adjudication content in shareable outputs, notebook stdout, public Git or published Kaggle artifacts.
8. **Final GO/NO-GO panel:** state what ran, what was skipped and why, what is verified/unverified, observed resource consumption, artifact checksums, scientific gate verdict and exactly which aggregate output the user should return.

### Notebook-specific resource expectations

| Notebook | Expected accelerator | Required resource / environment emphasis |
|---|---|---|
| 02 | CPU | Input availability, downloads with byte caps, CPU/RAM/disk footprint, archive-parsing safety, schema scans and source hashes |
| 03 | CPU | Parent-linked pair counts, bounded review sample, annotation reproducibility and private/public output separation |
| 04 | CPU | Cross-source key-memory footprint, scalable deduplication, lineage/split hash and memory use |
| 05 | CPU first; GPU for transformer | Baseline resource comparison, tokenizer truncation, training time, GPU VRAM peaks, early stopping, seeds and checkpoints |
| 06 | GPU only if fit | Matched training budgets, batch/microbatch/gradient accumulation, AMP configuration, per-run GPU-hours, ablation checkpoint integrity |
| 07 | CPU for scores; GPU only if needed | Frozen inference artifacts, per-source test volumes, group-bootstrap runtime and RAM, confidence intervals without test tuning |
| 08 | CPU | Provenance/figure/table generation, result version crosschecks, resource summary, final release/rights checks |

A notebook may skip unavailable hardware-specific metrics, but it **must report them as unavailable**, not omit or invent them. Store sensitive private artifacts separately from public aggregate reports. The user provides output from one notebook at a time; review/fix that notebook before authoring the next.

## Kaggle usage
1. Upload/open the current numbered notebook in Kaggle, use CPU for 01–04, and choose **Run All**. A single code cell performs the automated work.
2. Share **only** the generated aggregate JSON/text report or safe notebook console summary, not raw emails, per-record hashes, live phishing URLs, or private adjudication contents.
3. The next notebook is prepared only after the current output is reviewed; revise the current one when the evidence requires it.
4. If a private Kaggle Input is attached, its checksum is verified and reused. If no input is present, Notebook 01 may download only the five listed official Zenodo files to temporary runtime storage.
5. Data-intake or integrity PASS never implies license approval, trustworthy labels, or binary-model training approval.

Research controls: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/ROADMAP.md
Primary dataset source: https://zenodo.org/records/8339691
