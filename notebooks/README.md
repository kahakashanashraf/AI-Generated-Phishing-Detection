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

## Committed execution evidence (aggregate only)

- **Notebook 01 v1.1** — [full privacy-safe aggregate JSON](results/01_D1/d1_aggregate_report.json), [Kaggle summary TXT](results/01_D1/d1_aggregate_report.txt), and [provenance/rights gate receipt](results/01_D1/README.md).
- Executed notebook source, SHA256 fingerprints and output totals were checked against the uploaded 2026-10-31 run. These files contain **aggregate metadata only**, not raw third-party emails or per-record data.
- **Notebook 02** — [verified aggregate evidence and exact environment/resource/manifest files](results/02_D2_D5/README.md) committed after user-provided Kaggle execution. Full raw source emails and private per-record information remain excluded.

## Notebook 03 v1.2 final descriptive verification & Notebook 04 handoff (2026-10-31)

- User-submitted **N03 v1.2 Kaggle run** reviewed: all 6/6 SHA256-pinned inputs verified; 29,025 joins, 0 unmatched; 142 private review candidates. **0 completed independent human annotations**. Compared to v1.1, structural count and security-cue totals are unchanged. The updated reviewer panel includes security metadata; only the code and aggregate size are observable (the private panel is not part of the shared ZIP). [All five byte-identical safe outputs, environment/resource metadata and original artifact SHA256](results/03_Pairs/v1_2/README.md) committed.
- **Notebook 03 automatic structural audit: FINAL GO, no further rerun needed.** M2 human-adjudicated pair gold, label truth and rights remain **NO-GO/PENDING**. The `/kaggle/temp` private reviewer panel is ephemeral; independent reviewers need an authorized persistent private workflow.
- **Notebook 04:** [13-source global normalized-text / parent-lineage overlap audit](04_Global_Lineage_and_Frozen_Splits.ipynb) v1.2 prepared as the next CPU Run All. It deliberately **does not freeze train/test splits** while research rights, labels, paired semantic validity and the independent holdout design are pending. This is an early descriptive M3 preflight, **not M3 complete**. Notebook 04 has been pushed but is **not yet Kaggle-executed**.

## Notebook 03 status (2026-10-31)

**Executed v1.1:** [original safe results, source SHA256, environment/resource reports](results/03_Pairs/README.md) — all five aggregate outputs preserved **byte-identically** from the uploaded ZIP. Six verified sources; 29,025 structural candidate pairs; no unmatched variants; 142 pilot review candidates. **Descriptive structural GO, scientific M2 paired-gold NO-GO** because no independent human judgments yet.

**HIGH review-sheet problem corrected in [Notebook 03 v1.2](03_Pair_and_Security_Counterfactual_Review.ipynb):** Private review panel now includes original/variant sender, explicit URL, attachment, source and year (in addition to subject/body); stable v1.1 review IDs; idempotent decision-template preservation; optional private completed-decisions input; two-reviewer agreement/adjudication validation. The v1.2 notebook is pushed but **has not yet been run on Kaggle**. Do not mark M2 complete or create frozen research splits until provenance, label and pair approval requirements pass. Private panel contents must never enter public GitHub/Kaggle outputs.

## External rights/labels audit — completed without another Kaggle rerun (2026-10-31)

- [D1–D5 source rights, label definitions and D2→D3 row-ID inheritance audit](../data/audit/readiness/D1_D5_rights_labels_D2_D3_lineage_2026-10-31.md) and [machine-readable conservative source label/gate policy](../data/audit/readiness/source_label_gate_v1.json) are committed. This resolves the mysterious D2 35 class values as **`Phishing Simulation`**, not bad/missing data.
- Direct pinned-source inspection proves that **all 3,075 D2 original `No.` IDs recur in the 3,300 D3 seeds**; 2,971 same-ID texts unchanged, 104 altered. D3 adds 225 other IDs (74 Spam, 151 Valid; zero new Phishing labels). There are **35 `Phishing Simulation→Phishing`** D2→D3 category remaps and **one `Valid→Phishing`** conflict by the original ID. This is **not an independent cross-corpus data source**.
- D1 Zenodo catalog reports CC BY 4.0, D4 card declares Apache-2.0, D5 record states data CC BY 4.0/code MIT. **D2 and D3 public GitHub repositories have no discovered explicit LICENSE file/GitHub-declared license**: public download does not establish broad redistribution or unrestricted use rights. D1 original spam-vs-ham sources need careful source-label handling; downstream strict-phishing binary mapping remains scientifically unresolved.
- **No extra Notebook 04B run is needed merely to identify the 35 labels or the D2→D3 derived ID structure.** These checks were completed directly from the pinned public files. Remaining steps require real human review and rights/provenance judgments; future baseline training is gated and not authorized yet.

## Notebook 04 — Final executed descriptive audit (2026-10-31)

