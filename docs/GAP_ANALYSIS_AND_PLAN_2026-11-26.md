# Gap analysis, positioning and execution plan for PLOS ONE (v2.1, 2026-11-26)

> **v2.1 summary (read this first).** The rest of the document is v2 and still holds, except where this box overrides it.
>
> **Core novelty.** We are the first, to our knowledge, to measure a **dose–response of AI assistance** on phishing-detector false alarms. Each real legitimate email appears at five levels:
> - L0: human original
> - L1: proofread
> - L2: polish
> - L3: rewrite
> - L4: composed from the subject line
>
> URLs, emails and phone numbers are placeholder-locked, so they stay byte-identical across levels. The design separates this from AI-authored content (L4) and from source shift (IN, EXT and EXT2), and judges mitigations against **modern real phishing (Nazario 2023–2025)** and against AI-rewritten phishing. The design precedent is APT-Eval (AI-text detectors); nobody has done this for phishing detectors.
>
> **Contributions:**
> - C1: graded AI-assistance benchmark, released for legitimate email only.
> - C2: factorial separation of assistance, content and source.
> - C3: ranking-versus-threshold decomposition plus cue interventions.
> - C4: two-sided mitigation frontier with an "attacker benefit" measure.
> - C5: pre-registered, leakage-audited open protocol.
>
> **Datasets added in v2.1:**
> - Nazario monkey.org mboxes 2015–2025 (CC BY 4.0).
> - Greco et al. 2024 LLM-legitimate emails (CC-BY-NC-SA, evaluation only).
> - Hillary Clinton FOIA emails as a second external human source.
>
> Excluded: PhishFuzzer and DataPhish (derived from D2), and Anti-PLUTO (undocumented provenance).
>
> **Status:** pre-registration frozen (v2.1, commit `a17a720`). N15 implemented (`notebooks/15_…`) and running on Kaggle.
>
> **Two PLOS ONE submission routes (owner decides before N20):**
>
> | Route | How it works | Pros | Cons |
> |---|---|---|---|
> | **A. Registered Report** | Submit the Stage 1 protocol (intro, methods, Study 1 as pilot) **before** the locked evaluation (N20). Once accepted, it gets in-principle acceptance, and the final report is published whatever the results, provided the protocol is followed | Highest acceptance certainty. A null result is safe | Stage 1 review takes months. The protocol may be a separately charged article, so verify the fee. N20 must wait |
> | **B. Research Article** | Run everything and submit once, citing the frozen pre-registration (commit hash, plus optional OSF) | Faster, one fee | No in-principle acceptance |
>
> Recommendation: if the APC is waived (Research4Life Group A), choose A. Otherwise choose B, with an OSF registration of the frozen protocol.
>
> **Extra PLOS ONE items:**
> - **AI-use disclosure.** State in Methods that LLMs were the study instruments (generators and judge), and that an AI assistant helped with code and drafting, which the authors verified.
> - **Code archive.** Deposit the code in an open archive (Zenodo DOI). PLOS can require code that is central to the paper.
> - **CC-BY-NC-SA data.** The Greco24 data must not be redistributed; cite it and give access instructions.
> - **Data Availability Statement** with exact access routes for D2 (no licence, so only commit and URL are given).

# Gap analysis, positioning and execution plan for PLOS ONE (v2, 2026-11-26)

**This document supersedes** the framing in RESEARCH_BLUEPRINT.md, the "Security-Sensitive Invariance Learning" working title. The reasons are in [DECISION_LOG.md](DECISION_LOG.md) D007. The older documents are kept for history.
**Supporting files:**
- Frozen protocol: [PREREGISTRATION_V2.md](PREREGISTRATION_V2.md)
- Literature: [../paper/LITERATURE_2024_2026.md](../paper/LITERATURE_2024_2026.md)

## 1. Bottom line

The original plan rested on a bidirectional "security-sensitive invariance" method. That plan cannot be published as designed:
- The security-changing pairs were never human-adjudicated (gate G2 NO-GO).
- Every mitigation was designed after looking at the external set.
- The approach overlaps heavily with CheckList, contrast sets and recent rewrite-augmentation papers.

The data point to a different and stronger question:

> **When a phishing detector raises false alarms on AI-written legitimate email, is the cause the AI writing style, AI-authored content, or plain source shift? And can any mitigation reduce those false alarms without opening a bypass for AI-written phishing?**

