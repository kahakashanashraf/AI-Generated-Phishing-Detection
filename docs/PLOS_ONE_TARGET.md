# PLOS ONE — Journal Target and Compliance Plan (decision 2026-10-24)

## Target
**Primary target: PLOS ONE** (Research Article, engineering/computer security). Supersedes IEEE Access as the submission target. Do NOT change the underlying research question, falsifiability, lineage controls, or datasets simply to chase acceptance.

**Working scientific question:** Can a phishing-vs-legitimate email detector be stable across human-validated, security-equivalent rewrites, respond correctly to adjudicated security-changing counterfactuals, and retain useful reliability under source/generator shift and realistic false-alarm constraints?

## Why fit / what does not change
- PLOS ONE evaluates originality, ethical conduct, technical rigor, conclusions supported by data, clarity and availability; editorial decisions emphasize scientific rigor rather than subjective importance or novelty. It accepts negative or null original findings when valid. This does NOT exempt the paper from original research or meaningful evidence.
- Excellent reproducibility, leakage-controlled splits, source/generator provenance, validated pair labels and reasonable baselines are still mandatory. Do not report origin-attribution performance as phishing detection.
- Dataset provenance/copyright/privacy and open-access reproducibility are now even **more central** to the submission decision.

Official sources:
- https://journals.plos.org/plosone/s/criteria-for-publication
- https://journals.plos.org/plosone/s/editorial-and-peer-review-process
- https://journals.plos.org/plosone/s/what-we-publish
- https://journals.plos.org/plosone/s/submission-guidelines
- https://journals.plos.org/plosone/s/latex
- https://journals.plos.org/plosone/s/data-availability
- https://journals.plos.org/plosone/s/materials-software-and-code-sharing
- https://plos.org/fees/

## Research-design pivot (IMPORTANT)
Our main contribution can be a **rigorously evaluated empirical security study** and reproducible benchmark/protocol if the new training objective does NOT outperform strong baselines. Do **not** force model complexity. The research must still be original and substantive, with defensible source selection and new evidence not merely copies of past papers.

M0 (literature): keep the 30 curated papers + originality check; do not claim a new principle for invariance/directional edits (CheckList and contrast sets precede us). We do not need invented SOTA.
M1 (data): license/provenance/ethics audit and an **open minimal dataset access plan** are now blocker-level.
M2/M3 (pairs/splits): human-adjudicated label validity, original/campaign-disjoint splits, leak checks, locked tests.
M4 (baselines): TF-IDF, linear SVM, DistilBERT and matched-input baselines.
M5/M6 (methods/shift): run proposed security-sensitive constraints only if validated pairs exist; report negative results openly; rigorous unseen generator/corpus and false alarm metrics.
M7: uncertainty estimates based on independent parent/campaign units, multiplicity awareness, error analysis and resource usage.
M8/M9: PLOS ONE manuscript, ethics statements, Data Availability Statement, code release/licensing, repository DOI and reproducibility audit.

## PLOS ONE writing and typesetting
Use published manuscript order and official PLOS ONE template, not IEEEtran:
- Title page, abstract (maximum 300 words), introduction (context plus concise key literature), Materials and methods, Results, Discussion, optional Conclusions, Acknowledgments, References, and Supporting Information captions as needed.
- Existing 30-paper `paper/related_work.tex` is content input, not final formatting. Adapt its research-gap synthesis into Introduction or an appropriately justified dedicated prior-work subsection. Do not place a two-column `table*` blindly into the PLOS one-column style; convert to the template-compatible editable table placed immediately after first citation.
- References: PLOS uses **Vancouver/numbered citation-sequence** (numbered [1], [2], ... by order of first appearance), not IEEEtran formatting. Reuse `paper/references.bib` but select the **BibTeX style distributed with the official PLOS LaTeX template**. Do NOT assume that `IEEEtran.bst` is valid.
- PLOS LaTeX page: https://journals.plos.org/plosone/s/latex . Initial LaTeX submission PDF, figure files uploaded separately; after acceptance upload sources. Official formatting must be tested before submitting.
- No page/word limit stated, but be concise. Tables should follow the first referencing paragraph.
- The 30-study reference matrix can remain in the repo; only the most task-comparable studies belong in the main table, with broader information in Supporting Information if permitted.

## Reproducibility and data compliance — hard gate
PLOS expects the **minimal data required to reproduce reported findings** publicly accessible upon publication, except justified legal or ethical restrictions. Third-party data can be accessed from original sources when redistribution prohibited; provide exact access instructions, sources/DOIs, revision hashes and a clearly described restriction in the Data Availability Statement. Do not claim 'available on request from authors' without validating PLOS policy; controlled access via a non-author committee may be required.
- D1–D5 are *candidates* until label rights and provenance vetted. Public availability of a dataset does not prove redistribution permission.
- Deposit distributable data derivatives that are non-sensitive (de-identified labels, sample hashes, split/fold IDs, annotation protocol, synthetic benign examples where licensed, aggregate + per-sample predictions only if non-sensitive and lawful), and code/configs with a tagged commit + Zenodo DOI if feasible.
- Emails may contain personal contact information and live suspicious links. Do not put raw original emails, credentials, active phishing URLs, or identifying headers in public GitHub/dataset releases.
- If restrictions prevent sufficient independent reproducibility, do not submit: select different permissible corpora/derivatives or contact the journal for a compliant access mechanism.
- Code used for the findings should be publicly documented and shared, unless lawful exceptions justified.
- Annotation ethics: explain consent/usage rights, review arrangement, disclosure of human evaluation and potential privacy issues; do not assert IRB approval/exemption if not obtained.

## Fees (checked 2026-10-24)
Current general PLOS ONE APC for standard articles (without institutional arrangements or assistance): **USD $2,477**, assessed at applicable submission-date rate and normally payable on acceptance. This is not an unconditional charge for every author:
https://plos.org/fees/
Research4Life: eligible Group A institutions with no external funding may publish free; eligible Group B PLOS ONE authors without external funding have a listed reduced rate of $940. Institution/country status and eligibility must be verified in the official PLOS/Research4Life process, **not presumed from the user's location**. Apply at submission for assistance; PLOS also has a separate fee assistance process.

## PLOS-specific final submission checklist
- [ ] Is the research question original and clearly stated with no exaggerated novelty?
- [ ] Is the dataset and each human-generated synthetic subset legally and ethically reusable, with a compliant Data Availability Statement?
- [ ] Can an outside reviewer reproduce tables and figures from released scripts, metadata, and accessible original data?
- [ ] Have all independent/test/annotation units, statistics, and reporting checks passed?
- [ ] Are limitations, negative findings, and excluded/ambiguous pairs transparently documented?
- [ ] Are manuscript sections, references, figures, tables and supporting captions consistent with current PLOS instructions?
- [ ] Is the official PLOS LaTeX template used and compiled?
- [ ] Has the fee/waiver option been checked at submission for the author institution?

**Status:** TARGET SWITCH RECORDED. **No dataset/model GO yet; M0-M9 milestones are not marked complete.**
