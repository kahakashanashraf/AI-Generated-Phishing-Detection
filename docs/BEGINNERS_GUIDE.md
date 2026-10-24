# Start Here: A Beginner's Research Course (PLOS ONE-level scientific and reproducibility rigor)

This is your **first journal project**; every step must teach (1) why, (2) how, (3) what output means, (4) what could go wrong, and (5) how to validate. Do not confuse **code uploaded** with **research result obtained**.

## The research in everyday language
We want to detect **phishing vs legitimate** emails even when an unseen LLM rewrites their wording. The detector must be *invariant* to harmless style changes but *sensitive* when verified security meaning changes. It must not falsely flag legitimate AI-written emails just because they sound AI-written.

**Important:** `src/baseline.py` currently solves a **different auxiliary task**: AI-origin vs human-origin among phishing emails. It must not be used as the primary phishing detector until a separate proper classifier is implemented.

## Terms you need (learn each before running experiments)
- **Phishing:** deceptive action request for theft or unauthorized interaction. **Legitimate:** bona-fide email. **Spam** is not automatically phishing or legitimate.
- **Label:** what we ask the model to predict, NOT what generated a message.
- **Origin:** AI or human author; **generator:** which model/pipeline performed a rewrite.
- **Original / parent / variant:** source email and all derived messages. One family must stay in the *same* partition.
- **Train:** examples for fitting. **Validation:** examples for choosing hyperparameters/threshold. **Test:** locked final exam, never used to tune.
- **Leakage:** original and paraphrase in different splits; duplicated email corpus; selecting on held-out test results.
- **LO-G:** leave one verified generator out; **LO-C:** leave one corpus out; **joint shift:** both held out, only when data supports it.
- **FPR:** of legitimate messages, fraction falsely called phishing. **Recall:** of phishing messages, fraction caught.
- **Calibration:** match between predicted confidence and empirical likelihood; **abstention:** defer uncertain messages for review.
- **Ablation:** remove one method component to see if it actually helps. **Confidence interval:** uncertainty due to sample variation.

## Your personal Kaggle setup (already reported, not rerun by us)
Kaggle showed: Python 3.13.15; 2 x Tesla T4; NumPy 2.1.3; pandas 2.3.3; sklearn 1.6.1; PyTorch 2.11.0+cu128. This establishes GPU visibility, **not** model or dataset validation.

In a new Kaggle notebook (CPU initially):
```python
!git clone https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git
%cd AI-Generated-Phishing-Detection
!pip install -r requirements.txt
!python -m unittest discover -s tests -v
!python scripts/check_kaggle.py
```
If you already cloned it, inside that folder run `!git pull --ff-only` instead. Internet access may be required to clone. Never paste Kaggle/GitHub tokens into a public notebook. Turn GPU on only for transformer stages.

## Lesson sequence (one lesson = one milestone issue)
| Lesson | Why | Your action | Deliverable to show me | Pass condition |
|---|---|---|---|---|
| 0 Research problem | Accuracy is not novelty | Read `docs/RESEARCH_BLUEPRINT.md`; read related 2025 IEEE CARS and 2026 Frontiers abstracts; explain AI origin vs phishing label | Short written RQs/hypotheses | All target labels and knowledge gap consistent |
| 1 Dataset literacy | Bad data invalidates everything | Inspect D1 → D2 → D3 using `docs/DATASET_PLAYBOOK.md` | Receipt for each D1/D2/D3; metadata counts and rights | Real fields, label provenance, parent IDs, license status verified |
| 2 Paired data & annotation | Not all rewrites preserve intent | Audit matched parent-original/variant pairs; develop adjudication rubric | Validation panel and disagreement report | Style vs security-changing pair distinction trustworthy |
| 3 Leakage-proof evaluation | No testing on memorized siblings | Deduplicate globally, split by original/campaign/source/generator | Split manifest hash and overlap tests | No group/test/target leakage |
| 4 Simple baselines | Honest reference before new model | Run TF-IDF+LR/linear SVM with real phishing label | Confusion matrices and per-group metrics | Fully reproducible leakage-safe run |
| 5 Encoder & baselines | Compare to strong NLP methods | Fine-tune DistilBERT/MiniLM on a T4 | Config, seed, checkpoints, logs | Equal split; 3 seeds when feasible; no target tuning |
| 6 New method | Prove what helps, not just new name | Compare plain, style-only, sensitivity-only, combined, matched augmentation | Ablation and paired error/CI | Real improvement or correctly reported negative result |
| 7 Unseen+risk | Deployment realism | LO-G, LO-C, joint where possible; freeze threshold; simulate human review | Worst-group recall@FPR, risk–coverage, AI-benign FPR | All claims match actual source/generator provenance |
| 8 Paper | Turn evidence into a narrative | Write structured manuscript with figures, limitations, ethics | Draft + citation/evidence map | Internal strict GO/NO-GO review passed |

## Rule for checking any box
A box becomes `[x]` only with **(a)** an artifact (file, notebook, figure or receipt), **(b)** a test/audit, **(c)** a reproducible run URL or commit ID, and **(d)** dated GO/NO-GO note. If any is missing, leave `[ ]` and say what's missing. Tests failing isn't 'done'.

## Target-journal compliance first
PLOS ONE requires sufficient data and code access to reproduce the findings. See [journal target instructions](PLOS_ONE_TARGET.md). Verify underlying data copyright, privacy, de-identification, and third-party access instructions before training. A new model is optional; scientifically sound evidence is not.

## Your first hands-on activity — no GPU training
1. Open https://zenodo.org/records/8339691.
2. Write the file names and dataset source histories in `data/audit/receipts/D1.md`.
3. Record the visible file checksums, license status and how labels are defined. **Mark UNKNOWN instead of guessing**.
4. Inspect a tiny, sanitized sample; never click links inside emails.
5. Report columns, number of rows by class/source, missing fields, apparent duplicated copies.
6. Give me the receipt and sanitized summary. I will audit it and write the exact next code-level patch/test if necessary.

## Researcher habits to follow every session
- Record date, dataset version/SHA256, repository commit, random seed, Python/library versions, notebook version, commands and known failures.
- Always compare models with **same test set, same information access and similar compute budget**.
- Separate full-text-only vs email metadata models; metadata availability differences can fake an improvement.
- Don't ever call `cross-dataset` results valid when overlapping source corpora remain.
- Report what did not work. Statistical significance on *parent-group* resamples, not individual paraphrase rows.
- Update the linked milestone GitHub issue as a learning journal. The paper is built from these evidence receipts.

## Where every dataset file goes (new)
The single canonical [data workspace](../data/README.md) houses all five sources. On Kaggle, run `!python scripts/init_data_workspace.py`. Keep D1 Nazario under `data/datasets/D1_curated_emails/raw/Nazario.csv`, audit locally using `!python scripts/audit_d1_preview.py --file data/datasets/D1_curated_emails/raw/Nazario.csv --output data/audit/quality/D1_Nazario_preview.json` and only copy a redacted metadata summary into `data/audit/receipts/D1.md`. Do not train yet. Check `.gitignore` before committing anything.