This question suits PLOS ONE. That journal judges rigour, valid conclusions and data availability, not perceived impact, and it publishes null results. The question has practical weight because:
- LLM-written email is now the norm on the malicious side: at least about 51% of spam was LLM-written by April 2025 (Hao et al., IMC 2025).
- Legitimate senders use the same tools.

## 2. What Study 1 (N05–N14, exploratory) already shows

| # | Observation | Source file |
|---|---|---|
| 1 | **Paraphrase barely matters in-source.** D2 GPT-4o, DeepSeek and randomapi rewrites change at most 1 of 142 legitimate decisions and 1 of 162 phishing decisions. Exact McNemar p = 1 and the 95% CI of ΔFPR is [0, 2.1] pp | `phishing_n10_safe/table02_paired_exact_tests.csv` |
| 2 | **An external AI corpus produces severe false alarms.** At τ5 from D2 validation, E-PhishLLM-EN (5,506 legitimate) has FPR between 77.2% (NB) and 97.3% (char LR). DistilBERT gives 87.1% and 93.6%. Recall stays at about 98–99.5% | `phishing_n08_safe`, `phishing_n12_safe` |
| 3 | **Ranking survives and the threshold does not.** External AUROC is about 0.95, yet FPR at the frozen threshold is 89%. This matches CyberCane's calibration-transfer finding | `phishing_n08_safe/external_model_metrics.csv` |
| 4 | **Cue inversion (descriptive).** 77% of D2 legitimate emails contain a URL, against 10% of E-PhishLLM legitimate emails. Within D2, legitimate emails without a URL have 21% FPR and those with a URL have 8% | `phishing_n13_safe` |
| 5 | **Every mitigation trades.** Benign-rewrite augmentation reaches 66% FPR and 98.3% recall. Benign consistency reaches 47% FPR and 98.1% recall. Lexical evidence proxies reach 12% FPR but only 72% recall | `phishing_n11_safe`, `phishing_n14_safe`, `phishing_n09_safe` |

**Why Study 1 alone is not enough:**
- E-PhishLLM differs from D2 in *both* authorship and source, so the two are confounded.
- The test sets are small (142 and 162).
- There is a single split and only two transformer seeds.
- No per-row predictions were kept, so models cannot be compared with paired tests.
- External outcomes were inspected before the mitigations were designed.

## 3. What is established (no novelty claim possible)

Each item lists the papers that establish it. Details are in the literature file.
- LLM rephrasing degrades detectors: Afane 2024; Ferrell 2025; Thapa 2025; Hocevar 2025; SoK 2025; EdgeGuard 2026.
- Cross-corpus collapse and corpus-artifact learning: E-PhishGEN 2025; Bhuiyan 2026; Alisoy 2026; IJACSA 2026.
- Threshold and calibration transfer failure: CyberCane 2026; Litvak 2026.
- Rewrite augmentation: Ferrell 2025; Nance 2025; Tran-Truong 2027.
- Calibrated selective cascades: Electronics 2026.
- LLM-as-detector: Koide 2026; Zhang 2025; LLM-PEA 2025.
- Invariance and counterfactual testing as a paradigm: CheckList, contrast sets, CAD.

## 4. Gaps this paper fills

| Gap | Evidence that it is open | How Study 2 fills it |
|---|---|---|
| **G1: benign-side measurement** | Prior work reports miss rates on AI phishing. False alarms on legitimate AI mail appear only as small commercial-filter tests (Opara 2025, Yahoo 58–66%) or as accuracy for LLM judges (Zhang 2025) | ≥ 1,000 external legitimate parents per cell, frozen thresholds, Wilson CIs, alerts per 10k emails at realistic prevalence |
| **G2: style versus source confound** | Studies of degradation on AI mail compare different sources or generators | A factorial design. Source (IN, EXT) is crossed with authorship: **paired** rewrites of the same message, **subject-matched** from-scratch emails, and human originals. Generators are held out |
| **G3: failure decomposition** | CyberCane shows threshold transfer for *human* mail only | AUROC per cell compared with FPR at frozen versus oracle thresholds, plus controlled cue interventions (I1–I6) |
| **G4: two-sided mitigation accounting** | Mitigations are reported as accuracy gains within their own pipeline | Six pre-specified mitigations judged on AI-benign FPR **and** recall on AI-phishing from held-out generators, with non-inferiority margins |
| **G5: reproducibility** | E-PhishGEN notes missing code. CyberCane finds 96% split leakage | Pre-registration, hash-locked tests, MinHash and lineage decontamination, a REFORMS checklist, per-row predictions, and a Zenodo DOI |

