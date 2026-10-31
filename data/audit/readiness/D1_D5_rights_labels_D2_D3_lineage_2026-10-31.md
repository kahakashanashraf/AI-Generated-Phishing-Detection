# D1–D5 source rights, label semantics and D2→D3 derivation audit — 2026-10-31

**Decision: GO for independently verified metadata/documentation audit; NO-GO for declaring the binary phishing study data train-ready or publication-ready.** This record does not contain raw emails, individual identifiers, suspicious links, or private annotations. It supplements the [executed Notebook 04 lineage report](../../../notebooks/results/04_Global_Lineage/v1_2/README.md), not a new Kaggle run.

## What was independently verified

1. Checked publisher and original source documentation for D1–D5.
2. Queried both pinned public GitHub repositories' Git tree and license metadata. Neither D2 nor D3 advertises a GitHub repository license, and neither contains a named LICENSE/COPYING file as of this inspection. **Public access is not an express reuse or republication permission.** Absence of a license is not, by itself, a legal determination that every kind of private research analysis is prohibited; obtain rights clarification before broader reuse or text release.
3. Downloaded/parsing through the GitHub connector the **exact pinned Git blobs** of D2 `1_DataSet/cleaned_emails.json` (Git blob `b9d6dd2ac3d6e2d337b9b9d79fc8f1f4377ea4f9`) and D3 `PhishFuzzer_emails_original_seed_v1.json` (Git blob `294e84ed06957ab64b3a6fe4dfc05a6afda7f7de`). No source scripts were run, and no email text was exported.
4. Verified category, source, author-field and original-ID histograms; cross-compared all normalized subject/body pairs and the exact `No.` identifiers between the original data files. Findings below are **new evidence**, not inferred from previous aggregate overlap alone.

## Dataset license / rights and target-label assessment

| Corpus | Public license/documentation evidence | Scope of labels | Policy for this study |
|---|---|---|---|
| **D1** Zenodo 8339691, curated 11 corpora | Record catalog documents **CC BY 4.0**. However underlying real-person email and original subcorpus provenance/privacy can impose separate ethical/rights obligations. Published file MD5 verified in N01. | Heterogeneous original sources: `Nazario` phishing-specific, while SpamAssassin / Enron-Spam / CEAS-08 have substantial **spam-vs-ham** origins; a D1 CSV value `1` must **not** everywhere be assumed strictly phishing. | **Conditional**, source-by-source labeling and privacy audit; no raw email redistribution |
| **D2** HarmJ0y/PhishingSpamDataSet, pinned commit `d13e9bb73d03f458e6d5b6cb6c7b0a708ea47e3d` | Public README but **no LICENSE file / no declared repo license found**. Third-party email upstream reuse needs attention. | Four original `Type` classes (exact): `Phishing` 1,090; `Spam` 1,000; `Valid` 950; `Phishing Simulation` **35**. 3,075 rows; no missing Type. | **HOLD**: keep simulation separate and retain spam as separate; clarify permission |
| **D3** DataPhish/PhishFuzzer, pinned commit `1e21dd4edbe5c64694f156bf5318c97c7c80681c` | Public README but **no LICENSE file / no declared repo license found**. Repo says 300 private collected emails and 3,000 public aggregate sources. | 3,300 seeds: `Phishing` 1,126; `Spam` 1,074; `Valid` 1,100. Artificial descendants = 19,800; metadata-enriched/modified variants may change content. | **HOLD**, derived from D2; request terms, identity/intent adjudication |
| **D4** Dizzzy0x00 LLMGen-Phishing-Email-Dataset | Hugging Face dataset card explicitly declares **Apache-2.0** at checked revision `d717e54` (generative synthetic dataset). Upstream model/output rights and authenticity remain as described by source authors. | Source card: `0=legitimate`, `1=phishing`; English from OpenAI, Chinese from DeepSeek. 6,776 binary-labeled examples in executed N02. | **Candidate for synthetic-only, language-stratified exploratory work** under attribution and license compliance; **NOT independent generator evaluation** because language and claimed generator co-vary. No model training authorized by this audit alone. |
| **D5** Gutierrez et al., Zenodo 20250116 | Record explicitly states **CC BY 4.0 for data, MIT for code**, for defensive research; original source corpora remain traced and should be cited. | 9,986 phishing-context stylometric records (5,000 human-written; 4,986 model-generated) to classify **AI vs human provenance**, not phishing vs legitimate. | **EXCLUDE from primary binary study**; optional secondary authorship/stylometry context only. |

