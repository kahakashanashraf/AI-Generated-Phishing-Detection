"""Builds notebooks/07_Confirmatory_Evaluation.ipynb: the single locked evaluation (PE0–PE3, H2, H4, H4b, H6, H1-IN)."""
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
    "EXTENSION_INPUTS": ["records_ext3", "generated_qwen2.5-7b__ext3", "generated_phi-3.5-mini__ext3", "generated_qwen2.5-14b"],   # deviation 15
    "BOOTSTRAP_B": 10000,
    "TOST_MARGIN": 0.03,
    "PRIMARY": {"D2": "D2|R1|M0|s2026", "D5": "D5|R1|M0|ens"},
    "R2_MODELS": {"D2": "D2|R2|M0|s2026", "D5": "D5|R2|M0|ens"},
    "MITIGATIONS": {"D2": {"M1": "D2|R1|M1|s2026", "M2": "D2|R1|M2|s2026", "M3": "D2|R2|M0|s2026", "M4": "D2|R1|M4|s2026",
                           "M5": "D2|R1|M5|s2026", "M6": "D2|R1|M0|s2026"},
                    "D5": {"M1": "D5|R1|M1|ens", "M2": "D5|R1|M2|ens", "M3": "D5|R2|M0|ens", "M4": "D5|R1|M4|ens",
                           "M5": "D5|R1|M5|ens", "M6": "D5|R1|M0|ens"}},
    "M6_PREVALENCE": 0.05, "M6_BUDGET": 0.10,
    "PE3_MIN_FPR_REDUCTION": 0.10, "PE3_RECALL_MARGIN": -0.02, "PE3_IN_FPR_MARGIN": 0.02,
    "H4_MODELS": ["D1|R1|M0|s2026", "D2|R1|M0|s2026", "D3|R1|M0|s2026", "D5|R1|M0|ens"],
    "LEVEL_SCORE": {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4},
    "DECISIONS_PATH": "results/04_human_validation/score/decisions.json",   # §3.5 rule input (deviation 13)
}

