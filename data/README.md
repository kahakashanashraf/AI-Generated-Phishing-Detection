# Data Workspace — PLOS ONE Phishing Research

**Canonical root for all D1–D5 dataset files, audits, annotations, splits and release-ready evidence.**
The public GitHub repository stores **structure, instructions, approved metadata and redacted Markdown receipts only**. Actual raw email/URLs/PII and restricted derived examples must remain local/private (Kaggle private input or controlled storage). The presence of folders does **not** mean data have been downloaded or accepted.

## Directory map
```text
data/
  CATALOG.md                # authoritative source IDs and scientific roles
  .gitignore                # prevent accidental committing of datasets
  datasets/
    D1_curated_emails/
    D2_harmj0y/
    D3_phishfuzzer/
    D4_llmgen/
    D5_gutierrez_origin/
      # EACH D* directory contains:
      # README.md: origin, use, risks, current status
      # raw/: original archives (private and unchanged)
      # interim/: parsed/normalized working copies (private)
      # processed/: vetted training-compatible examples (private)
  audit/
    receipts/               # canonical D1.md, _TEMPLATE.md; later D2..D5
    rights/                 # copyright, original licenses, restrictions
    schema/                 # column mappings, label semantics, missingness
    quality/                # non-sensitive audit summaries/checksum receipts
    lineage/                # de-duplication and family/group leakage evidence
    privacy/                # ethics, redaction and disclosure assessments
  splits/
    README.md               # frozen split conventions and hashes
    private/                # full per-record assignment files, do not commit
  annotations/
    README.md               # adjudication process + rubric links
    private/                # unreleased pair assignments and sensitive edits
  combined/
    README.md               # merged data only after cross-source audit
    private/
  releases/
    README.md               # eventual source code/data-access release plan
```

## Dataset status (ALL candidates)
| ID | Dataset | First use | Approved for training? |
|---|---|---|---|
| D1 | [Curated email corpora](datasets/D1_curated_emails/README.md) | Intake, baseline, cross-corpus test | NO |
| D2 | [HarmJ0y](datasets/D2_harmj0y/README.md) | Provenance/origin/rewrites | NO |
| D3 | [PhishFuzzer](datasets/D3_phishfuzzer/README.md) | Parent-linked mutation audit | NO |
| D4 | [LLMGen](datasets/D4_llmgen/README.md) | Auxiliary synthetic testing | NO |
| D5 | [Gutierrez](datasets/D5_gutierrez_origin/README.md) | AI-vs-human authorship only | NOT for primary task |

Full scientific purpose: [CATALOG.md](CATALOG.md) and [Dataset Playbook](../docs/DATASET_PLAYBOOK.md).

## No more repeated Kaggle setup
Use [Kaggle persistence + one-cell resume](../docs/KAGGLE_PERSISTENCE.md). If a verified private Nazario.csv is present under an attached Kaggle Input, the resume script symlinks it and skips unchanged cached audit results. No source dataset is automatically uploaded, downloaded or redistributed.

## Kaggle/local setup
Within a cloned repo, **no GPU needed**:
```bash
python scripts/init_data_workspace.py
python -m unittest discover -s tests -v
```
Put a privately downloaded D1 Nazario CSV in
`data/datasets/D1_curated_emails/raw/Nazario.csv` and run:
```bash
python scripts/audit_d1_preview.py --file data/datasets/D1_curated_emails/raw/Nazario.csv --sample-rows 2000 --output data/audit/quality/D1_Nazario_preview.json
```
The resulting JSON is private/ignored; copy **verified, redacted non-sensitive aggregate findings** into [audit/receipts/D1.md](audit/receipts/D1.md). Do not link live phishing destinations or publish raw messages. Kaggle `/kaggle/working` is ephemeral unless output is saved in an explicitly controlled/private dataset version.

### Rules
1. Raw originals immutable; compute source checksum before processing.
2. Never make a binary phishing label by mapping AI authorship or generic spam.
3. No model training before license, meaning, lineage and split GO gates.
4. Paraphrases/derived variants share the same parent/campaign group across train, validation and test.
5. Share sanitized metadata/hashes only after privacy and rights review. `.gitignore` cannot protect against `git add -f`, `git lfs`, notebook outputs or historical commits.
6. Legacy `src/audit.py` + `src/baseline.py` remain **phishing-only AI-origin attribution**, not the primary detector.

**M1 tracking:** https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection/issues/2
