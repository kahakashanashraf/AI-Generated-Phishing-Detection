# Pair and Security Counterfactual Annotation Rubric — v0.1

## Purpose
A rewritten email is **NOT automatically label-preserving** just because it looks similar. Separate harmless stylistic rewriting from security-relevant edits. This rubric must be piloted on real source samples and refined **before** final blind annotation. Do not invent annotator results.

## Review setting
- Show the original and candidate variant side by side, plain-text only. Do not click/open URLs or attachments.
- Mask real PII, active URLs and credentials using offline reversible pseudonyms, while retaining critical risk features (e.g., sender ↔ purported domain mismatch and request type).
- Reviewers annotate independently; adjudicator resolves disagreements. Keep audit history and a withheld quality-control subset.
- Avoid using predicted model labels as annotation truth. Record source label as a reference, not instruction.

## Fields for a pair
- `original_id`, `variant_id`, `source`, `rewrite_generator_verified`, `pair_type_proposed`.
- `subject_preserved`, `sender_context_changed`, `url_target_changed`, `credential_request_changed`, `payment_request_changed`, `attachment_action_changed`.
- `original_class`, `variant_class`, `label_confidence`, `reviewer_id`, `adjudicated_class`, `exclusion_reason`.
- `same_security_intent`: yes/no/uncertain.
- `security_change_label_flip_verified`: yes/no/uncertain.
- `evidence_note`: sanitized explanation, not raw malicious URL.

## Distinguish three edit types
1. **Style-only:** wording, punctuation, tone, grammar; core requested action, sender/URL trust cues and deception remain equivalent. Both adjudicated labels must match.
2. **Security-changing:** verified deception/authentication/payment/credential/authorization semantics genuinely changed; class change has independent ground-truth reasoning. Merely editing domain spelling or swapping brands is NOT sufficient evidence.
3. **Ambiguous/mixed:** no reliable conclusion (e.g., original context missing, both versions still suspicious, transformed URL alone). Exclude from pair loss and security-sensitivity claim.

## Concrete reviewer questions
1. What action does recipient need to take?
2. Does message impersonate a sender/domain or claim false urgency/authority?
3. Are recipient's credentials, money, login, sensitive documents or arbitrary links involved?
4. Were URL destination, sender identity or attachment context meaningfully altered?
5. Is there external ground truth or is 'phishing' just an assumption based on words?
6. Does the change clearly preserve the correct class or clearly change it?
7. Is enough metadata present for a reproducible security judgment?
8. Can the pair reveal a source/template shortcut unrelated to phishing?

## Outputs, reliability and exclusion
- Pilot: record number attempted, excluded, within-class valid, verified label-flipping, all per source and generator.
- Report raw agreement and Cohen's kappa / appropriate multi-rater statistic if reviewer design warrants; do not silently discard disagreement.
- Label-preserving pairs form the style loss set; opposite-label verified pairs form the security-sensitivity set; ambiguous ones are excluded from those objectives.
- Any counterfactual leakage into train/test is blocked by `original_id` group split.
- Maintain a sealed annotated challenge set, never used for hyperparameter tuning.
- If no verified security-changing pairs exist, method is NO-GO for bidirectional novelty; evaluate simpler scientific measurement track instead.
