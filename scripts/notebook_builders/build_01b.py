"""Builds notebooks/01b_Extension_Newer_Human_Email.ipynb: the EXT3 cell of the pre-specified exploratory extension E1 (deviation 15)."""
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
    "LISTS": ["user@spark.apache.org", "users@kafka.apache.org", "user@flink.apache.org", "user@hadoop.apache.org",
              "user@cassandra.apache.org", "users@tomcat.apache.org", "users@httpd.apache.org", "dev@httpd.apache.org",
              "dev@airflow.apache.org", "general@incubator.apache.org", "dev@community.apache.org", "users@maven.apache.org"],
    "WINDOW": ["2019-01", "2022-10"],          # ends before ChatGPT's release (2022-11-30)
    "MONTHS_PER_LIST": 6,
    "N_EXT3": 500,
    "PER_LIST_CAP": 60,
    "HUMAN_FILTERS": {"min_words": 20, "max_words": 1500, "require_english": True},   # as for every human cell in 01
    "MINHASH": {"num_perm": 128, "bands": 16, "threshold": 0.80, "shingle_words": 5},
    "API": "https://lists.apache.org/api/mbox.lua?list={lst}&date={month}",
    "REQUEST_DELAY_S": 3,
    "USER_AGENT": "phishbench-research/1.0 (academic study; message text is never redistributed)",
}

