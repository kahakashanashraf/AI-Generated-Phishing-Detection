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
