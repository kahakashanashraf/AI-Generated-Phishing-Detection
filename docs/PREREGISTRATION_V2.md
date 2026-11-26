# Study 2 pre-registration: false alarms on AI-written legitimate email (style versus source)

**Status: FROZEN v2.1 on 2026-11-26.** The owner instructed us to proceed to the actual experiments. The freezing commit SHA is recorded in DECISION_LOG D010. Any later change must be appended in §9 as a deviation. D009 (public per-row predictions without text) was approved on 2026-11-26 (D012).
Changes from v2.0:
- graded AI-assistance levels L0–L4 and a primary trend endpoint PE0;
- modern Nazario 2023–2025 phishing (CC BY 4.0) as a security-cost test;
- Greco et al. 2024 LLM-legitimate emails as a second locked AI-authored set;
- Hillary Clinton FOIA emails as a secondary external human source.
The protocol is frozen when the owner approves it. At that point the commit SHA of this file is written into [DECISION_LOG.md](DECISION_LOG.md), and the file is optionally deposited as an OSF registration. After freezing, any change must be added as a dated, numbered deviation at the bottom. Earlier text is never silently edited.
**Rationale and literature:** [GAP_ANALYSIS_AND_PLAN_2026-11-26.md](GAP_ANALYSIS_AND_PLAN_2026-11-26.md) and [../paper/LITERATURE_2024_2026.md](../paper/LITERATURE_2024_2026.md).

## 0. Relation to existing results (Study 1)

N05–N14 (2026-11-02 to 2026-11-03) form **Study 1, which is exploratory**. Its findings:
- D2 LLM rewrites changed at most 1 of 142 legitimate decisions.
- Legitimate FPR on E-PhishLLM was 77–97% at thresholds set on D2 validation (5% FPR).
- Mitigations traded FPR against recall.

E-PhishLLM labels and outcomes have been inspected many times. From now on, E-PhishLLM is a **development (DEV)** external set: it is never used as confirmatory evidence and never used to choose between Study 2 configurations. Study 2 tests the hypotheses below on data that no model has scored yet.

## 1. Primary question

When a phishing-versus-legitimate email detector raises false alarms on AI-written legitimate email, which factor is responsible?
- **(a) How much AI assistance was used.** This is a graded, paired dose: proofreading, then polishing, then a full rewrite of the same message.
- **(b) AI-authored content and genre.** This is isolated by from-scratch emails matched to the original subject.
- **(c) Source shift.** This compares in-distribution mail with external corpora.

And can any pre-specified mitigation reduce those false alarms without lowering recall on modern and AI-rewritten phishing?

## 2. Design

### 2.1 Factors and cells

| Factor | Levels |
|---|---|
| **Source S** | `IN`: D2 HarmJ0y parent-held-out test (frozen N05 split: 142 legitimate, 162 phishing). `EXT` (primary): D1 Enron ham (label 0), from a corporate setting around 2000–2002. `EXT2` (secondary): Hillary Clinton FOIA emails (Kaggle `kaggle/hillary-clinton-emails`), from a government setting in 2009–2013, US-government public record |
| **AI-assistance level L** (legitimate, paired within parent) | `L0` human original. `L1` proofread: fix spelling and grammar only. `L2` polish: improve clarity and professional tone without changing content. `L3` rewrite: full rewrite (the RW cell). `L4` compose: written from scratch with the same subject (the DN cell) |
| **Authorship** (phishing) | `H` and `L3` only. We write no new phishing from scratch (ethics, §8) |
| **Generator G** (for L1–L4) | Test-only: `Qwen2.5-7B-Instruct` (Apache-2.0) and `Phi-3.5-mini-instruct` (MIT). In-source L3 also uses the GPT-4o, DeepSeek and randomapi rewrites shipped with D2 |

Phishing test sets:
- `EXT-phish-H`: Nazario `phishing-2022` (monkey.org, CC BY 4.0). These were collected before ChatGPT, so they are treated as human-written.
- `MODERN-phish`: Nazario `phishing-2023`, `-2024` and `-2025` (CC BY 4.0). These are real phishing whose authorship is **unknown**, and they serve as the realism test of security cost.
- Nazario 2015–2021 is used only for training (R2).

Off-the-shelf AI-authored corpora:
- `LLMGen-EN` (HF `Dizzzy0x00/LLMGen-Phishing-Email-Dataset`, revision `d717e5457b71cb44dd038dafe6a81cea5e0badab`, English rows, Apache-2.0) is **LOCKED**.
- `Greco24-LLM` (Kaggle `francescogreco97/human-llm-generated-phishing-legitimate-emails`, `llm-generated/legit.csv` and `phishing.csv`; Greco et al., ITASEC 2024) is **LOCKED**. No licence is stated, so it is used for evaluation only and never redistributed.
- `E-PhishLLM-EN` (Git blob `7a0e74ec…`) is **DEV**.

Excluded:
- PhishFuzzer and DataPhish, which are derived from D2.
- Kaggle `maarij/anti-pluto-email-corpus`, whose provenance is undocumented. It may be added only after a provenance audit, which must be recorded as a deviation.

### 2.2 Training regimes

- **R1 (primary):** the frozen N05 D2 split, train 1,418 and validation 304. This keeps results comparable with Study 1.
- **R2 (secondary, pooled multi-source):**
  - R1 train, plus SpamAssassin ham and CEAS_08 ham (legitimate, capped at 6,000 combined by stratified random sampling with seed 2026), plus Nazario `phishing-2015` to `phishing-2021` from monkey.org (phishing).
  - Validation is R1 validation plus a 10% group-stratified holdout of the added sources.
  - **Enron is excluded from R2 entirely**, because it is the external legitimate test source.
  - Sensitivity analysis: add D1 Nigerian_Fraud as phishing.
- Spam is never mapped to either class. This follows decision D001.

### 2.3 Generators and their roles (fixed)

| Model (Hugging Face id) | Licence | Role |
|---|---|---|
| `Qwen/Qwen2.5-7B-Instruct` | Apache-2.0 | test-only RW and DN generator |
| `microsoft/Phi-3.5-mini-instruct` | MIT | test-only RW and DN generator |
| `allenai/OLMo-2-1124-7B-Instruct` | Apache-2.0 | **train-only** generator (mitigations M1 and M5) |
| `ibm-granite/granite-3.1-8b-instruct` | Apache-2.0 | zero-shot detector D6 (a family different from every generator) |

All four are ungated. The Hugging Face commit SHA of each model is recorded at its first download in N16 or N19, and that revision is used for every later run. If vLLM cannot load a model on Kaggle T4 hardware, the fallback is to run the **same model** with Hugging Face `transformers` in fp16 or 4-bit. Model identities never change.

## 3. Data construction (N15 and N16)

### 3.1 Sampling

- **EXT-legitimate-H:** 1,000 Enron ham emails sampled uniformly at random (seed 2026) from those that pass all of these:
  - non-empty body;
  - 20–1,500 words;
  - English (langdetect);
  - decontamination (§3.3).
- **EXT2-legitimate-H:** 500 Clinton FOIA emails chosen at random from those that pass the same filters. FOIA header and release-stamp lines are removed by a fixed regex list.
- **EXT-phish-H:** every message in Nazario `phishing-2022` that survives parsing, the filters and decontamination against D2 and R2.
- **MODERN-phish:** all of Nazario 2023–2025 after the same processing, capped at 2,000 by random sampling stratified by year.
- **Nazario parsing:** messages are parsed from mbox with Python `mailbox`, keeping the text/plain body or else the html-to-text body. Attachments are ignored. Mail-system notices are removed by a fixed regex list, and the count removed is reported.
- **IN:** the frozen N05 test parents, with no resampling.
- **LLMGen-EN:** every English row that survives decontamination.

### 3.2 Generation protocol

- **Placeholder locking.** Before generation, every URL, email address and phone number is replaced with an indexed placeholder (`[URL_1]`, `[EMAIL_1]`, `[PHONE_1]`, …). After generation, the original strings are restored. Security-relevant evidence is therefore byte-identical between H and RW.
- **RW prompt.** The prompt does not tell the model the label. This exact text is used for both classes:
  > Rewrite the following email so that it reads as if you had written it yourself. Keep the same sender intent, requests, facts, names, numbers, and every placeholder token in square brackets exactly as written (for example [URL_1], [EMAIL_1], [PHONE_1]). Do not add or remove links, attachments, requests, or deadlines. Return only the rewritten email: the first line must be "Subject: ..." followed by the body.
  >
  > Subject: {subject}
  >
  > {body}
- **L1 proofread prompt.** This exact text is used:
  > Correct only the spelling, grammar and punctuation of the following email. Do not change wording otherwise, and keep every placeholder token in square brackets exactly as written. Return only the corrected email: the first line must be "Subject: ..." followed by the body.
- **L2 polish prompt.** This exact text is used:
  > Polish the following email so that it is clear, fluent and professional. Keep the same content, intent, requests, facts, names, numbers, structure, and every placeholder token in square brackets exactly as written. Return only the polished email: the first line must be "Subject: ..." followed by the body.
- **L3 rewrite prompt:** the RW prompt above.
- **L4 compose prompt (DN, legitimate only).** This exact text is used:
  > Write a realistic, legitimate email with the subject line below, as an ordinary sender would write it. Use 80–250 words. If the email would naturally include a link, write the placeholder [URL_1] instead of a real address. Return only the email: the first line must be "Subject: ..." followed by the body.
  >
  > Subject: {subject}

  In the output, `[URL_1]` is replaced by the fixed benign string `https://www.example.com/info`, and this is reported as a known artefact.
- **Decoding.** Temperature 0.7, top-p 0.95, max_new_tokens 700, one sample per input. The seed is the first 8 hex digits of sha256(sample_id) converted to an integer. The chat template is each model's default, and no system prompt is used.

### 3.3 Decontamination and grouping

- **Normalised key.** Lowercase the text, collapse whitespace, and take sha256 of subject + "\n" + body.
- **Near-duplicates.** MinHash with 128 permutations on 5-word shingles, using LSH. Pairs with Jaccard ≥ 0.80 are linked.
- **Groups.** Each group is the connected component of exact and near-duplicate links, together with D2 `No.` lineage and the rewrite family (a parent plus all its RW and DN outputs).
- **Rule.** Any test group with a member linked to any training or validation member, in any regime, is removed from test. Counts are reported per cell.
- **IN cells.** Each D2 test group is a parent plus its rewrites. A group is removed if any member is linked to R1 or R2 training or validation data. (N13 found 12 near-copies, cosine ≥ 0.98, among the frozen test parents.) The full, undecontaminated 304-parent N05 test is reported as a Study-1-comparable sensitivity analysis.
- **Protecting the frozen IN cells.** R2 pool candidates linked to any D2 validation or test parent, or to their rewrites, are removed from the pool *before* sampling.
- **Within-cell de-duplication.** Inside each cell, only one member per near-duplicate group is kept: the first one in seeded random order. This stops campaign copies from inflating n.
- **Filters for the R2 pool.** The pool uses the same filters as §3.1: non-empty body, 20–1,500 words, English.
- **Off-the-shelf locked and DEV cells** (LLMGen, Greco24, E-PhishLLM) use only the non-empty and English filters, with no word bounds. This keeps them comparable with N08.
- **Generation scope (N16).**
  - L1–L4 apply to EXT-legitimate (1,000) and IN-legitimate (142).
  - L3 applies to EXT-phish-H and IN-phishing.
  - EXT2 is L0 only, because it serves H2.
  - The train-only generator (OLMo-2) processes R1 training parents only.
- **Augmentation.** Augmentation text (M1, M5) is generated only from training-group parents.

### 3.4 Automatic quality filters (fixed; exclusions counted per cell and generator)

| Filter | RW | DN |
|---|---|---|
| Output parses into Subject plus body | ✓ | ✓ |
| Every input placeholder appears, and no new ones appear | ✓ | — |
| English (langdetect) | ✓ | ✓ |
| Body word ratio rewrite/original between 0.5 and 2.0 | ✓ | — |
| Body length 40–400 words | — | ✓ |
| No refusal (fixed regex list: "I can't", "I cannot", "As an AI", "I'm sorry") | ✓ | ✓ |
| Not identical to the input after normalisation | ✓ | — |
| Cosine similarity ≥ 0.70 to the original (`sentence-transformers/all-MiniLM-L6-v2`, pinned) | ✓ | — |

### 3.5 Human validation (N17, done by two authors)

- **RW sample.** 200 legitimate and 200 phishing RW pairs, stratified by generator and source. Two raters judge each pair independently on:
  - (a) Is the intent preserved?
  - (b) Was any security-relevant element added or removed (request, link, attachment, deadline)?
  - (c) What is the rewrite's label: phishing, legitimate or unsure?
