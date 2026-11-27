"""Builds notebooks/04_Human_Validation.ipynb (one notebook, two kernels; PART = kit | score).

kit   : draw the blinded §3.5 sample from the test generators and write one workbook per rater plus a private key.
score : after both raters finish and disagreements are adjudicated, compute kappa, preservation rates and the §3.5 rule.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import code, env_cell, header, md, params_cell, selftest_cell, write_notebook  # noqa: E402

OUT, COMMIT, PART = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
assert PART in ("kit", "score"), PART
PARAMS = {
    "REPO_URL": "https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git",
    "CODE_COMMIT": COMMIT,
    "SEED": 2026,
    "PART": PART,
    "EXPECTED_VERSIONS": {"sklearn": "1.6.1"},
    "INPUT_ROOT": "/kaggle/input",
    "TEST_GENERATORS": ["qwen2.5-7b", "phi-3.5-mini"],
    "SOURCES": ["EXT", "IN"],
    "RW_PER_STRATUM": 50,      # 2 generators x 2 sources x 50 = 200 per label (§3.5)
    "DN_PER_STRATUM": 25,      # 2 generators x 2 sources x 25 = 100 DN (§3.5)
    "RATERS": ["A", "B"],
    "PRACTICE_RW_PER_LABEL": 6,   # D2-provided GPT-4o rewrites, parents outside the real sample (deviation 11)
    "PRACTICE_DN_PER_CELL": 4,    # LLMGen-legit and Greco24-legit
    "PRESERVATION_MIN": 0.90,
    "KAPPA_TARGET": 0.60,
    "KAPPA_BOOTSTRAP_B": 2000,
    "RATINGS_DIR": "results/04_human_validation/ratings",
    "KIT_RESULTS_DIR": "results/04_human_validation/kit",
}

COMMON_OUT = "`safe_04/<part>/` (committed to `results/04_human_validation/<part>/`)"
if PART == "kit":
    head = header(
        "04", "Human validation — blinded rating kit",
        "Draw the pre-registered human-validation sample: 200 legitimate and 200 phishing L3 rewrites (RW), stratified by test "
        "generator and source with disjoint parents across generators, and 100 L4 compositions (DN). Items get opaque IDs, "
        "links are defanged, and each rater receives their own workbook in their own seeded order. The key that links items to "
        "generators stays private; only its SHA-256 is committed, so it cannot change after rating starts.",
        "§3.5, deviations 9–11 (rating guide: `docs/RATING_GUIDE.md`)",
        ["Kernel output of `01-data-sources-audit-and-locked-cells` (parents)",
         "Kernel outputs of `03-generation-qwen2-5-7b` and `03-generation-phi-3-5-mini` (generated text and run manifests)"],
        [COMMON_OUT + ": sample summary, rater instructions, run manifest with the key and item hashes",
         "`private_04/rater_A.xlsx`, `rater_B.xlsx`, `practice_A.xlsx`, `practice_B.xlsx`, `key.csv`, `practice_key.csv` (private; never committed)"],
        ["both generated files match the SHA-256 committed in `results/03_generation/<generator>/private_files_sha256.json`",
         "every stratum and the practice set reach their target sizes", "no email text in safe outputs"],
        "Kaggle GPU T4×2 image (CPU work), about 2 minutes")
else:
    head = header(
        "04", "Human validation — agreement and preservation",
        "Read both raters' answers (committed without text), verify the private key against the hash committed by the kit run, "
        "check that every disagreement is adjudicated, and compute: Cohen's kappa for the label question (target ≥ 0.60) and for the "
        "other questions with item-bootstrap CIs; the label-preservation rate per generator with a Wilson 95% CI, counting 'unsure' "
        "as not preserved; intent, security-element and DN plausibility rates; and the §3.5 rule (a generator below 90% label "
        "preservation has its RW results reported only as sensitivity analysis).",
        "§3.5, deviation 9",
        ["Kernel output of `04-human-validation-kit` (private key)",
         f"`{PARAMS['RATINGS_DIR']}/rater_A.csv`, `rater_B.csv`, `adjudication.csv` and `{PARAMS['KIT_RESULTS_DIR']}/run_manifest.json` "
         "at the pinned commit"],
        [COMMON_OUT + ": agreement.csv, rates.csv, items.csv (IDs and answers, no text), decisions.json, run manifest"],
        ["key hash equals the committed kit hash", "both raters answered every item", "every disagreement is resolved",
         "no email text in safe outputs"],
        "Kaggle GPU T4×2 image (CPU work), about 1 minute")

cells = [
    head,
    params_cell(PARAMS),
    env_cell("""from phishbench import human_validation as hv
SAFE, PRIVATE = WORK / "safe_04" / PART, WORK / "private_04"
for _p in (SAFE, PRIVATE):
    _p.mkdir(parents=True, exist_ok=True)
try:
    import openpyxl
except ImportError:   # recorded in the manifest; the pinned image normally ships openpyxl
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "openpyxl==3.1.5"], check=True)
    import openpyxl
