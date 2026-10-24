# PLOS ONE — Manuscript integration (current target, 2026-10-24)

**Research and citation content are preserved.** The earlier IEEE-style `related_work.tex` compiles in a generic two-column smoke test; the fact it compiles does **NOT** make it formatted for PLOS ONE.

## Existing reusable research artifacts
- [30-study Related Work text](related_work.tex): evidence-based literature prose, closest-work comparison table and **a separate Our Research Positioning table**; contains `\\cite{key}` entries.
- [BibTeX bibliography (30 papers)](references.bib): reusable source metadata.
- [Study-level evidence matrix](STUDY_MATRIX_30.md).
- [PLOS ONE policy and data-sharing plan](../docs/PLOS_ONE_TARGET.md).

## Submit using the OFFICIAL PLOS LaTeX template
1. Download official PLOS LaTeX ZIP and bundled Vancouver-compatible `.bst` from https://journals.plos.org/plosone/s/latex . Do not substitute an IEEEtran class or IEEEtran bibliography style for the final submission.
2. Keep a top-level paper structured with title page, abstract (max 300 words), introduction, Materials and Methods, Results, Discussion, optional Conclusions, acknowledgments, references and supporting-information captions.
3. Adapt the content of the existing Related Work into a concise Introduction literature synthesis (or a justified prior-work subsection). The current `\\section{Related Work}` was drafted for IEEE; fix headings for PLOS.
4. Two editable `table`/`tabularx` tables are now in the section (labels `tab:related_comparison`, `tab:our_positioning`); each is referenced in text and follows its discussion. Inspect whether they fit and float appropriately in the **official PLOS** template; adjust if needed.
5. Configure bibliographic citation format from the template. PLOS requires numbered, first-appearance citation sequencing and Vancouver-style bibliography. Reuse `references.bib` metadata but NOT `\\bibliographystyle{IEEEtran}` from the legacy test.
6. Initial LaTeX submission: PDF of manuscript text, captions, tables and references; submit figure files separately as instructed by PLOS. The source files are required after acceptance.
7. Verify exact rules on official page again immediately before actual submission.

## Data and code availability
Read [Data Availability policy](https://journals.plos.org/plosone/s/data-availability) and [Code policy](https://journals.plos.org/plosone/s/materials-software-and-code-sharing). Prepare dataset revision hashes, source access rights, de-identified usable annotations, run settings, predictions/figure data, and a DOI-archived public source release if lawful.
An 'available upon reasonable request from the authors' placeholder is NOT a solution to data-sharing rights. Third-party/source-holder restrictions or formal committee mediated access must be documented.

**Provisional Data Availability Statement template:** [DATA_AVAILABILITY_TEMPLATE.md](DATA_AVAILABILITY_TEMPLATE.md). Do not publish that template unfilled.

## Validation ledger
- [x] 30 distinct citations + 30 BibTeX entries checked at source level (metadata completeness still needs final publisher verification).
- [x] Historical generic two-column LaTeX/BibTeX smoke compile succeeded: https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/actions/runs/40103390554
- [ ] PLOS official class/style compilation: **NOT RUN**.
- [ ] Bibliography output in Vancouver format from official `.bst`: **NOT RUN**.
- [ ] Correct table placement/figure naming/title page/data and code declarations: **PENDING**.
- [ ] Final manuscript with source verified methods and results: **PENDING**.

## Retained history
The original draft was prepared under IEEE Access as a target, including the `paper/validation_main.tex` generic two-column validation. That was a layout/conversion convenience only. [Decision D006](../docs/DECISION_LOG.md) logs the new PLOS ONE target. Do not confuse an existing IEEE style test with a ready-to-submit PLOS ONE document.

## Research positioning table — added 2026-10-24
- `Table~\\ref{tab:our_positioning}` is separate from `Table~\\ref{tab:related_comparison}`.
- It distinguishes **prior established work**, **our prospective research question/protocol**, and **specific evidence required before claiming a contribution** for five strands: authorship, rewriting, corpus/generator shift, counterfactuals, and risk controls.
- This is a research hypothesis and experiment plan, **not** a measured improvement or a claim of first invention.
- `paper/validation_main.tex` now uses a generic **single-column** smoke layout and numbered `unsrt` bibliography so it better resembles PLOS formatting; it is **not** the PLOS official class or `.bst`.
