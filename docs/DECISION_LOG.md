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
