"""Builds notebooks/05_Detector_Training_and_Sealed_Scoring.ipynb (PART = 'classical', 'transformers-a' or 'transformers-b')."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import code, env_cell, header, md, params_cell, selftest_cell, write_notebook  # noqa: E402

OUT, COMMIT, PART = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
assert PART in ("classical", "transformers-a", "transformers-b")

PARAMS = {
    "REPO_URL": "https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git",
    "CODE_COMMIT": COMMIT,
    "PART": PART,
    "SEED": 2026,
    "SEEDS": [2026, 2027, 2028, 2029, 2030],
    "EXPECTED_VERSIONS": {"sklearn": "1.6.1", "transformers": "5.20.2"},
    "TEST_GENERATORS": ["qwen2.5-7b", "phi-3.5-mini"],
    "TRAIN_GENERATOR": "olmo-2-7b",
    "EXTENSION_INPUTS": ["records_ext3", "generated_qwen2.5-7b__ext3", "generated_phi-3.5-mini__ext3", "generated_qwen2.5-14b"],   # deviation 15
    "FPR_TARGETS": {"tau5": 0.05, "tau1": 0.01},
    "D1_C_GRID": [0.1, 1.0, 10.0],
    "D3_ALPHA_GRID": [0.1, 0.5, 1.0],
    "M2_LAMBDA": 0.2,
    "TRANSFORMERS": {"D4": {"repo": "distilbert/distilbert-base-uncased", "revision": "12040accade4e8a0f71eabdb258fecc2e7e948be", "max_epochs": 2},
                     "D5": {"repo": "FacebookAI/roberta-base", "revision": None, "max_epochs": 4}},
    "TRANSFORMER_PLAN": {"D4": [["R1", "M0"], ["R2", "M0"]],
                         "D5": [["R1", "M0"], ["R2", "M0"], ["R1", "M1"], ["R1", "M2"], ["R1", "M4"], ["R1", "M5"]]},
    # D019: the pre-registered plan above runs as two kernels, each well inside Kaggle's 12 h limit (union == plan)
    "TRANSFORMER_SHARDS": {"transformers-a": {"D4": [["R1", "M0"], ["R2", "M0"]], "D5": [["R1", "M0"], ["R2", "M0"]]},
                           "transformers-b": {"D5": [["R1", "M1"], ["R1", "M2"], ["R1", "M4"], ["R1", "M5"]]}},
    "H4_MODELS": ["D1|R1|M0", "D2|R1|M0", "D3|R1|M0", "D5|R1|M0"],
    "INPUT_ROOT": "/kaggle/input",
}

cells = [
    header("05", f"Detector training, validation-only selection and sealed scoring ({PART})",
           "Train every pre-registered detector and mitigation variant: D1 TF-IDF LR, D2 calibrated LinearSVC and D3 ComplementNB "
           "under R1, R2 and R2+Nigerian; D2 with M1/M2/M4/M5; D4 DistilBERT under R1 and R2; D5 RoBERTa under R1/R2/M1/M2/M4/M5, five seeds each. "
           "Hyperparameters and τ5/τ1 thresholds come **only** from training and validation data. Then score every cell (locked cells included) "
           "into **sealed** per-model files (deviation 7): **no locked-cell metric is computed or shown here**.",
           "§4, §5, deviations 6–7",
           ["`01` private records (training/validation roles and locked cells)",
            "`03` generated records: test-only Qwen/Phi cells; OLMo training-side augmentation"],
           ["`safe_05/<part>/` (committed): model registry (hyperparameters, validation metrics, thresholds), training histories, seal hashes",
            "`private_05/<part>/scores/*.csv.gz` (sealed, private): per-model scores for every cell, opened only by 07"],
           ["every planned model trained", "every model's validation FPR at τ5 ≤ 0.05", "the seal manifest lists every score file with its SHA-256"],
           "Kaggle GPU T4×2 (the classical part uses CPU only), internet ON; classical about 30 minutes, transformers about 4–6 hours"),
    params_cell(PARAMS),
    env_cell("""import numpy as np
from phishbench import models, stats, interventions
SAFE, PRIVATE = WORK / "safe_05" / PART, WORK / "private_05" / PART
SCORES = PRIVATE / "scores"
for _p in (SAFE, PRIVATE, SCORES):
    _p.mkdir(parents=True, exist_ok=True)"""),
    selftest_cell(),
    md("## 1. Load the locked records (01) and the generated records (03)"),
    code("""
read_gz = manifest.read_jsonl          # .jsonl.gz from kernel outputs, .jsonl from Kaggle datasets (deviation 12)
INPUTS = {"01": manifest.find_artifact(INPUT_ROOT, "records")}
for g in TEST_GENERATORS + [TRAIN_GENERATOR]:
    INPUTS[g] = manifest.find_artifact(INPUT_ROOT, f"generated_{g}")
for stem in EXTENSION_INPUTS:   # deviation 15: extension cells are scored in the same sealed run
    INPUTS[stem] = manifest.find_artifact(INPUT_ROOT, stem)
INPUT_SHA256 = {k: manifest.content_sha256(v) for k, v in INPUTS.items()}
by_cell = defaultdict(list)
for k, p in INPUTS.items():
    for r in read_gz(p):
        by_cell[r["cell"]].append(r)
ROLE_KEYS = {"train_r1", "val_r1", "train_r1_rw", "val_r1_rw", "train_r2_extra", "val_r2_extra", "train_r2_sens_nigerian"}
TRAIN_SIDE = {c for c in by_cell if c.startswith("train_r1-")}
SCORE_CELLS = sorted(c for c in by_cell if c not in ROLE_KEYS and c not in TRAIN_SIDE)
log("inputs", {k: v[:12] for k, v in INPUT_SHA256.items()}, "| cells to score", len(SCORE_CELLS))

# H4 intervention cells (legitimate only): EXT-legit-L0 and EXT-legit-L4 from each test generator
H4_SOURCES = ["EXT-legit-L0"] + [f"EXT-legit-L4-{g}" for g in TEST_GENERATORS]
for src in H4_SOURCES:
    for kind in interventions.KINDS:
        by_cell[f"H4|{src}|{kind}"] = [{**r, "sample_id": f"{r['sample_id']}|{kind}", "body": interventions.apply(kind, r["body"]),
                                        "cell": f"H4|{src}|{kind}"} for r in by_cell[src]]
H4_CELLS = sorted(c for c in by_cell if c.startswith("H4|"))

def text(r, norm=False):
    t = textnorm.detector_input(r["subject"], r["body"])
    return textnorm.artifact_normalize(t) if norm else t
"""),
    md("## 2. Training sets for every regime and mitigation (frozen definitions, §2.2 and §5)"),
    code("""
R1_tr, R1_va = by_cell["train_r1"], by_cell["val_r1"]
legit_rw = [r for r in by_cell["train_r1_rw"] if r["label"] == 0] + by_cell[f"train_r1-legit-L3-{TRAIN_GENERATOR}"]
fam = Counter(r["parent_id"] for r in legit_rw)
def family_weight(r):
    return 1.0 / (1 + fam[r["parent_id"]]) if r["label"] == 0 and fam.get(r["parent_id"]) else 1.0