**Candidate titles (to be chosen after the results, following the §7 claim table in the pre-registration):**
- *"Is it the AI or the inbox? Disentangling writing style from source shift in phishing detectors' false alarms on AI-written legitimate email"*
- *"False alarms on AI-written legitimate email: a pre-registered, leakage-controlled evaluation of phishing detectors"*

**Contributions (worded so they hold whichever way the results go):**
- **C1.** A factorial, leakage-controlled protocol and benchmark that separates AI style, AI-authored content and source shift on the benign side.
- **C2.** Pre-registered estimates of each factor's effect across 6 detector families and 2 training regimes.
- **C3.** A decomposition of the failure into ranking loss and threshold transfer, plus a cue-level mechanism.
- **C4.** A two-sided evaluation of mitigations.

## 5. Positioning against the closest work (for Introduction and Discussion)

| Paper | What they did | What we add |
|---|---|---|
| E-PhishGEN (AISec 2025) | Built E-PhishLLM and showed the cross-benchmark drop | Separate AI authorship from source. Benign-side frozen-threshold analysis. Paired design |
| CyberCane (arXiv 2026) | Thresholds calibrated on old public mail overrun on DataPhish 2025 | Show whether the overrun is specific to **AI-written** legitimate mail. Paired rewrites. Mitigation trade-offs |
| Bhuiyan & Bhuiyan (BDCC 2026) | Corpus-artifact learning across six human corpora | An AI-benign stratum, plus interventional cue tests rather than only corpus-ID probes |
| Ferrell et al. (CARS 2025) | Rephrased phishing *and* safe emails and reported accuracy drops | Frozen-threshold FPR, an external source, held-out generators, CIs and equivalence tests |
| Opara et al. (ESWA 2025) | Commercial filters falsely flagged legitimate AI emails | Controlled detectors, n ≥ 1,000, a mechanism, and mitigations |
| Tran-Truong et al. (ESWA 2027) | Leakage-resistant audit of rewrite augmentation | We test augmentation (M1, M5) as one of six mitigations under two-sided criteria. **Read the full text first** |
| Zhang et al. (IEEE Access 2025) | LLM detectors on human/AI × phishing/legitimate cells | Conventional and fine-tuned detectors, source separation, and frozen operating points |

## 6. Execution roadmap (each notebook has a GO/NO-GO gate)

All code goes in a shared package `src/phishbench/`, covered by unit tests. Notebooks import from it instead of copying cells, unlike the N10 style.

| Step | Notebook | What it does | Hardware | Gate to pass |
|---|---|---|---|---|
| 0 | — | Freeze PREREGISTRATION_V2 (owner approval, commit SHA, optional OSF). Build the `src/phishbench` library and tests. Fix the manifest bug | local and CI | Tests pass in CI |
| 1 | **N15** Data freeze v2 | Pinned downloads of D1 (Enron, SpamAssassin, CEAS_08, Nazario, Nigerian_Fraud), D2, LLMGen and E-PhishLLM. MinHash and lineage decontamination. Sampling. Locked-ID manifest | Kaggle CPU | Per-cell counts meet §3.1. Zero cross-split links |
| 2 | **N16** Generation | RW and DN with Qwen2.5-7B and Phi-3.5 (test-only) and OLMo-2 (train-only). Placeholder locking. §3.4 filters | Kaggle 2×T4, about 6–10 h | Pass rate ≥ 80% per generator. Exclusions reported |
| 3 | **N17** Human validation kit | Private annotation sheets. κ and preservation rate once both raters finish | local | κ ≥ 0.60. Preservation ≥ 90% |
| 4 | **N18** Detector training | D1–D5 under R1 and R2 with the M0–M5 variants. Validation-only selection | CPU + T4, about 8 h | Validation metrics and model hashes logged |
| 5 | **N19** Zero-shot judge | Granite-3.1-8B scores on validation and all cells | T4, about 2 h | Prompt and revision pinned |
| 6 | **N20** Confirmatory evaluation | **Single run** on locked cells. PE1, PE2, H2, H6. Per-row predictions | CPU | Locked manifest hash matches |
| 7 | **N21** Mechanism | Interventions I1–I6 and the ranking-versus-threshold decomposition | CPU / T4 | — |
| 8 | **N22** Mitigations | PE3 with M1–M6 on locked cells | CPU / T4 | — |
| 9 | **N23** Paper package | Tables, figures (TIFF for PLOS), REFORMS checklist, Zenodo release, Data Availability Statement | local | Reproducibility audit from a clean clone |
| 10 | Manuscript | PLOS LaTeX template, Vancouver references. Study 1 (exploratory) is reported first, then Study 2 (confirmatory) | local | Internal review using the §7 checklist |

