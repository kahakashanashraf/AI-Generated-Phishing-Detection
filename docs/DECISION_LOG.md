# Research Decision Log (append-only)

Every entry must include date, evidence, alternatives, decision and reason. If an earlier choice changes, ADD a new decision rather than silently rewriting history.

## D001 — 2026-10-24 — Freeze primary task
**Decision:** Main task is phishing vs legitimate email. `src/baseline.py` currently predicts AI-vs-human origin among phishing-only samples, an **auxiliary separate task**. Do NOT report its outputs as phishing-detection results. Spam must remain distinct until a policy is written.
**Evidence:** https://doi.org/10.3389/fdata.2026.1883452 (phishing-only authorship data).
**Status:** ACTIVE, labels require data audit.

## D002 — 2026-10-24 — Conditional novelty
**Decision:** Hypothesize that *verified style-preserving invariance + verified security-changing sensitivity*, along with generator/corpus joint-shift and risk-constrained deployment evaluation, improves on strong baseline controls.
**Reason:** Simple unseen LLM detection, stylistic cues, rephrasing and calibration have already been studied.
**Counterevidence checks:** https://doi.org/10.1109/CARS67163.2025.11337548 ; https://github.com/DataPhish/PhishFuzzer
**Status:** CONDITIONAL, NOT DEMONSTRATED. A consistency loss alone is not claimed as novel.

## D003 — 2026-10-24 — Dataset roles
**Decision:** D1 Zenodo 8339691 baseline/held-out corpus; D2 HarmJ0y human/AI original+rewrite and conditional generator test; D3 PhishFuzzer parent-linked robustness; D4 LLMGen synthetic auxiliary only; D5 Zenodo 20250116 authorship replication only.
**Status:** ALL CANDIDATES awaiting per-source rights, records, hashes and labels.
**Details:** [Dataset Playbook](DATASET_PLAYBOOK.md).

## D004 — 2026-10-24 — Scientific fail-closed policy
**Decision:** If a security-changing pair is not genuinely adjudicated or a held-out generator ID is unknown, report missing evidence, omit affected claim, and stop the corresponding experiment. Never use target-test labels to tune a zero-shot model.
**Status:** ACTIVE.

## D005 — 2026-10-24 — First-time researcher workflow
**Decision:** Work one linked GitHub issue at a time. For a task to be `[x]`, supply artifact, actual validation result, run/checksum/commit link and GO decision. `ROADMAP.md` milestone tick is set only after its issue is fully complete and closed.
**Status:** ACTIVE.

## Example evidence append
```
## D006 — YYYY-MM-DD — Short decision
Task/issue:
Options:
Evidence URLs, dataset revision/sha256, experiment split hash:
What was observed (include failure):
Decision and scope:
Consequence and next item:
```

## D006 — 2026-10-24 — Journal target changed to PLOS ONE
**Decision:** Primary submission target changed from IEEE Access to PLOS ONE at the user's explicit direction. All data/provenance, research questions, related-paper evidence, and statistical standards remain unchanged. PLOS uses scientific rigor over subjective perceived novelty but still requires original research.
**Policy sources:** https://journals.plos.org/plosone/s/criteria-for-publication ; https://journals.plos.org/plosone/s/submission-guidelines ; https://journals.plos.org/plosone/s/data-availability ; https://journals.plos.org/plosone/s/latex .
**New blocking requirement:** Share/recreate the minimal necessary data under third-party license/privacy rules and accessible code; use the current PLOS Vancouver bibliographic template instead of IEEEtran. See [PLOS ONE plan](PLOS_ONE_TARGET.md).
**Status:** TARGET SELECTED; feasibility contingent on data reuse rights and ethical compliance. No claim of submission or acceptance.

## D007 — 2026-11-26 — Reframe the paper: benign-side false alarms, AI style vs source shift
**Evidence:** Study 1 aggregates. D2 paraphrase changed at most 1 of 142 legitimate decisions (`phishing_n10_safe/table02_paired_exact_tests.csv`). Legitimate FPR on E-PhishLLM-EN is 77–97% at τ5 (`phishing_n08_safe`, `phishing_n12_safe`). The 2024–2026 literature was re-searched and verified ([paper/LITERATURE_2024_2026.md](../paper/LITERATURE_2024_2026.md)).
**Options:**
- (a) Keep "security-sensitive invariance learning". Blocked by G2 (no adjudicated security-changing pairs) and by heavy prior art.
- (b) Reframe as a pre-registered factorial study of false alarms on AI-written legitimate email, separating paraphrase style, AI-authored content and source shift, with two-sided mitigation accounting.
**Decision:** (b). Plan: [GAP_ANALYSIS_AND_PLAN_2026-11-26.md](GAP_ANALYSIS_AND_PLAN_2026-11-26.md). Protocol: [PREREGISTRATION_V2.md](PREREGISTRATION_V2.md).
**Status:** ACTIVE once the owner approves the pre-registration.

