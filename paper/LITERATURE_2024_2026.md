# Related literature 2024–2026: verified matrix and gap synthesis

**Compiled:** 2026-11-26. **Scope:** email phishing detection under LLM-era shift. It covers LLM-generated and LLM-rewritten phishing, false alarms on legitimate email, cross-corpus and calibration transfer, LLMs as detectors, and the methodological foundations we rely on.
**Companion files:** [STUDY_MATRIX_30.md](STUDY_MATRIX_30.md) is the earlier 30-paper matrix, and [references.bib](references.bib) holds its BibTeX. This file extends that matrix; it does not replace it.
**Status:** this is a structured narrative review. It is not a PRISMA systematic review.

## How the search was done

1. Every DOI already in the repository was re-checked against the Crossref API on 2026-11-26. All 30 resolved to real records, and none was fabricated.
2. We chased citations forward with the Semantic Scholar graph API. The seeds were E-PhishGEN (10.1145/3733799.3762967), PhishFuzzer (arXiv 2511.21448) and Opara et al. 2025 (10.1016/j.eswa.2025.127044).
3. We ran targeted web searches. The topics were: false positives on AI-written legitimate email, LLM paraphrase robustness, cross-corpus fragility, calibration transfer, zero-shot LLM detectors, and the prevalence of LLM-written email.
4. Every new entry was checked against Crossref (DOI) or the arXiv API (arXiv ID). The **Depth** column states how much of each paper was read:
   - **A**: abstract only.
   - **S**: abstract plus search snippets or author blog.
   - **T**: title and metadata only. A full-text read is needed before we cite any specific claim from it.
   - **F**: full text, as recorded earlier in STUDY_MATRIX_30.

**Overlap** shows how close each paper is to our reframed contribution, which is false alarms on AI-written *legitimate* email, with AI style separated from source shift:
- **HIGH**: must be cited and explicitly differentiated in the manuscript.
- **MED**: related.
- **LOW**: background.

---

## T1. LLM-generated or LLM-rewritten phishing versus detectors (attack side)

| Ref | Venue | What it shows | Limitation for our question | Overlap | Depth |
|---|---|---|---|---|---|
| Afane et al. 2024, arXiv 2411.13874 | arXiv | GPT-4 and Llama-3 rephrase Nazario phishing. SpamAssassin, Gmail, Proofpoint, SVM, LR and NB all degrade after rephrasing | Phishing side only, and an old source corpus | MED | S |
| Heiding et al. 2024, 10.1109/ACCESS.2024.3375882 | IEEE Access | LLM-devised phishing, human responses, LLM detection | User susceptibility is not detector FPR | LOW | S |
| Opara, Modesti & Golightly 2025, 10.1016/j.eswa.2025.127044 | ESWA | 47 stylometric features. Commercial filters were tested on GPT-generated phishing. The author blog reports that Yahoo flagged **58–66% of legitimate AI-generated emails** as spam | Commercial black-box filters with small n. Authorship and source are not separated, and no mechanism is given | **HIGH** | S |
| Ferrell et al. (CARS 2025), 10.1109/CARS67163.2025.11337548 | IEEE conf. | Three LLMs rephrase **both phishing and safe** emails. Accuracy drops 3–4% for BERT and 8–20% for Word2Vec and stylometric models, and retraining helps | Reports accuracy only, with no FPR on the benign class at frozen thresholds. Single source | **HIGH** | A |
| Nance et al. (CARS 2025), 10.1109/CARS67163.2025.11337886 | IEEE conf. | LLM data augmentation for phishing detection | Within-pipeline gains only | MED | T |
| Thapa et al. 2025, arXiv 2507.07406 | SNPD 2025 / arXiv | On paraphrased inputs, quantized LLMs degrade less than classical models (GPT-4 about −4 points versus SVM about −9) | Accuracy only | MED | S |
| Hocevar et al. 2025, 10.1145/3787279.3787313 | ACM conf. | Naive Bayes accuracy drops by more than 30 points on Llama-3.3-70B-modified spam | Spam rather than phishing, and the attack side only | LOW | A |
| Chen et al. 2025 (SoK), arXiv 2508.21457 | arXiv | Taxonomy. Benchmarks 5 academic and 5 industrial detectors across LLM generation methods. Robustness depends heavily on the generator | Mainly miss rates on phishing | MED | A |
| EdgeGuard 2026, 10.1007/s44443-026-01351-9 | JKSU-CIS | Source-aware protocol. LR and SVM trained on Enron and TREC. GPT-3.5 phishing stays easy (99.8% recall), while Llama-3.2 and Gemma-2 cause source-shift misses | Phishing side, and the protocol is the contribution | MED | A |
| Gutierrez et al. 2026, 10.3389/fdata.2026.1883452 | Front. Big Data | Cross-generator **authorship** attribution (AI versus human) among phishing only | Different task: not phishing versus legitimate | MED | F |
| Commey et al. 2026 (CuePhish), 10.1109/LCN67947.2026.11660775 | IEEE LCN | Interpretable stylometric cues for LLM-origin phishing | Authorship task | LOW | A |
| ICCSDFAI 2026, 10.1109/ICCSDFAI70505.2026.11648017 | IEEE conf. | 28 linguistic-forensic features, human versus GPT-4 phishing | Authorship task | LOW | A |
| Akdağ et al. 2026, 10.1109/ICCSDFAI70505.2026.11647988 | IEEE conf. | Turkish LLM-generated email dataset and benchmark | Non-English | LOW | T |