The total GPU need is about 20–25 T4-hours, which fits within roughly one to two weeks of Kaggle's 30 h/week quota.

## 7. Reviewer-risk register (likely PLOS ONE objections and our answers)

| Likely objection | Answer built into the design |
|---|---|
| "Your training set is tiny (1,418 emails)" | R2 pooled multi-source regime, plus a fine-tuned RoBERTa and a zero-shot 8B LLM |
| "E-PhishLLM is synthetic and unrealistic" | It is DEV only. The confirmatory evidence uses paired rewrites of *real* Enron mail and a locked second corpus (LLMGen) |
| "The rewrites may change meaning or label" | Placeholder locking (byte-identical URLs), automatic filters, two-rater validation (κ) and sensitivity analysis |
| "HARKing / multiple comparisons" | Pre-registration before any new data exist, Holm correction within each primary family, and a pre-stated claim table. Study 1 is labelled exploratory |
| "No LLM baseline" | D6, a Granite-3.1-8B zero-shot judge. Generators and judge come from different model families |
| "Generators are small open models" | D2 already includes GPT-4o and DeepSeek rewrites, and LLMGen is OpenAI-generated. We chose open models for reproducibility and privacy, since no email text leaves Kaggle |
| "Enron is old" | That age difference is the source shift under study. Paired rewrites hold content and time constant. Listed as a limitation |
| "English only" | Limitation. Multilingual E-PhishLLM (Italian, German) is optional exploratory work |
| "Thresholds are arbitrary" | τ5 and τ1, full ROC and PR curves, and the label-free alert-budget mode (M6) |
| "The data are not shareable" | Data Availability plan: IDs, hashes, scripts, per-row predictions, and source DOIs or commits |
| "Dual-use" | No new phishing written from scratch, phishing rewrites not released, defanged examples, an ethics statement |
| "Is it novel versus CyberCane or E-PhishGEN?" | The §5 positioning table, and the factorial separation of authorship from source |

## 8. Mapping to PLOS ONE criteria

| PLOS ONE criterion | Where it is satisfied |
|---|---|
| 1. Original research | G1–G4 |
| 2. Not published elsewhere | arXiv preprint allowed |
| 3. Rigorous methods | Pre-registration, decontamination, CIs, equivalence tests |
| 4. Conclusions supported by data | §7 claim table in the pre-registration |
| 5. Intelligible | PLOS template, Vancouver references |
| 6. Ethics | §8 of the pre-registration |
| 7. Data availability | Data Availability Statement plus Zenodo |

**Fees.** The APC is USD 2,477. Check Research4Life Group A or B eligibility for the author's institution and country in the PLOS submission system. Do not assume it.

## 9. Execution workflow (Kaggle, run by the assistant once access is given)

1. The owner places `kaggle.json` at `C:\Users\DIGITAL OUTLET\.kaggle\kaggle.json`. It must never be pasted into chat or committed. The Kaggle account needs phone verification for GPU and internet access.
2. Each notebook is pushed as a **private** kernel with `kaggle kernels push`. Raw data are downloaded inside the kernel from pinned URLs and checked against their hashes. Private intermediates (generated text) pass between kernels as private kernel outputs or private datasets, and are never committed.
3. After a run, the assistant downloads the outputs. Only the safe folder is copied into the repository:
   - aggregates;
   - per-row predictions without text (once D009 is approved);
   - manifests.
4. Safe outputs are checked and then committed and pushed with a descriptive message. Failures are reported and logged, not hidden.

## 10. Owner actions (cannot be delegated)

- [ ] Approve or edit PREREGISTRATION_V2. That freezes it. Optionally create an OSF registration.
- [ ] Approve D009: public per-row predictions without text.
- [ ] Provide `kaggle.json` (local file).
- [ ] Recruit a second rater for N17 (400 pairs plus 100 DN emails, about 5–6 h each). Confirm the institution's policy on author annotation.
- [ ] Read the 7 "must-read" full texts listed in the literature file (or share PDFs you can access through your institution).
- [ ] Check APC waiver eligibility.