ENV["pkg_openpyxl"] = openpyxl.__version__"""),
    selftest_cell(),
]

if PART == "kit":
    cells += [
        md("## 1. Load the parents (01) and the generated records of the test generators (03), and check the 03 manifests"),
        code("""
root = Path(INPUT_ROOT)
src01 = manifest.find_artifact(root, "records")
parents = {r["sample_id"]: r for r in manifest.read_jsonl(src01)}
INPUT_HASHES = {"records_01": manifest.content_sha256(src01)}
generated, GEN_MANIFESTS = [], {}
for g in TEST_GENERATORS:
    gp = manifest.find_artifact(root, f"generated_{g}")
    mp = [p for p in root.rglob("run_manifest.json") if json.loads(p.read_text(encoding="utf-8")).get("generator") == g]
    assert mp, f"03 run manifest for {g} missing"
    m = json.loads(mp[0].read_text(encoding="utf-8"))
    GEN_MANIFESTS[g] = {"status": m["status"], "model_revision": m.get("model_revision"), "phishbench_commit": m.get("phishbench_commit")}
    INPUT_HASHES[f"generated_{g}"] = manifest.content_sha256(gp)
    committed = json.loads((REPO / "results" / "03_generation" / g / "private_files_sha256.json").read_text(encoding="utf-8"))
    GEN_MANIFESTS[g]["matches_committed_sha256"] = committed["content_sha256"].get(f"generated_{g}") == INPUT_HASHES[f"generated_{g}"]
    generated += manifest.read_jsonl(gp)
log("parents", len(parents), "| generated", Counter(r["generator"] for r in generated), "| 03 manifests", GEN_MANIFESTS)
"""),
        md("## 2. Draw the stratified sample, blind it, and write one workbook per rater"),
        code("""