## T2. Benchmarks, datasets and prevalence

| Ref | Venue | What it shows | Relevance to us | Overlap | Depth |
|---|---|---|---|---|---|
| Pajola et al. 2025 (E-PhishGEN), 10.1145/3733799.3762967 | ACM AISec | Prior benchmarks are pre-2010 and mix spam with phishing. Detectors are near-perfect in-dataset but much weaker on the new **E-PhishLLM** (16,616 synthetic emails, 3 languages, MIT licence). The code is released | Shows the cross-benchmark drop but does not separate AI style from source. E-PhishLLM is our *development* external set | **HIGH** | F |
| Toth et al. 2025 (PhishFuzzer), arXiv 2511.21448 | arXiv | 3,300 seeds and 19,800 to 23,100 LLM variants with three classes and a human/LLM source field. Only Qwen-2.5-72B and Gemini are benchmarked | It is derived from D2 (all 3,075 D2 IDs reappear), so it **cannot** serve as an independent test. No conventional-detector FPR on LLM-valid mail | MED | A |
| MeAJOR, 10.1016/j.dib.2026.112595 | Data in Brief | Merged multi-source corpus | Optional additional source. Overlaps with Nazario, TREC and Enron must be checked | LOW | T |
| Park et al. 2026, arXiv 2609.30683 | arXiv | 2.9M real phishing emails from APWG, June 2025 to June 2026. Themes are diverse, and 73% use a URL-navigation call to action | Motivates modern-content realism. The data are not public | MED | A |
| **Hao et al. 2025 (IMC)**, 10.1145/3730567.3732922 | ACM IMC | At least about 51% of spam and about 14% of BEC were LLM-generated by April 2025 (Barracuda data) | **Motivation**: AI text in email is now the norm on the malicious side. Legitimate senders use the same tools | MED | S |
| LLMGen-Phishing-Email-Dataset (HF, rev d717e54) | Dataset | Synthetic phishing and legitimate emails, Apache-2.0. English comes from OpenAI and Chinese from DeepSeek | Becomes our **locked** AI-authored external test (English only). Only its schema has been audited, and no model scores exist | — | dataset card |

## T3. Cross-corpus shift, artifacts, leakage and calibration transfer