- **DN sample.** 100 DN emails, each rated as a plausible legitimate email or not.
- **Reporting.** Cohen's κ for (c), with a target of ≥ 0.60. The label-preservation rate is reported with a Wilson 95% CI. Disagreements are resolved by discussion, and the resolution is logged.
- **Rule.** If label preservation is below 90% for a generator, that generator's RW results are reported only as sensitivity analysis.

### 3.6 Locking

- N15 commits `data/splits/locked_test_v2_manifest.json`. It contains the sha256 of the sorted locked sample-ID list per cell and the per-cell counts. Text stays private.
- No model is scored on locked cells until N20.
- N20 runs once on frozen models, whose file hashes are recorded. If a run is repeated, the reason goes into DECISION_LOG and every run is reported.

## 4. Detectors (fixed)

| ID | Detector | Notes |
|---|---|---|
| D1 | TF-IDF (word 1–2) logistic regression | Same vectorizer as N05 (min_df 2, max_df 0.98, sublinear tf, 120k features). C ∈ {0.1, 1, 10} chosen by train-only grouped 5-fold CV (average precision) |
| **D2** | TF-IDF + LinearSVC, Platt-calibrated | N05 configuration. **Primary** |
| D3 | TF-IDF Complement Naive Bayes | α ∈ {0.1, 0.5, 1} chosen by inner CV |
| D4 | DistilBERT-base-uncased (N12 configuration) | 5 seeds |
| **D5** | RoBERTa-base | max_len 256 (head 128 + tail 128 tokens), lr 2e-5, batch 16, ≤ 4 epochs with early stopping on validation AP, weight decay 0.01, warmup 6%. 5 seeds. **Primary**. Primary analyses use the mean probability across seeds, and the per-seed spread is reported |
| D6 | Granite-3.1-8B-Instruct, zero-shot | Fixed prompt. Score = P("phishing") from next-token logits over {phishing, legitimate} |

The seeds are 2026, 2027, 2028, 2029 and 2030. The input is always `Subject: … \n\n body`.

**Threshold rule.**
- τ5 is the smallest threshold whose FPR on source validation is ≤ 5% (primary). τ1 does the same at ≤ 1% (secondary).
- Thresholds come only from the regime's own validation set. They are never tuned on DEV or LOCKED data.

## 5. Mitigations (fixed; H5)

| ID | Mitigation | Fixed settings |
|---|---|---|
| M0 | None | — |
| M1 | Benign rewrite augmentation | OLMo-2 rewrites of R1 training legitimate parents plus the D2-provided rewrites of training parents. Each parent gets equal total weight (as N11) |
| M2 | Paired logit consistency | λ = 0.2, benign pairs only (N14 `benign_consistency_02`). For D5, a symmetric KL term between parent and rewrite predictions with λ = 0.2 |
| M3 | Pooled multi-source training | Regime R2 |
| M4 | Artifact normalisation at train and test time | Mask URLs to `<URL>`, emails to `<EMAIL>`, numbers to `<NUM>` and dates to `<DATE>`. Strip quoted-reply blocks and footers by a fixed regex list |
| M5 | Balanced AI exposure | Add OLMo-2 DN legitimate emails **and** OLMo-2 RW of training phishing in equal numbers, so that AI style does not predict the label |
| M6 | Label-free alert-budget threshold | For each target cell, build an unlabeled pool at 5% phishing prevalence. Set the threshold to flag 10% of the pool. No target labels are used |

**Success criterion.** All three must hold on locked cells, at τ5, for D2 and D5:
- **(a)** Pooled locked AI-legitimate FPR (EXT-RW, EXT-DN and LLMGen-legitimate) falls by ≥ 10 percentage points against M0, and the 95% CI excludes 0.
- **(b)** Pooled locked phishing recall (EXT-phish-H, EXT-phish-L3 and LLMGen-phishing) **and** MODERN-phish recall, each judged separately, are non-inferior with a −2 pp margin. The one-sided 95% lower bound of Δrecall must be above −2 pp. The "attacker benefit", meaning the change in miss rate on L3 phishing from the held-out generators, is reported for every mitigation.
- **(c)** FPR on IN-legitimate-H rises by no more than 2 pp (one-sided 95% upper bound).

## 6. Hypotheses, endpoints and tests

The unit of analysis is the parent message. Rewrites are always clustered with their parent.

| ID | Hypothesis | Endpoint | Test | Family |
|---|---|---|---|---|
| **PE0 / H0** | False alarms on legitimate mail change monotonically with the level of AI assistance (dose–response) | FPR at L0, L1, L2, L3 and L4 on EXT-legitimate, paired within parent | GEE logistic regression with an exchangeable working correlation clustered by parent: decision ~ level (ordinal score 0–4) + generator. Two-sided Wald test of the trend coefficient, plus an exact McNemar test of each level against L0 | Primary, Holm over D2 and D5. The level-versus-L0 contrasts are Holm-adjusted within each detector |
| **PE1 / H1** | Paraphrase-level AI style does not change false alarms on external legitimate mail | ΔFPR_RW = FPR(EXT-legitimate-RW) − FPR(EXT-legitimate-H), paired and pooled over test-only generators | **TOST equivalence**, margin ±3 pp, α = 0.05 (90% cluster-bootstrap CI inside ±3 pp). Exact McNemar is also reported | Primary, Holm over D2 and D5 |
| **PE2 / H3** | AI-authored content adds false alarms beyond source | ΔFPR_DN = FPR(EXT-legitimate-DN) − FPR(EXT-legitimate-H), matched on the parent subject | Exact McNemar (two-sided) plus a 95% cluster-bootstrap CI | Primary, Holm over D2 and D5 |
| **PE3 / H5** | Some mitigation meets the §5 criterion | Criteria (a), (b) and (c) | Cluster bootstrap with one-sided bounds as specified | Primary, Holm over the 6 mitigations × 2 detectors |
| H2 | Source shift raises false alarms | FPR(EXT-legitimate-H) − FPR(IN-legitimate-H) | 95% CI only. Descriptive, because sources are not randomised | Secondary |
| H4 | Mechanism: cue interventions move scores in the directions predicted from training-source cue statistics (N13) | Mean Δlogit after each intervention (I1–I6 below) on EXT-legitimate-H and EXT-legitimate-DN | Paired bootstrap CI. **Predicted direction:** for R1 TF-IDF models, removing URLs raises the phishing score, and adding a neutral URL line or an unsubscribe footer lowers it | Secondary, direction pre-stated |
| H4b | Failure decomposition | AUROC for each legitimate cell against same-source phishing. FPR at τ5 versus FPR at the oracle threshold that matches validation recall | Descriptive with CI | Secondary |
| H6 | PE1 and PE2 conclusions hold under R2 | As PE1 and PE2 | As PE1 and PE2 | Secondary, Holm within |
| H1-IN | In-source replication of the paraphrase null | As PE1 on IN | TOST ±3 pp | Secondary |

**Interventions for H4.** All are applied to legitimate emails only, so they cannot change the true label:
- I1 adds the line `More information: https://www.example.com/info`.
- I2 removes all URLs.
- I3 adds a fixed signature block.
- I4 removes the greeting and the sign-off.
- I5 adds a fixed unsubscribe footer.
- I6 truncates the body to its first 50% of words.

**Secondary metrics, reported for every detector, cell and regime:**
- FPR and recall at τ5 and τ1, each with a Wilson 95% CI;
- AUROC and AUPRC;
- Brier score;
- ECE (10 equal-width bins, plus 15 equal-mass bins);
- risk–coverage curves;
- alerts per 10,000 emails and precision at 1% and 5% prevalence.

**Statistics.**
- Cluster bootstrap over parents with B = 10,000 and seed 2026.
- Exact McNemar for paired binary decisions.
- Holm correction within each primary family.
- All exploratory analyses are labelled as such and are not adjusted for multiplicity.

**Power.**
- With n = 1,000 legitimate parents and a discordance rate of 10% (Study 1 observed ≤ 1%), the SE of a paired ΔFPR is about 1.0 pp. The 90% CI half-width is then about 1.6 pp, so TOST at ±3 pp has high power when the true Δ is about 0.
- The Wilson half-width at FPR = 50% is about ±3.1 pp.

## 7. What we will claim for each outcome (decided in advance)

| PE1 (RW) | PE2 (DN) | Pre-registered claim |
|---|---|---|
| Equivalent | Not significant | False alarms on AI-written legitimate email are a **source-shift** problem. Neither paraphrase-level nor from-scratch AI authorship adds measurable false alarms |
| Equivalent | Significantly > 0 | Paraphrase style is harmless, but **AI-authored content or genre** adds false alarms beyond source |
| Not equivalent, Δ > 0 significant | Any | AI rewriting style itself raises false alarms in external mail. This is an interaction with source, because the in-source result was null |
| Inconclusive (CI crosses a margin) | Any | Report as inconclusive with CIs. No directional claim |
| Any | Significantly < 0 | AI-authored legitimate mail is flagged *less* often. Report and discuss the security implication |