**Important D1 original-task correction:** The CEAS 2008 organizers call it the *CEAS Spam Filter Challenge*. Original SpamAssassin and Enron-Spam also address spam/ham rather than guaranteed credential-stealing phishing. Curated downstream `label=1` is not automatically a verified strict-phishing label. Examine source-level meaning and mark ambiguity instead of inventing a class mapping.

## New direct D2→D3 identity and label findings

Both pinned original JSON files have an explicit `No.` key. It is unique for all 3,075 D2 originals; D3 has 3,300 seed records. A direct same-ID join gives:

- **All 3,075 D2 IDs reoccur as D3 seeds** (zero missing D2 IDs); **225 D3 IDs are additional**.
- **2,971 / 3,075** same-ID records have equal subject and body after casefold/whitespace normalization. **104 / 3,075** have altered normalized text. Mere text equality misses these lineage links.
- Same-ID `Type` transition matrix across **all 3,075** reused IDs:

| D2 original Type → D3 seed Type | Number |
|---|---:|
| Phishing → Phishing | 1,090 |
| Phishing Simulation → Phishing | **35** |
| Spam → Spam | 1,000 |
| Valid → Valid | 949 |
| Valid → Phishing | **1** |
| TOTAL | **3,075** |

- For **2971 unchanged-text same-ID records**, there are 16 `Phishing Simulation→Phishing`, one `Valid→Phishing`, and the remaining category matches. The other **19** simulated-phishing records were among the 104 altered-text same-ID entries.
- The **225 new D3 IDs** have `Spam` 74 and `Valid` 151, with **zero new labeled Phishing rows**. `Source` counts: `SpamAssassin.csv` 122; `Manual` 87; `spam_assassin.csv` 16. These groups are not certified independent source collections.
- `Created by` is **not a clean human-vs-LLM gold field**: D2 original: `Human` 3,073, `Huamn` typo 1, null 1. D3 seeds: `Human` 3,176, `SpamAssassin` 122 (corpus name, not an author), `Huamn` typo 1, missing 1.
- The broader strict-text and parent-aware N04 global audit found 2,896 common **unique normalized keys** between D2 originals and D3 seeds, comprising 2,971 repeated **rows** on each side. The direct same-ID join strengthens the finding: D3 is **D2-derived**, not a clean independent held-out corpus.

### Correct scientific interpretation

The 35 `Phishing Simulation` rows are an *explicit fourth source category*, not corrupted labels. All 35 are classified `Phishing` in D3, a **source taxonomy merge** that has not been independently adjudicated. The single `Valid→Phishing` same-ID relabel is a source conflict; its true intent is **unresolved**. None may be used as automatically verified label-changing counterfactuals.

The 104 changed-text same-ID records are **not** proven same-intent paraphrases, nor label-changing pairs. All D2/D3 original and rewritten offspring sharing an ID or text match should be linked for contamination control. D2→D3 training/test transfer cannot be described as held-out external corpus transfer.

## Gate matrix and next responsible actions