| Ref | Venue | What it shows | Limitation for our question | Overlap | Depth |
|---|---|---|---|---|---|
| **Bhuiyan & Bhuiyan 2026**, 10.3390/bdcc10070211 | BDCC (MDPI) | Six corpora. Single-corpus transfer is unstable, and leave-one-corpus-out pooled LR reaches F1 0.82–0.90. Corpus identity is learnable at 97–98%, with reliance on date, URL and header tokens. Includes prevalence shift and alert budgets | All human corpora, with no AI-written legitimate stratum | **HIGH** | S |
| Alisoy et al. 2026, 10.69760/lumin.2026003001 | Luminis | Transfer between two *synthetic* LLM corpora. External F1 drops from 0.93–0.97 to 0.85–0.90, with reliance on recurrent lexical templates | Synthetic to synthetic, with no human-versus-AI contrast | MED | A |
| **CyberCane (Hakim et al.) 2026**, arXiv 2604.23563 | arXiv | Detectors calibrated at **1% FPR on older public mail realise 20–23% FPR on DataPhish 2025**. The cause is calibration transfer, not ranking. LLM rewriting does not evade embedding detectors. A random split of DataPhish leaks 96% of its test set. Protocols were fixed in advance | Closest methodological neighbour. It does not separate AI authorship from source and does not test paired benign rewrites. DataPhish is from the D2/D3 family | **HIGH** | A |
| Electronics 2026 (Classical-First Selective Cascades), 10.3390/electronics15143051 | Electronics | A calibrated TF-IDF SVM matches DistilBERT in-domain. Covers cross-corpus testing, calibration and selective cascades | No AI-benign stratum | MED | A |
| IJACSA 2026 vol. 17 no. 10, paper 10, https://thesai.org/Downloads/Volume17No10/Paper_10-Email_Phishing_Detection_Using_NLP_and_Machine_Learning.pdf | IJACSA | Corpus-identifying tokens alone predict the class with ROC-AUC up to 0.85 | Provenance shortcut evidence for human corpora | MED | S |
| Le et al. 2026, 10.1109/ICITCOM70739.2026.11714372 | IEEE conf. | MIME, HTML and URL obfuscation raise FPR from 1.3% to 23.8%, and canonical normalisation restores it | A representation artefact rather than AI style. Motivates our M4 normalisation | MED | A |
| AURA (Berjawi et al.) 2026, arXiv 2609.19873 | arXiv | Uncertainty-routed URL plus transformer cascade. Holds F1 of about 0.94–0.95 on held-out NazPhish and GuenterTrap | Uses macro-F1 only | LOW | A |
| Bobe et al. 2026, arXiv 2601.10524 | arXiv | Fine-tuned Llama, Gemma and Mistral generalise only when trained on stylistically diverse data, and the effect depends on architecture | Supports the case for pooled or diverse training (our R2) | MED | S |
| **Tran-Truong et al. 2027**, 10.1016/j.eswa.2026.134963 | ESWA | Title: *"Within-pipeline gains, proximity-bound real-world detection: a leakage-resistant, provenance-audited evaluation of rewrite augmentation for phishing detection"* | Very close to our N11 augmentation result. **Read the full text before writing the Discussion** | **HIGH** | T |
| Robustness & interpretability under GenAI shifts 2026, 10.1016/j.cose.2026.105109 | Computers & Security | Per an earlier repo note: DistilBERT, a semantic-stability index, an SHAP/entropy gate and four LLMs | Full text is paywalled. Re-verify before citing details | MED | T |
| Kulal et al. 2025, arXiv 2510.11915 | arXiv | Preprocessing (spell correction, word splitting) against conventional, LLM and adversarial phishing | Phishing side | LOW | A |
| RMF-PC preprint 2026, preprints.org 202611.0528 | Preprint | Auditable paraphrase protocol for spam filters with a human-validated LLM paraphrase set (38 of 100 candidates valid). Separates denominators per research question | Spam, and only the miss side. Supports our human-validation design | MED | A |

## T4. LLMs as detectors (baselines that reviewers will expect)