rng = random.Random(SEED)
dn = sorted(by_cell[f"train_r1-legit-L4-{TRAIN_GENERATOR}"], key=lambda r: r["sample_id"])
rwp = sorted(by_cell[f"train_r1-phish-L3-{TRAIN_GENERATOR}"], key=lambda r: r["sample_id"])
n5 = min(len(dn), len(rwp))
m5_extra = rng.sample(dn, n5) + rng.sample(rwp, n5)
TRAINSETS = {   # key -> (train rows, train weights, validation rows, normalise?, pairs as (parent_row, rewrite_row) indices)
    ("R1", "M0"): (R1_tr, None, R1_va, False, None),
    ("R2", "M0"): (R1_tr + by_cell["train_r2_extra"], None, R1_va + by_cell["val_r2_extra"], False, None),
    ("R2S", "M0"): (R1_tr + by_cell["train_r2_extra"] + by_cell["train_r2_sens_nigerian"], None, R1_va + by_cell["val_r2_extra"], False, None),
    ("R1", "M4"): (R1_tr, None, R1_va, True, None),
    ("R1", "M5"): (R1_tr + m5_extra, None, R1_va, False, None),
}
m1_rows = R1_tr + legit_rw
m1_w = np.array([family_weight(r) for r in m1_rows])
pos = {r["sample_id"]: i for i, r in enumerate(m1_rows)}
m1_pairs = [(pos[r["parent_id"]], pos[r["sample_id"]]) for r in legit_rw if r["parent_id"] in pos]
TRAINSETS[("R1", "M1")] = (m1_rows, m1_w, R1_va, False, None)
TRAINSETS[("R1", "M2")] = (m1_rows, m1_w, R1_va, False, m1_pairs)
log({f"{k[0]}|{k[1]}": len(v[0]) for k, v in TRAINSETS.items()}, "| M2 pairs", len(m1_pairs), "| M5 extra", len(m5_extra))

REGISTRY, HISTORY, SEAL = [], [], {}
def finish(model_id, detector, regime, mit, seed, val_rows, val_scores, score_fn, hparams, seconds, norm):
    yv = np.array([r["label"] for r in val_rows])
    sv = np.asarray(val_scores, dtype=float)
    taus = {k: stats.threshold_at_fpr(yv, sv, v) for k, v in FPR_TARGETS.items()}
    from sklearn.metrics import average_precision_score, roc_auc_score
    REGISTRY.append({"model_id": model_id, "detector": detector, "regime": regime, "mitigation": mit, "seed": seed,
                     "hyperparameters": json.dumps(hparams), "n_val": len(yv), "val_ap": average_precision_score(yv, sv),
                     "val_auroc": roc_auc_score(yv, sv), **taus,
                     "val_fpr_at_tau5": float(np.mean(sv[yv == 0] >= taus["tau5"])),
                     "val_recall_at_tau5": float(np.mean(sv[yv == 1] >= taus["tau5"])), "train_seconds": round(seconds, 1)})
    cells_here = SCORE_CELLS + (H4_CELLS if "|".join(model_id.split("|")[:3]) in H4_MODELS else [])
    path = SCORES / (model_id.replace("|", "__") + ".csv.gz")
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:      # SEALED: scores only, no metric computed here
        wr = csv.writer(f, lineterminator="\\n"); wr.writerow(["model_id", "cell", "sample_id", "score"])
        for c in cells_here:
            rows = by_cell[c]
            for r, s in zip(rows, score_fn([text(x, norm) for x in rows])):
                wr.writerow([model_id, c, r["sample_id"], f"{float(s):.8f}"])
        for r, s in zip(val_rows, sv):
            wr.writerow([model_id, "VALIDATION", r["sample_id"], f"{float(s):.8f}"])
    SEAL[path.name] = manifest.sha256_file(path)
    log(f"  sealed {model_id}: val AP {REGISTRY[-1]['val_ap']:.4f}, val FPR@tau5 {REGISTRY[-1]['val_fpr_at_tau5']:.3f}")
"""),
]

if PART == "classical":
    cells += [md("## 3. Classical detectors D1–D3 and D2 mitigations (validation-only selection; sealed scoring)"),
              code("""
