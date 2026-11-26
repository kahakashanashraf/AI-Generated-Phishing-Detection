"""Builds notebooks/01_Data_Sources_Audit_and_Locked_Cells.ipynb (replaces the old N01–N04 and N15)."""
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
    "MINHASH": {"num_perm": 128, "bands": 16, "threshold": 0.80, "shingle_words": 5},
    "HUMAN_FILTERS": {"min_words": 20, "max_words": 1500, "require_english": True},
    "OFFSHELF_FILTERS": {"require_english": True},
    "R2_HAM_CAP": 6000, "R2_VAL_FRACTION": 0.10,
    "EXT_LEGIT_N": 1000, "EXT2_LEGIT_N": 500, "MODERN_CAP": 2000,
    "NAZARIO_TRAIN_YEARS": [2015, 2016, 2017, 2018, 2019, 2020, 2021],
    "NAZARIO_EXT_YEAR": 2022, "NAZARIO_MODERN_YEARS": [2023, 2024, 2025],
    "KAGGLE_INPUTS": {"clinton": "kaggle/hillary-clinton-emails", "greco24": "francescogreco97/human-llm-generated-phishing-legitimate-emails"},
}

cells = [
    header("01", "Data sources: audit, decontamination and locked cells",
           "Acquire and verify every source. Audit the label taxonomy and lineage (D1 label semantics, the D2 taxonomy, D2→D3 reuse). "
           "Reproduce the frozen N05 D2 split. Build the R2 pooled training pool. Decontaminate with exact keys plus "
           "MinHash/LSH. Sample every locked test cell with a fixed seed. Write the locked-ID manifest. "
           "No detector is trained or scored. This notebook replaces the earlier N01–N04 and N15.",
           "§2–§3, deviations 4–5",
           ["Pinned public sources downloaded inside the kernel: Zenodo D1, monkey.org Nazario, HarmJ0y D2, DataPhish D3, HF LLMGen, E-PhishLLM",
            "Kaggle datasets attached to the kernel: Hillary Clinton emails, Greco et al. 2024"],
           ["`safe_01/` (committed to `results/01_data/`): receipts, audit tables, cell counts, exclusions, locked manifest, run manifest",
            "`private_01/` (private kernel output only): records with text, used as input to 03"],
           ["all source pins verified", "N05 split reproduced (1418/304/304)", "train/val and test IDs disjoint",
            "no test record linked to train/val", "EXT = 1000 and EXT2 = 500", "no email text in safe outputs"],
           "Kaggle CPU, internet ON, about 10 minutes"),
    params_cell(PARAMS),
    env_cell("from phishbench import d2split, loaders, sources, freeze\nfrom phishbench.dedup import MinHasher, LSHIndex"),
    selftest_cell(),
    md("## 1. Acquire and verify every source"),
    code("""
SAFE, PRIVATE, CACHE = WORK / "safe_01", WORK / "private_01", TEMP / "cache"
for _p in (SAFE, PRIVATE, CACHE):
    _p.mkdir(parents=True, exist_ok=True)
tofu = json.loads((REPO / "phishbench" / "tofu_sha256.json").read_text())
receipts, paths = {}, {}
for name, src in sources.registry().items():
    receipts[name] = sources.download(src, CACHE, tofu=tofu)
    paths[name] = CACHE / name.replace("/", "__")
for key, (rel, size, blob) in d2split.D2_FILES.items():
    src = sources.Source(f"d2/{key}", d2split.d2_url(rel), "no licence declared (cited; not redistributed)", "R1 / IN", size=size, git_blob=blob)
    receipts[src.name] = sources.download(src, CACHE)
    paths[src.name] = CACHE / src.name.replace("/", "__")

def find_input(pattern):
    hits = sorted(Path("/kaggle/input").rglob(pattern)) if Path("/kaggle/input").exists() else []
    if not hits:
        raise FileNotFoundError(f"Kaggle input not attached: {pattern}")
    return hits[0]
clinton_csv = find_input("Emails.csv")
greco_root = find_input("llm-generated").parent
for name, p, lic, role in ([("kaggle/hillary-clinton-emails/Emails.csv", clinton_csv, "US Government public record (FOIA)", "EXT2 legitimate")] +
                           [(f"kaggle/greco24/{q.relative_to(greco_root).as_posix()}", q, "CC-BY-NC-SA-4.0", "LOCKED AI-authored")
                            for q in sorted(greco_root.rglob("llm-generated/*.csv"))]):
    receipts[name] = {"name": name, "bytes": p.stat().st_size, "sha256": manifest.sha256_file(p), "licence": lic, "role": role,
                      "origin": "kaggle_input", "pin": "sha256-recorded (Kaggle dataset version)", "kaggle_dataset": KAGGLE_INPUTS["clinton" if "clinton" in name else "greco24"]}
first_use = {k: v["sha256"] for k, v in receipts.items() if v.get("pin") == "tofu-first-use"}
log(len(receipts), "sources verified;", len(first_use), "first-use hashes;", Counter(v["pin"] for v in receipts.values()))
"""),
    md("## 2. Label-taxonomy and lineage audit (dataset section of the paper)"),
    code("""
raw = {k: d2split.load_json_list(paths[f"d2/{k}"]) for k in d2split.D2_FILES}
d2_types = Counter(str(d2split.get(r, "Type")) for r in raw["original"])
d3 = d2split.load_json_list(paths["d3/PhishFuzzer_emails_original_seed_v1.json"])
d2_by = d2split.index_by_no(raw["original"])
d3_by = {}
for r in d3:
    k = d2split.ident(d2split.get(r, "No."))
    if k is not None:
        d3_by.setdefault(k, r)
common = sorted(set(d2_by) & set(d3_by))
same_text = sum(textnorm.normalize(d2split.n05_text(d2_by[k])) == textnorm.normalize(d2split.n05_text(d3_by[k])) for k in common)
transitions = Counter(f"{d2split.get(d2_by[k], 'Type')} -> {d2split.get(d3_by[k], 'Type')}" for k in common)
d1_label_counts = {}
for f in ("Enron.csv", "SpamAssasin.csv", "CEAS_08.csv", "Nigerian_Fraud.csv"):
    with open(paths[f"d1/{f}"], encoding="utf-8", errors="replace", newline="") as fh:
        d1_label_counts[f] = dict(Counter(row.get("label") for row in csv.DictReader(fh)))
audit = {
    "d2_type_counts": dict(d2_types),
    "d3_seed_rows": len(d3), "d2_ids_reused_in_d3": len(common), "d2_ids_total": len(d2_by),
    "reused_ids_with_identical_normalised_text": same_text, "d2_to_d3_type_transitions": dict(transitions),
    "d1_label_counts (1 = spam in spam/ham corpora; spam never mapped to phishing, D001)": d1_label_counts,
    "decisions": {"D3": "excluded: derived from D2 (every D2 ID reappears)", "D5": "excluded: phishing-only authorship data (no legitimate class)",
                  "LLMGen": "English (OpenAI) file only; the Chinese/DeepSeek file is not used (language and generator are confounded)"},
}
log("audit", {k: v for k, v in audit.items() if not isinstance(v, dict)})
"""),
    md("## 3. Load sources into one record schema and reproduce the frozen N05 split"),
    code("""
split = d2split.n05_split(raw["original"])          # asserts 1418 / 304 / 304 (142 legit, 162 phish)
valid = split["valid"]
def d2_rec(no, row, provider=None):
    s, b = d2split.subject_body(row)
    lab = d2split.label(valid[no])
    if provider is None:
        return loaders.record(f"d2:{no}", "d2", no, s, b, lab, "human")
    return loaders.record(f"d2_{provider}:{no}", f"d2_{provider}", no, s, b, lab, "ai", parent_id=f"d2:{no}", generator=provider, level="L3")
all_d2 = split["train"] + split["val"] + split["test"]
d2_parents = {no: d2_rec(no, valid[no]) for no in all_d2}
d2_rw, rw_excluded = defaultdict(list), Counter()
for provider in ("gpt4o", "deepseek", "randomapi"):
    idx = d2split.index_by_no(raw[provider])
    for no in all_d2:
        r = idx.get(no)
        if r is None or not d2split.n05_text(r).strip():
            rw_excluded[f"{provider}:missing_or_empty"] += 1; continue
        t = d2split.get(r, "Type")
        if t is not None and t != d2split.get(split["orig"][no], "Type"):
            rw_excluded[f"{provider}:type_conflict"] += 1; continue
        d2_rw[no].append(d2_rec(no, r, provider))
enron_ham = loaders.load_d1_csv(paths["d1/Enron.csv"], "enron", 0)
sa_ham = loaders.load_d1_csv(paths["d1/SpamAssasin.csv"], "spamassassin", 0)
ceas_ham = loaders.load_d1_csv(paths["d1/CEAS_08.csv"], "ceas08", 0)
nigerian = loaders.load_d1_csv(paths["d1/Nigerian_Fraud.csv"], "nigerian", 1)
nazario, notices = {}, {}
for y in NAZARIO_TRAIN_YEARS + [NAZARIO_EXT_YEAR] + NAZARIO_MODERN_YEARS:
    nazario[y], notices[y] = loaders.load_nazario_mbox(paths[f"nazario/{y}"], y)
llmgen = loaders.load_llmgen(paths["llmgen/GPT_Phishing_Email_dataset.csv"])
greco = loaders.load_greco_llm(greco_root)
clinton = loaders.load_clinton(clinton_csv)
ephish = loaders.load_ephish(paths["ephish/ephishLLM.json"])
loaded = {"enron_ham": len(enron_ham), "spamassassin_ham": len(sa_ham), "ceas08_ham": len(ceas_ham), "nigerian": len(nigerian),
          "llmgen": len(llmgen), "greco24_llm": len(greco), "clinton": len(clinton), "ephish_en": len(ephish),
          **{f"nazario{y}": len(v) for y, v in nazario.items()}}
log("loaded", loaded)
"""),
    md("## 4. Decontamination and seeded selection (§3.1, §3.3)"),
    code("""
hasher = MinHasher(MINHASH["num_perm"], SEED)
SIG, exclusions = {}, {}
H, O = HUMAN_FILTERS, OFFSHELF_FILTERS
P_IN = freeze.Decontaminator(hasher, threshold=MINHASH["threshold"], cache=SIG)
for no in split["val"] + split["test"]:
    for r in [d2_parents[no]] + d2_rw[no]:
        P_IN.add(r)
ham_pool, exclusions["R2-ham-pool"] = freeze.select_cell(sa_ham + ceas_ham, None, SEED, P_IN, hasher, **H)
alloc = freeze.proportional_allocation(Counter(r["source"] for r in ham_pool), R2_HAM_CAP)
taken, r2_ham = Counter(), []
for r in ham_pool:
    if taken[r["source"]] < alloc[r["source"]]:
        r2_ham.append(r); taken[r["source"]] += 1
naz_train, exclusions["R2-nazario-train-years"] = freeze.select_cell([r for y in NAZARIO_TRAIN_YEARS for r in nazario[y]], None, SEED, P_IN, hasher, **H)
nig_pool, exclusions["R2-sens-nigerian"] = freeze.select_cell(nigerian, None, SEED, P_IN, hasher, **H)
by_src = defaultdict(list)
for r in freeze.seeded_order(r2_ham + naz_train, SEED + 1):
    by_src[r["source"]].append(r)
r2_val = [r for s in sorted(by_src) for r in by_src[s][: round(R2_VAL_FRACTION * len(by_src[s]))]]
val_ids = {r["sample_id"] for r in r2_val}
r2_train = [r for r in r2_ham + naz_train if r["sample_id"] not in val_ids]
P_TV = freeze.Decontaminator(hasher, threshold=MINHASH["threshold"], cache=SIG)
for no in split["train"] + split["val"]:
    for r in [d2_parents[no]] + d2_rw[no]:
        P_TV.add(r)
for r in r2_train + r2_val + nig_pool:
    P_TV.add(r)
in_kept, in_removed = [], []
for no in split["test"]:
    (in_removed if any(P_TV.linked(r) for r in [d2_parents[no]] + d2_rw[no]) else in_kept).append(no)
cells = {}
def by_label(recs, lab): return [r for r in recs if r["label"] == lab]
for tag, nos in (("IN", in_kept), ("INFULL", split["test"])):
    parents = [d2_parents[no] for no in nos]
    cells[f"{tag}-legit-L0"], cells[f"{tag}-phish-H"] = by_label(parents, 0), by_label(parents, 1)
    for provider in ("gpt4o", "deepseek", "randomapi"):
        rws = [r for no in nos for r in d2_rw[no] if r["generator"] == provider]
        cells[f"{tag}-legit-L3-{provider}"], cells[f"{tag}-phish-L3-{provider}"] = by_label(rws, 0), by_label(rws, 1)
cells["EXT-legit-L0"], exclusions["EXT-legit-L0"] = freeze.select_cell(enron_ham, EXT_LEGIT_N, SEED, P_TV, hasher, **H)
cells["EXT2-legit-L0"], exclusions["EXT2-legit-L0"] = freeze.select_cell(clinton, EXT2_LEGIT_N, SEED, P_TV, hasher, **H)
cells["EXT-phish-H"], exclusions["EXT-phish-H"] = freeze.select_cell(nazario[NAZARIO_EXT_YEAR], None, SEED, P_TV, hasher, **H)
modern_pool, exclusions["MODERN-phish"] = freeze.select_cell([r for y in NAZARIO_MODERN_YEARS for r in nazario[y]], None, SEED, P_TV, hasher, **H)
alloc_m = freeze.proportional_allocation(Counter(r["year"] for r in modern_pool), MODERN_CAP)
taken, cells["MODERN-phish"] = Counter(), []
for r in modern_pool:
    if taken[r["year"]] < alloc_m[r["year"]]:
        cells["MODERN-phish"].append(r); taken[r["year"]] += 1
for name, pool in (("LLMGen", llmgen), ("Greco24", greco), ("DEV-ephish", ephish)):
    kept, exclusions[name] = freeze.select_cell(pool, None, SEED, P_TV, hasher, **O)
    cells[f"{name}-legit"], cells[f"{name}-phish"] = by_label(kept, 0), by_label(kept, 1)
log("cells", {k: len(v) for k, v in cells.items() if not k.startswith("INFULL")})
"""),
    md("## 5. Integrity gates"),
    code("""
roles = {"train_r1": [d2_parents[no] for no in split["train"]], "val_r1": [d2_parents[no] for no in split["val"]],
         "train_r1_rw": [r for no in split["train"] for r in d2_rw[no]], "val_r1_rw": [r for no in split["val"] for r in d2_rw[no]],
         "train_r2_extra": r2_train, "val_r2_extra": r2_val, "train_r2_sens_nigerian": nig_pool}
test_cells = {k: v for k, v in cells.items() if not k.startswith("INFULL")}
relinked = {k: sum(P_TV.linked(r) for r in v) for k, v in test_cells.items()}
train_ids = {r["sample_id"] for v in roles.values() for r in v}
test_ids = {r["sample_id"] for v in test_cells.values() for r in v}
cross, owner, cross_pairs = LSHIndex(MINHASH["num_perm"], MINHASH["bands"], MINHASH["threshold"]), {}, Counter()
for k, v in test_cells.items():
    for r in v:
        cross.add(r["sample_id"], P_TV.signature(r)); owner[r["sample_id"]] = k
for k, v in test_cells.items():
    for r in v:
        for other in cross.query(SIG[r["sample_id"]]):
            if owner[other] != k:
                cross_pairs[tuple(sorted((k, owner[other])))] += 1
GATES = {"all_source_pins_verified": True,   # sources.download raises on any mismatch
         "n05_split_reproduced": True,       # d2split.n05_split raises if not reproduced
         "train_test_ids_disjoint": not (train_ids & test_ids),
         "no_test_record_linked_to_train_or_val": all(v == 0 for v in relinked.values()),
         "EXT-legit-L0_is_1000": len(cells["EXT-legit-L0"]) == EXT_LEGIT_N,
         "EXT2-legit-L0_is_500": len(cells["EXT2-legit-L0"]) == EXT2_LEGIT_N,
         "both_classes_in_LLMGen_Greco24_DEV": all(len(cells[f"{n}-{c}"]) > 0 for n in ("LLMGen", "Greco24", "DEV-ephish") for c in ("legit", "phish"))}
log("gates", GATES)
"""),
    md("## 6. Outputs: private records for 03, and safe aggregates for the paper"),
    code("""
with gzip.open(PRIVATE / "records.jsonl.gz", "wt", encoding="utf-8") as f:
    for role, recs in list(roles.items()) + list(cells.items()):
        for r in recs:
            f.write(json.dumps({**r, "cell": role}, ensure_ascii=False) + "\\n")
manifest.write_json(PRIVATE / "cell_ids.json", {k: sorted(r["sample_id"] for r in v) for k, v in {**roles, **cells}.items()})
def wc(recs):
    w = np.array([textnorm.word_count(r["body"]) for r in recs]) if recs else np.array([0])
    return int(np.median(w)), int(np.percentile(w, 10)), int(np.percentile(w, 90))
with (SAFE / "cell_counts.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f, lineterminator="\\n")
    wr.writerow(["cell", "kind", "n", "n_legit", "n_phish", "sources", "authorship", "median_words", "p10_words", "p90_words"])
    for k, v in {**roles, **cells}.items():
        kind = "train/val" if k in roles else ("sensitivity" if k.startswith("INFULL") else ("DEV" if k.startswith("DEV") else "LOCKED test"))
        wr.writerow([k, kind, len(v), sum(r["label"] == 0 for r in v), sum(r["label"] == 1 for r in v),
                     ";".join(sorted({r["source"] for r in v})), ";".join(sorted({r["authorship"] for r in v})), *wc(v)])
with (SAFE / "exclusions.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f, lineterminator="\\n"); wr.writerow(["stage", "reason", "count"])
    for stage, c in exclusions.items():
        for reason, n in sorted(c.items()):
            wr.writerow([stage, reason, n])
    for reason, n in sorted(rw_excluded.items()):
        wr.writerow(["d2_rewrites", reason, n])
    wr.writerow(["IN_test_groups", "linked_to_train_or_val", len(in_removed)])
    wr.writerow(["IN_test_groups", "linked_legit", sum(d2_parents[no]["label"] == 0 for no in in_removed)])
    wr.writerow(["IN_test_groups", "linked_phish", sum(d2_parents[no]["label"] == 1 for no in in_removed)])
    for y, n in sorted(notices.items()):
        wr.writerow([f"nazario{y}", "mail_system_notice_removed", n])
with (SAFE / "cross_cell_near_duplicates.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f, lineterminator="\\n"); wr.writerow(["cell_a", "cell_b", "linked_records"])
    for (a, b), n in sorted(cross_pairs.items()):
        wr.writerow([a, b, n])
manifest.write_json(SAFE / "dataset_audit.json", audit)
manifest.write_json(SAFE / "locked_test_v2_manifest.json", {
    "preregistration": "docs/PREREGISTRATION_V2.md (frozen v2.1)", "code_commit": CODE_COMMIT,
    "rule": "sha256 over sorted, newline-joined sample_ids; IDs and text are kept private",
    "test_cells": {k: {"n": len(v), "sha256_ids": manifest.sha256_of_ids(r["sample_id"] for r in v)} for k, v in cells.items()},
    "train_val_roles": {k: {"n": len(v), "sha256_ids": manifest.sha256_of_ids(r["sample_id"] for r in v)} for k, v in roles.items()}})
manifest.write_json(SAFE / "source_receipts.json", receipts)
manifest.write_json(SAFE / "tofu_first_use_sha256.json", first_use)
manifest.write_json(SAFE / "loaded_counts.json", {**loaded, "r2_ham_allocation": alloc, "modern_year_allocation": {str(k): v for k, v in alloc_m.items()}})
safe_blob = textnorm.normalize("\\n".join(p.read_text(encoding="utf-8") for p in SAFE.glob("*") if p.is_file()))
probe = random.Random(SEED).sample([r for v in cells.values() for r in v], 500)
GATES["no_email_text_in_safe_outputs"] = not any(len(textnorm.normalize(r["body"])) >= 40 and textnorm.normalize(r["body"])[:40] in safe_blob for r in probe)
STATUS = "COMPLETED" if all(GATES.values()) else "COMPLETED_WITH_GATE_FAILURES"
manifest.write_json(SAFE / "run_manifest.json", {"notebook": "01_Data_Sources_Audit_and_Locked_Cells", "status": STATUS, "gates": GATES,
                    "params": PARAMS, "environment": ENV, "selftest": SELFTEST, "runtime_seconds": round(time.time() - T0, 1),
                    "files": manifest.file_hashes(SAFE)})
log("STATUS", STATUS)
for k, v in GATES.items():
    print(f"  {'PASS' if v else 'FAIL'}  {k}")
assert all(GATES.values()), "Gate failure: outputs must not be used downstream"
"""),
]
write_notebook(OUT, cells)
print("wrote", OUT)
