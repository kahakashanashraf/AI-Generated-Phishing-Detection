# DATASET RECEIPT TEMPLATE — copy to D1.md, D2.md, D3.md, D4.md or D5.md

> Status: PENDING. Never mark a source GO from its README alone.

## A. Identify
- Dataset ID/name:
- Source URL and citation:
- Author/publisher:
- DOI or pinned Git commit/version:
- Inspection UTC date:
- Source files inspected:

## B. Rights and integrity
- License as actually displayed (URL):
- Underlying constituent corpus license / restrictions:
- Redistribution of original email bodies allowed? YES / NO / UNKNOWN
- Downloaded exact filename, byte size, SHA256:
- Was raw content kept out of public Git? YES / NO
- Suspected personal data and active-looking malicious URLs:

## C. Labels and features
- Real column names (not assumed from paper/README):
- Actual row counts:
- True phishing/legitimate/spam definitions:
- AI origin counts:
- Generator exact model and family counts (unknown explicitly):
- Source corpus and language counts:
- Parent original_id linkage: how verified?
- Label source: humans, heuristics, LLM or synthetic prompt?
- Features: subject/body, sender, URLs/attachments:
- Missing and ambiguous fields:

## D. Leakage & confounding
- Exact duplicate count and normalized duplicate count:
- Near duplicate screening method, threshold and sample verification:
- Matches against other dataset candidates:
- Prompt/template fingerprints:
- Label correlated with source/generator/language/length?
- Original↔rewrite label preservation manually verified?
- Security evidence changes found:

## E. Research suitability verdict
- Human phishing/legitimate baseline: GO / RESTRICTED / NO-GO
- AI-written benign testing: GO / RESTRICTED / NO-GO
- Same-intent pair evaluation: GO / RESTRICTED / NO-GO
- Security-changing counterfactual: GO / RESTRICTED / NO-GO
- Unseen-generator test: GO / RESTRICTED / NO-GO
- Unseen-corpus test: GO / RESTRICTED / NO-GO
- License for public release: GO / RESTRICTED / NO-GO

## F. Evidence and next action
- Notebook URL:
- Code commit:
- Validation commands/tests and output:
- Failures, proposed fixes and tests:
- Author/reviewer:
- Next unchecked checklist item:
