# Kaggle Persistence and One-Cell Resume (2026-10-27)

## UI correction from Kaggle editor screenshot (2026-10-27)

Researcher's live Kaggle Notebook editor shows **Settings** with Internet, Accelerator, and Environment Preferences only; **no Persistence menu is exposed**. Do NOT tell this user to find a control that is not present. `Environment Preferences > Pin to original environment` changes the environment/image selection, **NOT data-file persistence**.

The notebook sidebar shows **Input: No input attached**, while **Output: 8.3 MiB / 19.5 GiB** and the running quality audit reports Nazario checksum and 1,565 rows. The 8.3 MiB shown does not, by itself, prove those files are persisted in a published notebook Version or that they may be lawfully republished.

**Immediate workflow without Persistence:**
1. Keep the first cell containing the one-cell clone/update + `kaggle_resume.py` logic.
2. Use **Save Version > Quick Save** to preserve notebook code/progress; check any advanced options and never presume it preserves live working files.
3. **Do not save/share notebook output containing raw third-party emails** until rights and privacy are explicitly approved. Files under `/kaggle/working` may be included in a notebook output Version when enabled, so inspect output contents before publication/version sharing.
4. Once rights are verified, store private source files as an authorized **private Kaggle Dataset** or a private notebook output version; attach with the screenshot's **Input > Add Input**. Then the bootstrap verifies the published MD5 and symlinks `/kaggle/input/.../Nazario.csv`, making the data available from a fresh session without redownloading.
5. Current completed quality audit's **non-sensitive statistics** can be read from `data/audit/quality/D1_Nazario_full_quality.json` and recorded to canonical GitHub Markdown receipt; no rerun needed for this evidence.

Sources: https://www.kaggle.com/docs/notebooks and https://www.kaggle.com/docs/datasets

## Why the reset occurs
Kaggle editing sessions are often ephemeral. Files in the working directory may disappear with a new session; files attached from Kaggle Inputs are read-only and can be reattached. Saving a notebook version preserves the version and its output artifacts, not unconditional live restoration of the next session's working files.

## Recommended setup
1. In the Kaggle editor, open Settings > Persistence if available. Choose Files only, or Variables & Files. This is best-effort, not guaranteed storage.
2. Save notebook versions regularly, especially after significant milestones.
3. For long-term reuse, where **rights and privacy permit**, create a PRIVATE Kaggle Dataset and attach it under Input > Add Input. The dataset then appears under /kaggle/input/, available across fresh sessions. Alternatively attach the versioned output of a PRIVATE notebook if legally permissible.
4. **Do not upload raw third-party Nazario/Enron emails to public Kaggle datasets, publicly shared notebook outputs, or GitHub.** Private rehosting still requires adequate rights/privacy checks. Our D1 constituent-license review is pending; use an authorized controlled source if not permitted.

Official Kaggle docs:
- https://www.kaggle.com/docs/notebooks
- https://www.kaggle.com/docs/datasets
- https://www.kaggle.com/product-feedback/355440

## Top-of-notebook ONE CELL — idempotent
Copy into a Kaggle Python cell, save the notebook once, and run this one cell to resume:

    from pathlib import Path
    import subprocess
    import sys

    repo = Path("/kaggle/working/AI-Generated-Phishing-Detection")
    url = "https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git"

    if not (repo / ".git").is_dir():
        if repo.exists():
            raise RuntimeError("Repo path exists but is not a Git repo; inspect manually.")
        subprocess.run(["git", "clone", "--depth", "1", url, str(repo)], check=True)
    else:
        subprocess.run(["git", "-C", str(repo), "pull", "--ff-only"], check=True)

    subprocess.run([sys.executable, str(repo / "scripts/kaggle_resume.py")], check=True)

## What the resume script performs
- Creates and verifies all D1–D5 folder structure.
- Reuses the existing private Nazario.csv when it has the correct published MD5.
- Otherwise searches attached /kaggle/input/**/Nazario.csv, verifies MD5 and symlinks the right file (read-only input, no copied dataset).
- Skips cached Nazario preview and full-quality scans only when the result records the exact current SHA256. Missing audits run once as safe aggregate summaries.
- Does not download, retrain, publish private messages, or treat labels/licenses as approved.
- If there is no local file and no attached private input, reports that explicitly: use a permitted data storage/access route.

The audit JSON in /kaggle/working can itself disappear between fresh sessions. If it disappears, re-scanning this small 7.8 MB file is harmless and uses only CPU; a saved, legally shareable snapshot or Files persistence avoids it.

## Research status
D1 Nazario file MD5: 4022d055bb7cf8602f30f768f652e91e.
Previously observed 1,565 rows, all label=1. Rights, label truth, and source overlap remain unapproved; no phishing-vs-legitimate model training GO.