rw, dn, report = hv.draw_sample(generated, TEST_GENERATORS, SOURCES, RW_PER_STRATUM, DN_PER_STRATUM, SEED)
items, key = hv.make_items(rw, dn, parents, SEED)
log("items", Counter(x["task"] for x in items))
with (PRIVATE / "key.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(key[0]), lineterminator="\\n"); w.writeheader(); w.writerows(key)
WORKBOOKS = {}
for rater in RATERS:
    p = PRIVATE / f"rater_{rater}.xlsx"
    hv.write_workbook(p, hv.rater_order(items, rater, SEED), rater)
    WORKBOOKS[p.name] = manifest.sha256_file(p)
    assert sorted(hv.workbook_item_ids(p)) == sorted(x["item_id"] for x in items), f"workbook {p.name} is incomplete"

# practice round (docs/RATING_GUIDE.md section 6): items outside the real sample, same file for both raters
practice, practice_key, practice_report = hv.draw_practice(list(parents.values()), rw, dn, PRACTICE_RW_PER_LABEL,
                                                           PRACTICE_DN_PER_CELL, SEED)
with (PRIVATE / "practice_key.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(practice_key[0]), lineterminator="\\n"); w.writeheader(); w.writerows(practice_key)
for rater in RATERS:
    p = PRIVATE / f"practice_{rater}.xlsx"
    hv.write_workbook(p, practice, f"{rater} (PRACTICE)")
    WORKBOOKS[p.name] = manifest.sha256_file(p)
with (SAFE / "practice_summary.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(practice_report[0]), lineterminator="\\n"); w.writeheader(); w.writerows(practice_report)
RATING_GUIDE_SHA256 = manifest.sha256_file(REPO / "docs" / "RATING_GUIDE.md")
log("practice items", Counter(x["task"] for x in practice), "| rating guide", RATING_GUIDE_SHA256[:12])

with (SAFE / "sample_summary.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(report[0]), lineterminator="\\n"); w.writeheader(); w.writerows(report)
(SAFE / "rater_instructions.txt").write_bytes(("\\n".join(hv.INSTRUCTIONS) + "\\n").encode("utf-8"))
for row in report:
    print(row)
"""),
        md("## 3. Gates, privacy check and run manifest"),
        code("""
safe_blob = textnorm.normalize("\\n".join(p.read_text(encoding="utf-8") for p in SAFE.glob("*") if p.is_file()))
probe = [x for x in items + practice if len(textnorm.normalize(x["body"])) >= 40]
leaks = sum(1 for x in probe if textnorm.normalize(x["body"])[:40] in safe_blob)
gates = {"03_outputs_match_committed_sha256": all(m["matches_committed_sha256"] for m in GEN_MANIFESTS.values()),
         "every_stratum_at_target": all(r["drawn"] == r["target"] for r in report),
         "practice_at_target": all(r["drawn"] == r["target"] for r in practice_report),
         "privacy_no_text_in_safe_outputs": leaks == 0}
manifest.write_json(SAFE / "run_manifest.json", {
    "notebook": "04_Human_Validation[kit]", "status": "COMPLETED" if all(gates.values()) else "COMPLETED_WITH_GATE_FAILURES",
    "gates": gates, "n_items": dict(Counter(x["task"] for x in items)),
    "key_sha256": manifest.sha256_file(PRIVATE / "key.csv"), "items_sha256": hv.items_digest(items),
    "sample_ids_sha256": {t: manifest.sha256_of_ids([k["sample_id"] for k in key if k["task"] == t]) for t in ("RW", "DN")},
    "workbooks_sha256": WORKBOOKS, "rating_guide_sha256": RATING_GUIDE_SHA256,
    "practice_key_sha256": manifest.sha256_file(PRIVATE / "practice_key.csv"), "n_practice": dict(Counter(x["task"] for x in practice)), "inputs_sha256": INPUT_HASHES, "generation_manifests": GEN_MANIFESTS,
    "parent_reuse_total": sum(r["parent_reuse"] for r in report), "phishbench_commit": CODE_COMMIT,
    "runtime_seconds": round(time.time() - T0, 1), "params": PARAMS, "environment": ENV, "selftest": SELFTEST,
    "files": manifest.file_hashes(SAFE),
})
log("gates", gates)
assert all(gates.values()), "Gate failure: do not hand out the workbooks"
"""),
    ]
else:
    cells += [
        md("## 1. Verify the key against the committed kit hash, then load both raters' answers and the adjudication"),
        code("""
root = Path(INPUT_ROOT)
kp = sorted(root.rglob("key.csv")); assert kp, "Attach the 04-human-validation-kit kernel output"
kit_manifest = json.loads((REPO / KIT_RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
KEY_SHA = manifest.sha256_file(kp[0])
with kp[0].open(encoding="utf-8") as f:
    key = [{**r, "label": int(r["label"])} for r in csv.DictReader(f)]
def read_csv(name):
    with (REPO / RATINGS_DIR / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))
ra, rb, adj = read_csv("rater_A.csv"), read_csv("rater_B.csv"), read_csv("adjudication.csv")
INPUT_HASHES = {n: manifest.sha256_file(REPO / RATINGS_DIR / n) for n in ("rater_A.csv", "rater_B.csv", "adjudication.csv")}
COMPLETE = {}
for name, rows in (("A", ra), ("B", rb)):
    bad = [r["item_id"] for r in rows if any(r.get(q, "") not in allowed for q, allowed in hv.QUESTIONS[r["task"]].items())]
    COMPLETE[name] = not bad and {r["item_id"] for r in rows} == {k["item_id"] for k in key}
log("key", KEY_SHA[:12], "| committed", kit_manifest["key_sha256"][:12], "| complete", COMPLETE, "| adjudication rows", len(adj))
"""),
        md("## 2. Agreement, preservation and the §3.5 rule"),
        code("""
S = hv.summarize(key, ra, rb, adj, PRESERVATION_MIN, KAPPA_TARGET, KAPPA_BOOTSTRAP_B, SEED)
def write_rows(name, rows):
    with (SAFE / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\\n"); w.writeheader(); w.writerows(rows)
write_rows("agreement.csv", S["agreement"])
write_rows("rates.csv", S["rates"])
write_rows("items.csv", [{k: x.get(k, "") for k in sorted({c for y in S["items"] for c in y}, key=lambda c: (c.startswith(("A_", "B_", "final_")), c))}
                         for x in S["items"]])
manifest.write_json(SAFE / "decisions.json", {k: S[k] for k in ("decisions", "kappa_rewrite_label", "kappa_target", "kappa_target_met",
                                                                "n_disagreements", "preservation_min")})
for r in S["agreement"]:
    print(r)
print(json.dumps(S["decisions"], indent=1))
"""),
        md("## 3. Gates and run manifest"),
        code("""
gates = {"key_hash_matches_kit": KEY_SHA == kit_manifest["key_sha256"],
         "rater_A_complete": COMPLETE["A"], "rater_B_complete": COMPLETE["B"],
         "every_disagreement_resolved": True,   # summarize() raises otherwise
         "privacy_no_text_columns": not any(c in ("subject", "body", "original_subject", "original_body", "comment")
                                            for p in SAFE.glob("*.csv") for c in next(csv.reader(p.open(encoding="utf-8"))))}
manifest.write_json(SAFE / "run_manifest.json", {
    "notebook": "04_Human_Validation[score]", "status": "COMPLETED" if all(gates.values()) else "COMPLETED_WITH_GATE_FAILURES",
    "gates": gates, "key_sha256": KEY_SHA, "ratings_sha256": INPUT_HASHES, "kappa_rewrite_label": S["kappa_rewrite_label"],
    "kappa_target_met": S["kappa_target_met"], "decisions": S["decisions"], "phishbench_commit": CODE_COMMIT,
    "runtime_seconds": round(time.time() - T0, 1), "params": PARAMS, "environment": ENV, "selftest": SELFTEST,
    "files": manifest.file_hashes(SAFE),
})
log("gates", gates)
assert all(gates.values()), "Gate failure"
"""),
    ]

write_notebook(OUT, cells, gpu=False)
print("wrote", OUT)
