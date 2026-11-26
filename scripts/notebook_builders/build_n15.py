"""Builds notebooks/15_Data_Freeze_v2_Sources_Decontamination_Locked_Cells.ipynb from cell sources."""
import json
import sys
from pathlib import Path

COMMIT = sys.argv[2]
OUT = Path(sys.argv[1])

md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}
code = lambda s: {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                  "source": s.strip("\n").splitlines(keepends=True)}

cells = [
md("""
# N15 — Data freeze v2: sources, decontamination and locked cells (Study 2, confirmatory)

Implements `docs/PREREGISTRATION_V2.md` (frozen v2.1) §2–§3:

- pinned downloads with MD5, Git-blob, SHA-256 or trust-on-first-use (TOFU) verification;
- exact reproduction of the frozen N05 D2 split;
- R2 pooled training pool;
- MinHash/LSH plus exact-key decontamination;
- seeded sampling of every locked test cell;
- a locked-ID manifest.

**No detector is trained or scored in this notebook.**

Outputs:
- `phishing_n15_safe/`: aggregates and hashes only, with no email text. These are committed to GitHub.
- `private_n15/`: records with text, used as the input to N16. This folder stays in this private kernel and is never committed.
"""),
code(f"""
import os, sys, subprocess, json, gzip, time, csv, random
from pathlib import Path
from collections import Counter, defaultdict

PHISHBENCH_COMMIT = "{COMMIT}"
ON_KAGGLE = Path("/kaggle/working").exists()
WORK = Path("/kaggle/working") if ON_KAGGLE else Path.cwd() / "n15_local"
TEMP = Path("/kaggle/temp") if ON_KAGGLE else WORK / "_temp"
REPO, CACHE = TEMP / "repo", TEMP / "cache"
SAFE, PRIVATE = WORK / "phishing_n15_safe", WORK / "private_n15"
for p in (WORK, TEMP, CACHE, SAFE, PRIVATE):
    p.mkdir(parents=True, exist_ok=True)
if not (REPO / ".git").exists():
    subprocess.run(["git", "clone", "--quiet", "https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git", str(REPO)], check=True)
subprocess.run(["git", "-C", str(REPO), "checkout", "--quiet", PHISHBENCH_COMMIT], check=True)
sys.path.insert(0, str(REPO))
subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "langdetect==1.0.9"], check=True)

import numpy as np
from phishbench import __version__ as PB_VERSION, d2split, loaders, sources, freeze, manifest, textnorm
from phishbench.dedup import MinHasher, LSHIndex

SEED = 2026
T0 = time.time()
def log(*a): print(f"[{{time.time()-T0:7.1f}}s]", *a, flush=True)
log("phishbench", PB_VERSION, "at commit", PHISHBENCH_COMMIT)
"""),
md("## 1. Acquire and verify every source"),
code("""
tofu = json.loads((REPO / "phishbench" / "tofu_sha256.json").read_text())
receipts, paths = {}, {}
for name, src in sources.registry().items():
    receipts[name] = sources.download(src, CACHE, tofu=tofu)
    paths[name] = CACHE / name.replace("/", "__")
    log("verified", name, receipts[name]["pin"], receipts[name]["bytes"])
for key, (rel, size, blob) in d2split.D2_FILES.items():
    src = sources.Source(f"d2/{key}", d2split.d2_url(rel), "no licence declared (cited; not redistributed)",
                         "R1 / IN", size=size, git_blob=blob)
    receipts[src.name] = sources.download(src, CACHE)
    paths[src.name] = CACHE / src.name.replace("/", "__")
    log("verified", src.name, "git_blob")

def find_input(pattern):
    hits = sorted(Path("/kaggle/input").rglob(pattern)) if Path("/kaggle/input").exists() else []
    if not hits:
        raise FileNotFoundError(f"Kaggle input not attached: {pattern}")
    return hits[0]

clinton_csv = find_input("Emails.csv")
greco_root = find_input("llm-generated").parent
kaggle_inputs = [("kaggle/hillary-clinton-emails/Emails.csv", clinton_csv, "US Government public record (FOIA)", "EXT2 legitimate")]
kaggle_inputs += [(f"kaggle/greco24/{q.relative_to(greco_root).as_posix()}", q, "CC-BY-NC-SA-4.0", "LOCKED AI-authored")
                  for q in sorted(greco_root.rglob("llm-generated/*.csv"))]
for name, p, lic, role in kaggle_inputs:
    receipts[name] = {"name": name, "bytes": p.stat().st_size, "sha256": manifest.sha256_file(p), "licence": lic,
                      "role": role, "origin": "kaggle_input", "pin": "sha256-recorded (Kaggle dataset version in kernel metadata)"}
first_use = {k: v["sha256"] for k, v in receipts.items() if v.get("pin") == "tofu-first-use"}
log(len(receipts), "sources verified;", len(first_use), "first-use hashes recorded")
"""),
md("## 2. Load sources into one record schema and reproduce the frozen N05 split"),
code("""
raw = {k: d2split.load_json_list(paths[f"d2/{k}"]) for k in d2split.D2_FILES}
split = d2split.n05_split(raw["original"])          # asserts 1418 / 304 / 304 (142 legit, 162 phish)
valid = split["valid"]

def d2_rec(no, row, provider=None):
    s, b = d2split.subject_body(row)
    lab = d2split.label(valid[no])
    if provider is None:
        return loaders.record(f"d2:{no}", "d2", no, s, b, lab, "human")
    return loaders.record(f"d2_{provider}:{no}", f"d2_{provider}", no, s, b, lab, "ai",
                          parent_id=f"d2:{no}", generator=provider, level="L3")

all_d2 = split["train"] + split["val"] + split["test"]
d2_parents = {no: d2_rec(no, valid[no]) for no in all_d2}
d2_rw, rw_excluded = defaultdict(list), Counter()
for provider in ("gpt4o", "deepseek", "randomapi"):
    idx = d2split.index_by_no(raw[provider])
    for no in all_d2:
        r = idx.get(no)
        if r is None or not d2split.n05_text(r).strip():
            rw_excluded[f"{provider}:missing_or_empty"] += 1
            continue
        t = d2split.get(r, "Type")
        if t is not None and t != d2split.get(split["orig"][no], "Type"):
            rw_excluded[f"{provider}:type_conflict"] += 1
            continue
        d2_rw[no].append(d2_rec(no, r, provider))

enron_ham = loaders.load_d1_csv(paths["d1/Enron.csv"], "enron", 0)
sa_ham = loaders.load_d1_csv(paths["d1/SpamAssasin.csv"], "spamassassin", 0)
ceas_ham = loaders.load_d1_csv(paths["d1/CEAS_08.csv"], "ceas08", 0)
nigerian = loaders.load_d1_csv(paths["d1/Nigerian_Fraud.csv"], "nigerian", 1)
nazario, notices = {}, {}
for y in range(2015, 2026):
    nazario[y], notices[y] = loaders.load_nazario_mbox(paths[f"nazario/{y}"], y)
llmgen = loaders.load_llmgen(paths["llmgen/GPT_Phishing_Email_dataset.csv"])
greco = loaders.load_greco_llm(greco_root)
clinton = loaders.load_clinton(clinton_csv)
ephish = loaders.load_ephish(paths["ephish/ephishLLM.json"])
loaded = {"enron_ham": len(enron_ham), "spamassassin_ham": len(sa_ham), "ceas08_ham": len(ceas_ham),
          "nigerian": len(nigerian), "llmgen": len(llmgen), "greco24_llm": len(greco), "clinton": len(clinton),
          "ephish_en": len(ephish), **{f"nazario{y}": len(v) for y, v in nazario.items()}}
log("loaded", loaded)
"""),
md("## 3. Decontamination and seeded selection (§3.1, §3.3)"),
code("""
hasher = MinHasher(128, SEED)
SIG = {}
H = dict(min_words=20, max_words=1500, require_english=True)   # human / external filters (§3.1)
O = dict(require_english=True)                                  # off-the-shelf locked / DEV cells
exclusions = {}

# (a) Protect the frozen IN validation and test parents and their rewrites before building the R2 pool.
P_IN = freeze.Decontaminator(hasher, cache=SIG)
for no in split["val"] + split["test"]:
    for r in [d2_parents[no]] + d2_rw[no]:
        P_IN.add(r)

ham_pool, exclusions["R2-ham-pool"] = freeze.select_cell(sa_ham + ceas_ham, None, SEED, P_IN, hasher, **H)
alloc = freeze.proportional_allocation(Counter(r["source"] for r in ham_pool), 6000)
taken, r2_ham = Counter(), []
for r in ham_pool:                       # ham_pool is already in seeded random order
    if taken[r["source"]] < alloc[r["source"]]:
        r2_ham.append(r); taken[r["source"]] += 1
naz_train, exclusions["R2-nazario-2015-2021"] = freeze.select_cell(
    [r for y in range(2015, 2022) for r in nazario[y]], None, SEED, P_IN, hasher, **H)
nig_pool, exclusions["R2-sens-nigerian"] = freeze.select_cell(nigerian, None, SEED, P_IN, hasher, **H)

by_src = defaultdict(list)
for r in freeze.seeded_order(r2_ham + naz_train, SEED + 1):
    by_src[r["source"]].append(r)
r2_val = [r for s in sorted(by_src) for r in by_src[s][: round(0.10 * len(by_src[s]))]]
val_ids = {r["sample_id"] for r in r2_val}
r2_train = [r for r in r2_ham + naz_train if r["sample_id"] not in val_ids]
log("R2 extra train", len(r2_train), "val", len(r2_val), "nigerian sensitivity", len(nig_pool))

# (b) Everything that any regime trains or validates on.
P_TV = freeze.Decontaminator(hasher, cache=SIG)
for no in split["train"] + split["val"]:
    for r in [d2_parents[no]] + d2_rw[no]:
        P_TV.add(r)
for r in r2_train + r2_val + nig_pool:
    P_TV.add(r)

# (c) IN cells: drop whole test groups (parent plus rewrites) linked to any training or validation data.
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

# (d) External human cells.
cells["EXT-legit-L0"], exclusions["EXT-legit-L0"] = freeze.select_cell(enron_ham, 1000, SEED, P_TV, hasher, **H)
cells["EXT2-legit-L0"], exclusions["EXT2-legit-L0"] = freeze.select_cell(clinton, 500, SEED, P_TV, hasher, **H)
cells["EXT-phish-H"], exclusions["EXT-phish-H"] = freeze.select_cell(nazario[2022], None, SEED, P_TV, hasher, **H)
modern_pool, exclusions["MODERN-phish"] = freeze.select_cell(
    [r for y in (2023, 2024, 2025) for r in nazario[y]], None, SEED, P_TV, hasher, **H)
alloc_m = freeze.proportional_allocation(Counter(r["year"] for r in modern_pool), 2000)
taken, cells["MODERN-phish"] = Counter(), []
for r in modern_pool:
    if taken[r["year"]] < alloc_m[r["year"]]:
        cells["MODERN-phish"].append(r); taken[r["year"]] += 1

# (e) Off-the-shelf AI-authored cells (LOCKED and DEV).
for name, pool in (("LLMGen", llmgen), ("Greco24", greco), ("DEV-ephish", ephish)):
    kept, exclusions[name] = freeze.select_cell(pool, None, SEED, P_TV, hasher, **O)
    cells[f"{name}-legit"], cells[f"{name}-phish"] = by_label(kept, 0), by_label(kept, 1)
log("cells", {k: len(v) for k, v in cells.items()})
"""),
md("## 4. Integrity checks and gates"),
code("""
roles = {
    "train_r1": [d2_parents[no] for no in split["train"]],
    "val_r1": [d2_parents[no] for no in split["val"]],
    "train_r1_rw": [r for no in split["train"] for r in d2_rw[no]],
    "val_r1_rw": [r for no in split["val"] for r in d2_rw[no]],
    "train_r2_extra": r2_train, "val_r2_extra": r2_val, "train_r2_sens_nigerian": nig_pool,
}
test_cells = {k: v for k, v in cells.items() if not k.startswith("INFULL")}

# Re-check: no confirmatory test record may be linked to training or validation data.
relinked = {k: sum(P_TV.linked(r) for r in v) for k, v in test_cells.items()}
train_ids = {r["sample_id"] for v in roles.values() for r in v}
test_ids = {r["sample_id"] for v in test_cells.values() for r in v}

# Cross-cell near-duplicates between different test cells (reported, not removed).
cross = LSHIndex(128, 16, 0.80)
owner = {}
for k, v in test_cells.items():
    for r in v:
        cross.add(r["sample_id"], SIG.get(r["sample_id"], P_TV.signature(r))); owner[r["sample_id"]] = k
cross_pairs = Counter()
for k, v in test_cells.items():
    for r in v:
        for other in cross.query(SIG[r["sample_id"]]):
            if owner[other] != k:
                cross_pairs[tuple(sorted((k, owner[other])))] += 1

gates = {
    "n05_split_reproduced": True,
    "train_test_ids_disjoint": not (train_ids & test_ids),
    "no_test_record_linked_to_train_or_val": all(v == 0 for v in relinked.values()),
    "EXT-legit-L0_target_1000": len(cells["EXT-legit-L0"]) == 1000,
    "EXT2-legit-L0_target_500": len(cells["EXT2-legit-L0"]) == 500,
    "both_classes_present_in_LLMGen_Greco24_DEV": all(len(cells[f"{n}-{c}"]) > 0 for n in ("LLMGen", "Greco24", "DEV-ephish") for c in ("legit", "phish")),
}
log("gates", gates)
"""),
md("## 5. Write private records (N16 input) and safe aggregate outputs"),
code("""
with gzip.open(PRIVATE / "records.jsonl.gz", "wt", encoding="utf-8") as f:
    for role, recs in list(roles.items()) + list(cells.items()):
        for r in recs:
            f.write(json.dumps({**r, "cell": role}, ensure_ascii=False) + "\\n")
manifest.write_json(PRIVATE / "cell_ids.json", {k: sorted(r["sample_id"] for r in v) for k, v in {**roles, **cells}.items()})

def wc_stats(recs):
    w = np.array([textnorm.word_count(r["body"]) for r in recs]) if recs else np.array([0])
    return int(np.median(w)), int(np.percentile(w, 10)), int(np.percentile(w, 90))

with (SAFE / "cell_counts.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f, lineterminator="\\n")
    wr.writerow(["cell", "kind", "n", "n_legit", "n_phish", "sources", "authorship", "median_words", "p10_words", "p90_words"])
    for k, v in {**roles, **cells}.items():
        kind = "train/val" if k in roles else ("sensitivity" if k.startswith("INFULL") else ("DEV" if k.startswith("DEV") else "LOCKED test"))
        wr.writerow([k, kind, len(v), sum(r["label"] == 0 for r in v), sum(r["label"] == 1 for r in v),
                     ";".join(sorted({r["source"] for r in v})), ";".join(sorted({r["authorship"] for r in v})), *wc_stats(v)])
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

manifest.write_json(SAFE / "locked_test_v2_manifest.json", {
    "preregistration": "docs/PREREGISTRATION_V2.md (frozen v2.1)", "phishbench_commit": PHISHBENCH_COMMIT,
    "rule": "sha256 over sorted, newline-joined sample_ids; IDs and text are kept private",
    "test_cells": {k: {"n": len(v), "sha256_ids": manifest.sha256_of_ids(r["sample_id"] for r in v)} for k, v in cells.items()},
    "train_val_roles": {k: {"n": len(v), "sha256_ids": manifest.sha256_of_ids(r["sample_id"] for r in v)} for k, v in roles.items()},
})
manifest.write_json(SAFE / "source_receipts.json", receipts)
manifest.write_json(SAFE / "tofu_first_use_sha256.json", first_use)
manifest.write_json(SAFE / "loaded_counts.json", {**loaded, "r2_ham_allocation": alloc, "modern_year_allocation": {str(k): v for k, v in alloc_m.items()}})

# Privacy check: no email text may appear in any safe file.
safe_blob = "\\n".join(p.read_text(encoding="utf-8") for p in SAFE.glob("*") if p.is_file())
rng = random.Random(SEED)
probe = [r for v in cells.values() for r in v]
leaks = sum(1 for r in rng.sample(probe, min(500, len(probe)))
            if len(textnorm.normalize(r["body"])) >= 40 and textnorm.normalize(r["body"])[:40] in textnorm.normalize(safe_blob))
gates["privacy_no_text_in_safe_outputs"] = leaks == 0

status = "COMPLETED" if all(gates.values()) else "COMPLETED_WITH_GATE_FAILURES"
manifest.write_json(SAFE / "run_manifest.json", {
    "release": "N15-DataFreeze-v2.1", "status": status, "gates": gates,
    "preregistration": "docs/PREREGISTRATION_V2.md (frozen v2.1)", "phishbench_commit": PHISHBENCH_COMMIT,
    "seed": SEED, "minhash": {"num_perm": 128, "bands": 16, "threshold": 0.80, "shingle_words": 5},
    "runtime_seconds": round(time.time() - T0, 1), "environment": manifest.environment(REPO),
    "files": manifest.file_hashes(SAFE),
})
log("status", status)
for k, v in gates.items():
    print(f"  {'PASS' if v else 'FAIL'}  {k}")
"""),
]

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                   "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
OUT.write_bytes((json.dumps(nb, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
print("wrote", OUT)