## D008 — 2026-11-26 — E-PhishLLM demoted to development; new locked tests
**Reason:** E-PhishLLM outcomes were inspected before N11–N14 were designed, so they cannot provide confirmatory evidence.
**Decision:** E-PhishLLM-EN becomes DEV only. Confirmatory cells are:
- LLMGen-EN (rev `d717e54`, schema audited, never scored);
- newly generated paired rewrites and subject-matched from-scratch emails of decontaminated Enron ham and late Nazario;
- the frozen N05 D2 test.
None of these may be scored before N20.
**Status:** ACTIVE.

## D009 — 2026-11-26 — PROPOSED: release per-row predictions without text
**Reason:** PLOS ONE expects the minimal data behind every reported number. Paired model comparisons need per-row decisions. Study 1 could not run them because only aggregates were kept.
**Proposal:** Publicly release per-row predictions keyed by pseudonymous sample IDs that are derivable from the public source datasets. Fields: cell, generator, label, score, decision. No subject, body, URL, sender or other text. Raw and generated text stays private.
**Status:** PENDING owner approval. Until approved, keep per-row predictions private.

## D010 — 2026-11-26 — Pre-registration v2.1 frozen; Study 2 execution started
**Trigger:** the owner instructed us to run the actual experiments for the journal.
**Frozen:** `docs/PREREGISTRATION_V2.md` v2.1 at commit `a17a7206fc86883023607438265ae897dd600bba`. v2.1 adds:
- graded AI-assistance L0–L4 with a primary trend endpoint PE0;
- Nazario 2022 (EXT-phish-H) and 2023–2025 (MODERN-phish), CC BY 4.0;
- Greco24 LLM-legitimate as a locked set;
- Clinton FOIA as EXT2;
- IN-cell decontamination (N13 found 12 near-copies) and within-cell de-duplication.

**Started:** N15 (`notebooks/15_Data_Freeze_v2_Sources_Decontamination_Locked_Cells.ipynb`, commit `03c7439`), using the phishbench library (21 unit tests). From now on, every change to the protocol is a dated deviation in §9 of the pre-registration.
**Still pending:** D009 (public per-row predictions without text) and the choice of submission route (Registered Report or Research Article).

## D011 — 2026-11-26 — N15 run 1 superseded (Greco24 parsing bug); N15 re-run
**Run 1:** Kaggle kernel `ddipra/15-data-freeze-v2` version 1, phishbench@a17a720, runtime 436 s. All 7 gates PASSED.
- Cells: IN 139 legitimate and 147 phishing (18 test groups removed as linked to training); EXT 1,000; EXT2 500; EXT-phish-H 142; MODERN 970; LLMGen 1,269 / 2,477; DEV 5,506 / 5,996; R2 extra 6,529 train and 726 validation.
- **Defect:** Greco24-phish had only 102 usable records with a median of 3 words, because the source CSV is unquoted (deviation 4).

**Also observed:** many D2-provided rewrites are near-copies of their parents (cross-cell near-duplicates: randomapi 74 and DeepSeek 60 of 139 legitimate, against GPT-4o 14). This is a plausible contributor to Study 1's paraphrase null. Deviation 5 adds a manipulation check.
**Action:** fixed the loader and added a unit test, then re-ran N15 (version 2). Only run 2 outputs are committed.

