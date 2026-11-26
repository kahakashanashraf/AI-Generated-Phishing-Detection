# Human validation: how to run it

This is the owner's guide to notebook 04. The protocol is in `docs/PREREGISTRATION_V2.md` §3.5, with the details in deviations 9–11. The code is in `phishbench/human_validation.py`.

**What the raters read: `docs/RATING_GUIDE.md`.** It holds every definition, rule and example.

## What is rated

| Sheet | Items | What the rater sees | Questions |
|---|---|---|---|
| RW | 400: 200 with a legitimate original and 200 with a phishing original | an original email and an AI rewrite of it (L3) | (a) intent preserved? (b) security-relevant element added or removed? (c) the rewrite's label |
| DN | 100 | one email an AI wrote from a subject line (L4) | plausible legitimate email? |

The items come from Qwen2.5-7B and Phi-3.5-mini, stratified by generator and source. They are shuffled and carry opaque IDs (`RW-001`, `DN-001`). Links are defanged.

## Before rating starts (deviation 10)
1. **Roles.** The team has three authors and no institution.
   - Two authors are the independent raters, **A** and **B**.
   - The third author is the **coordinator**. The coordinator distributes the workbooks, runs the extraction, and acts as adjudicator of last resort.
   - Record who takes which role in `docs/DECISION_LOG.md` (D015).
2. **Ethics.** No approval is sought, because there are no human participants: the raters are authors rating text. The manuscript explains this in its Ethics Statement (draft: `paper/ETHICS_AND_DECLARATIONS.md`). Confirm this route with PLOS ONE staff before submission.
3. **Check the kit run.** The kit kernel (`04-human-validation-kit`) has finished, and `results/04_human_validation/kit/run_manifest.json` is committed. That file holds `key_sha256`, which fixes the key before anyone rates.
4. **Nobody opens `key.csv`.** Only the score kernel reads it. This includes the coordinator.
5. **Raters stay blind by procedure.** The draw is reproducible from public code, so blinding is a promise, not a lock. Until the score run, raters A and B must not:
   - open the 04 kernel outputs on Kaggle;
   - open `key.csv`;
   - run the sampling code on the real data.
   They confirm this, and that they rated independently, with a dated line under D015 in `docs/DECISION_LOG.md` when the ratings are committed.

## Steps

1. **Find the workbooks.** The pipeline downloads the kit output to `AI-Generated-Phishing-Detection_private/04-kit_<timestamp>/private_04/`. It contains:
   - `rater_A.xlsx` and `rater_B.xlsx`, one per rater;
   - `practice_A.xlsx` and `practice_B.xlsx`, the practice round, plus `practice_key.csv`;
   - `key.csv`, the private key. **Nobody opens it.**
2. **Run the practice round first** (`docs/RATING_GUIDE.md` section 6).
   - Give `practice_A.xlsx` to rater A and `practice_B.xlsx` to rater B. Each rater fills it alone.
   - Run `python scripts/human_validation.py practice practice_A.xlsx practice_B.xlsx`.
   - Discuss every listed disagreement with the guide open. `practice_key.csv` may be opened at this point: it shows the original label of each practice item.
   - Clarify the guide wording at most once, as a dated commit logged in DECISION_LOG.
   - Commit `results/04_human_validation/practice/practice_ratings.csv`.
3. **Hand out the real workbooks.** Give each rater only their own file, through a private channel. These files contain email text, including phishing, so:
   - never upload them anywhere public;
   - never commit them.
4. **Rate independently.**
   - Each rater reads the `Instructions` sheet first, then fills every answer cell using the drop-down lists.
   - Raters must not discuss items until both are finished.
   - Expected effort: about 6–8 hours per rater, in several sittings.
5. **Extract the answers.** This keeps item IDs and answers only, with no text:
   ```
   python scripts/human_validation.py extract A path/to/rater_A.xlsx
   python scripts/human_validation.py extract B path/to/rater_B.xlsx
   ```
   The extractor refuses a workbook that has any missing or invalid answer.
6. **List the disagreements:**
   ```
   python scripts/human_validation.py disagreements
   ```
   This writes `results/04_human_validation/ratings/adjudication.csv`.
7. **Adjudicate.**
   - Raters A and B discuss each row together and fill `resolved` with one allowed value.
   - If they still disagree, the coordinator decides. The coordinator does not look at the key.
   - In `note`, write who decided (`raters` or `coordinator`) and, optionally, a few words of reason. Never put email text in it.
8. **Commit and push** the three files in `results/04_human_validation/ratings/`. The pipeline then runs `04-human-validation-score` by itself. You can also start it with:
   ```
   python scripts/pipeline.py --only 04-score
   ```

## What the score run reports
- **Agreement:** Cohen's κ with a bootstrap 95% CI, from the independent ratings. The target for (c) is ≥ 0.60. Gwet's AC1 and raw agreement are given alongside.
- **Label preservation per generator:** a Wilson 95% CI, where "unsure" counts as not preserved.
  - Below 90%, that generator's RW results become **sensitivity-only** in the paper.
- **Other rates:** intent-preserved, security-element-changed and DN-plausible.
- **Item file:** `items.csv`, with item IDs, metadata and answers but no text. The key is published at this point, after rating is complete.
