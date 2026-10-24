# Copy into IEEE Access LaTeX — integration instructions

The following two files are **ready to paste into a manuscript project**:
- \`paper/related_work.tex\` — English Related Work with \`\\cite{}\`, subsections, and a \`table*\`.
- \`paper/references.bib\` — BibTeX with DOI/URL for 30 cited studies.

## In the main IEEE Access template, not a replacement for the official class
1. Put \`related_work.tex\` and \`references.bib\` under \`paper/\` relative to the main \`.tex\`.
2. Add these packages in the preamble **only if not already loaded**:

\`\`\`latex
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}
\usepackage{cite}
% \usepackage{hyperref} % only if your template has not already loaded it
\`\`\`

3. Place the Related Work after Introduction:

\`\`\`latex
\input{paper/related_work}
\`\`\`

4. Place the BibTeX commands near the end of your main manuscript:

\`\`\`latex
\bibliographystyle{IEEEtran}
\bibliography{paper/references}
\`\`\`

5. Compile with a standard LaTeX/BibTeX workflow in the actual target class
(\`pdflatex\` -> \`bibtex\` -> \`pdflatex\` -> \`pdflatex\`), or use Overleaf Recompile.
With the IEEE Access official template, preserve its own reference/bibliography configuration and adjust the path instead of loading conflicting packages.

## Citation and clickable links
Use \`\\cite{pajola2025ephishgen}\` in the running text. \`hyperref\` (when supported by the template) makes in-text references clickable to their bibliography entries. DOI or \`url\` fields in \`references.bib\` provide the actual outbound source URLs. In a published journal manuscript, use numeric IEEE references rather than pasting raw HTTP links next to every sentence.

## Before paper submission
- [ ] Actual IEEE Access template compile succeeds without warnings from this input.
- [ ] BibTeX creates all 30 entries with no undefined citations.
- [ ] Reference author lists and dates verified against publisher Export Citation.
- [ ] M0 literature novelty gate complete; abstract-only claims appropriately qualified.
- [ ] Table fits two-column double-column width; no awkward overfull boxes.
- [ ] Fill in measured values only after actual experiments; manuscript currently claims NO empirical improvement.

## Current quality-check result
- GitHub read-back + static \`\\cite{key}\` / BibTeX key comparison: **all citation keys resolved** after first draft.
- Brace count for TeX and BibTeX: balanced in first draft; rerun check after edits.
- Full IEEE Access LaTeX compilation: **NOT RUN** here.
- Literature completeness: **M0 IN PROGRESS**; see [evidence audit](LITERATURE_EVIDENCE_AUDIT.md).

Never treat a working LaTeX file as peer-reviewed or already novel.

## Literature round v0.2 — 30 selected studies (2026-10-24)
- [30-study evidence matrix](STUDY_MATRIX_30.md) identifies task, contribution, exact novelty constraint, URL, and whether full text or only abstract was inspected for each source.
- [related_work.tex](related_work.tex) now cites **all 30 unique BibTeX entries** in six thematic subsections plus a comparable-task table.
- [references.bib](references.bib) contains exactly 30 entries; citation/brace/key checks passed on 2026-10-24.
- Automated [LaTeX smoke-test workflow](../.github/workflows/paper-latex.yml) compiles an ordinary article-based validation manuscript. This is **NOT** the journal's official IEEE Access class/word layout; test it separately before submission.
- Crucial correction: CheckList (ACL 2020) already defines invariance and directional expectation; Gardner/Kaushik similarly cover label-changing counterfactuals. Do NOT describe bidirectional behavior testing as a new concept.
- Some IEEE/Elsevier papers remain publisher-abstract only; their full methods are not claimed as reviewed. The literature gate cannot be marked GO based solely on this draft.