CV_SCORES = []
for (regime, mit), (tr, w, va, norm, pairs) in TRAINSETS.items():
    t = time.time()
    vec = models.make_vectorizer().fit([text(r, norm) for r in tr])
    X = vec.transform([text(r, norm) for r in tr]); y = np.array([r["label"] for r in tr])
    Xv = vec.transform([text(r, norm) for r in va])
    groups = np.array([r["parent_id"] for r in tr])
    ww = None if w is None else np.asarray(w)
    plan = [("D1", "D2", "D3")] if mit == "M0" else [("D2",)]
    for det in plan[0]:
        t1 = time.time()
        if det == "D1":
            best, cv = models.grouped_cv_select(lambda a, b, c, C: models.fit_d1_lr(a, b, c, C, SEED), D1_C_GRID, X, y, ww, groups, SEED)
            clf = models.fit_d1_lr(X, y, ww, best, SEED); hp = {"C": best}
            CV_SCORES += [{"model": f"D1|{regime}|{mit}", "value": k, "cv_ap": v} for k, v in cv.items()]
        elif det == "D3":
            best, cv = models.grouped_cv_select(lambda a, b, c, al: models.fit_d3_cnb(a, b, c, al), D3_ALPHA_GRID, X, y, ww, groups, SEED)
            clf = models.fit_d3_cnb(X, y, ww, best); hp = {"alpha": best}
            CV_SCORES += [{"model": f"D3|{regime}|{mit}", "value": k, "cv_ap": v} for k, v in cv.items()]
        elif mit == "M2":
            for lam_tag, lam in (("M2", M2_LAMBDA), ("M2ctrl", 0.0)):
                P = X[[a for a, _ in pairs]]; Rr = X[[b for _, b in pairs]]
                clf = models.ConsistencyLinear(lam=lam).fit(X, y, ww, P, Rr).calibrate(Xv, np.array([r["label"] for r in va]))
                finish(f"D2|{regime}|{lam_tag}|s{SEED}", "D2", regime, lam_tag, SEED, va, clf.predict_proba(Xv)[:, 1],
                       lambda txts, c=clf: c.predict_proba(vec.transform(txts))[:, 1],
                       {"lambda": lam, "C": 1.0, "converged": clf.converged_, "iterations": clf.n_iter_}, time.time() - t1, norm)
            continue
        else:
            clf = models.fit_d2_svm(X, y, ww, SEED); hp = {"C": 1.0, "calibration": "sigmoid cv=3"}
        finish(f"{det}|{regime}|{mit}|s{SEED}", det, regime, mit, SEED, va, clf.predict_proba(Xv)[:, 1],
               lambda txts, c=clf: c.predict_proba(vec.transform(txts))[:, 1], hp, time.time() - t1, norm)
    log(regime, mit, "done in", round(time.time() - t, 1), "s")