PE0 (dose–response) is reported alongside every row:
- A significant positive trend means false alarms rise with the level of AI assistance. Whether the rise starts already at L1 or L2 is read from the level-versus-L0 contrasts, and that point is the practical threshold for AI-assisted legitimate senders.
- A flat trend with a jump only at L4 means content or genre, not assistance.
- A flat trend throughout means source shift.

Mitigations are claimed as useful **only** if they pass all of §5 (a), (b) and (c).

## 8. Ethics, data and code

- **Human subjects.** No human participants. The raters in §3.5 are authors. The institution's policy on author-annotation must be confirmed before N17.
- **Dual use.** No new phishing is written from scratch. Phishing rewrites keep their original (already public) URLs. They stay private and are **not released**. Any quoted examples in the paper are defanged.
- **Data that are released:**
  - code with a Zenodo DOI;
  - prompts, model revisions and seeds;
  - locked ID manifests;
  - per-row predictions keyed by pseudonymous sample IDs that are derivable from the public source datasets (no text). D009 was approved on 2026-11-26 (D012);
  - aggregate tables and figure source data.
- **Third-party data.**
  - D2 has no licence, so it is cited with its commit and not redistributed.
  - D1 is under CC BY 4.0 at the collection level, and its constituent rights are noted.
  - E-PhishLLM is MIT.
  - LLMGen is Apache-2.0.
- **Reporting.** A REFORMS checklist is filed as Supporting Information.

## 9. Deviations

*(Append after freezing: number, date, what changed, why, and which results are affected.)*

**Deviation 1 (2026-11-26, before any generation).**
- *What changed:* the "not identical to the input" filter (§3.4) is applied to L2 and L3 but not to L1. The other RW filters, including cosine ≥ 0.70, apply to L1–L3.
- *Why:* proofreading an already-correct email can legitimately return it unchanged, and that is a valid L1 outcome. The number of unchanged L1 outputs is reported.
- *Results affected:* L1 cells only.

**Deviation 2 (2026-11-26, before any generation).**
- *What changed:* the sampling seed is set per batch, as the first 8 hex digits of sha256 over the sorted sample IDs in the batch. It was planned per row.
- *Why:* batched sampling in Hugging Face `transformers` cannot seed rows individually.
- *How batches are formed:* deterministically, by sorting on (input token length, sample ID).
- *Results affected:* none in expectation. Only exact reproducibility of the sampled text depends on batch composition and hardware.

**Deviation 3 (2026-11-26, before any generation).**
- *What changed:* `max_new_tokens` goes from 700 to 2048.
- *Why:* inputs can reach 1,500 words. A 700-token cap would truncate rewrites of emails longer than about 450 words, and the length-ratio filter would then reject them. That would cause length-dependent attrition across the L1–L3 levels.
- *Results affected:* fewer exclusions of long emails, and therefore less biased paired cells.

**Deviation 4 (2026-11-26, after N15 run 1, before any scoring).**
- *What changed:* the Greco24 loader now reads one physical line per email, taking the text before the last comma.
- *Why:* N15 run 1 showed that Greco24 `llm-generated/phishing.csv` is unquoted CSV whose text contains commas. The standard CSV reader split each email into fragments: the cell's median length was 3 words, and 854 records were dropped as "not English". The `label` column in that dataset is the authorship label (all 1), so the phishing label continues to come from the file name.
- *How it was handled:* N15 was re-run with the fixed loader. The run 1 outputs are superseded and recorded in DECISION_LOG D011.
- *Results affected:* only the Greco24 cells. No model had been scored.

**Deviation 5 (2026-11-26, before any generation): added manipulation check.**
- *What changed:* for every generated cell (L1–L4) and for the D2-provided rewrites, we report how far each output moved from its parent. The measures are the MinHash-estimated Jaccard similarity of 5-word shingles, the cosine similarity, and the word-count ratio. The expected order is L1 > L2 > L3 > L4 in similarity.
- *Why:* N15 found that many D2-provided rewrites are near-copies of their parents (Jaccard ≥ 0.8 for 74 of 139 randomapi and 60 of 139 DeepSeek legitimate rewrites). The dose levels therefore need to be verified directly.
- *Results affected:* this is descriptive and secondary. It does not change any primary test.

