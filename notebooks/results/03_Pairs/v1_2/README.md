# Notebook 03 v1.2 — Verified executed Kaggle evidence (2026-10-31)

**Code:** [Notebook 03](../../../03_Pair_and_Security_Counterfactual_Review.ipynb). **Run status:** `STRUCTURAL_PAIR_AUDIT_COMPLETE_HUMAN_REVIEW_PENDING`.

These five **safe aggregate files** were committed unchanged from the user's uploaded ZIP, with each Git blob checked against the corresponding original member:

- [pair_audit.json](pair_audit.json)
- [environment.json](environment.json)
- [resource_usage.json](resource_usage.json)
- [run_manifest.json](run_manifest.json)
- [summary.txt](summary.txt)

## Evidence and status

- All **six source files SHA256-verified**. Self-test PASS.
- **29,025 candidate parent joins**, including three D2 sets of 3,075 and D3 19,800 variants over 3,300 parents; **zero unmatched variants**. Structural matching is not semantic/campaign or maliciousness adjudication.
- **19,997 pairs flagged** for URL, sender, attachment or embedded URL changes. This **does not imply 19,997 true security-label changes**.
- The updated private reviewer panel includes original and variant subject/body, sender, explicit URL, attachment, source and year. It is **not in the uploaded safe ZIP**, so panel-level verification was limited to code, declared fields and aggregate size.
- **142 deterministic private sample candidates**, **0 completed human reviews**, observed agreement `null`, Cohen's kappa `null`, valid same-intent gold `0`, validated security-changed gold `0`.
- ZIP resource summary: **28.646 s**, peak process RSS **610.44 MB**, source downloads **85,481,663 bytes**, GPU use 0. Notebook saved console instead showed **21.181 s / 636.72 MB**, a distinct run snapshot; do not conflate timing evidence.
- **GO:** source identity and descriptive structural pairing. **NO-GO:** use of the private panel as already-annotated gold, source-rights clearance, claim of label-preserving/reversing edits, frozen train/test split, training, or public raw-email sharing.

## Original artifact SHA256

| Uploaded artifact | SHA256 |
|---|---|
| Executed Notebook 03 v1.2 | `841e332e6012ded8d3eb795bbfceca96954dd694060ef87457f73c26eb56ef60` |
| Results ZIP | `cb9da5defabb8f829e0ee3bc43542484e4506fe4765223d5f06c26877bf99c31` |
| pair_audit.json | `bf8696b81ecf47e5c8f7334e2bb32577ecfd8c35ce7b4c7aa9e88efe5cafd00e` |
| environment.json | `5f2c4c1b35809605a1eb19b9fd01ffef0bf733fcc4dd022c84838f5a29a5f47f` |
| resource_usage.json | `4c51e4d5bcc028222dd423e466376e9c43d62e96ae14ca171fabc4178201da7a` |
| run_manifest.json | `1b5220d4ef8c2e5a31b8d2972805c0473f1dd69fbeaf3828bb1e89ba4bce7027` |
| summary.txt | `c7d432df981f37aeeb3a1a2c435b2971792c423efcdf51cef7e2f71a5bc5c8ae` |

## Next stage

No further **automatic N03 rerun** is scientifically informative until two independent reviewers complete a **private** sample review under the rubric and approved source-rights/data-access process. The reviewer panel is located under `/kaggle/temp/phishing_pair_private/` in the original runtime, which may not survive a Kaggle session reset. Do not pretend the panel was durably saved; create an authorized private local workflow for the review, subject to rights and privacy restrictions.

[Notebook 04](../../../04_Global_Lineage_and_Frozen_Splits.ipynb) is an independent **descriptive global-overlap audit** that can proceed now without human gold. It must not freeze splits or train models until scientific gates are independently cleared.

**Privacy:** Do not put private review files, raw source emails, per-record text hashes or active phishing URLs into public GitHub, Kaggle outputs, notebooks or chat.