with (SAFE / "cv_scores.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=["model", "value", "cv_ap"], lineterminator="\\n"); wr.writeheader(); wr.writerows(CV_SCORES)
""")]
else:
    cells += [md("## 3. Transformer detectors D4 and D5, five seeds each (validation-only epoch selection; sealed scoring)"),
              code("""
import torch
from transformers import AutoTokenizer
from huggingface_hub import HfApi, snapshot_download
from phishbench import transformer_train as tt
api = HfApi()
PLAN = TRANSFORMER_SHARDS[PART]
_union = sorted((d, tuple(c)) for sh in TRANSFORMER_SHARDS.values() for d, cs in sh.items() for c in cs)
assert _union == sorted((d, tuple(c)) for d, cs in TRANSFORMER_PLAN.items() for c in cs), "shards must cover the plan exactly once"
RESOLVED = {}
for det, cfg in [(d, TRANSFORMERS[d]) for d in PLAN]:
    rev = cfg["revision"] or api.model_info(cfg["repo"]).sha
    RESOLVED[det] = {"repo": cfg["repo"], "revision": rev,
                     "path": snapshot_download(cfg["repo"], revision=rev, allow_patterns=["*.json", "*.safetensors", "*.txt", "merges.txt", "vocab*"])}
    log(det, cfg["repo"], rev)
for det, plan in PLAN.items():
    tok = AutoTokenizer.from_pretrained(RESOLVED[det]["path"])
    cache = {}
    def enc_texts(txts):
        missing = sorted({t for t in txts if t not in cache})
        for t, e in zip(missing, tt.encode(tok, missing)):
            cache[t] = e
        return [cache[t] for t in txts]
    def enc(rows, norm):
        return enc_texts([text(r, norm) for r in rows])
    for regime, mit in plan:
        tr, w, va, norm, pairs = TRAINSETS[(regime, mit)]
        etr, eva = enc(tr, norm), enc(va, norm)
        y = np.array([r["label"] for r in tr]); yv = np.array([r["label"] for r in va])
        for seed in SEEDS:
            t1 = time.time(); log(f"{det}|{regime}|{mit}|s{seed}")
            model, hist = tt.train_classifier(RESOLVED[det]["path"], tok, etr, y, w, eva, yv, seed, TRANSFORMERS[det]["max_epochs"],
                                              pairs=pairs, lam=M2_LAMBDA if mit == "M2" else 0.0, log=log)
            HISTORY += [{"model_id": f"{det}|{regime}|{mit}|s{seed}", **h} for h in hist]
            finish(f"{det}|{regime}|{mit}|s{seed}", det, regime, mit, seed, va, tt.predict_proba(model, tok, eva),
                   lambda txts, m=model: tt.predict_proba(m, tok, enc_texts(txts)),
                   {"repo": RESOLVED[det]["repo"], "revision": RESOLVED[det]["revision"], "lr": 2e-5, "batch": 16,
                    "max_len": 256, "max_epochs": TRANSFORMERS[det]["max_epochs"], "best_epoch": int(max(hist, key=lambda h: h["val_ap"])["epoch"]),
                    "m2_lambda": M2_LAMBDA if mit == "M2" else 0.0}, time.time() - t1, norm)
            del model; torch.cuda.empty_cache()
with (SAFE / "training_history.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=["model_id", "epoch", "train_loss", "val_ap", "seconds"], lineterminator="\\n"); wr.writeheader(); wr.writerows(HISTORY)
""")]

cells += [md("## 4. Registry, seal manifest and gates"),
          code("""
with (SAFE / "model_registry.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(REGISTRY[0].keys()), lineterminator="\\n"); wr.writeheader(); wr.writerows(REGISTRY)
expected = (sum(3 if m == "M0" else (2 if m == "M2" else 1) for (_, m) in TRAINSETS) if PART == "classical"
            else sum(len(p) * len(SEEDS) for p in TRANSFORMER_SHARDS[PART].values()))
manifest.write_json(SAFE / "seal_manifest.json", {"part": PART, "rule": "deviation 7: per-model score files are opened only by 07",
                                                  "files": SEAL, "combined_sha256": manifest.sha256_of_ids(f"{k}:{v}" for k, v in SEAL.items())})
GATES = {"every_planned_model_trained": len(REGISTRY) == expected,
         "validation_fpr_at_tau5_le_0.05": all(r["val_fpr_at_tau5"] <= 0.05 + 1e-12 for r in REGISTRY),
         "seal_lists_every_model": len(SEAL) == len(REGISTRY)}
STATUS = "COMPLETED" if all(GATES.values()) else "COMPLETED_WITH_GATE_FAILURES"
manifest.write_json(SAFE / "run_manifest.json", {"notebook": f"05_Detector_Training_and_Sealed_Scoring[{PART}]", "status": STATUS, "gates": GATES,
                    "models": len(REGISTRY), "input_sha256": INPUT_SHA256, "params": PARAMS, "environment": ENV, "selftest": SELFTEST,
                    "runtime_seconds": round(time.time() - T0, 1), "files": manifest.file_hashes(SAFE)})
log("STATUS", STATUS, GATES)
assert all(GATES.values())
""")]
write_notebook(OUT, cells, gpu=(PART != "classical"))
print("wrote", OUT)
