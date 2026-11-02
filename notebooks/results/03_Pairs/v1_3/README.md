# N03 v1.3 full-text recovery — Kaggle execution receipt (2026-11-02)

Status: **technical descriptive execution GO; annotated pair gold NO-GO; training not authorized by this report alone.**

The researcher supplied the executed `03-v1-3-full-text-recovery-annotation-preparat.ipynb` and `results (2)(4).zip`. These metadata below are from the supplied safe reports, **not an independent re-execution**.

## Verification extracted from uploaded safe ZIP
- `n03_v1_3_safe_fulltext_summary.json` SHA256 `1fc48381b725c078...` (prefix; record the complete hash in private run manifest).
- Release `N03-PAIR-v1.3-FULLTEXT-2026-11-02`.
- `review_rows=142`, `unique_review_ids=142`.
- `has_truncation_marker=false`.
- `reviewer_aid_file_created_private=true`.
- `privacy_status=MANUAL_PII_CHECK_REQUIRED`.
- `full_text_status=RECOVERED_FROM_SHA256_VERIFIED_PINNED_SOURCE`.
- `human_annotation_status=PENDING`, `training_gate=NO_GO`.
- The supplied safe ZIP contained `environment.json`, `n03_v1_3_safe_fulltext_summary.json`, `pair_audit.json`, `resource_usage.json`, `run_manifest.json`, `summary.txt`.
- **No private full-text reviewer-aid content is committed here.**

The report confirms source-based recovery and absence of the specified truncation marker; it does **not** prove an exact rowwise comparison against the earlier 51 truncated cases because the old panel was not compared. The generated reviewer aid requires manual privacy check before any distribution.

## Independent AI-assisted first-pass triage (not human annotation)
A separate preliminary pass over the 142-row uploaded N03 panel reported:
- `APPARENT_SAME_INTENT_CANDIDATE`: 41
- `INCOMPLETE_CONTEXT`: 40
- `SECURITY_CUE_DIFF_REVIEW`: 24
- `UNRESOLVED_SOURCE_CLASS`: 19
- `MATERIAL_ENTITY_OR_CONTEXT_REWRITE`: 18

These five exclusive triage counts sum to 142. Across categories, 70 rows had a security-cue flag and 51 had truncation in the older panel (overlapping diagnostics).
Sources: D2 DeepSeek 40, D2 GPT-4o 42, D2 RandomAPI 42, D3 variants 18.
- Verified same-intent gold: **0**
- Verified security-label-flip gold: **0**
- Independent human reviewers: **not performed**

A private panel and per-row raw-text derivations **must not be made public**. Only this aggregate decision record and execution metadata may be public.

## Next use
Use N03 data as preliminary descriptive paired-robustness evidence, not a gold-label counterfactual training set. Prioritize independently sourced AI-written benign controls and leakage-safe source splits for the main empirical paper.