cells = [
    header("07", "Confirmatory evaluation (single locked run)",
           "Verify the seals of 05 and 06, build the five-seed ensembles (thresholds from validation), then compute every pre-registered "
           "endpoint on the locked cells once: PE0 dose–response (GEE plus level-versus-L0 McNemar), PE1 TOST ±3 pp, PE2, PE3 mitigation "
           "criteria (a), (b) and (c) with Holm correction, and the secondary H2, H4, H4b, H6 and H1-IN. Write the per-row predictions without "
           "text (D009) and apply the §7 claim table mechanically.",
           "§6–§7, deviations 1–8",
           ["01 records, 03 generated records (Qwen, Phi)", "05 classical and transformer seals, registries and score files; 06 judge seal, registry and scores"],
           ["`safe_07/` (committed): endpoint tables, secondary metrics, per-row predictions (IDs only), claims.json, run manifest"],
           ["every seal hash verifies", "every primary endpoint is computed or explicitly marked not estimable", "per-row file contains no text"],
           "Kaggle GPU T4×2 image (CPU work), about 30 minutes"),
    params_cell(PARAMS),
    env_cell("""import numpy as np, pandas as pd
from phishbench import stats
SAFE = WORK / "safe_07"; SAFE.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(SEED)"""),
    selftest_cell(),
    md("## 1. Verify the seals, then load scores and metadata"),
    code("""
root = Path(INPUT_ROOT)
SEALS = {}
for sm_path in sorted(root.rglob("seal_manifest.json")):
    sm = json.loads(sm_path.read_text(encoding="utf-8"))
    for fname, h in sm["files"].items():
        hits = sorted(root.rglob(fname)); assert hits, f"sealed file missing: {fname}"
        SEALS[fname] = {"expected": h, "found": manifest.sha256_file(hits[0]), "path": str(hits[0]), "part": sm.get("part")}
SEAL_OK = all(v["expected"] == v["found"] for v in SEALS.values())
log("seals", len(SEALS), "verified" if SEAL_OK else "MISMATCH")
assert SEAL_OK, "Seal verification failed: refusing to evaluate"

def read_gz(p):
    if str(p).endswith(".jsonl"):
        return manifest.read_jsonl(p)
    with gzip.open(p, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f]
meta = {}
for p in ([manifest.find_artifact(root, "records")] + [manifest.find_artifact(root, f"generated_{g}") for g in TEST_GENERATORS]
          + [manifest.find_artifact(root, stem) for stem in EXTENSION_INPUTS]):
    for r in read_gz(p):
        meta[r["sample_id"]] = {"label": r["label"], "parent_id": r["parent_id"], "level": r.get("level") or "L0",
                                "generator": r.get("generator"), "source": r["source"]}
reg = pd.concat([pd.read_csv(p) for p in sorted(root.rglob("model_registry.csv"))], ignore_index=True)
scores = pd.concat([pd.read_csv(v["path"]) for v in SEALS.values()], ignore_index=True)
base_id = scores["sample_id"].str.rsplit("|", n=1).str[0].where(scores["cell"].str.startswith("H4|"), scores["sample_id"])
scores["label"] = base_id.map(lambda s: meta.get(s, {}).get("label"))
scores["parent_id"] = base_id.map(lambda s: meta.get(s, {}).get("parent_id", s))
missing = scores["label"].isna().sum()
log("score rows", len(scores), "| models", scores["model_id"].nunique(), "| rows without metadata", int(missing))
assert missing == 0
# §3.5 (deviation 13): RW results of a generator below 90% label preservation are sensitivity-only
_dp = REPO / DECISIONS_PATH
assert _dp.exists(), "07 runs only after 04-score: human-validation decisions are missing"
HV = json.loads(_dp.read_text(encoding="utf-8"))
RW_GENS = [g for g in TEST_GENERATORS if HV["decisions"].get(g, {}).get("rw_results_role") == "primary"]
log("§3.5 human validation:", {g: HV["decisions"].get(g) for g in TEST_GENERATORS}, "| RW primary generators:", RW_GENS)
"""),
    md("## 2. Five-seed ensembles (D4, D5) and decisions at the validation thresholds"),
    code("""
scores["family"] = scores["model_id"].str.rsplit("|", n=1).str[0]
seeded = scores[scores["model_id"].str.match(r"^D[45]\\|")]
ens = (seeded.groupby(["family", "cell", "sample_id"], as_index=False)
       .agg(score=("score", "mean"), label=("label", "first"), parent_id=("parent_id", "first"), n_seeds=("model_id", "nunique")))
ens["model_id"] = ens["family"] + "|ens"
TAU = {r.model_id: {"tau5": r.tau5, "tau1": r.tau1} for r in reg.itertuples()}
for fam_id, g in ens[ens["cell"] == "VALIDATION"].groupby("model_id"):
    TAU[fam_id] = {"tau5": stats.threshold_at_fpr(g["label"], g["score"], 0.05), "tau1": stats.threshold_at_fpr(g["label"], g["score"], 0.01)}
ALL = pd.concat([scores[["model_id", "cell", "sample_id", "label", "parent_id", "score"]],
                 ens[["model_id", "cell", "sample_id", "label", "parent_id", "score"]]], ignore_index=True)
ALL["dec5"] = (ALL["score"] >= ALL["model_id"].map(lambda m: TAU[m]["tau5"])).astype(int)
ALL["dec1"] = (ALL["score"] >= ALL["model_id"].map(lambda m: TAU[m]["tau1"])).astype(int)
LOCK = ALL[ALL["cell"] != "VALIDATION"].copy()
log("models incl. ensembles", ALL["model_id"].nunique(), "| ensemble seeds", sorted(ens["n_seeds"].unique().tolist()))
def rows(model, cell): return LOCK[(LOCK["model_id"] == model) & (LOCK["cell"] == cell)]
"""),
    md("## 3. Primary endpoints PE0, PE1 and PE2 (EXT legitimate, paired within parent)"),
    code("""
def level_table(model, src="EXT", gens=None):
    gens = TEST_GENERATORS if gens is None else gens
    l0 = rows(model, f"{src}-legit-L0").set_index("sample_id")["dec5"]
    out = []
    for g in gens:
        lv = {L: rows(model, f"{src}-legit-{L}-{g}").set_index("parent_id")["dec5"] for L in ("L1", "L2", "L3", "L4")}
        complete = set(l0.index).intersection(*[set(v.index) for v in lv.values()])
        for p in sorted(complete):
            out.append({"parent": p, "generator": g, "L0": int(l0[p]), **{L: int(lv[L][p]) for L in lv}})
    return pd.DataFrame(out, columns=["parent", "generator", *LEVEL_SCORE])

# primary pools the generators that passed §3.5 for anything containing RW (L3); DN (L4, PE2) is not an RW result
ANALYSES = [("primary", RW_GENS)] + ([("sensitivity_all_generators", TEST_GENERATORS)] if RW_GENS != TEST_GENERATORS else [])
PE0, PE1, PE2 = [], [], []
for analysis, gens in ANALYSES:
    for tag, models_ in (("R1", PRIMARY), ("R2 (H6)", R2_MODELS)):
        for det, model in models_.items():
            t = level_table(model, "EXT", gens)
            long = t.melt(id_vars=["parent", "generator"], value_vars=list(LEVEL_SCORE), var_name="level", value_name="dec")
            g = stats.gee_trend(long["dec"], long["level"].map(LEVEL_SCORE), long["generator"], long["parent"])
            fpr = {L: float(t[L].mean()) if len(t) else None for L in LEVEL_SCORE}
            mc = {L: stats.mcnemar_exact(*stats.paired_discordance(t["L0"], t[L])) for L in ("L1", "L2", "L3", "L4")}
            PE0.append({"analysis": analysis, "generators": "+".join(gens), "regime": tag, "detector": det, "model": model,
                        "complete_parents": int(t["parent"].nunique()) if len(t) else 0,
                        **{f"fpr_{L}": v for L, v in fpr.items()}, **{f"gee_{k}": v for k, v in g.items()},
                        **{f"mcnemar_p_{L}": v for L, v in mc.items()}, **{f"holm_p_{L}": v for L, v in stats.holm(mc).items()}})
            todo = [("L3", PE1, t, analysis, gens)]
            if analysis == "primary":
                todo.append(("L4", PE2, level_table(model, "EXT", TEST_GENERATORS), "primary", TEST_GENERATORS))
            for L, store, tt_, an, gs in todo:
                par, a, b = tt_["parent"].values, tt_["L0"].values, tt_[L].values
                row = {"analysis": an, "generators": "+".join(gs), "regime": tag, "detector": det, "model": model, "n_pairs": len(a)}
                if len(a) == 0:
                    store.append({**row, "status": "not_estimable_no_pairs", "fpr_L0": None, f"fpr_{L}": None, "delta": None, "ci90": None,
                                  "ci95": None, "mcnemar_p": None, "n01": 0, "n10": 0, "tost_p": None, "tost_equivalent": False})
                    continue
                boot = stats.cluster_bootstrap_delta(par, a, b, iterations=BOOTSTRAP_B, seed=SEED, return_draws=True)
                n01, n10 = stats.paired_discordance(a, b)
                store.append({**row, "status": "ok", "fpr_L0": float(np.mean(a)), f"fpr_{L}": float(np.mean(b)), "delta": boot["delta"],
                              "ci90": boot["ci90"], "ci95": boot["ci95"], "mcnemar_p": stats.mcnemar_exact(n01, n10), "n01": n01, "n10": n10,
                              "tost_p": stats.bootstrap_tost_p(boot["draws"], TOST_MARGIN), "tost_equivalent": stats.tost_equivalent(boot, TOST_MARGIN)})
for store, key in ((PE1, "tost_p"), (PE2, "mcnemar_p")):
    for an, tag in sorted({(r["analysis"], r["regime"]) for r in store}):
        grp = [r for r in store if r["analysis"] == an and r["regime"] == tag]
        adj = stats.holm({r["detector"]: r[key] for r in grp if r[key] is not None}) if any(r[key] is not None for r in grp) else {}
        for r in grp:
            r[f"holm_{key}"] = adj.get(r["detector"])
pd.DataFrame(PE0).to_csv(SAFE / "pe0_dose_response.csv", index=False, lineterminator="\\n")
pd.DataFrame(PE1).to_csv(SAFE / "pe1_rewrite_equivalence.csv", index=False, lineterminator="\\n")
pd.DataFrame(PE2).to_csv(SAFE / "pe2_compose_effect.csv", index=False, lineterminator="\\n")
print(pd.DataFrame(PE0)[["analysis", "regime", "detector", "complete_parents", "fpr_L0", "fpr_L1", "fpr_L2", "fpr_L3", "fpr_L4", "gee_coef", "gee_p"]].to_string())
"""),
    md("## 4. PE3: mitigations, criteria (a), (b) and (c), with Holm over the 12 tests"),
    code("""
def pools(rw_gens):   # §3.5: L3 (RW) cells only for generators whose RW results are primary in this analysis
    ai = [f"EXT-legit-L3-{g}" for g in rw_gens] + [f"EXT-legit-L4-{g}" for g in TEST_GENERATORS] + ["LLMGen-legit"]
    ph = ["EXT-phish-H"] + [f"EXT-phish-L3-{g}" for g in rw_gens] + ["LLMGen-phish"]
    return ai, ph
def stack(model, cells_, col="dec5"):
    d = LOCK[(LOCK["model_id"] == model) & (LOCK["cell"].isin(cells_))]
    return d.set_index(["cell", "sample_id"])
def m6_decisions(model, legit_cells, phish_cells, seed):
    lg, ph = stack(model, legit_cells), stack(model, phish_cells)
    k = int(round(M6_PREVALENCE / (1 - M6_PREVALENCE) * len(lg)))
    ph_s = ph.sample(n=min(k, len(ph)), random_state=seed)
    thr = stats.alert_budget_threshold(np.r_[lg["score"].values, ph_s["score"].values], M6_BUDGET)
    out = pd.concat([lg, ph]).copy(); out["dec5"] = (out["score"] >= thr).astype(int)
    return out, thr
def compare(base, alt, cells_, label, worse_is):
    b, a = stack(base, cells_), alt.loc[alt.index.intersection(stack(base, cells_).index)] if isinstance(alt, pd.DataFrame) else stack(alt, cells_)
    j = b[["dec5", "parent_id", "label"]].join(a[["dec5"]], rsuffix="_m", how="inner")
    j = j[j["label"] == label]
    boot = stats.cluster_bootstrap_delta(j["parent_id"].values, j["dec5"].values, j["dec5_m"].values, iterations=BOOTSTRAP_B, seed=SEED)
    n01, n10 = stats.paired_discordance(j["dec5"], j["dec5_m"])
    return {"n": len(j), "base": float(j["dec5"].mean()), "mitigated": float(j["dec5_m"].mean()), **boot, "mcnemar_p": stats.mcnemar_exact(n01, n10)}
def pe3(rw_gens, analysis):
    AI_LEGIT, PHISH_POOL = pools(rw_gens)
    out = []
    for det, mits in MITIGATIONS.items():
        base = PRIMARY[det]
        for mname, model in mits.items():
            if mname == "M6":
                alt_ai, thr_ai = m6_decisions(base, AI_LEGIT, PHISH_POOL, SEED)
                alt_mod, _ = m6_decisions(base, AI_LEGIT, ["MODERN-phish"], SEED)
                alt_in, _ = m6_decisions(base, ["IN-legit-L0"], ["IN-phish-H"], SEED)
                a_ = compare(base, alt_ai, AI_LEGIT, 0, "higher"); b_ = compare(base, alt_ai, PHISH_POOL, 1, "lower")
                bm = compare(base, alt_mod, ["MODERN-phish"], 1, "lower"); c_ = compare(base, alt_in, ["IN-legit-L0"], 0, "higher")
            else:
                a_ = compare(base, model, AI_LEGIT, 0, "higher"); b_ = compare(base, model, PHISH_POOL, 1, "lower")
                bm = compare(base, model, ["MODERN-phish"], 1, "lower"); c_ = compare(base, model, ["IN-legit-L0"], 0, "higher")
            out.append({"analysis": analysis, "rw_generators": "+".join(rw_gens), "detector": det, "mitigation": mname, "model": model,
                        "ai_legit_fpr_base": a_["base"], "ai_legit_fpr_mitigated": a_["mitigated"], "ai_legit_delta": a_["delta"], "ai_legit_ci95": a_["ci95"],
                        "a_p_mcnemar": a_["mcnemar_p"],
                        "recall_delta_pool": b_["delta"], "recall_pool_lower95": b_["one_sided_95_lower"],
                        "recall_delta_modern": bm["delta"], "recall_modern_lower95": bm["one_sided_95_lower"],
                        "attacker_benefit_miss_rate_change_L3": (compare(base, model if mname != "M6" else alt_ai,
                                                                        [f"EXT-phish-L3-{g}" for g in rw_gens], 1, "lower")["delta"] * -1) if rw_gens else None,
                        "in_fpr_delta": c_["delta"], "in_fpr_upper95": c_["one_sided_95_upper"]})
    holm3 = stats.holm({(r["detector"], r["mitigation"]): r["a_p_mcnemar"] for r in out})
    for r in out:
        r["a_holm_p"] = holm3[(r["detector"], r["mitigation"])]
        r["crit_a"] = bool(r["ai_legit_delta"] <= -PE3_MIN_FPR_REDUCTION and r["ai_legit_ci95"][1] < 0 and r["a_holm_p"] < 0.05)
        r["crit_b"] = bool(r["recall_pool_lower95"] > PE3_RECALL_MARGIN and r["recall_modern_lower95"] > PE3_RECALL_MARGIN)
        r["crit_c"] = bool(r["in_fpr_upper95"] <= PE3_IN_FPR_MARGIN)
        r["passes_all"] = r["crit_a"] and r["crit_b"] and r["crit_c"]
    return out
PE3 = pe3(RW_GENS, "primary") + (pe3(TEST_GENERATORS, "sensitivity_all_generators") if RW_GENS != TEST_GENERATORS else [])
pd.DataFrame(PE3).to_csv(SAFE / "pe3_mitigations.csv", index=False, lineterminator="\\n")
print(pd.DataFrame(PE3)[["analysis", "detector", "mitigation", "ai_legit_delta", "recall_delta_pool", "recall_delta_modern", "in_fpr_delta", "crit_a", "crit_b", "crit_c", "passes_all"]].to_string())
"""),
    md("## 5. Secondary analyses: per-cell metrics, H2 source effect, H4 interventions, H4b failure decomposition, H1-IN"),
    code("""
from sklearn.metrics import roc_auc_score
SEC = []
for (m, c), d in LOCK[~LOCK["cell"].str.startswith("H4|")].groupby(["model_id", "cell"]):
    lab = d["label"].iloc[0] if d["label"].nunique() == 1 else None
    for tau in ("dec5", "dec1"):
        k, n = int(d[tau].sum()), len(d)
        lo, hi = stats.wilson_ci(k, n)
        SEC.append({"model": m, "cell": c, "threshold": tau.replace("dec", "tau"), "n": n, "class": {0: "legitimate", 1: "phishing", None: "mixed"}[lab],
                    "rate": k / n, "metric": "FPR" if lab == 0 else "recall" if lab == 1 else "flag_rate", "wilson95": (lo, hi)})
sec = pd.DataFrame(SEC); sec.to_csv(SAFE / "secondary_cell_metrics.csv", index=False, lineterminator="\\n")
H2 = []
for m in sorted(LOCK["model_id"].unique()):
    base = rows(m, "IN-legit-L0")["dec5"]
    for c in ("EXT-legit-L0", "EXT2-legit-L0"):
        x = rows(m, c)["dec5"]
        if len(base) and len(x):
            bb = [RNG.choice(x.values, len(x)).mean() - RNG.choice(base.values, len(base)).mean() for _ in range(2000)]
            H2.append({"model": m, "cell": c, "fpr_cell": x.mean(), "fpr_IN": base.mean(), "delta": x.mean() - base.mean(),
                       "ci95": (float(np.quantile(bb, .025)), float(np.quantile(bb, .975)))})
pd.DataFrame(H2).to_csv(SAFE / "h2_source_effect.csv", index=False, lineterminator="\\n")
logit = lambda p: np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
H4 = []
for m in H4_MODELS:
    for src in ["EXT-legit-L0"] + [f"EXT-legit-L4-{g}" for g in TEST_GENERATORS]:
        o = rows(m, src).set_index("sample_id")
        for kind in ("I1", "I2", "I3", "I4", "I5", "I6"):
            iv = rows(m, f"H4|{src}|{kind}").copy()
            if not len(iv) or not len(o):
                continue
            iv["base_id"] = iv["sample_id"].str.rsplit("|", n=1).str[0]
            j = iv.join(o[["score"]], on="base_id", rsuffix="_orig").dropna(subset=["score_orig"])
            dl = logit(j["score"].values) - logit(j["score_orig"].values)
            bs = [RNG.choice(dl, len(dl)).mean() for _ in range(2000)]
            H4.append({"model": m, "source": src, "intervention": kind, "n": len(dl), "mean_delta_logit": float(dl.mean()),
                       "ci95": (float(np.quantile(bs, .025)), float(np.quantile(bs, .975))),
                       "decision_flip_rate": float(np.mean((j["score"] >= TAU[m]["tau5"]) != (j["score_orig"] >= TAU[m]["tau5"])))})
pd.DataFrame(H4).to_csv(SAFE / "h4_interventions.csv", index=False, lineterminator="\\n")
VAL_RECALL = {r.model_id: r.val_recall_at_tau5 for r in reg.itertuples()}
for fam_id, g in ens[ens["cell"] == "VALIDATION"].groupby("model_id"):
    VAL_RECALL[fam_id] = float(np.mean(g.loc[g["label"] == 1, "score"] >= TAU[fam_id]["tau5"]))
PAIRS = [("IN-legit-L0", "IN-phish-H"), ("EXT-legit-L0", "EXT-phish-H"), ("LLMGen-legit", "LLMGen-phish"),
         ("Greco24-legit", "Greco24-phish"), ("DEV-ephish-legit", "DEV-ephish-phish")] + \\
        [(f"EXT-legit-{L}-{g}", "EXT-phish-H") for L in ("L1", "L2", "L3", "L4") for g in TEST_GENERATORS]
H4B = []
for m in list(PRIMARY.values()) + ["D6|zero-shot|M0|s0"]:
    for lc, pc in PAIRS:
        L, P = rows(m, lc), rows(m, pc)
        if not len(L) or not len(P):
            continue
        y = np.r_[np.zeros(len(L)), np.ones(len(P))]; s = np.r_[L["score"].values, P["score"].values]
        oracle_t = np.quantile(P["score"].values, 1 - VAL_RECALL.get(m, 0.95), method="lower")
        H4B.append({"model": m, "legit_cell": lc, "phish_cell": pc, "auroc": roc_auc_score(y, s), "fpr_at_tau5": float(L["dec5"].mean()),
                    "fpr_at_oracle_matched_recall": float(np.mean(L["score"].values >= oracle_t)),
                    **{f"{k}_prev{int(pi * 100)}pct": v for pi in (0.01, 0.05) for k, v in (
                        ("alerts_per_10k", 1e4 * (pi * P["dec5"].mean() + (1 - pi) * L["dec5"].mean())),
                        ("precision", (pi * P["dec5"].mean()) / max(1e-12, pi * P["dec5"].mean() + (1 - pi) * L["dec5"].mean())))}})
pd.DataFrame(H4B).to_csv(SAFE / "h4b_failure_decomposition.csv", index=False, lineterminator="\\n")
H1IN = []
for det, model in PRIMARY.items():
    l0 = rows(model, "IN-legit-L0").set_index("parent_id")["dec5"]
    for c in [f"IN-legit-L3-{p}" for p in ("gpt4o", "deepseek", "randomapi")] + [f"IN-legit-L3-{g}" for g in TEST_GENERATORS]:
        r_ = rows(model, c).set_index("parent_id")["dec5"]; common = sorted(set(l0.index) & set(r_.index))
        if not common:
            continue
        b = stats.cluster_bootstrap_delta(common, l0[common].values, r_[common].values, iterations=BOOTSTRAP_B, seed=SEED)
        H1IN.append({"detector": det, "cell": c, "n": len(common), "delta": b["delta"], "ci90": b["ci90"], "tost_equivalent": stats.tost_equivalent(b, TOST_MARGIN)})
pd.DataFrame(H1IN).to_csv(SAFE / "h1_in_replication.csv", index=False, lineterminator="\\n")
log("secondary analyses written")

# ---- Deviation 15: pre-specified EXPLORATORY extensions (never in the §7 claims or the primary Holm families) ----
def pairs_for(model, l0_cell, lk_cells):
    l0 = rows(model, l0_cell).set_index("sample_id")["dec5"]
    out = []
    for c in lk_cells:
        d = rows(model, c)
        out += [(pid, int(l0[pid]), int(dec)) for pid, dec in zip(d["parent_id"], d["dec5"]) if pid in l0.index]
    return out
def x_row(endpoint, det, model, prs, ref="L0"):
    row = {"endpoint": endpoint, "detector": det, "model": model, "reference": ref, "n_pairs": len(prs)}
    if not prs:
        return {**row, "status": "not_estimable_no_pairs"}
    par, a, b = (list(t) for t in zip(*prs))
    boot = stats.cluster_bootstrap_delta(par, a, b, iterations=BOOTSTRAP_B, seed=SEED)
    n01, n10 = stats.paired_discordance(a, b)
    return {**row, "status": "ok", "rate_ref": float(np.mean(a)), "rate_cmp": float(np.mean(b)), "delta": boot["delta"],
            "ci90": boot["ci90"], "ci95": boot["ci95"], "mcnemar_p": stats.mcnemar_exact(n01, n10),
            "tost_equivalent_descriptive": stats.tost_equivalent(boot, TOST_MARGIN)}
XR = []
for det, model in PRIMARY.items():
    XR.append(x_row("X1a_EXT3_L3_vs_L0", det, model, pairs_for(model, "EXT3-legit-L0", [f"EXT3-legit-L3-{g}" for g in RW_GENS])))
    XR.append(x_row("X1b_EXT3_L4_vs_L0", det, model, pairs_for(model, "EXT3-legit-L0", [f"EXT3-legit-L4-{g}" for g in TEST_GENERATORS])))
    x, b = rows(model, "EXT3-legit-L0")["dec5"].values, rows(model, "EXT-legit-L0")["dec5"].values
    if len(x) and len(b):
        bb = [RNG.choice(x, len(x)).mean() - RNG.choice(b, len(b)).mean() for _ in range(2000)]
        XR.append({"endpoint": "X1c_EXT3_L0_minus_EXT_L0", "detector": det, "model": model, "reference": "EXT-legit-L0", "status": "ok",
                   "n_pairs": None, "rate_ref": float(b.mean()), "rate_cmp": float(x.mean()), "delta": float(x.mean() - b.mean()),
                   "ci95": (float(np.quantile(bb, .025)), float(np.quantile(bb, .975)))})
    XR.append(x_row("X2a_14B_L3_vs_L0", det, model, pairs_for(model, "EXT-legit-L0", ["EXT-legit-L3-qwen2.5-14b"])))
    XR.append(x_row("X2b_14B_L4_vs_L0", det, model, pairs_for(model, "EXT-legit-L0", ["EXT-legit-L4-qwen2.5-14b"])))
    for L in ("L3", "L4"):   # X2c: same parents, 14B decision minus 7B decision
        d14 = rows(model, f"EXT-legit-{L}-qwen2.5-14b").set_index("parent_id")["dec5"]
        d7 = rows(model, f"EXT-legit-{L}-qwen2.5-7b").set_index("parent_id")["dec5"]
        common = sorted(set(d14.index) & set(d7.index))
        XR.append(x_row(f"X2c_scale_{L}_14B_minus_7B", det, model, [(p, int(d7[p]), int(d14[p])) for p in common], ref=f"{L} Qwen2.5-7B"))
for r in XR:
    r["qwen_rw_role"] = HV["decisions"].get("qwen2.5-7b", {}).get("rw_results_role")
pd.DataFrame(XR).to_csv(SAFE / "exploratory_extensions.csv", index=False, lineterminator="\\n")
log("exploratory extensions", len(XR), "rows")
"""),
    md("## 6. Per-row predictions (D009: IDs only), claims (§7) and manifest"),
    code("""
pred = ALL.merge(pd.Series({k: v["level"] for k, v in meta.items()}, name="level"), left_on="sample_id", right_index=True, how="left")
pred[["model_id", "cell", "sample_id", "parent_id", "label", "level", "score", "dec5", "dec1"]].to_csv(
    SAFE / "per_row_predictions.csv.gz", index=False, compression="gzip", lineterminator="\\n")
def claim(det):
    prim = lambda store: next(r for r in store if r["analysis"] == "primary" and r["regime"] == "R1" and r["detector"] == det)
    p1, p2, p0 = prim(PE1), prim(PE2), prim(PE0)
    if p1["status"] != "ok":
        pe1 = "not_estimable"
    else:
        lo, hi = p1["ci90"]
        pe1 = "equivalent" if p1["tost_equivalent"] and p1["holm_tost_p"] < 0.05 else ("increase" if lo > 0 and p1["mcnemar_p"] < 0.05 else "inconclusive")
    pe2 = ("not_estimable" if p2["status"] != "ok" else "increase" if p2["holm_mcnemar_p"] < 0.05 and p2["delta"] > 0 else
           "decrease" if p2["holm_mcnemar_p"] < 0.05 and p2["delta"] < 0 else "not_significant")
    pe0 = ("rising" if p0.get("gee_p") is not None and p0["gee_p"] < 0.05 and p0["gee_coef"] > 0 else
           "falling" if p0.get("gee_p") is not None and p0["gee_p"] < 0.05 and p0["gee_coef"] < 0 else "flat_or_not_estimable")
    table = {("equivalent", "not_significant"): "source-shift problem: neither paraphrase-level nor de-novo AI authorship adds measurable false alarms",
             ("equivalent", "increase"): "AI-authored content/genre adds false alarms beyond source; paraphrase style harmless",
             ("increase", "increase"): "AI rewriting style itself raises false alarms in external mail (interaction with source)",
             ("increase", "not_significant"): "AI rewriting style itself raises false alarms in external mail (interaction with source)"}
    text = table.get((pe1, pe2), "inconclusive: report CIs, no directional claim")
    if pe2 == "decrease":
        text += "; AI-authored legitimate mail flagged LESS often (discuss the security implication)"
    return {"PE0": pe0, "PE1": pe1, "PE2": pe2, "claim": text, "rw_primary_generators": RW_GENS,
            "mitigations_passing_all": [r["mitigation"] for r in PE3 if r["analysis"] == "primary" and r["detector"] == det and r["passes_all"]]}
CLAIMS = {det: claim(det) for det in PRIMARY}
manifest.write_json(SAFE / "claims.json", CLAIMS)
manifest.write_json(SAFE / "thresholds.json", TAU)
txt_leak = pred.columns.intersection(["subject", "body"]).tolist()
n_prim = lambda store: sum(r["analysis"] == "primary" for r in store)
GATES = {"all_seals_verified": SEAL_OK, "human_validation_decisions_applied": True,
         "primary_endpoints_present": n_prim(PE0) == 4 and n_prim(PE1) == 4 and n_prim(PE2) == 4 and n_prim(PE3) == 12,
         "per_row_file_has_no_text_columns": not txt_leak,
         "exploratory_extensions_computed": len(XR) == 7 * len(PRIMARY)}
manifest.write_json(SAFE / "run_manifest.json", {"notebook": "07_Confirmatory_Evaluation", "status": "COMPLETED" if all(GATES.values()) else "COMPLETED_WITH_GATE_FAILURES",
                    "gates": GATES, "seals": {k: v["found"] for k, v in SEALS.items()}, "claims": CLAIMS, "params": PARAMS, "environment": ENV,
                    "selftest": SELFTEST, "runtime_seconds": round(time.time() - T0, 1), "files": manifest.file_hashes(SAFE)})
log("CLAIMS", json.dumps(CLAIMS, indent=1)); log("gates", GATES); assert all(GATES.values())
"""),
]
write_notebook(OUT, cells, gpu=False)
print("wrote", OUT)