cells = [
    header("01b", "Extension E1: newer human email (EXT3, Apache mailing lists 2019–2022)",
           "Build the EXT3 cell of the pre-specified exploratory extension E1. Download the seeded months of the 12 fixed public Apache "
           "lists, keep thread-starting human messages (no replies, no automated senders, no votes, no patches or code), apply the "
           "same filters as every human cell, decontaminate against all training and validation data, and draw n = 500 with at most "
           "60 per list. Text stays private; only counts, hashes and provenance are committed.",
           "deviation 15 (E1)",
           ["Kernel output of `01-data-sources-audit-and-locked-cells` (training and validation records for decontamination)",
            "lists.apache.org mbox API (public archives, ASF Public Forum Archive Policy)"],
           ["`safe_01b/` (committed to `results/01b_ext3/`): fetch provenance with SHA-256, exclusion counts, cell counts, run manifest",
            "`private_01b/records_ext3.jsonl.gz` (private): the EXT3 cell, input to 03 (extension) and 05–07"],
           ["every planned month fetched or its failure recorded", "no record linked to training or validation", "no email text in safe outputs"],
           "Kaggle CPU session, same pinned image (D018), internet ON, about 20 minutes"),
    params_cell(PARAMS),
    env_cell("""import hashlib, requests
from phishbench import freeze, loaders
from phishbench.dedup import MinHasher
SAFE, PRIVATE, RAW = WORK / "safe_01b", WORK / "private_01b", TEMP / "ext3_mbox"
for _p in (SAFE, PRIVATE, RAW):
    _p.mkdir(parents=True, exist_ok=True)"""),
    selftest_cell(),
    md("## 1. Protected set: every training and validation record from 01"),
    code("""
ROLES = {"train_r1", "val_r1", "train_r1_rw", "val_r1_rw", "train_r2_extra", "val_r2_extra", "train_r2_sens_nigerian"}
src01 = manifest.find_artifact(INPUT_ROOT, "records")
recs01 = manifest.read_jsonl(src01)
hasher = MinHasher(MINHASH["num_perm"], SEED)
SIG = {}
P_TV = freeze.Decontaminator(hasher, threshold=MINHASH["threshold"], cache=SIG)
n_prot = 0
for r in recs01:
    if r["cell"] in ROLES:
        P_TV.add(r); n_prot += 1
log("01 records", len(recs01), "| protected train/val records", n_prot)
"""),
    md("## 2. Seeded months per list, polite download, provenance"),
    code("""
y0, m0 = map(int, WINDOW[0].split("-")); y1, m1 = map(int, WINDOW[1].split("-"))
MONTHS = [f"{y:04d}-{m:02d}" for y in range(y0, y1 + 1) for m in range(1, 13) if (y, m) >= (y0, m0) and (y, m) <= (y1, m1)]
rng = np.random.default_rng(SEED)
PLAN = {lst: sorted(rng.choice(MONTHS, MONTHS_PER_LIST, replace=False).tolist()) for lst in LISTS}
PROV, CANDIDATES, EXCL = [], [], defaultdict(Counter)
session = requests.Session(); session.headers["User-Agent"] = USER_AGENT
for lst in LISTS:
    for month in PLAN[lst]:
        url = API.format(lst=lst, month=month)
        row = {"list": lst, "month": month, "url": url, "http_status": None, "bytes": 0, "sha256": None, "messages": 0, "candidates": 0, "error": ""}
        try:
            resp = session.get(url, timeout=180)
            row["http_status"] = resp.status_code
            if resp.status_code == 200 and resp.content:
                p = RAW / f"{lst.replace('@', '_at_')}_{month}.mbox"
                p.write_bytes(resp.content)
                row.update(bytes=len(resp.content), sha256=hashlib.sha256(resp.content).hexdigest())
                recs, why = loaders.load_apache_mbox(p, lst, WINDOW[0], WINDOW[1])
                row["messages"] = sum(why.values())   # every message gets exactly one outcome, "candidate" included
                row["candidates"] = len(recs)
                for k, v in why.items():
                    EXCL[lst][k] += v
                CANDIDATES += recs
        except Exception as e:   # recorded, never retried blindly
            row["error"] = f"{type(e).__name__}: {e}"[:200]
        PROV.append(row)
        time.sleep(REQUEST_DELAY_S)
    log(lst, "| candidates so far", len(CANDIDATES))
with (SAFE / "fetch_provenance.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(PROV[0]), lineterminator="\\n"); w.writeheader(); w.writerows(PROV)
"""),
    md("## 3. Filters, decontamination, per-list cap and the seeded draw (n = 500)"),
    code("""
by_list = defaultdict(list)
for r in CANDIDATES:
    by_list[r["list"]].append(r)
stage1, EXCL_SEL = [], {}
for lst in LISTS:   # stage 1: filters + decontamination + within-list near duplicates, capped per list
    kept, why = freeze.select_cell(by_list[lst], PER_LIST_CAP, SEED, P_TV, hasher, **HUMAN_FILTERS)
    stage1 += kept; EXCL_SEL[lst] = dict(why)
ext3, why_all = freeze.select_cell(stage1, N_EXT3, SEED, P_TV, hasher)   # stage 2: cross-list near duplicates, final draw
EXCL_SEL["_final_draw"] = dict(why_all)
assert not any(P_TV.linked(r) for r in ext3), "an EXT3 record is linked to training or validation"
with gzip.open(PRIVATE / "records_ext3.jsonl.gz", "wt", encoding="utf-8") as f:
    for r in ext3:
        f.write(json.dumps(r, ensure_ascii=False) + "\\n")
COUNTS = {"n": len(ext3), "target": N_EXT3, "by_list": dict(Counter(r["list"] for r in ext3)),
          "by_year": dict(sorted(Counter(r["year"] for r in ext3).items())),
          "median_words": float(np.median([textnorm.word_count(r["body"]) for r in ext3])) if ext3 else None,
          "candidates": len(CANDIDATES), "stage1": len(stage1)}
rows = [{"list": lst, "stage": "parse", "reason": k, "count": v} for lst in LISTS for k, v in sorted(EXCL[lst].items())]
rows += [{"list": lst, "stage": "select", "reason": k, "count": v} for lst, d in EXCL_SEL.items() for k, v in sorted(d.items())]
with (SAFE / "exclusions.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["list", "stage", "reason", "count"], lineterminator="\\n"); w.writeheader(); w.writerows(rows)
manifest.write_json(SAFE / "cell_counts.json", COUNTS)
log("EXT3", COUNTS)
"""),
    md("## 4. Gates, privacy check and run manifest"),
    code("""
safe_blob = textnorm.normalize("\\n".join(p.read_text(encoding="utf-8") for p in SAFE.glob("*") if p.is_file()))
probe = [r for r in ext3 if len(textnorm.normalize(r["body"])) >= 40]
leaks = sum(1 for r in random.Random(SEED).sample(probe, min(300, len(probe))) if textnorm.normalize(r["body"])[:40] in safe_blob)
GATES = {"every_planned_month_attempted": len(PROV) == len(LISTS) * MONTHS_PER_LIST,
         "no_record_linked_to_train_or_val": True,   # asserted above
         "privacy_no_text_in_safe_outputs": leaks == 0}
manifest.write_json(SAFE / "private_files_sha256.json", {"content_sha256": {"records_ext3": manifest.content_sha256(PRIVATE / "records_ext3.jsonl.gz")}})
manifest.write_json(SAFE / "run_manifest.json", {
    "notebook": "01b_Extension_Newer_Human_Email", "status": "COMPLETED" if all(GATES.values()) else "COMPLETED_WITH_GATE_FAILURES",
    "gates": GATES, "counts": COUNTS, "n_at_target": len(ext3) == N_EXT3, "plan": PLAN,
    "fetch_failures": [r for r in PROV if r["http_status"] != 200 or r["error"]],
    "records_01_sha256": manifest.content_sha256(src01),
    "private_files_sha256": {"content_sha256": {"records_ext3": manifest.content_sha256(PRIVATE / "records_ext3.jsonl.gz")}},
    "phishbench_commit": CODE_COMMIT, "runtime_seconds": round(time.time() - T0, 1), "params": PARAMS, "environment": ENV,
    "selftest": SELFTEST, "files": manifest.file_hashes(SAFE)})
log("gates", GATES)
assert GATES["privacy_no_text_in_safe_outputs"], "Privacy gate failure"
"""),
]
write_notebook(OUT, cells, gpu=False)
print("wrote", OUT)
