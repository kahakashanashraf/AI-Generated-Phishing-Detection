"""Builds notebooks/08_Paper_Tables_Figures_and_Reproducibility.ipynb.

Paper tables (CSV and LaTeX) and PLOS-ready figures (TIFF, LZW, 300 dpi) from the committed safe outputs; the attrition
analysis promised in deviation 12 (private inputs, aggregate outputs only); a reproducibility audit (every committed result
file against its run manifest, and every pushed Kaggle notebook rebuilt byte for byte from its builder at its pinned commit);
the claims summary and the Zenodo file manifest.
"""
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
    "INPUT_ROOT": "/kaggle/input",
    "TEST_GENERATORS": ["qwen2.5-7b", "phi-3.5-mini"],
    "TRAIN_GENERATOR": "olmo-2-7b",
    "PRIMARY": {"D2": "D2|R1|M0|s2026", "D5": "D5|R1|M0|ens"},
    "FIG_DPI": 300,
    "FIG_WIDTH_IN": {"full": 7.5, "column": 5.2},   # PLOS: 2.63–7.5 in wide, at most 8.75 in high
    "TOST_MARGIN": 0.03,
    "REQUIRED_RESULTS": ["01_data", "02_study1", "03_generation", "04_human_validation/kit", "04_human_validation/score",
                         "05_training/classical", "05_training/transformers-a", "05_training/transformers-b", "06_judge",
                         "07_confirmatory"],
}

