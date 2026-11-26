"""Builds notebooks/02_Study1_Exploratory_Reproduction.ipynb: re-executes the frozen Study 1 notebooks on Kaggle."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import code, env_cell, header, md, params_cell, selftest_cell, write_notebook  # noqa: E402

OUT, COMMIT = Path(sys.argv[1]), sys.argv[2]

PARAMS = {
    "REPO_URL": "https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git",
    "CODE_COMMIT": COMMIT,
    "SEED": 2026,
    "EXPECTED_VERSIONS": {"sklearn": "1.6.1"},
    "STUDY1_REFERENCE_COMMIT": "0705745806991f817037921cf06660f477194799",
    "STUDY1_NOTEBOOKS": [
        ["10_Paper_Tables_Figures_and_Manifest.ipynb", ["phishing_n05_safe", "phishing_n06_safe", "phishing_n07_safe",
                                                        "phishing_n08_safe", "phishing_n09_safe", "phishing_n10_safe"]],
        ["11_Parent_Safe_LLM_Rewrite_Augmentation.ipynb", ["phishing_n11_safe"]],
        ["12_DistilBERT_Fine_Tune_External_Reliability.ipynb", ["phishing_n12_safe"]],
        ["13_False_Alarm_Mechanism_and_Source_Shift.ipynb", ["phishing_n13_safe"]],
        ["14_Parent_Paired_Consistency_Training.ipynb", ["phishing_n14_safe"]],
    ],
    "NOTEBOOK_TIMEOUT_SECONDS": 7200,
    "ABS_TOLERANCE": 1e-6,
    "MPLBACKEND": "Agg",
}

cells = [
    header("02", "Study 1 (exploratory) re-executed in the unified Kaggle environment",
           "Re-execute the frozen Study 1 notebooks (archive_v1 N05–N14; N10 contains the N05–N09 code) **unchanged**, "
           "in the same pinned Kaggle image as every Study 2 notebook. Compare every committed aggregate CSV with the "
           "originals produced on GitHub Actions (commit `0705745`). The re-executed outputs are the canonical Study 1 "
           "results of the paper; the cross-environment comparison is reported as a robustness check.",
           "§0 (Study 1 is exploratory)",
           ["`notebooks/archive_v1/10…14_*.ipynb` at the pinned code commit (each downloads its own pinned sources)",
            "Reference aggregates: `phishing_n05_safe … phishing_n14_safe` at commit `0705745`"],
           ["`safe_02/` (committed to `results/02_study1/`): re-executed aggregate folders, `reproduction_report.csv`, run manifest"],
           ["every Study 1 notebook executes without error", "every reference CSV is reproduced (identical or within tolerance); "
            "any difference is listed explicitly, never hidden"],
           "Kaggle GPU T4×2 (the transformer notebook N12 uses the GPU), internet ON, about 1–3 hours"),
    params_cell(PARAMS),
    env_cell("import nbformat, nbclient, shutil, io, traceback"),
    selftest_cell(),
    md("## 1. Execute the frozen Study 1 notebooks, unchanged, one after another"),
    code("""
os.environ["MPLBACKEND"] = MPLBACKEND
SAFE = WORK / "safe_02"
SAFE.mkdir(parents=True, exist_ok=True)
runs = []
for nb_name, out_dirs in STUDY1_NOTEBOOKS:
    path = REPO / "notebooks" / "archive_v1" / nb_name
    nb = nbformat.read(str(path), as_version=4)
    t = time.time(); err = None
    try:
        nbclient.NotebookClient(nb, timeout=NOTEBOOK_TIMEOUT_SECONDS, kernel_name="python3", allow_errors=False,
                                resources={"metadata": {"path": str(WORK)}}).execute()
    except Exception as e:
        err = f"{type(e).__name__}: {str(e)[-1500:]}"
    runs.append({"notebook": nb_name, "seconds": round(time.time() - t, 1), "error": err,
                 "notebook_sha256": manifest.sha256_file(path)})
    log(nb_name, "OK" if err is None else "FAILED", runs[-1]["seconds"], "s")
    if err:
        print(err)