| Ref | Venue | What it shows | Note | Overlap | Depth |
|---|---|---|---|---|---|
| Koide et al. 2026 (ChatSpamDetector), 10.1109/ACCESS.2026.3704566 | IEEE Access | LLM header and body reasoning detector | A zero-shot LLM baseline is now expected | MED | A |
| Zhang et al. 2025 (SME), 10.1109/ACCESS.2025.3540075 | IEEE Access | Base LLMs (Llama-3-8B best) on **human/AI × phishing/legitimate** cells | Accuracy and F1 per model. No frozen-threshold FPR and no source separation | **HIGH** | A |
| Hasan et al. 2025 (LLM-PEA), arXiv 2512.10104 | arXiv | GPT-4o, Claude and Grok under rephrasing, prompt injection and multilingual attacks | Phishing side | LOW | A |
| Litvak 2026, arXiv 2603.25056 | arXiv | Synthetic 2,000-email benchmark in which 98.4% of legitimate emails have matching sender and URL domains. Low-FPR prompts are **benchmark-conditional** and FPR rises sharply on cross-domain legitimate mail | Direct evidence that FPR depends on the benign distribution | MED | S |
| Tan et al. 2026 (AgentPhishing), arXiv 2610.31404 | arXiv | Email agents under adaptive attack | Agent compliance rather than classification | LOW | S |
| Pan et al. 2026, 10.1016/j.eswa.2026.131507 | ESWA | Persuasion-principle quantification on 340k emails | Cue engineering is prior art | LOW | A |

## T5. Benign-side evidence: false alarms on AI-written legitimate text

| Ref | What it shows | Use in our paper |
|---|---|---|
| Opara et al. 2025 (blog: Yahoo 58–66% false flags on legitimate AI emails) | The only direct observation we found on *commercial* filters | Motivation. Our work adds n ≥ 1,000, frozen thresholds, a paired design and a mechanism |
| Zhang et al. 2025 | Human/AI × phishing/legitimate cells for LLM detectors | Shows the cells exist but not the style-versus-source question |
| Litvak 2026; CyberCane 2026 | FPR budgets break when the benign distribution moves | Calibration-transfer framing |
| Liang et al. 2023, 10.1016/j.patter.2023.100779 | Text detectors flag non-native writers as AI | **Fairness analogy**: penalising AI-assisted legitimate writers can fall unevenly on people who use LLMs to polish their English |

### T5b. Graded AI involvement and four-cell email corpora (added for v2.1)

| Ref | What it shows | Use in our paper | Overlap | Depth |
|---|---|---|---|---|
| Saha & Feizi 2025 (APT-Eval), arXiv 2502.15666, ACL Findings 2025 | 15K samples at graded AI-polish levels. AI-text detectors flag lightly polished human text as AI: GLTR flags 40.9% of "extremely minor" polish against 6.8% FPR on pure human text, and GPTZero flags 64.7% | **Methodological precedent for our L0–L4 dose design**. It covers AI-text detectors, *not* phishing detectors | **HIGH** (design) | A+S |
| Guo et al. 2025, arXiv 2506.03501 | Human involvement varies continuously, and detectors fail to measure it | Supports treating AI assistance as a graded variable | MED | A |
| PAN/ELOQUENT 2025 "Voight-Kampff" subtask 2 | Six degrees of human–AI collaboration | Context for graded authorship | LOW | S |
| Greco, Desolda, Esposito & Carelli 2024, ITASEC (CEUR Vol-3731, paper 41); data on Kaggle `francescogreco97/human-llm-generated-phishing-legitimate-emails` (CC-BY-NC-SA-4.0) | Human/LLM × phishing/legitimate cells, used for **authorship** detection (WormGPT-generated phishing) | Prior art for four-cell corpora. Its LLM-legitimate file becomes our **locked** AI-authored test (evaluation only) | **HIGH** | S |
| Kaggle `maarij/anti-pluto-email-corpus` (2026) | Masked human/LLM × benign/phishing JSONL | Provenance undocumented, so **excluded** (pre-registration §2.1) | — | metadata |
| Nazario phishing corpus, monkey.org yearly mboxes 2015–2025 (CC BY 4.0, README) | Hand-classified real phishing up to 2025 | Training (2015–2021), EXT-phish-H (2022), MODERN-phish (2023–2025) | — | README |