cells = [
    header("08", "Paper tables, figures and reproducibility audit",
           "Turn the committed, text-free results of 01–07 into the paper's tables (CSV and LaTeX) and figures (TIFF, LZW, 300 dpi, "
           "PLOS size limits). Run the attrition analysis promised in deviation 12 on the private generation records (aggregates only). "
           "Audit reproducibility: every committed result file must match the SHA-256 in its run manifest, and every pushed Kaggle "
           "notebook must rebuild byte for byte from its builder at its pinned commit. Write the claims summary and the Zenodo file manifest.",
           "§6–§8, deviations 12–13",
           ["`results/` at the pinned commit (all committed safe outputs of 01–07)",
            "Kernel outputs of 01 and 03 (Phi, OLMo) and the Qwen dataset (attrition analysis only)"],
           ["`safe_08/` (committed to `results/08_paper/`): tables, figures, attrition analysis, audit reports, claims summary, "
            "Zenodo manifest, results summary, run manifest"],
           ["every required result folder is present", "every committed result file matches its manifest hash",
            "every pushed notebook rebuilds byte for byte", "no email text in any output"],
           "Kaggle CPU session, same pinned image (D018), about 10 minutes"),
    params_cell(PARAMS),
    env_cell("""import ast, re, shutil
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
SAFE = WORK / "safe_08"
TAB, FIG = SAFE / "tables", SAFE / "figures"
for _p in (SAFE, TAB, FIG):
    _p.mkdir(parents=True, exist_ok=True)
RES = REPO / "results"
_fonts = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ("Arial", "Liberation Sans", "DejaVu Sans") if f in _fonts), "DejaVu Sans")   # PLOS asks for Arial
plt.rcParams.update({"font.family": FONT, "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "figure.dpi": FIG_DPI})
OKABE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]   # colour-blind safe
ENV["figure_font"] = FONT"""),
    selftest_cell(),
    md("## 1. Load the committed results (pinned commit) and check that every required folder is present"),
    code("""
PRESENT = {d: (RES / d).is_dir() and any((RES / d).rglob("run_manifest.json")) for d in REQUIRED_RESULTS}
log("required results present:", PRESENT)
def tup(x):
    if isinstance(x, str) and x.strip()[:1] in "([":
        v = ast.literal_eval(x)
        return (float(v[0]), float(v[1])) if v is not None and len(v) == 2 else (np.nan, np.nan)
    return (np.nan, np.nan)
def rcsv(rel):
    p = RES / rel
    return pd.read_csv(p) if p.exists() else pd.DataFrame()
C07 = {k: rcsv(f"07_confirmatory/{k}.csv") for k in ("pe0_dose_response", "pe1_rewrite_equivalence", "pe2_compose_effect",
                                                    "pe3_mitigations", "secondary_cell_metrics", "h2_source_effect",
                                                    "h4_interventions", "h4b_failure_decomposition", "h1_in_replication",
                                                    "exploratory_extensions")}
CLAIMS = json.loads((RES / "07_confirmatory/claims.json").read_text(encoding="utf-8")) if (RES / "07_confirmatory/claims.json").exists() else {}
HV = json.loads((RES / "04_human_validation/score/decisions.json").read_text(encoding="utf-8")) if (RES / "04_human_validation/score/decisions.json").exists() else {}
GEN_SUM = {g: rcsv(f"03_generation/{g}/generation_summary.csv") for g in TEST_GENERATORS + [TRAIN_GENERATOR]}
MANIP = {g: rcsv(f"03_generation/{g}/manipulation_check.csv") for g in TEST_GENERATORS}
REG = pd.concat([pd.read_csv(p) for p in sorted((RES / "05_training").rglob("model_registry.csv"))] +
                ([pd.read_csv(RES / "06_judge/model_registry.csv")] if (RES / "06_judge/model_registry.csv").exists() else []),
                ignore_index=True) if (RES / "05_training").exists() else pd.DataFrame()
log({k: len(v) for k, v in C07.items()}, "| registry models", len(REG))
"""),
    md("## 2. Tables (CSV for the record, LaTeX for the manuscript)"),
    code("""
def latex(df, name, caption):
    cols = list(df.columns)
    esc = lambda v: (str(v).replace("\\\\", "\\\\textbackslash{}").replace("&", "\\\\&").replace("%", "\\\\%").replace("_", "\\\\_")
                     .replace("#", "\\\\#").replace("|", "\\\\textbar{}"))
    lines = ["\\\\begin{table}[!ht]", "\\\\centering", f"\\\\caption{{{esc(caption)}}}", f"\\\\label{{tab:{name}}}",
             "\\\\begin{tabular}{" + "l" * len(cols) + "}", "\\\\hline", " & ".join(esc(c) for c in cols) + " \\\\\\\\", "\\\\hline"]
    lines += [" & ".join(esc(v) for v in row) + " \\\\\\\\" for row in df.itertuples(index=False)]
    lines += ["\\\\hline", "\\\\end{tabular}", "\\\\end{table}"]
    (TAB / f"{name}.tex").write_bytes(("\\n".join(lines) + "\\n").encode("utf-8"))
def save_table(df, name, caption):
    df.to_csv(TAB / f"{name}.csv", index=False, lineterminator="\\n")
    latex(df, name, caption)
    return df
pct = lambda x: "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{100 * float(x):.1f}"
ci_pct = lambda t: "" if any(np.isnan(v) for v in t) else f"[{100 * t[0]:.1f}, {100 * t[1]:.1f}]"
pval = lambda p: "" if p is None or (isinstance(p, float) and np.isnan(p)) else ("<0.001" if float(p) < 0.001 else f"{float(p):.3f}")
TABLES = {}

cc = rcsv("01_data/cell_counts.csv")
if len(cc):
    t1 = cc[cc["kind"].str.contains("LOCKED", na=False)][["cell", "n", "n_legit", "n_phish", "sources", "authorship", "median_words"]]
    TABLES["T1_locked_cells"] = save_table(t1, "T1_locked_cells", "Locked evaluation cells (counts and sources)")

rows = []
for g, df in GEN_SUM.items():
    if not len(df):
        continue
    for cell, d in df.groupby("cell", sort=True):
        head_ = d[d["requested"].notna() & (d["requested"].astype(str) != "")].iloc[0]
        rs = d[d["reason"].notna() & (d["reason"].astype(str) != "")].sort_values("count", ascending=False)
        rows.append({"generator": g, "cell": cell, "requested": int(float(head_["requested"])), "kept": int(float(head_["kept"])),
                     "kept_pct": pct(head_["kept_rate"]),
                     "main_exclusions": "; ".join(f"{r.reason} {int(r.count)}" for r in rs.head(3).itertuples())})
if rows:
    TABLES["T2_generation_attrition"] = save_table(pd.DataFrame(rows), "T2_generation_attrition",
                                                   "Generated cells: requested, kept after the fixed quality filters, and the main exclusion reasons")

ag, rt = rcsv("04_human_validation/score/agreement.csv"), rcsv("04_human_validation/score/rates.csv")
if len(rt):
    t3 = rt[rt["subset"] == "all"].copy()
    t3["rate_pct"] = t3["rate"].map(pct); t3["ci95_pct"] = [ci_pct((a, b)) for a, b in zip(t3["ci95_low"], t3["ci95_high"])]
    t3 = t3[["generator", "measure", "n", "k", "rate_pct", "ci95_pct"]]
    t3["rw_results_role"] = t3["generator"].map(lambda g: HV.get("decisions", {}).get(g, {}).get("rw_results_role", ""))
    TABLES["T3_human_validation"] = save_table(t3, "T3_human_validation", "Human validation: preservation and plausibility rates (Wilson 95% CI)")
if len(ag):
    TABLES["S_T_agreement"] = save_table(ag, "S_T_agreement", "Inter-rater agreement (Cohen's kappa with bootstrap CI; Gwet's AC1)")

pe0, pe1, pe2 = C07["pe0_dose_response"], C07["pe1_rewrite_equivalence"], C07["pe2_compose_effect"]
if len(pe1):
    rows = []
    for src_name, df, L in (("PE1 (L3 rewrite vs L0)", pe1, "L3"), ("PE2 (L4 compose vs L0)", pe2, "L4")):
        for r in df.itertuples():
            rows.append({"endpoint": src_name, "analysis": r.analysis, "regime": r.regime, "detector": r.detector, "n_pairs": r.n_pairs,
                         "fpr_L0_pct": pct(r.fpr_L0), f"fpr_{L}_pct": pct(getattr(r, f"fpr_{L}")), "delta_pp": pct(r.delta),
                         "ci90_pp": ci_pct(tup(r.ci90)), "ci95_pp": ci_pct(tup(r.ci95)), "mcnemar_p": pval(r.mcnemar_p),
                         "holm_p": pval(getattr(r, "holm_tost_p", None) if L == "L3" else getattr(r, "holm_mcnemar_p", None)),
                         "tost_equivalent": bool(r.tost_equivalent) if L == "L3" else ""})
    TABLES["T4_primary_endpoints"] = save_table(pd.DataFrame(rows), "T4_primary_endpoints",
                                                "Primary endpoints PE1 and PE2: paired false-positive rates (percent) and differences (percentage points)")
if len(pe0):
    t = pe0[["analysis", "regime", "detector", "complete_parents"] + [f"fpr_L{i}" for i in range(5)] + ["gee_odds_ratio_per_level", "gee_p"]].copy()
    for i in range(5):
        t[f"fpr_L{i}"] = t[f"fpr_L{i}"].map(pct)
    t["gee_p"] = t["gee_p"].map(pval)
    TABLES["T5_dose_response"] = save_table(t, "T5_dose_response", "PE0 dose-response: FPR (percent) by AI-assistance level and GEE trend")
pe3 = C07["pe3_mitigations"]
if len(pe3):
    t = pd.DataFrame({"analysis": pe3["analysis"], "detector": pe3["detector"], "mitigation": pe3["mitigation"],
                      "ai_legit_fpr_delta_pp": pe3["ai_legit_delta"].map(pct), "ai_legit_ci95_pp": pe3["ai_legit_ci95"].map(lambda x: ci_pct(tup(x))),
                      "recall_pool_lower95_pp": pe3["recall_pool_lower95"].map(pct), "recall_modern_lower95_pp": pe3["recall_modern_lower95"].map(pct),
                      "in_fpr_upper95_pp": pe3["in_fpr_upper95"].map(pct), "holm_p_a": pe3["a_holm_p"].map(pval),
                      "crit_a": pe3["crit_a"], "crit_b": pe3["crit_b"], "crit_c": pe3["crit_c"], "passes_all": pe3["passes_all"]})
    TABLES["T6_mitigations"] = save_table(t, "T6_mitigations", "PE3 mitigations against M0: criteria (a) AI-legitimate FPR, (b) recall, (c) in-source FPR")
for key, name, cap in (("h2_source_effect", "S_T_h2_source", "H2: external minus in-source FPR"),
                       ("h1_in_replication", "S_T_h1_in", "H1-IN: in-source L3 rewrite equivalence by provider"),
                       ("h4b_failure_decomposition", "S_T_h4b", "H4b: ranking versus threshold failure, alerts and precision at 1% and 5% prevalence"),
                       ("h4_interventions", "S_T_h4", "H4: cue interventions, mean change in logit"),
                       ("exploratory_extensions", "S_T_exploratory_extensions",
                        "Exploratory extensions (deviation 15): E1 newer human email (EXT3) and E2 generator scale (Qwen2.5-14B)")):
    if len(C07[key]):
        TABLES[name] = save_table(C07[key], name, cap)
if len(REG):
    cols = [c for c in ("model_id", "val_ap", "val_auroc", "tau5", "tau1", "val_fpr_at_tau5", "val_recall_at_tau5") if c in REG.columns]
    TABLES["S_T_detector_registry"] = save_table(REG[cols], "S_T_detector_registry", "Detectors: validation metrics and thresholds (validation data only)")
rr = rcsv("02_study1/reproduction_report.csv")
if len(rr):
    TABLES["S_T_study1_reproduction"] = save_table(rr.groupby(["notebook", "status"]).size().reset_index(name="tables"),
                                                   "S_T_study1_reproduction", "Study 1 re-execution in the unified image (see REPRODUCTION_NOTE)")
log("tables", sorted(TABLES))
"""),
    md("## 3. Figures (TIFF with LZW compression, 300 dpi, within PLOS size limits; PNG previews)"),
    code("""
FIGS = {}
def save_fig(fig, name):
    w, h = fig.get_size_inches()
    assert w <= 7.5 + 1e-6 and h <= 8.75 + 1e-6, f"{name}: {w:.2f}x{h:.2f} in exceeds PLOS limits"
    fig.savefig(FIG / f"{name}.tif", dpi=FIG_DPI, format="tiff", pil_kwargs={"compression": "tiff_lzw"}, facecolor="white")
    fig.savefig(FIG / f"{name}.png", dpi=120, facecolor="white")
    plt.close(fig)
    FIGS[name] = {"inches": [round(float(w), 2), round(float(h), 2)], "pixels": [int(round(w * FIG_DPI)), int(round(h * FIG_DPI))]}

sec = C07["secondary_cell_metrics"]
if len(sec):
    sec = sec[sec["threshold"] == "tau5"]
    fig, axes = plt.subplots(1, len(PRIMARY), figsize=(FIG_WIDTH_IN["full"], 2.8), sharey=True)
    for ax, (det, model) in zip(np.atleast_1d(axes), PRIMARY.items()):
        for k, g in enumerate(TEST_GENERATORS):
            xs, ys, lo, hi = [], [], [], []
            for i, L in enumerate(("L0", "L1", "L2", "L3", "L4")):
                cell = "EXT-legit-L0" if L == "L0" else f"EXT-legit-{L}-{g}"
                r = sec[(sec["model"] == model) & (sec["cell"] == cell)]
                if len(r):
                    a, b = tup(r["wilson95"].iloc[0]); v = float(r["rate"].iloc[0])
                    xs.append(i + (k - 0.5) * 0.12); ys.append(100 * v); lo.append(100 * (v - a)); hi.append(100 * (b - v))
            ax.errorbar(xs, ys, yerr=[lo, hi], marker="o", ms=4, lw=1.2, capsize=2, color=OKABE[k], label=g)
        ax.set_xticks(range(5)); ax.set_xticklabels(["L0\\nhuman", "L1\\nproofread", "L2\\npolish", "L3\\nrewrite", "L4\\ncompose"])
        ax.set_title(f"{det} ({model})"); ax.grid(axis="y", lw=0.4, alpha=0.5)
    np.atleast_1d(axes)[0].set_ylabel("False-positive rate at τ5 (%)"); np.atleast_1d(axes)[-1].legend(frameon=False)
    fig.tight_layout(); save_fig(fig, "Fig2_fpr_by_assistance_level")

if len(pe1):
    rows = [("PE1 L3", r) for r in pe1[pe1["analysis"] == "primary"].itertuples()] + [("PE2 L4", r) for r in pe2.itertuples()]
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN["column"], 0.32 * len(rows) + 1.0))
    ax.axvspan(-100 * TOST_MARGIN, 100 * TOST_MARGIN, color="0.9", zorder=0, label=f"±{100 * TOST_MARGIN:.0f} pp equivalence margin")
    ax.axvline(0, color="0.4", lw=0.8)
    for y, (ep, r) in enumerate(rows):
        if r.status != "ok":
            continue
        a90, b90 = tup(r.ci90); a95, b95 = tup(r.ci95)
        ax.plot([100 * a95, 100 * b95], [y, y], color="0.3", lw=0.8)
        if not np.isnan(a90):
            ax.plot([100 * a90, 100 * b90], [y, y], color=OKABE[0] if ep.startswith("PE1") else OKABE[1], lw=2.4)
        ax.plot(100 * r.delta, y, "o", color="black", ms=3.5)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([f"{ep} | {r.regime} | {r.detector}" for ep, r in rows])
    ax.invert_yaxis(); ax.set_xlabel("Paired ΔFPR vs human L0 (percentage points)"); ax.legend(frameon=False, loc="lower right")
    fig.tight_layout(); save_fig(fig, "Fig3_paired_effects_forest")

if len(pe3):
    p3 = pe3[pe3["analysis"] == "primary"]
    fig, axes = plt.subplots(1, p3["detector"].nunique(), figsize=(FIG_WIDTH_IN["full"], 3.0), sharey=True)
    for ax, (det, d) in zip(np.atleast_1d(axes), p3.groupby("detector")):
        ax.axvline(-10, ls="--", color="0.5", lw=0.8); ax.axhline(-2, ls="--", color="0.5", lw=0.8); ax.axvline(0, color="0.8", lw=0.6)
        for k, r in enumerate(d.itertuples()):
            a, b = tup(r.ai_legit_ci95)
            ax.errorbar(100 * r.ai_legit_delta, 100 * r.recall_pool_lower95, xerr=[[100 * (r.ai_legit_delta - a)], [100 * (b - r.ai_legit_delta)]],
                        fmt="o" if bool(r.passes_all) else "o", mfc=OKABE[k % 8] if bool(r.passes_all) else "white", color=OKABE[k % 8], capsize=2, ms=5)
            ax.annotate(r.mitigation, (100 * r.ai_legit_delta, 100 * r.recall_pool_lower95), textcoords="offset points", xytext=(4, 4), fontsize=8)
        ax.set_title(det); ax.set_xlabel("Δ AI-legitimate FPR (pp, 95% CI)")
    np.atleast_1d(axes)[0].set_ylabel("Δ recall, one-sided 95% lower bound (pp)")
    fig.tight_layout(); save_fig(fig, "Fig4_mitigation_tradeoffs")

if any(len(v) for v in MANIP.values()):
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH_IN["full"], 2.6))
    for k, g in enumerate(TEST_GENERATORS):
        m = MANIP[g]
        if not len(m):
            continue
        for ax, metric in zip(axes, ("cosine_median", "jaccard_median")):
            ys = [float(m.loc[m["cell"] == f"EXT-legit-{L}-{g}", metric].iloc[0]) if (m["cell"] == f"EXT-legit-{L}-{g}").any() else np.nan
                  for L in ("L1", "L2", "L3", "L4")]
            ax.plot(range(1, 5), ys, marker="o", color=OKABE[k], label=g)
    for ax, lab in zip(axes, ("Cosine similarity to parent (median)", "5-gram Jaccard to parent (median)")):
        ax.set_xticks(range(1, 5)); ax.set_xticklabels(["L1", "L2", "L3", "L4"]); ax.set_ylabel(lab); ax.grid(axis="y", lw=0.4, alpha=0.5)
    axes[0].legend(frameon=False); fig.tight_layout(); save_fig(fig, "Fig5_manipulation_check")

h4 = C07["h4_interventions"]
if len(h4):
    models_ = list(dict.fromkeys(h4["model"]))
    fig, axes = plt.subplots(len(models_), 1, figsize=(FIG_WIDTH_IN["column"], 1.5 * len(models_) + 0.6), sharex=True)
    for ax, m in zip(np.atleast_1d(axes), models_):
        d = h4[h4["model"] == m]
        for k, (src, dd) in enumerate(d.groupby("source", sort=True)):
            xs = np.arange(len(dd)) + (k - 1) * 0.18
            ci = np.array([tup(c) for c in dd["ci95"]])
            ax.errorbar(xs, dd["mean_delta_logit"], yerr=[dd["mean_delta_logit"] - ci[:, 0], ci[:, 1] - dd["mean_delta_logit"]],
                        fmt="o", ms=3, capsize=2, color=OKABE[k], label=src)
        ax.axhline(0, color="0.5", lw=0.6); ax.set_title(m, fontsize=8); ax.set_xticks(range(6)); ax.set_xticklabels([f"I{i}" for i in range(1, 7)])
    np.atleast_1d(axes)[0].legend(frameon=False, fontsize=7); np.atleast_1d(axes)[-1].set_xlabel("Intervention")
    fig.supylabel("Mean Δ logit (95% CI)"); fig.tight_layout(); save_fig(fig, "Fig6_cue_interventions")
log("figures", FIGS)
"""),
    md("## 4. Attrition analysis (deviation 12): kept versus excluded generation tasks, aggregates only"),
    code("""
root = Path(INPUT_ROOT)
ATTR_ROWS, ATTR_MISSING = [], []
try:
    rec01 = {r["sample_id"]: r for r in manifest.read_jsonl(manifest.find_artifact(root, "records"))}
except FileNotFoundError:
    rec01 = {}
    ATTR_MISSING.append("01 records")
def task_cell(p, level, g):
    kind = "legit" if int(p["label"]) == 0 else "phish"
    if p["cell"].startswith("train_r1"):
        return f"train_r1-{kind}-{level}-{g}"
    return p["cell"].replace("-L0", f"-{level}-{g}").replace("-H", f"-{level}-{g}")
for g in TEST_GENERATORS + [TRAIN_GENERATOR]:
    try:
        gen = manifest.read_jsonl(manifest.find_artifact(root, f"generated_{g}"))
    except FileNotFoundError:
        ATTR_MISSING.append(g); continue
    rj = sorted(root.rglob(f"rejected_ids_{g}.json"))
    rejected = json.loads(rj[0].read_text(encoding="utf-8")) if rj else []
    for sid, why in [(r["sample_id"], None) for r in gen] + [tuple(x) for x in rejected]:
        parent_id, level, _g = sid.rsplit("|", 2)
        p = rec01.get(parent_id)
        if p is None:
            continue
        _, mapping = textnorm.lock_placeholders(p["subject"] + "\\n" + p["body"])
        ATTR_ROWS.append({"generator": g, "cell": task_cell(p, level, g), "level": level, "source": p["cell"].split("-")[0],
                          "label": int(p["label"]), "kept": why is None, "reason": why or "",
                          "words": textnorm.word_count(p["body"]), "placeholders": len(mapping)})
A = pd.DataFrame(ATTR_ROWS)
ATTR = {}
if len(A):
    summ = (A.groupby(["generator", "cell"]).apply(lambda d: pd.Series({
        "requested": len(d), "kept_pct": round(100 * d["kept"].mean(), 1),
        "median_words_kept": d.loc[d["kept"], "words"].median(), "median_words_excluded": d.loc[~d["kept"], "words"].median(),
        "mean_placeholders_kept": round(d.loc[d["kept"], "placeholders"].mean(), 2),
        "mean_placeholders_excluded": round(d.loc[~d["kept"], "placeholders"].mean(), 2) if (~d["kept"]).any() else np.nan}),
        include_groups=False).reset_index())
    A["placeholder_bin"] = pd.cut(A["placeholders"], [-1, 0, 2, 5, 10_000], labels=["0", "1-2", "3-5", "6+"])
    A["length_tertile"] = A.groupby("generator")["words"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["short", "mid", "long"]))
    by_bins = (A.groupby(["generator", "label", "placeholder_bin"], observed=True)["kept"].agg(["size", "mean"]).reset_index()
               .rename(columns={"size": "n", "mean": "kept_rate"}))
    by_len = (A.groupby(["generator", "label", "length_tertile"], observed=True)["kept"].agg(["size", "mean"]).reset_index()
              .rename(columns={"size": "n", "mean": "kept_rate"}))
    LOGIT = []
    import statsmodels.formula.api as smf
    for g, d in A.groupby("generator"):
        d = d.assign(excluded=(~d["kept"]).astype(int), log_words=np.log1p(d["words"]))
        if d["excluded"].nunique() < 2:
            continue
        try:
            fit = smf.logit("excluded ~ log_words + placeholders + label + C(level) + C(source)", d).fit(disp=0)
            for term in ("log_words", "placeholders", "label"):
                lo, hi = fit.conf_int().loc[term]
                LOGIT.append({"generator": g, "term": term, "odds_ratio": float(np.exp(fit.params[term])),
                              "ci95_low": float(np.exp(lo)), "ci95_high": float(np.exp(hi)), "p": float(fit.pvalues[term]), "n": int(len(d))})
        except Exception as e:   # report, never hide
            LOGIT.append({"generator": g, "term": "fit_failed", "odds_ratio": None, "ci95_low": None, "ci95_high": None, "p": None,
                          "n": int(len(d)), "error": f"{type(e).__name__}: {e}"[:150]})
    save_table(summ, "S_T_attrition_by_cell", "Attrition: kept versus excluded tasks by cell (parent length and placeholder counts)")
    by_bins.to_csv(TAB / "S_T_attrition_by_placeholders.csv", index=False, lineterminator="\\n")
    by_len.to_csv(TAB / "S_T_attrition_by_length.csv", index=False, lineterminator="\\n")
    pd.DataFrame(LOGIT).to_csv(TAB / "S_T_attrition_logit.csv", index=False, lineterminator="\\n")
    ATTR = {"tasks": int(len(A)), "generators": sorted(A["generator"].unique().tolist()), "missing_inputs": ATTR_MISSING}
log("attrition", ATTR or {"missing_inputs": ATTR_MISSING})
"""),
    md("## 5. Reproducibility audit: committed results against manifests; pushed notebooks rebuilt from their builders"),
    code("""
AUDIT_FILES = []
for man in sorted(RES.rglob("run_manifest.json")):
    if "08_paper" in man.parts:
        continue
    m = json.loads(man.read_text(encoding="utf-8"))
    for rel, h in (m.get("files") or {}).items():
        f = man.parent / rel
        AUDIT_FILES.append({"manifest": str(man.relative_to(REPO)), "file": rel, "present": f.exists(),
                            "sha256_match": f.exists() and manifest.sha256_file(f) == h})
af = pd.DataFrame(AUDIT_FILES, columns=["manifest", "file", "present", "sha256_match"])
# every run must have executed in the one pinned image (D013); the run manifests record the image each kernel actually used
IMAGES = {}
for man in sorted(RES.rglob("run_manifest.json")):
    img = (json.loads(man.read_text(encoding="utf-8")).get("environment") or {}).get("kaggle_docker_image")
    if img:
        IMAGES[str(man.relative_to(REPO))] = img
pd.DataFrame(sorted(IMAGES.items()), columns=["manifest", "kaggle_docker_image"]).to_csv(SAFE / "audit_images.csv", index=False, lineterminator="\\n")
IMAGE_DIGESTS = sorted({v.split("@")[-1] for v in IMAGES.values()})
af.to_csv(SAFE / "audit_result_files.csv", index=False, lineterminator="\\n")

def builder_for(step):
    for pre, b in (("03-", "build_03.py"), ("04-", "build_04.py"), ("05-", "build_05.py")):
        if step.startswith(pre):
            return b, [step[len(pre):]]
    return {"01": ("build_01.py", []), "02": ("build_02.py", []), "06": ("build_06.py", []), "07": ("build_07.py", [])}.get(step, (None, []))
AUDIT_NB = []
for kdir in sorted(p for p in (REPO / "kaggle_kernels").iterdir() if p.is_dir()):
    meta = json.loads((kdir / "kernel-metadata.json").read_text(encoding="utf-8"))
    nbp = kdir / meta["code_file"]
    b, args = builder_for(kdir.name)
    row = {"step": kdir.name, "notebook": meta["code_file"], "builder": b, "args": " ".join(args)}
    if b is None or not nbp.exists():
        AUDIT_NB.append({**row, "commit": None, "rebuild_identical": False, "note": "no builder mapping or notebook missing"}); continue
    params_src = "".join(next(c for c in json.loads(nbp.read_text(encoding="utf-8"))["cells"] if c["cell_type"] == "code")["source"])
    commit = re.search(r"'CODE_COMMIT': '([0-9a-f]{7,40})'", params_src).group(1)
    tmp = TEMP / "rebuild" / kdir.name
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        for fname in (b, "common.py"):
            blob = subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:scripts/notebook_builders/{fname}"], capture_output=True, check=True).stdout
            (tmp / fname).write_bytes(blob)
        out_nb = tmp / meta["code_file"]
        subprocess.run([sys.executable, str(tmp / b), str(out_nb), commit, *args], capture_output=True, check=True, cwd=tmp)
        same = out_nb.read_bytes() == nbp.read_bytes()
        AUDIT_NB.append({**row, "commit": commit, "rebuild_identical": same, "note": ""})
    except subprocess.CalledProcessError as e:
        AUDIT_NB.append({**row, "commit": commit, "rebuild_identical": False, "note": (e.stderr or b"")[-200:].decode("utf-8", "replace")})
an = pd.DataFrame(AUDIT_NB)
an.to_csv(SAFE / "audit_notebook_rebuilds.csv", index=False, lineterminator="\\n")
log("result files", len(af), "| hash mismatches", int((~af["sha256_match"]).sum()), "| notebooks", len(an),
    "| rebuild mismatches", int((~an["rebuild_identical"]).sum()) if len(an) else 0)
print(an.to_string())
"""),
    md("## 6. Claims summary, results summary, Zenodo file manifest, gates and run manifest"),
    code("""
CLAIM_ROWS = [{"detector": det, **{k: (", ".join(v) if isinstance(v, list) else v) for k, v in c.items()}} for det, c in CLAIMS.items()]
if CLAIM_ROWS:
    save_table(pd.DataFrame(CLAIM_ROWS), "T7_claims", "Pre-registered claims (§7) applied mechanically to the primary analysis")
lines = ["# Results at a glance (generated by notebook 08; numbers only, no email text)", ""]
if HV:
    lines.append("## Human validation (§3.5)")
    for g, d in HV.get("decisions", {}).items():
        lines.append(f"- {g}: label preservation {d.get('label_preservation')} (95% CI {d.get('ci95')}); RW results: {d.get('rw_results_role')}")
    lines.append(f"- Cohen's kappa (rewrite label): {HV.get('kappa_rewrite_label')} (target {HV.get('kappa_target')}; met: {HV.get('kappa_target_met')})")
    lines.append("")
if "T4_primary_endpoints" in TABLES:
    lines.append("## Primary endpoints (R1, primary analysis)")
    t4 = TABLES["T4_primary_endpoints"]
    for r in t4[(t4["analysis"] == "primary") & (t4["regime"] == "R1")].itertuples():
        lines.append(f"- {r.endpoint} | {r.detector}: Δ {r.delta_pp} pp, 90% CI {r.ci90_pp}, 95% CI {r.ci95_pp}, Holm p {r.holm_p}")
    lines.append("")
if CLAIMS:
    lines.append("## Claims (§7)")
    for det, c in CLAIMS.items():
        lines.append(f"- {det}: PE0 {c.get('PE0')}, PE1 {c.get('PE1')}, PE2 {c.get('PE2')} -> {c.get('claim')}; "
                     f"mitigations passing all criteria: {c.get('mitigations_passing_all')}")
(SAFE / "RESULTS_SUMMARY.md").write_bytes(("\\n".join(lines) + "\\n").encode("utf-8"))

tracked = subprocess.run(["git", "-C", str(REPO), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\\n")
zen = [{"path": t, "sha256": manifest.sha256_file(REPO / t), "bytes": (REPO / t).stat().st_size} for t in tracked if t and (REPO / t).is_file()]
pd.DataFrame(zen).to_csv(SAFE / "zenodo_file_manifest.csv", index=False, lineterminator="\\n")

safe_blob = textnorm.normalize("\\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in SAFE.rglob("*")
                                         if p.is_file() and p.suffix in (".csv", ".tex", ".md", ".json")))
probe = [r for r in rec01.values() if len(textnorm.normalize(r["body"])) >= 60]
probe = random.Random(SEED).sample(probe, min(500, len(probe)))
leaks = sum(1 for r in probe if textnorm.normalize(r["body"])[:60] in safe_blob)
GATES = {"required_results_present": all(PRESENT.values()),
         "result_files_match_manifests": bool(len(af)) and bool(af["present"].all() and af["sha256_match"].all()),
         "notebooks_rebuild_identically": bool(len(an)) and bool(an["rebuild_identical"].all()),
         "one_pinned_image_digest": len(IMAGE_DIGESTS) == 1,
         "privacy_no_text_in_outputs": leaks == 0,
         "figures_within_plos_limits": all(v["pixels"][0] <= 2250 and v["pixels"][1] <= 2625 for v in FIGS.values())}
manifest.write_json(SAFE / "run_manifest.json", {
    "notebook": "08_Paper_Tables_Figures_and_Reproducibility", "status": "COMPLETED" if all(GATES.values()) else "COMPLETED_WITH_GATE_FAILURES",
    "gates": GATES, "present": PRESENT, "tables": sorted(TABLES), "figures": FIGS, "figure_font": FONT, "attrition": ATTR,
    "image_digests": IMAGE_DIGESTS,
    "audit": {"result_files": len(af), "hash_mismatches": int((~af["sha256_match"]).sum()) if len(af) else None,
              "notebooks": len(an), "rebuild_mismatches": int((~an["rebuild_identical"]).sum()) if len(an) else None},
    "phishbench_commit": CODE_COMMIT, "runtime_seconds": round(time.time() - T0, 1), "params": PARAMS, "environment": ENV,
    "selftest": SELFTEST, "files": manifest.file_hashes(SAFE)})
log("gates", GATES)
assert GATES["privacy_no_text_in_outputs"], "Privacy gate failure"
"""),
]
write_notebook(OUT, cells, gpu=False)
print("wrote", OUT)