| Gate | Observed status | What remains |
|---|---|---|
| Pinned data files and descriptive schema | **GO** | Preserve source SHA256 and revision manifest |
| Specific D2 35-label mystery | **RESOLVED** | It is `Phishing Simulation`; keep separate; independently adjudicate mapping if required |
| D2→D3 reused lineage | **RESOLVED at the ID/linkage level** | 3,075 common IDs; still need campaign/semantic evidence |
| Label shift detection | **FOUND** | Quarantine `Phishing Simulation→Phishing` and `Valid→Phishing` until validated |
| Per-record author/generator truth | **NO-GO** | Creator metadata needs audit; generic `Created by` does not prove per-email LLM provenance |
| Rights and permitted redistribution D2/D3 | **NO-GO / permission unverified** | Clarify dataset/corpus rights and allowed defensive research/release |
| Genuine human-reviewed style/security pair gold | **NO-GO** | Two independent qualified reviewers + third-party adjudication on the N03 private 142-pair panel |
| Global leakage-safe split freeze | **NO-GO** | Rights/labels, D2→D3 inherited IDs, D1/D2/D3 overlap, semantic/near duplicates and model-selection policy must be finalized |
| Training and claims about real-world phishing | **NO-GO** | Do not train/tune/evaluate under an incorrectly mapped target or contaminated holdout |

## Conservative provisional label taxonomy

- **D1:** Preserve `source_name` and original `label`; don't globally map `1` to strict phishing across the mixed corpora. Treat spam/ham corpora as a separate task or auxiliary negatives only when verified and justified.
- **D2:** `Phishing` → tentative phishing; `Valid` → tentative legitimate; `Spam` → separate spam; `Phishing Simulation` → quarantine/independent review. No automatic `Phishing Simulation→Phishing`.
- **D3:** Three-class source annotation; enforce **D2-original-ID ancestry** and quarantine 35 inherited simulation relabelings plus one `Valid→Phishing` conflict, irrespective of D3 `Type`.
- **D4:** Card-claimed synthetic binary labels; avoid mixing English/OpenAI and Chinese/DeepSeek into a supposedly controlled per-generator comparison.
- **D5:** Do not treat human-written phishing as legitimate negatives.

**No training, no frozen splits and no redistribution of private review/raw emails is authorized by this metadata audit.**

## Source URLs (full)

- D1 original record / curated metadata: https://zenodo.org/records/8339691
- D1 catalog rights evidence: https://datasetcatalog.nlm.nih.gov/dataset?q=0002120019
- CEAS original task: https://ceas.cc/2008/challenge.html?redirect=true
- Enron original corpus and privacy warning: https://www.cs.cmu.edu/~enron/
- D2 pinned repo: https://github.com/HarmJ0y/PhishingSpamDataSet/tree/d13e9bb73d03f458e6d5b6cb6c7b0a708ea47e3d
- D2 original blob: https://github.com/HarmJ0y/PhishingSpamDataSet/blob/d13e9bb73d03f458e6d5b6cb6c7b0a708ea47e3d/1_DataSet/cleaned_emails.json
- D3 pinned repo: https://github.com/DataPhish/PhishFuzzer/tree/1e21dd4edbe5c64694f156bf5318c97c7c80681c
- D3 seed blob: https://github.com/DataPhish/PhishFuzzer/blob/1e21dd4edbe5c64694f156bf5318c97c7c80681c/PhishFuzzer_emails_original_seed_v1.json
- D4 card + declared license: https://huggingface.co/datasets/Dizzzy0x00/LLMGen-Phishing-Email-Dataset
- D4 historical card: https://huggingface.co/datasets/Dizzzy0x00/LLMGen-Phishing-Email-Dataset/blob/f00dd998b3013160faeddffa67590f1cb1ca034c/README.md
- D5 record: https://zenodo.org/records/20250116
- The checked N04 full aggregate report: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/blob/main/notebooks/results/04_Global_Lineage/v1_2/lineage_audit.json

**Rights caveat:** This is a documented research-risk assessment, not a legal opinion. Licenses displayed by aggregators do not override third-party privacy or intellectual-property rights in original emails.