"""),
    md("## 2. Compare every re-executed aggregate CSV with the committed GitHub Actions original"),
    code("""
import pandas as pd
def ref_files(folder):
    out = subprocess.run(["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", STUDY1_REFERENCE_COMMIT, folder],
                         capture_output=True, text=True, check=True).stdout.split()
    return [f for f in out if f.endswith(".csv")]
def ref_csv(f):
    return pd.read_csv(io.StringIO(subprocess.run(["git", "-C", str(REPO), "show", f"{STUDY1_REFERENCE_COMMIT}:{f}"],
                                                  capture_output=True, text=True, check=True).stdout))
rows = []
for nb_name, out_dirs in STUDY1_NOTEBOOKS:
    for d in out_dirs:
        for f in ref_files(d):
            new_path = WORK / f
            rec = {"notebook": nb_name, "file": f}
            if not new_path.exists():
                rows.append({**rec, "status": "MISSING_IN_REPRODUCTION"}); continue
            a, b = ref_csv(f), pd.read_csv(new_path)
            rec.update(rows_ref=len(a), rows_new=len(b))
            if list(a.columns) != list(b.columns) or len(a) != len(b):
                rows.append({**rec, "status": "SHAPE_OR_COLUMNS_DIFFER"}); continue
            num = [c for c in a.columns if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c])]
            txt = [c for c in a.columns if c not in num]
            text_equal = all((a[c].astype(str) == b[c].astype(str)).all() for c in txt)
            diffs = (a[num] - b[num]).abs() if num else pd.DataFrame()
            max_abs = float(np.nanmax(diffs.values)) if num and diffs.size else 0.0
            exact = int((diffs.fillna(0).values == 0).sum()) if num else 0
            status = ("IDENTICAL" if text_equal and max_abs == 0 else
                      "WITHIN_TOLERANCE" if text_equal and max_abs <= ABS_TOLERANCE else "DIFFERENT")
            worst = None
            if num and max_abs > 0:
                col = diffs.max().idxmax(); worst = f"{col} (max |Δ| {max_abs:.6g})"
            rows.append({**rec, "numeric_cells": int(diffs.size) if num else 0, "exact_equal_cells": exact,
                         "max_abs_diff": max_abs, "text_columns_equal": text_equal, "worst_column": worst, "status": status})
report = pd.DataFrame(rows)
report.to_csv(SAFE / "reproduction_report.csv", index=False, lineterminator="\\n")
print(report["status"].value_counts().to_string())
print(report[report["status"] != "IDENTICAL"][["file", "status", "worst_column"]].to_string())
"""),
    md("## 3. Save re-executed aggregates, gates and run manifest"),
    code("""
for nb_name, out_dirs in STUDY1_NOTEBOOKS:
    for d in out_dirs:
        if (WORK / d).exists():
            shutil.copytree(WORK / d, SAFE / d, dirs_exist_ok=True)
manifest.write_json(SAFE / "notebook_runs.json", runs)
GATES = {"all_study1_notebooks_executed": all(r["error"] is None for r in runs),
         "every_reference_csv_present": not (report["status"] == "MISSING_IN_REPRODUCTION").any(),
         "no_shape_or_column_changes": not (report["status"] == "SHAPE_OR_COLUMNS_DIFFER").any()}
STATUS = "COMPLETED" if all(GATES.values()) else "COMPLETED_WITH_GATE_FAILURES"
manifest.write_json(SAFE / "run_manifest.json", {
    "notebook": "02_Study1_Exploratory_Reproduction", "status": STATUS, "gates": GATES,
    "reproduction_summary": report["status"].value_counts().to_dict(), "params": PARAMS, "environment": ENV,
    "selftest": SELFTEST, "runtime_seconds": round(time.time() - T0, 1), "files": manifest.file_hashes(SAFE)})
log("STATUS", STATUS, GATES)
"""),
]
write_notebook(OUT, cells, gpu=True)
print("wrote", OUT)