## D012 — 2026-11-26 — Owner decisions: Research Article route; D009 approved
- **Submission route:** a PLOS ONE **Research Article** (Route B). Study 2 runs to completion before submission. The frozen pre-registration (commit `a17a720`) is cited, and an OSF registration of the frozen file is recommended before N20.
- **D009 approved.** Per-row predictions will be released publicly. Each row carries the pseudonymous sample ID (derivable from the public sources), cell, generator, level, label, score and decision, with **no** subject, body, URL, sender or other text. Raw and generated text stays private. The legitimate-only generated benchmark text (C1) is released separately, after a PII check, because its parents are already-public Enron or D2 emails. Generated *phishing* text is never released.
- **Kaggle visibility of Study 1.** N05–N14 ran on GitHub Actions, and N01–N04 ran in the owner's own Kaggle session. They will be re-executed on Kaggle during the N23 reproducibility audit, and their aggregates compared byte for byte with the committed CSVs.

## D013 — 2026-11-26 — One organised Kaggle suite in one pinned environment
**Owner request:** run everything, Study 1 included, on Kaggle in the same environment, merging notebooks where possible.
**Decision:**
- All experiments run as Kaggle kernels on one pinned GPU image (`kaggle-private-byod/python@sha256:fc720c15…`, T4×2, pinning "original"). That includes the CPU-only steps, so the environment is identical everywhere.
- The v1 notebooks are archived in `notebooks/archive_v1/`, and the GitHub Actions experiment workflows are disabled. Only unit tests and the LaTeX CI remain.
- New suite: 01 (data audit plus locked cells; merges v1 01–04 and N15), 02 (Study 1 re-execution), 03 (generation), 04 (validation), 05 (training), 06 (judge), 07 (confirmatory evaluation), 08 (paper package).
- The pre-registration's N17–N23 map to 04–08. This is renumbering only, with no protocol change.
- Study 1 results re-executed in the unified image become the canonical Study 1 numbers. Differences from the GitHub Actions originals are reported in `results/02_study1/reproduction_report.csv`.

## D014 — 2026-11-26 — Notebook 04 (human validation) as two kernels; deviation 9
- **`04-human-validation-kit`** runs as soon as the Qwen and Phi generations complete. It draws the §3.5 sample and writes one private workbook per rater, plus a private key whose SHA-256 is committed.
- **`04-human-validation-score`** runs only after both raters' answers (`rater_A.csv`, `rater_B.csv`, without text) and the adjudication file are committed. It reports κ, Gwet's AC1, the preservation rates and the §3.5 decision per generator.
- **What the pipeline does:** it starts 04-score automatically once those three files are tracked in git.
- **What 08 does:** it reads `decisions.json` to mark any generator below 90% label preservation as sensitivity-only in the paper tables.
- **Owner actions before rating:**
  - Confirm the institution's policy on author annotation (§8).
  - Name the second rater.
  - Follow `docs/HUMAN_VALIDATION_PROTOCOL.md`.

## D015 — 2026-11-26 — Team of three authors, no institution: ethics route and rater roles (deviation 10)
- **Team.** The study is run by three authors as team research, with no institutional affiliation or IRB.
- **Ethics.** There are no human participants: the raters are authors rating text. The manuscript's Ethics Statement explains why no approval was needed and gives the privacy assessment for the third-party email datasets. A draft is in `paper/ETHICS_AND_DECLARATIONS.md`.
- **To do before submission:** email PLOS ONE staff to confirm (a) the ethics route and (b) the affiliation line for authors without an institution. Record the reply here.
- **Human validation roles.** Two authors rate (A and B) and the third coordinates and adjudicates last. Names go only into the manuscript's CRediT statement. Owner to confirm who takes which role.

**D015 update (2026-11-26): roles confirmed by the owner.**
- **Rater A:** Dipra Das. **Rater B:** Amit Dasgupta. **Coordinator:** the repository owner. The coordinator runs the pipeline, holds the private folder, hands out the workbooks, runs the extraction and is adjudicator of last resort.
- **Blinding caveat.** The draw is deterministic from public code, a public seed and Kaggle inputs. Blinding therefore rests on procedure, not secrecy. The Kaggle account that runs the kernels is accessible to a rater. Each rater therefore must not:
  - open the outputs of the `04-human-validation-*` kernels on Kaggle;
  - open `key.csv`;
  - run or inspect the sampling code on the real inputs.
- **Attestation.** When the ratings are committed, each rater adds a dated one-line confirmation of this, and of independent rating, below this entry.

## D016 — 2026-11-26 — 02 (Study 1 re-execution) finished with one gate failure: explained, results committed
- **Gate.** `no_shape_or_column_changes` failed. The cause is environmental, not a defect:
  - LightGBM is installed in the unified Kaggle image but was skipped on GitHub Actions ("not-installed: SKIPPED"), so N07, N08 and N10 gained `word_lgb` rows.
  - All original rows reproduce to ≤ 6e-16.
