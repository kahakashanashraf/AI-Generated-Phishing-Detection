# Notebook suite (v2): one organised pipeline, one pinned Kaggle environment

Every notebook below runs on **Kaggle** in **one pinned GPU image**:
`gcr.io/kaggle-private-byod/python@sha256:fc720c15545eb096a510e1f085b17fc118387a007599424d953a4f327b71cacf`, T4×2, with `docker_image_pinning_type: original`.

Every notebook has the same structure:
1. **Header:** purpose, pre-registration sections, inputs, outputs, gates, hardware.
2. **PARAMETERS:** every constant in one cell.
3. **ENVIRONMENT:** clone at a pinned commit, pinned extra packages (`requirements-kaggle.txt`), version capture and assertion, determinism flags.
4. **SELF-TEST:** the `phishbench` unit tests run inside the image.
5. **Body.**
6. **Gates, privacy check and `run_manifest.json`:** parameters, environment, input and output hashes.

Notebooks are **generated** by `scripts/notebook_builders/build_XX.py`. Edit the builder, not the notebook.
Run with `scripts/kaggle_run.py` (push, wait, collect). Only `safe_XX/` folders, which are aggregates without any email text, are copied into `results/`. `private_XX/` folders stay in the private kernels.

| # | Notebook | What it does | Needs | Committed results |
|---|---|---|---|---|
| 01 | `01_Data_Sources_Audit_and_Locked_Cells` | Pinned downloads; label and lineage audit (D1 label semantics, D2 taxonomy, D2→D3 reuse); exact N05 split reproduction; R2 pool; MinHash and exact decontamination; seeded locked cells; locked manifest | internet, 2 Kaggle datasets | `results/01_data/` |
| 02 | `02_Study1_Exploratory_Reproduction` | Re-executes the frozen Study 1 notebooks (`archive_v1/10–14`) unchanged in this image, with a cell-level comparison against the GitHub Actions originals | internet | `results/02_study1/` |
| 03 | `03_Graded_AI_Assistance_Generation` (×3 kernels) | L1–L4 for Qwen2.5-7B and Phi-3.5-mini (test-only); L3/L4 training-side for OLMo-2-7B; filters; manipulation check | 01 | `results/03_generation/` |
| 04 | `04_Human_Validation` (kit and score kernels) | **kit:** blinded §3.5 sample (400 RW and 100 DN), one private workbook per rater, key hash committed. **score:** κ (plus AC1), label-preservation per generator with Wilson CI, §3.5 rule (`docs/HUMAN_VALIDATION_PROTOCOL.md`) | 01, 03; score also needs committed ratings | `results/04_human_validation/` |
| 05 | `05_Detector_Training_and_Mitigations` | D1–D5 under R1 and R2, plus M0–M5 variants; validation-only selection | 01, 03 | `results/05_training/` |
| 06 | `06_Zero_Shot_LLM_Judge` | Granite-3.1-8B zero-shot scores | 01, 03 | `results/06_judge/` |
| 07 | `07_Confirmatory_Evaluation` | **Single locked run**: PE0–PE3, H2, H4, H6; per-row predictions without text (D009) | 01, 03, 05, 06 | `results/07_confirmatory/` |
| 08 | `08_Paper_Tables_Figures_and_Reproducibility` | Paper tables and figures (TIFF), REFORMS checklist, Zenodo package, clean-clone audit | all | `results/08_paper/` |

## Mapping from the archived v1 notebooks (`archive_v1/`)

| v1 | Now |
|---|---|
| 01–04 (D1 intake, D2–D5 provenance, pair review, global lineage) | merged into **01**. The pair-review panel (old 03) belongs to the abandoned v1 design |
| 05–10 (Study 1 benchmark; 10 is cumulative), 11–14 (augmentation, DistilBERT, diagnostics, consistency) | re-executed unchanged by **02** |
| 15 (data freeze v2) | merged into **01**, which produces identical locked cells (D011) |
| 16 (generation) | **03** |
| planned N17–N23 in the pre-registration | 04–08 (renumbered only, no protocol change; DECISION_LOG D013) |