- **N04 v1.2 executed** on Kaggle; **13/13 verified SHA256-pinned inputs**, 121,536 source-file rows, 85,721 candidate components, 4,838 multi-source-file components, 3,018 cross-family components; one candidate D2/D3 three-class text-label conflict. CPU 174.18 s; peak RSS 653.22 MB; download 242,291,702 B.
- **Critical overlap:** D2 original ↔ D3 seeds = **2,896 identical normalized text keys** / 3,000 unique original D2 text keys = **96.53%**. A naive leave-D3-out evaluation after D2 training is **not an independent corpus test**.
- **Full exact reports**: [lineage audit JSON (13 sources/78 pairs)](results/04_Global_Lineage/v1_2/lineage_audit.json), [environment](results/04_Global_Lineage/v1_2/environment.json), [resource](results/04_Global_Lineage/v1_2/resource_usage.json), [manifest](results/04_Global_Lineage/v1_2/run_manifest.json), [summary](results/04_Global_Lineage/v1_2/summary.txt). All five have Git blob fingerprints identical to the user-uploaded ZIP members. [Execution and SHA256 receipt](results/04_Global_Lineage/v1_2/README.md) and [canonical lineage research receipt](../data/audit/lineage/D1_D4_global_overlap_2026-10-31.md).
- **N04 v1.3 source-only bugfix:** [current code](04_Global_Lineage_and_Frozen_Splits.ipynb) suppresses misleading components if any input scan fails mid-file, and separates observed input SHA256 from expected fingerprints. Synthetic PASS, transitive-union PASS, explicit injected malformed CSV fail-closed PASS. **v1.3 was not run on Kaggle**; the successful v1.2 execution remains the evidence. **No N04 re-run needed**.
- **Gate:** Descriptive global-overlap audit GO. **Frozen split NO-GO / binary model training NO-GO.** Before Notebook 05 can train, obtain source-rights/label-ground-truth approval, a private two-reviewer semantic pilot (142 N03 candidates currently unreviewed), and a frozen leak-free manifest with explicit source/campaign/parent controls. Do not equate the completed audit to scientific M3 completion.

## Execution log

- **Notebook 01 FINAL GO (descriptive only):** User-provided executed **v1.1** Kaggle notebook and aggregate results ZIP independently inspected 2026-10-31. Five of five published-MD5-pinned D1 CSVs scanned, 79,360 source rows (not independent/unique), all files `PASS_DESCRIPTIVE`, synthetic self-test `PASS`. Normalized subject/body overlap: Nazario ↔ Nazario_5 **1,552 keys / 1,565 rows on each side**; Nazario_5 ↔ SpamAssasin **239 keys**, Nazario_5 ↔ CEAS_08 **298 keys**, SpamAssasin ↔ Enron **2 keys**. Private review queue bug corrected to **1-based CSV data-record index**; isolated multiline CSV test PASS (second record begins on physical line four). Execution output matches corrected v1.1 release; safe results ZIP contains only aggregate JSON/TXT. For reproducibility, provided-run artifact SHA256: notebook `133fc513db82bd710afdccfd300f7ddb2d681c2d5e6f8b6f55498d7314a9691e`; results ZIP `fdd301efdee9faf577892735c32bf5f31e5d682375c9ecb274bc11a7c9f15fa4`; aggregate JSON `71fc63aea2d8663344b9f78e8c40190a3a61d6400c788b2782619e3ca4cb6c56`. **No further Notebook 01 rerun required. Training/rights/labels/parent-safe split gates remain NO-GO/PENDING; manual candidate adjudication remains outstanding.**
- **Notebook 02 descriptive GO (2026-10-31):** User-provided executed Notebook 02 and result ZIP reviewed. D2 5/5, D3 2/2, D4 2/2 and D5 1/1 source files PASS_DESCRIPTIVE; 10/10 complete. D2 original + 3 rewrite files each have 3,075 rows, while its categorized file has 12,300 including all four groups; D3 3,300 parents and 19,800 child variants (6 per Original_ID); D4 6,776 rows total; D5 9,986 authorship-related examples plus ZIP analyses. The ZIP's resource JSON reports 22.442 seconds / 588.66 MB peak RSS / 134,216,458 bytes downloaded; the saved notebook console instead reports 12.879 seconds / 589.16 MB, so **these execution timings are not from one identical snapshot**. [Verified privacy-safe summary and source SHA256](results/02_D2_D5/d2_d5_verified_summary.json), [environment](results/02_D2_D5/environment.json), [resource](results/02_D2_D5/resource_usage.json), [manifest](results/02_D2_D5/run_manifest.json) and [summary](results/02_D2_D5/summary.txt) committed. The four original execution output files are byte-identical to the attached ZIP members; the larger aggregate report is preserved as a reviewed derivative and its original SHA256 recorded. Scientific license, label, parent/generator ancestry, and secure binary training gates remain NO-GO/PENDING.
- **Notebook 03:** v1.1 and corrected v1.2 **both executed; structural GO** (6/6 sources, 29,025 candidate matches). [v1.2 exact executed aggregate evidence](results/03_Pairs/v1_2/README.md). **Human-review gold 0/142 remains PENDING**. Notebook 04 global overlap preflight may proceed; frozen splits remain blocked.

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