**What we did not find (as of 2026-11-26):** a study that measures false alarms on legitimate email by authorship (human, AI rewrite of the same message, AI written from scratch) across sources (in-distribution versus external), using paired tests at thresholds frozen on source validation. This absence holds only within the search described above and must be re-checked right before submission.

## T6. Methodological foundations we will follow

| Ref | Use |
|---|---|
| Kapoor & Narayanan 2023, 10.1016/j.patter.2023.100804 | Leakage taxonomy. Our rewrite-family grouping and decontamination address it |
| Kapoor et al. 2024 (REFORMS), 10.1126/sciadv.adk3452 | Reporting checklist, submitted as a Supporting Information file |
| Ribeiro et al. 2020 (CheckList); Gardner et al. 2020 (contrast sets); Kaushik et al. 2020 | Invariance and counterfactual testing are prior art, so we cite them and do not claim them |
| Geirhos et al. 2020 | Shortcut-learning framing |
| Saito & Rehmsmeier 2015, 10.1371/journal.pone.0118432 (PLOS ONE) | PR curves for imbalanced evaluation |
| Geifman & El-Yaniv 2019; El-Yaniv & Wiener 2010 | Selective classification and risk-coverage |

---

## Synthesis: what is saturated and what is open

**Saturated (no novelty claim possible):**
- "LLM rephrasing hurts detectors" (Afane, Ferrell, Thapa, Hocevar, SoK, EdgeGuard).
- "Cross-corpus performance drops" (E-PhishGEN, Bhuiyan, Alisoy).
- "Detectors learn corpus artifacts" (Bhuiyan, IJACSA 2026).
- "Augment with LLM rewrites" (Ferrell, Nance, Tran-Truong).
- "Calibrated selective cascade" (Electronics 2026).
- "LLM as detector" (Koide, Zhang, LLM-PEA).
- "Thresholds do not transfer" (CyberCane).

**Open (our gap):**
1. **Benign-side measurement.** Almost all prior work reports *miss* rates on AI phishing. False-alarm rates on *legitimate* AI-written email are rarely measured, and when they are, it is with small samples on commercial black boxes (Opara) or as accuracy for LLM judges (Zhang).
2. **Style versus source confound.** Papers that report degradation on AI emails compare different sources or generators, so AI writing style and corpus, topic, time or format shift move together. No study combines paired rewrites of the *same* legitimate messages with topic-matched from-scratch AI emails in an *external* source. Our preliminary data suggest the two effects differ sharply: paraphrase changes almost nothing in-source, while an external AI corpus produces 77–97% FPR.
3. **Failure decomposition.** It is not known whether false alarms on AI-benign mail come from ranking loss or from threshold and calibration transfer. CyberCane shows threshold transfer for human mail, and nobody has shown it for AI-benign mail.
4. **Two-sided mitigation accounting.** Mitigations are judged by accuracy gains within their own pipeline. Nobody reports FPR gained on AI-benign mail against recall lost on AI-phishing from held-out generators. That trade-off is the security risk: a model that learns "AI style ⇒ benign" hands attackers a bypass.
5. **Reproducibility.** E-PhishGEN laments missing code, and CyberCane finds 96% split leakage. A pre-registered, hash-locked, leakage-audited protocol is itself a valuable contribution for PLOS ONE.

## Must-read full texts before the Discussion is written

1. Tran-Truong et al. 2027 (ESWA), on rewrite augmentation. Closest to M1.
2. CyberCane 2026, on calibration transfer. Closest to the failure decomposition.
3. Ferrell et al. 2025 (CARS), which rephrased safe emails.
4. Opara et al. 2025 (ESWA). Confirm the exact legitimate-AI false-positive numbers and generator (GPT-4 versus GPT-4o).
5. Bhuiyan & Bhuiyan 2026. Check the artifact analysis method.
6. Robustness & interpretability under GenAI shifts 2026 (Computers & Security).
7. Zhang et al. 2025, for the cell construction of the human/AI × phishing/legitimate dataset.
