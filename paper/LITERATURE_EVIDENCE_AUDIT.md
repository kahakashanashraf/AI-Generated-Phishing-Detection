> **ARCHIVED first-pass audit (18 papers). The current 30-study version is [STUDY_MATRIX_30.md](STUDY_MATRIX_30.md). Do not treat the counts below as current.**

# Related-work evidence audit — M0 working record

**Search date: 2026-10-24. Status: DRAFT for manuscript, NOT literature novelty GO.**

## Deliverables now stored in GitHub
- [Related Work, manuscript LaTeX](related_work.tex) — original English prose organized by topic; comparative `table*` and `\cite{key}`.
- [BibTeX database](references.bib) — publication URLs, DOIs where available.
- This ledger documents **what was really accessible and read**; do not claim the full text of a restricted paper was reviewed.

## Meaning of access categories
- **FT-RW** = accessible HTML/publisher full text and relevant **Related Work/Literature** section read.
- **FT-SECTION** = accessible HTML full text and relevant method/result sections inspected, but work was peripheral or did not label a Related Work section.
- **PUBLISHER-ABSTRACT** = checked the publisher's abstract/metadata only; full text was blocked or not independently retrieved.
- **PREPRINT-FT** = arXiv HTML full text read; peer-reviewed version (if any) not independently inspected.
- A row marked PUBLISHER-ABSTRACT must never substantiate a detailed full-method claim absent an additional verified source.

## Directly relevant literature (NOT a claim of exhaustive systematic review)

| Key / date | Paper and persistent source | Primary task / contribution | Access | Implication |
|---|---|---|---|---|
| `fette2007learning`, 2007 | [Fette et al., Learning to Detect Phishing Emails](https://doi.org/10.1145/1242572.1242660) | Early supervised phishing-email feature modeling | bibliographic/publisher | Background only |
| `kavya2025review`, 2025 | [Kavya & Sumathi, Artificial Intelligence Review](https://doi.org/10.1007/s10462-024-11055-z) | Historical to modern phishing detection survey | FT-SECTION (review article; full HTML available) | Avoid sweeping 'first' claims |
| `weinz2025impact`, 2025 | [Weinz et al., ACM AsiaCCS](https://doi.org/10.1145/3708821.3736195) | Organizational LLM phishing / quishing effects | abstract + author institutional page | Threat relevance, NOT classifier performance |
| `opara2025stylometry`, 2025 | [Opara et al., ESWA](https://doi.org/10.1016/j.eswa.2025.127044) | Commercial filters; 47 stylistic features | PUBLISHER-ABSTRACT | Stylometry prior art |
| `ferrell2025rephrasing`, 2025 | [Ferrell et al., IEEE CARS](https://doi.org/10.1109/CARS67163.2025.11337548) | Both phishing and safe rephrased via 3 LLMs; retrain benefits | PUBLISHER-ABSTRACT; IEEE full text blocked | Direct overlap; cannot claim first rewriting robustness |
| `nance2025augmentation`, 2025 | [Nance et al., IEEE CARS](https://doi.org/10.1109/CARS67163.2025.11337886) | LLM-based phishing data augmentation | Publisher/bibliographic metadata only | Augmentation alone prior art; methods need full text |
| `pajola2025ephishgen`, 2025 | [Pajola et al., ACM AISec](https://doi.org/10.1145/3733799.3762967) | E-PhishGEN, multilingual E-PhishLLM, benchmark critique | FT-RW: ACM accessible indexed full-text sections 2.2–2.3, data/method discussion | Cross-dataset/synthetic data already covered; spam-phish conflation |
| `kulal2025robust`, 2025 | [Kulal et al., arXiv](https://arxiv.org/abs/2510.11915) | NLP preprocessing, adversarial/LLM phishing detection | PREPRINT-FT: Section 2 (2.1–2.3) read | Advanced preprocessing already tested |
| `li2024mage`, 2024 | [Li et al., ACL](https://aclanthology.org/2024.acl-long.3/) | Cross-model generalization for AI-vs-human text attribution | ACL official abstract & metadata | Different task from maliciousness |
| `gutierrez2026crossmodel`, 2026 | [Gutierrez et al., Frontiers](https://doi.org/10.3389/fdata.2026.1883452) | 3-generator AI-vs-human authorship among phishing; target threshold calibration | **FT-RW** Section 2.1–2.4 + methodology/results | Phishing-only data never supplies benign FPR; target adaptation not zero-shot |
| `toth2026phishfuzzer`, 2026 | [Toth, Bisztray & Gruschka, arXiv HTML](https://arxiv.org/html/2511.21448) | Three-class metadata-rich 3300 parent / 19800 variant corpus; LLM classification benchmark | **PREPRINT-FT** Section II-A/II-B, methodology | Need verify semantic preservation of URL/sender mutations |
| `bhuiyan2026fragility`, 2026 | [Bhuiyan & Bhuiyan, BDCC](https://doi.org/10.3390/bdcc10070211) | Leave-one-corpus-out, source artifacts, prevalence and alert budgets | Detailed publisher-indexed abstract, methods/results snippets; direct page rate-limited | Strong competing evaluation; cross-corpus + prevalence NOT novel |
| `arharbi2026shifts`, 2026 | [Arharbi & El Qadi, Computers & Security](https://doi.org/10.1016/j.cose.2026.105109) | GenAI adaptive shift, SHAP+entropy gate, SDI, DistilBERT | PUBLISHER-ABSTRACT and public section snippets; paywalled full text | Risk/XAI + shift NOT new; December 2026 issue shown but online entry visible by October |
| `guo2017calibration`, 2017 | [Guo et al., ICML](https://proceedings.mlr.press/v70/guo17a.html) | Neural probability calibration / temperature scaling | Publisher proceedings text/metadata | Confidence metrics are established methods |
| `geifman2019selectivenet`, 2019 | [Geifman & El-Yaniv, ICML](https://proceedings.mlr.press/v97/geifman19a.html) | Risk--coverage / reject-option classifier | Publisher proceedings text/metadata | Abstention is established prior art |
| `saito2015precision`, 2015 | [Saito & Rehmsmeier, PLOS ONE](https://doi.org/10.1371/journal.pone.0118432) | PR curve under imbalance | bibliographic/abstract | Evaluate rarity-aware operational metrics |

## High-priority papers found, NOT YET manuscript-cited or fully reviewed
| Work | Source | Read status | Why it matters |
|---|---|---|---|
| **CuePhish** (IEEE LCN 2026) | https://doi.org/10.1109/LCN67947.2026.11660775 | Publisher abstract only; author list not verified | Stylometric urgency cue, evasion, adversarial hardening, origin-only labels; obtain full BibTeX |
| **The Anatomy of a Resilient Phishing Detector** (Frontiers, 2026) | https://doi.org/10.3389/fcomp.2026.1836418 | FT-RW Section 2 and counterfactual analysis inspected; **URL-only** task, not email | Shows counterfactual flips and explainability studied in phishing URLs; do not mischaracterize as email counterfactual method |
| **ChatSpamDetector** (IEEE Access 2026) | https://doi.org/10.1109/ACCESS.2026.3704566 | Publisher abstract only | LLM-as-detector with headers and reasoning (email intent, unlike authorship-only) |
| **SLR on LLM phishing** (Array 2026) | https://doi.org/10.1016/j.array.2026.100775 | Publisher abstract only | 36 included studies; search citations for missed competitors |
| **Cross-corpus lightweight detectors** (Alisoy 2026) | https://doi.org/10.69760/lumin.2026003001 | Publisher HTML abstract with metrics read | External synthetic corpus may share provenance; do not call it independent real-world shift |

## Four methodological non-negotiables learned from papers' related-work and methods
1. **Fix task semantics.** One study's AI-vs-human origin classifier must not be compared numerically with another's phishing-vs-benign classifier as though scores were comparable.
2. **Avoid unsupported novelty.** E-PhishGEN, CARS 2025, PhishFuzzer, Frontiers 2026, BDCC 2026, and Computers & Security 2026 already overlap proposed dataset, augmentation, generator, source shift, calibration, and risk.
3. **Measure pair validity and parent leakage.** Original IDs permit grouping but not automatic proof of unchanged security intent; code must fail closed on unresolved pair edits.
4. **Freeze target thresholds.** Calibrating using the exact target generator in the final test invalidates a claim of label-free zero-shot generalization. Test FPR must be measured, not promised under shift.

## Remaining M0 scientific reviewer checks
- [ ] Inspect the **full text** of CARS 2025 rephrasing and augmentation papers if obtainable from authors or a legal open copy; update method comparison.
- [ ] Verify full author list/BibTeX of CuePhish and read its method/related-work section (publisher abstract alone insufficient).
- [ ] Inspect Arharbi 2026 full method (only abstract/snippets currently accessible) to quantify overlap with bidirectional style/security edits.
- [ ] Add at least 5 more high-signal directly relevant studies using backward/forward citations; record actual search scope/date and exclusion criteria, not an invented PRISMA review.
- [ ] Validate bibliography via actual IEEE LaTeX compilation with the target class (only static brace/citation checks performed so far).
- [ ] Declare research G0 GO/NO-GO **after** close competitor comparison. Do not tick completed milestone prematurely.

## Wording policy for paper
Use cautious phrases such as: 'This study investigates...', 'The available literature motivates...', 'We evaluate whether...'. Do NOT write 'we are the first...', 'our novel solution achieves...', or 'all prior work fails...' prior to verified evidence.