**Deviation 6 (2026-11-26, before any generation): numeric precision per generator.**
- *What changed:*
  - Phi-3.5-mini runs in float32. It fits on 2×T4.
  - Qwen2.5-7B and OLMo-2-7B run in float16, because float32 does not fit, with `remove_invalid_values=True` set during sampling.
- *Why:* T4 GPUs have no fast bfloat16, and float16 activation overflow can produce NaN or inf logits in these model families. In float32 the problem does not arise for Phi. For the 7B models, any degraded output is rejected by the §3.4 filters, and a fail-fast check on the first batch stops a run whose pass rate is below 0.5.
- *Results affected:* only the numerical stability of generation. The exclusion counts are reported.

**Deviation 7 (2026-11-26, before any detector is trained): sealed scoring.**
- *What changed:* §3.6 said "no model is scored on locked cells until N20". Instead, notebook 05 trains each detector and immediately scores every cell, locked cells included. It writes the scores only to a private **sealed** file whose SHA-256 is recorded in the 05 run manifest.
- *What 05 is allowed to do:* compute and inspect validation metrics. It must not compute or display any metric on a locked cell.
- *What 07 does:* the confirmatory notebook (N20) verifies the seal hash, then computes every locked-cell statistic once.
- *Why:* re-loading about 35 fine-tuned transformer checkpoints (about 17 GB) in a separate session is impractical on Kaggle. Sealing keeps the intent of §3.6: nobody sees a locked-cell outcome before the single confirmatory run.
- *Same treatment for:* the judge notebook 06 and the H4 intervention cells.

**Deviation 8 (2026-11-26, before any judge scoring): judge details the protocol left open.**
- *Truncation:* each email is cut to at most 1,536 tokens, keeping the first 1,024 and the last 512.
- *Prompt:* fixed. It defines phishing in one sentence and asks for exactly one word.
- *Score:* the sigmoid of the difference between the log-sum-exp first-token logits of "phishing" and of "legitimate". All casing and leading-space variants of each word are included, and the two token sets must not overlap.
- *Validation:* τ5 and τ1 come from R1 validation. The argmax decision rate is reported as secondary.
- *Why:* §4 fixed the judge model and the score definition but not these mechanics. They are set here before any score exists.
- *Results affected:* D6 only.

**Deviation 9 (2026-11-26, before any generated text is drawn or rated): human-validation details the protocol left open.**
- *Generators:* §3.5 covers the two test generators, Qwen2.5-7B and Phi-3.5-mini, whose RW and DN outputs enter the confirmatory endpoints. The §3.5 rule ("RW results reported only as sensitivity analysis") applies to them. OLMo-2-7B is train-only (M1 and M5) and is not rated. The D2-provided rewrites are not rated either, because the manipulation check covers them (deviation 5).
- *Strata:* RW items are stratified generator × source × label, with 50 per stratum (2 × 2 × 50 = 200 per label). DN items are stratified generator × source, with 25 per stratum (100 in total).
- *Parents:* within each source and label, the two generators get disjoint parents where possible. Any reuse is counted and reported.
- *Draw:* seeded and independent of input order (`phishbench.human_validation`, seed 2026).
- *Blinding:*
  - Items carry opaque IDs, so generator, cell and level are hidden.
  - Links are defanged (`hxxp`, `www[.]`) in every item alike.
  - Each rater gets their own workbook in their own seeded order.
  - The key stays private. Its SHA-256 is committed by the kit run before rating starts.
- *Question (b)* is answered as `no / added / removed / added_and_removed`.
- *Label preservation:* the final label is the shared answer of the two raters, or the adjudicated answer where they disagree. "Unsure" counts as **not preserved**, which is conservative. The rate is per generator, with a Wilson 95% CI, and the §3.5 rule uses its point estimate.
- *Agreement:*
  - Cohen's κ, from the independent ratings before adjudication, with a 2,000-draw item-bootstrap 95% CI. The target is κ ≥ 0.60 for (c).
  - Gwet's AC1 and raw agreement are reported as supplementary measures, because κ is unstable when one category dominates.
- *Release:* only item IDs and answers, with no text, are committed (`results/04_human_validation/`). Rater comments are never released.
- *Why:* §3.5 fixed the sample sizes, questions and rule but not these mechanics. They are set before any item is drawn or rated.
- *Results affected:* human validation only. No detector endpoint changes.