- **Other differences.**
  - N11: ≤ 0.71 pp, from platform floating-point in logistic regression on augmented sets.
  - N12: DistilBERT ≤ 3.5 pp FPR, GPU versus CPU, single seed.
- **Handling.**
  - The gate was not changed after the fact, and the kernel was not re-run. The failure and its explanation are documented in `results/02_study1/REPRODUCTION_NOTE.md`.
  - The safe outputs were committed by hand, because the pipeline commits only COMPLETED runs.
  - Per D013, these are the canonical Study 1 numbers.

## D017 — 2026-11-27 — Qwen generation accepted; Phi re-run in float16 (deviation 12)

**Qwen2.5-7B** (kernel `03-generation-qwen2-5-7b`, 24,563 s):
- 4,364 of 4,845 tasks kept.
- A builder-level gate (kept ≥ 0.80 per cell), which is not in §3.4, failed in four cells. The worst is IN-phish-L3 at 0.327: 51 length-ratio and 46 placeholder exclusions.
- The outputs are accepted as produced and frozen as a private dataset with content hashes.

**Manipulation check (deviation 5), Qwen, EXT median cosine:**

| Level | Median cosine |
|---|---|
| L1 | 0.991 |
| L2 | 0.952 |
| L3 | 0.976 |
| L4 | 0.545 |

- L2 changed the text more than L3 (Jaccard medians 0.086 and 0.141).
- The nominal dose order is therefore not monotone between L2 and L3 for this generator. This is reported descriptively, as deviation 5 anticipated.
- PE0 stays as pre-registered, ordinal L0–L4. A measured-distance analysis may be added only as clearly labelled exploratory.

**Phi-3.5-mini:** the float32 run hit Kaggle's 12-hour limit at 3,725 of 4,845 tasks and saved no outputs. It is re-run in float16 with a larger KV budget and a time guard.

**Pipeline:**
- Qwen is marked done.
- Downstream steps read Qwen from the dataset `ddipra/phishbench-03-qwen2-5-7b-outputs`.
- The runner gained a heartbeat lock, so two runners never act at once, and it logs any crash to `pipeline.log`. It still runs inside the coordinator's editor session. If that session closes, restarting the runner resumes from the saved state, and Kaggle kernels keep running in the meantime.

## D018 — 2026-11-27 — GPU quota: CPU-only steps move to CPU sessions with the same image; GPU steps sequenced
- **Situation.** The owner reported 8 GPU hours left in this week's Kaggle quota.
- **Probe.** A private probe kernel (`zz-cpu-image-probe`) ran in a CPU session with the same pinned image. It reported the identical image digest (`fc720c15…`), Python 3.13.16, scikit-learn 1.6.1, transformers 5.20.2 and torch 2.11.0+cu130, with CUDA unavailable.
- **Decision.** 04 (kit and score), 05-classical and 07 never use a GPU, so they now run in CPU sessions:
  - `enable_gpu: false`, with the same `docker_image` pin;
  - this uses no GPU quota and does not count against the 2 GPU slots.
  - The single-environment principle (D013) holds, because only the hardware differs, and none of these steps uses a GPU.
- **Sequencing.**
  - Phi (test generator, on the critical path to human validation) keeps the GPU.
  - OLMo was cancelled by the owner and is held, together with 06 and 05-transformers, until the weekly quota resets.
  - 04-kit runs on CPU as soon as Phi completes.

## D019 — 2026-11-27 — 05-transformers runs as two kernels (same pre-registered plan)
- **Estimate.** The transformer plan is 40 models: D4 2 configurations × 5 seeds, and D5 6 configurations × 5 seeds. Each model scores every cell. The estimate is about 8–9 hours, too close to Kaggle's 12-hour session limit, which already cost one Phi run.
- **Decision.** Two shards, each kept well inside the limit:
  - `transformers-a`: D4 R1 and R2, and D5 R1 and R2.
  - `transformers-b`: D5 M1, M2, M4 and M5.
- **Safeguards.**
  - Each configuration keeps all five seeds inside one shard, so the five-seed ensembles are unchanged.
  - The notebook asserts that the shards cover the pre-registered plan exactly once.
  - 07 already reads every seal manifest and registry it finds.
