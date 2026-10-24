# Dataset Playbook — v0.1, 2026-10-24

**ALL SOURCES ARE CANDIDATES, NOT YET ROW-AUDITED OR LICENSE-CLEARED.** No claims of unseen generator, security-sensitive pairs, or independent tests until provenance checks pass.

| ID | Source | When | Purpose | Blocking concerns | Status |
|---|---|---|---|---|---|
| D1 | [Champa curated 11 email corpora](https://zenodo.org/records/8339691) | M1 intake; M3 human baseline; M6 held-out corpus | Human original phishing and legitimate. Inspect CEAS_08.csv, Nazario.csv, SpamAssasin.csv, Enron.csv, then TREC; separate constituent sources | Mixed spam/phishing semantics, duplicates/overlapping corpora, vintage; license and rights of original corpora must be checked; no LLM rewrites | PENDING |
| D2 | [HarmJ0y PhishingSpamDataSet](https://github.com/HarmJ0y/PhishingSpamDataSet) | M1 audit; M2 pairs; M4/6 generator tests | Human/AI; Phishing, Spam, Valid; GPT-4o, DeepSeek, multi-provider rewriting pipelines, rich features | True-vs-predicted category; exact per-row generator vs 'RandomAPI'; original parent link; provenance and redistribution license not yet verified | PENDING |
| D3 | [DataPhish PhishFuzzer](https://github.com/DataPhish/PhishFuzzer) | M1/2 paired audit; M4/6 robustness | 3,300 seeds + 19,800 variants, Original_ID, class and sender/URL/attachment metadata | Variants intentionally change entities/URL domains; do not assume purely style-preserving; `Created by` is not necessarily rewriting generator; license and citation need verification | PENDING |
| D4 | [LLMGen Phishing Email Dataset](https://huggingface.co/datasets/Dizzzy0x00/LLMGen-Phishing-Email-Dataset) | M1 inspect; M6 auxiliary synthetic-only test | 6,776 LLM-produced phishing/legitimate; fields content,label | DeepSeek Chinese vs OpenAI English creates language-generator confound; cannot claim unseen-LLM from 2-column schema. HF lists Apache 2.0; original rights need review | AUXILIARY |
| D5 | [Gutierrez et al. code+features](https://zenodo.org/records/20250116) | M0 literature; M4 auxiliary replication only | 9,986 **phishing-only** samples; 5,000 human vs 4,986 LLM; 17 stylometric features, 3 generators | Binary task is authorship, NOT phishing detection; cannot estimate legitimate false positives; raw text fields must be checked | REPRODUCTION ONLY |

## Which source is used for which scientific question?
- **Human phishing-vs-legitimate baseline:** D1, individual corpora tracked separately; D2 after validating its labels.
- **Same-parent original/rewrite stability:** D3 first because `Original_ID` documented; D2 only after checking parent link.
- **AI legitimate false-positive control:** verified D2 `Valid` & AI; D4 English legitimate is auxiliary, not independent gold.
- **Leave-one-generator-out (LO-G):** D2 ONLY IF record-level exact generator and ancestry are verified; not `RandomAPI` assumed as model. D4 does not support LO-G without language confounding; D5 LO-G applies to *authorship task* only.
- **Leave-one-family-out (LO-F):** conditional; may be impossible if family metadata/coverage missing.
- **Leave-one-corpus-out (LO-C):** held-out D1 constituent dataset vs vetted D2 or D3; global duplicate screening first.
- **Joint unseen generator+corpus:** conditional; only when actual factorial generator×corpus coverage supports it.
- **Security-changing label counterfactuals:** **no approved gold dataset yet**. Small human-adjudicated sanitized panel required; otherwise no bidirectional method claim.
- **Final locked test:** one unrelated auditable source family preserved unused through tuning; if impossible, say so.

## Phase M1 exact intake order
1. **D1:** source page -> file list/checksums -> preview 20–100 rows for Nazario, SpamAssasin, Enron, CEAS -> identify raw labels and source overlap. Do not start with aggregate merged CSV.
2. **D2:** view files under `1_DataSet`, `3_RePhrase`, `4_MergeDataSet`; inspect first rows, exact generators, origin, labels, parent IDs and license.
3. **D3:** open two source JSON files; join on `Original_ID`; check each of 6 variants for security evidence mutations.
4. **D4:** inspect schema, language counts and duplicates; classify as auxiliary if provenance inadequate.
5. **D5:** inspect actual archive for code + features and task semantics, not primary email text by assumption.

## Manifest schema (mapping audited per source, never guessing)
`sample_id,text,label,source_corpus,source_revision,original_id,group_id,variant_id,origin,generator_model,generator_family,rewrite_pipeline,edit_type,language,review_status,label_verified,text_sha256`
- Binary label: 1=phishing, 0=legitimate. **Spam is separate/unknown** until policy freeze.
- Missing metadata are explicit NULL; never invent `Original_ID` or a generator name.
- Parent/group ID covers all rewrites, close template copies and known cross-corpus duplicates.
- Keep raw `text` and suspicious URLs in private secured inputs, **not** public GitHub.
- Any label-preserving pairs and label-changing security edits require independent audit.

## Repeatable dataset receipt (one file `reports/dataset_receipts/Dx.md`)
- Source URL and version/commit/DOI; original citation.
- Fetch date, file name, SHA256 and bytes.
- License text URL and underlying source rights. Unknown means redistribution BLOCKED.
- Rows, features, true/predicted labels and origin/generator/language/source counts.
- Missing values and conflicts; exact + near duplicates within/across datasets.
- How original_id and rewrite provenance were verified.
- Label semantics; what is phishing vs spam vs valid? Annotation method and uncertainty.
- Security changes (URL, sender, financial/credential demand) and pair validity.
- Privacy / deidentification / handling of live-looking links.
- Final verdict **GO / RESTRICTED / NO-GO**, evidence and date.

## Responsible data rules
Open-source availability is not an automatic redistribution license. Public email corpora may contain personal data. No live URL clicks, email sending, phishing deployment, attachment execution, or publishing raw records. Preserve only citations, aggregate counts, hashes and redacted illustrative examples.