- **What does not change:** no model, hyperparameter, seed or endpoint.

## D020 — 2026-11-27 — 07 waits for human validation (deviation 13)
- **Order.** The pipeline makes 07 depend on 04-score. The confirmatory run therefore happens once, after both raters' adjudicated answers and the §3.5 decisions are committed.
- **Dry runs.**
  - When both generators pass, the output has primary rows only.
  - When Phi fails, the primary analysis pools only Qwen's RW cells, and a full-generator sensitivity set is written alongside.

**D015 update (2026-11-27): affiliation.**
- **Owner decision:** the paper is submitted from **EliteLab**.
- **The three authors:**
  - are each students at a university;
  - did not do the study under any university supervisor;
  - did not use any university resources; all computing was on Kaggle.
- **Affiliation line:** "EliteLab, City, Country" for every author.
- **University affiliations:** listed only where that university's policy allows it.
- **Pending:** PLOS ONE staff are to confirm both the ethics route and the affiliation before submission. The draft email is held by the coordinator.

**D015 update (2026-11-27): author list.**
- **Order given by the owner:**
  1. Dipra Das
  2. [name to come]
  3. Kahakashan Ashraf
  4. [name to come]
  5. Md Kishor Morol
  6. Tze Hui Liew
- **Human-validation roles are unchanged:** rater A Dipra Das, rater B Amit Dasgupta, coordinator Kahakashan Ashraf.
- **If any author is a university supervisor,** the affiliation and ethics route of deviation 10 should be re-checked before the human rating starts.
- **Release metadata:** `CITATION.cff` and `.zenodo.json` hold the list. `scripts/check_release_metadata.py` blocks a release while any name is a placeholder.
- **Licences:** code is MIT (`LICENSE`). Results and documents are CC BY 4.0 (`LICENSE-CC-BY-4.0.md`). The authors can still change either before the first Zenodo release.

## D021 — 2026-11-28 — Phi continued, OLMo re-run (deviation 14)
- **Phi run 1:** `PARTIAL_TIME_LIMIT` at 10.5 h.
  - Kept 2,915 of 4,845. The rest were 766 not run, 374 `oom` caused by a recovery bug, and §3.4 exclusions.
  - **Early quality signal (descriptive):** Phi's L2 polish often changes length beyond the 0.5–2.0 ratio (223 cases), and its L3 rewrite often drops or alters placeholders (360 cases). Attrition will be reported in full (deviation 12).
- **Continuation:** `03-generation-phi-3-5-mini-cont` generates only the 1,140 technically failed tasks and merges the result with run 1. The fixed OLMo run starts once the owner has cancelled the buggy version 2.
- **Runner:** a pending step whose kernel still runs from an older push now waits (`adopt: false`) instead of adopting it.
- **Lesson:** the editor session ended twice while kernels were running, and nothing was collected in the meantime. The coordinator keeps the session open; on return, the runner resumes from its saved state.

**D015 update (2026-11-28): author order confirmed.**
1. Dipra Das
2. Johora Bibi Juhi
3. Kahakashan Ashraf
4. Amit Dasgupta
5. Md Kishor Morol
6. Tze Hui Liew

`CITATION.cff` and `.zenodo.json` are complete, and `scripts/check_release_metadata.py` passes.

**D015 update (2026-11-28): roles reassigned before any rating.**
- **Human validation:**
  - Rater A: Dipra Das.
  - Rater B: **Johora Bibi Juhi**.
  - Coordinator: Kahakashan Ashraf.
- **Amit Dasgupta** reviews the writing and helps with the literature search. He no longer rates.
- **Why this is safe:** no workbook has been issued yet, so the change cannot affect any rating.
- **Attestation:** the blinding rules and the attestation (D015) now apply to Dipra Das and Johora Bibi Juhi.

## D022 — 2026-11-28 — Clean-up of superseded Kaggle runs
- **Owner request:** remove superseded or buggy runs on Kaggle and in git.
- **Kaggle:**
  - Deleted the one-off probe kernel `zz-cpu-image-probe`, after committing its output to `results/00_environment/`.
  - Kaggle refused to delete individual notebook versions ("Deleting individual kernel versions is not supported"). Deleting a whole kernel would also delete the versions the study uses, so the superseded versions stay inside their notebooks:
    - 01 v1;
    - 02 v1 and v2;
    - Phi v1, the float32 run;
    - OLMo v1 and v2.
  - These kernels are private, and their history agrees with the deviation log.
- **Git:** history is not rewritten. Every pushed notebook pins its code commit, and 08 audits rebuilds against those commits, so rewriting history would break reproducibility. Superseded result folders, such as `results/03_generation/phi-3.5-mini-run1-partial/`, are kept on purpose because they document deviation 14.
## D023 — 2026-11-28 — Protocol snapshot archived on Zenodo (replaces OSF)
- **Record.** GitHub release `v0.1-protocol` was archived by Zenodo as **10.5281/zenodo.24627573** (concept DOI 10.5281/zenodo.24627572). It was created on 2026-11-28 at 12:39:13 UTC.
- **What the record holds:** six creators in the confirmed order, the MIT licence, and a single 1.8 MB repository archive.
- **Timing.** The snapshot predates every detector training and scoring run (05, 06) and the confirmatory evaluation (07). It is therefore the independent timestamp of the frozen protocol (v2.1) and deviations 1–14.
- **OSF.** The owners chose Zenodo instead of OSF, which PLOS ONE does not require for this study type.
- **Final package.** It will be a new version under the same concept DOI.

## D024 — 2026-11-28 — Owner chose two free exploratory extensions (deviation 15)
- **Choice.** Asked about free ways to pre-empt reviewer criticism, the owner chose:
  - **E1:** newer human email from Apache mailing lists, 2019–2022.
  - **E2:** Qwen2.5-14B in 4-bit, to test scale.
- **Rejected:** the Gemini free API. On the unpaid tier, submitted content may be used for product improvement and read by human reviewers, which conflicts with the privacy assessment. It is also not reproducible.
- **Timing.**
  - 05 and 06 are held, so that all cells are scored in one sealed run.
  - Phi continuation, OLMo and 04 continue.
  - A delay of a few weeks is acceptable to the owner.
- **Recommended:** a Zenodo release `v0.2-extensions` before the E1 data are collected, so that this pre-specification is timestamped independently.
## D025 — 2026-11-28 — Deviation 15: implementation notes, fixed before any extension data are collected
- **Automated-sender filter.** It matches whole words: jira, git or github, bot, commits; and substrings: notification, noreply / no-reply, jenkins, buildbot. Real names such as "Brigitte" are therefore not excluded.
  - Lists append their own footer ("To unsubscribe…"). The sender did not write it, so it is stripped before any filter runs.
- **Draw in two stages.**
  1. Per list: filters, decontamination and within-list near-duplicate removal, capped at 60.
  2. Across lists: near duplicates (for example, cross-posted announcements) are removed and the seeded n = 500 is drawn.
- **E2 package.** The pinned image lacks bitsandbytes (checked with a CPU probe kernel), so the E2 kernel alone installs `bitsandbytes==0.50.2` (released 2026-08-27) and records its version. No other kernel changes.
- **Verified on synthetic inputs before release:**
  - 01b, run on two real months.
  - 03 in ext3 and e2 modes, with a tiny model.
  - 05 scores all seven extension cells.
  - 07 computes the 14 exploratory rows (X1a–X1c and X2a–X2c for D2 and D5).
- **Order.** 01b and the E2 generation are held until the owner's Zenodo release `v0.2-extensions` timestamps deviation 15. 05 and 06 wait for every extension cell, so all cells are scored in one sealed run.
## D026 — 2026-11-28 — Deviation 15 timestamped on Zenodo; extension hold released
- **Record.** GitHub release `v0.2-extensions` (tag at commit 4e84b32, which contains deviation 15, D024 and D025) was archived by Zenodo as **10.5281/zenodo.24629702** (same concept DOI 10.5281/zenodo.24627572). It was created on 2026-11-28 at 14:24:19 UTC.
- **What the record holds:** the same six creators, the MIT licence, and a single 1.8 MB repository archive (md5 a28af14f0e1f54d3c21dadd6f5030510).
- **Timing.** The snapshot predates the E1 data collection (01b), every extension generation run (03 ext3, 03 e2), every detector training and scoring run (05, 06) and the evaluation (07). The only earlier contact with Apache data is the API checks already disclosed in deviation 15 and D025; no message content from them enters any result.
- **Action.** The pipeline holds on `01b-ext3` and `03-e2-qwen2.5-14b` were released after this record existed.
