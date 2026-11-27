"""Builds notebooks/03_Graded_AI_Assistance_Generation.ipynb (one notebook, three kernels; GENERATOR differs)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import code, env_cell, header, md, params_cell, selftest_cell, write_notebook  # noqa: E402

OUT, COMMIT, GEN = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
PARAMS = {
    "REPO_URL": "https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git",
    "CODE_COMMIT": COMMIT,
    "SEED": 2026,
    "GENERATOR": GEN,
    "GENERATORS": {
        "qwen2.5-7b": {"repo": "Qwen/Qwen2.5-7B-Instruct", "role": "test", "kv_budget_gb": 6.0, "dtype": "float16"},
        # deviation 12: Phi in float16 (float32 needed > 12 h); KV budgets use the memory left after the weights
        "phi-3.5-mini": {"repo": "microsoft/Phi-3.5-mini-instruct", "role": "test", "kv_budget_gb": 12.0, "dtype": "float16"},
        "olmo-2-7b": {"repo": "allenai/OLMo-2-1124-7B-Instruct", "role": "train", "kv_budget_gb": 10.0, "dtype": "float16"},
    },
    "EMBED_REPO": "sentence-transformers/all-MiniLM-L6-v2",
    "COSINE_THRESHOLD": 0.70,
    "MAX_BATCH": 32,
    "FIRST_BATCH_MIN_PASS": 0.5,
    "MAX_GEN_SECONDS": 37800,        # 10.5 h: stop starting new batches, keep time to embed and write (Kaggle 12 h limit)
    "ATTRITION_FLAG_BELOW": 0.80,    # reported for the paper, not a gate: §3.4 counts exclusions (deviation 12)
    "EXPECTED_VERSIONS": {"sklearn": "1.6.1", "transformers": "5.20.2", "sentence_transformers": "5.7.0"},
}

cells = [
    header("03", f"Graded AI-assistance generation ({GEN})",
           "Produce paired, placeholder-locked AI-assisted versions of real emails. Test-only generators write L1 proofread, "
           "L2 polish, L3 rewrite and L4 compose-from-subject for EXT and IN legitimate parents, and L3 for EXT and IN phishing parents. "
           "The train-only generator writes L3 and L4 for R1 training legitimate parents and L3 for R1 training phishing parents "
           "(mitigations M1 and M5). The same notebook runs once per generator.",
           "§3.2, §3.4, deviations 1–3 and 5",
           ["Kernel output of `01-data-sources-audit-and-locked-cells` (`private_01/records.jsonl.gz`)",
            "Pinned Hugging Face model revisions (resolved and recorded at run time)"],
           ["`safe_03/<generator>/` (committed to `results/03_generation/`): generation summary, manipulation check, run manifest",
            "`private_03/generated_<generator>.jsonl.gz` (private): generated text, used as input to 05 and 07"],
           ["first-batch pass rate ≥ 0.5 (fail fast on numerical issues)", "every task attempted within the time guard",
            "no email text in safe outputs (cells with kept rate < 0.80 are flagged for reporting, as §3.4 counts exclusions)"],
           "Kaggle GPU T4×2, internet ON, about 4–7 hours per generator"),
    params_cell(PARAMS),
    env_cell("""import numpy as np, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import HfApi, snapshot_download
from phishbench import generation
from phishbench.dedup import MinHasher, shingles, estimated_jaccard
CFG = GENERATORS[GENERATOR]
DTYPE = getattr(torch, CFG["dtype"])
SAFE, PRIVATE = WORK / "safe_03" / GENERATOR, WORK / "private_03"
for _p in (SAFE, PRIVATE):
    _p.mkdir(parents=True, exist_ok=True)"""),
    selftest_cell(),
md("## 1. Load the locked records from 01 and build the generation tasks (§3.3 generation scope)"),
code("""
src = sorted(Path("/kaggle/input").rglob("records.jsonl.gz"))
assert src, "Attach kernel output ddipra/01-data-sources-audit-and-locked-cells as an input"
RECORDS_01_SHA256 = manifest.sha256_file(src[0])
by_cell = defaultdict(list)
with gzip.open(src[0], "rt", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        by_cell[r["cell"]].append(r)
log("01 records", RECORDS_01_SHA256[:12], {k: len(v) for k, v in by_cell.items() if not k.startswith("INFULL")})

tasks = []   # (parent, level, out_cell)
if CFG["role"] == "test":
    for cell in ("EXT-legit-L0", "IN-legit-L0"):
        for p in by_cell[cell]:
            for lv in ("L1", "L2", "L3", "L4"):
                tasks.append((p, lv, cell.replace("-L0", f"-{lv}-{GENERATOR}")))
    for cell in ("EXT-phish-H", "IN-phish-H"):
        for p in by_cell[cell]:
            tasks.append((p, "L3", cell.replace("-H", f"-L3-{GENERATOR}")))
else:
    for p in by_cell["train_r1"]:
        levels = ("L3", "L4") if p["label"] == 0 else ("L3",)
        for lv in levels:
            tasks.append((p, lv, f"train_r1-{'legit' if p['label'] == 0 else 'phish'}-{lv}-{GENERATOR}"))
log("tasks", len(tasks), Counter(t[2] for t in tasks))
"""),
md("## 2. Load the pinned model and generate in token-budgeted batches"),
code("""
api = HfApi()
REV = api.model_info(CFG["repo"]).sha
mpath = snapshot_download(CFG["repo"], revision=REV, allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.tiktoken", "tokenizer*"])
tok = AutoTokenizer.from_pretrained(mpath)
tok.padding_side = "left"
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
try:
    model = AutoModelForCausalLM.from_pretrained(mpath, dtype=DTYPE, device_map="auto")
except TypeError:
    model = AutoModelForCausalLM.from_pretrained(mpath, torch_dtype=DTYPE, device_map="auto")
model.eval()
cfg = model.config
head_dim = getattr(cfg, "head_dim", None) or cfg.hidden_size // cfg.num_attention_heads
kv_heads = getattr(cfg, "num_key_value_heads", None) or cfg.num_attention_heads
KV_BYTES_PER_TOKEN = 2 * cfg.num_hidden_layers * kv_heads * head_dim * torch.tensor([], dtype=DTYPE).element_size()
log("model", CFG["repo"], "rev", REV, "| KV bytes/token", KV_BYTES_PER_TOKEN)

requests = []
for i, (p, lv, out_cell) in enumerate(tasks):
    req = generation.build_request(p, lv)
    chat = tok.apply_chat_template([{"role": "user", "content": req["prompt"]}], add_generation_prompt=True, tokenize=False)
    n_in = len(tok(chat, add_special_tokens=False)["input_ids"])
    requests.append({"i": i, "id": f"{p['sample_id']}|{lv}|{GENERATOR}", "chat": chat, "n_in": n_in, "req": req,
                     "parent": p, "level": lv, "cell": out_cell})
requests.sort(key=lambda r: (r["n_in"], r["id"]))            # deviation 2: deterministic batch formation

def reserve(r):   # expected output tokens, used only for batch sizing (generation itself allows 2048)
    return 700 if r["level"] == "L4" else int(1.6 * r["n_in"]) + 256

budget = CFG["kv_budget_gb"] * 1e9
batches, cur = [], []
for r in requests:
    trial = cur + [r]
    need = len(trial) * (max(x["n_in"] for x in trial) + max(reserve(x) for x in trial)) * KV_BYTES_PER_TOKEN
    if cur and (need > budget or len(trial) > MAX_BATCH):
        batches.append(cur); cur = [r]
    else:
        cur = trial
if cur:
    batches.append(cur)
log("batches", len(batches))

DEC = generation.DECODING
def run_batch(batch):
    torch.manual_seed(generation.batch_seed([r["id"] for r in batch]))
    enc = tok([r["chat"] for r in batch], return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
    try:
        with torch.no_grad():
            out = model.generate(**enc, do_sample=True, temperature=DEC["temperature"], top_p=DEC["top_p"],
                                 max_new_tokens=DEC["max_new_tokens"], pad_token_id=tok.pad_token_id,
                                 remove_invalid_values=True)   # deviation 6
    except torch.cuda.OutOfMemoryError:
        del enc; torch.cuda.empty_cache()
        if len(batch) == 1:
            return [(batch[0], None, "oom")]
        h = len(batch) // 2
        return run_batch(batch[:h]) + run_batch(batch[h:])
    texts = tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    n_new = (out[:, enc["input_ids"].shape[1]:] != tok.pad_token_id).sum(dim=1).tolist()
    return [(r, t, n) for r, t, n in zip(batch, texts, n_new)]

results, new_tokens = [], 0
for bi, batch in enumerate(batches):
    if time.time() - T0 > MAX_GEN_SECONDS:   # time guard: record the rest as not run, so nothing already generated is lost
        for b2 in batches[bi:]:
            results += [(r, None, "not_run_time_limit") for r in b2]
        log(f"TIME GUARD at batch {bi+1}/{len(batches)}: {sum(len(b2) for b2 in batches[bi:])} tasks not run")
        break
    for r, text, n in run_batch(batch):
        if text is None:
            results.append((r, None, "oom")); continue
        new_tokens += n
        res, why = generation.quality_check(r["parent"], r["level"], r["req"], text)
        results.append((r, res, why))
    if bi == 0:   # fail fast on numerical problems (for example fp16 overflow), before spending the GPU quota
        ok0 = sum(1 for x in results if x[2] is None) / max(1, len(results))
        assert ok0 >= FIRST_BATCH_MIN_PASS, f"First batch pass rate {ok0:.2f} < 0.5: stop and inspect dtype/prompting"
    if bi % 20 == 0 or bi == len(batches) - 1:
        el = time.time() - T0
        log(f"batch {bi+1}/{len(batches)} | done {len(results)}/{len(requests)} | new tokens {new_tokens} | {new_tokens/max(1,el):.0f} tok/s")
"""),
md("## 3. Cosine similarity filter (L1–L3) and manipulation check (deviation 5)"),
code("""
from sentence_transformers import SentenceTransformer
EMBED_REV = api.model_info(EMBED_REPO).sha
embedder = SentenceTransformer(EMBED_REPO, revision=EMBED_REV, device="cuda:0")
def emb(texts): return embedder.encode(texts, batch_size=128, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)

passed = [(r, res) for r, res, why in results if why is None]
pt = [textnorm.detector_input(r["parent"]["subject"], r["parent"]["body"]) for r, _ in passed]
gt = [textnorm.detector_input(res["subject"], res["body"]) for _, res in passed]
cos = (emb(pt) * emb(gt)).sum(axis=1) if passed else np.array([])
hasher = MinHasher(128, SEED)
final, reasons = [], Counter((r["cell"], why) for r, res, why in results if why is not None)
metrics = defaultdict(list)
for (r, res), c in zip(passed, cos):
    if r["level"] != "L4" and c < COSINE_THRESHOLD:
        reasons[(r["cell"], "low_similarity")] += 1; continue
    jac = estimated_jaccard(hasher.signature(shingles(r["parent"]["subject"] + "\\n" + r["parent"]["body"])),
                            hasher.signature(shingles(res["subject"] + "\\n" + res["body"])))
    ratio = textnorm.word_count(res["body"]) / max(1, textnorm.word_count(r["parent"]["body"]))
    unchanged = textnorm.normalize(res["subject"] + "\\n" + res["body"]) == textnorm.normalize(r["parent"]["subject"] + "\\n" + r["parent"]["body"])
    metrics[r["cell"]].append((jac, float(c), ratio, unchanged))
    p = r["parent"]
    final.append({"sample_id": r["id"], "source": f"gen_{GENERATOR}", "native_id": p["sample_id"], "parent_id": p["parent_id"],
                  "subject": res["subject"], "body": res["body"], "label": p["label"], "authorship": "ai",
                  "generator": GENERATOR, "level": r["level"], "year": p.get("year"), "cell": r["cell"],
                  "parent_cell": p["cell"]})

# D2-provided rewrites: same manipulation check (test-role kernels only)
d2_metrics = defaultdict(list)
if CFG["role"] == "test":
    parents = {r["sample_id"]: r for c in ("IN-legit-L0", "IN-phish-H") for r in by_cell[c]}
    for c in [k for k in by_cell if k.startswith("IN-") and "-L3-" in k]:
        rows = [(parents[r["parent_id"]], r) for r in by_cell[c] if r["parent_id"] in parents]
        if not rows: continue
        cc = (emb([textnorm.detector_input(p["subject"], p["body"]) for p, _ in rows]) *
              emb([textnorm.detector_input(r["subject"], r["body"]) for _, r in rows])).sum(axis=1)
        for (p, r), c2 in zip(rows, cc):
            jac = estimated_jaccard(hasher.signature(shingles(p["subject"] + "\\n" + p["body"])), hasher.signature(shingles(r["subject"] + "\\n" + r["body"])))
            d2_metrics[c].append((jac, float(c2), textnorm.word_count(r["body"]) / max(1, textnorm.word_count(p["body"])), False))
log("final passed", len(final), "| rejected", sum(reasons.values()))
"""),
md("## 4. Write private generated records and safe aggregate outputs"),
code("""
with gzip.open(PRIVATE / f"generated_{GENERATOR}.jsonl.gz", "wt", encoding="utf-8") as f:
    for r in final:
        f.write(json.dumps(r, ensure_ascii=False) + "\\n")
manifest.write_json(PRIVATE / f"rejected_ids_{GENERATOR}.json", sorted([r["id"], why] for r, res, why in results if why is not None))
PRIVATE_HASHES = {"file_sha256": {p.name: manifest.sha256_file(p) for p in sorted(PRIVATE.glob(f"*_{GENERATOR}.*"))},
                  "content_sha256": {f"generated_{GENERATOR}": manifest.content_sha256(PRIVATE / f"generated_{GENERATOR}.jsonl.gz")}}
manifest.write_json(SAFE / "private_files_sha256.json", PRIVATE_HASHES)   # downstream notebooks verify these

requested = Counter(r["cell"] for r in requests)
kept = Counter(r["cell"] for r in final)
with (SAFE / "generation_summary.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f, lineterminator="\\n")
    wr.writerow(["cell", "level", "requested", "kept", "kept_rate", "reason", "count"])
    for cell in sorted(requested):
        lv = cell.split("-")[2] if not cell.startswith("train") else cell.split("-")[2]
        wr.writerow([cell, lv, requested[cell], kept[cell], round(kept[cell] / requested[cell], 4), "", ""])
        for (c, why), n in sorted(reasons.items()):
            if c == cell:
                wr.writerow([cell, lv, "", "", "", why, n])

def summ(vals):
    a = np.array(vals, dtype=float)
    return [round(float(np.mean(a)), 4), round(float(np.median(a)), 4), round(float(np.percentile(a, 10)), 4), round(float(np.percentile(a, 90)), 4)]
with (SAFE / "manipulation_check.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f, lineterminator="\\n")
    wr.writerow(["cell", "n", "jaccard_mean", "jaccard_median", "jaccard_p10", "jaccard_p90",
                 "cosine_mean", "cosine_median", "cosine_p10", "cosine_p90",
                 "word_ratio_mean", "word_ratio_median", "word_ratio_p10", "word_ratio_p90", "unchanged_share"])
    for cell, m in sorted({**metrics, **d2_metrics}.items()):
        j, c, w, u = zip(*m)
        wr.writerow([cell, len(m), *summ(j), *summ(c), *summ(w), round(sum(u) / len(u), 4)])

safe_blob = "\\n".join(p.read_text(encoding="utf-8") for p in SAFE.glob("*") if p.is_file())
probe = random.Random(SEED).sample(final, min(300, len(final))) if final else []
leaks = sum(1 for r in probe if len(textnorm.normalize(r["body"])) >= 40 and textnorm.normalize(r["body"])[:40] in textnorm.normalize(safe_blob))
gates = {"privacy_no_text_in_safe_outputs": leaks == 0,
         "every_task_attempted": not any(why == "not_run_time_limit" for _, _, why in results)}
ATTRITION = {c: round(kept[c] / requested[c], 4) for c in sorted(requested) if kept[c] / requested[c] < ATTRITION_FLAG_BELOW}
manifest.write_json(SAFE / "run_manifest.json", {
    "notebook": f"03_Graded_AI_Assistance_Generation[{GENERATOR}]", "status": "COMPLETED" if all(gates.values()) else ("PARTIAL_TIME_LIMIT" if gates["privacy_no_text_in_safe_outputs"] else "COMPLETED_WITH_GATE_FAILURES"),
    "attrition_flags_kept_rate_below_0.80": ATTRITION, "private_files_sha256": PRIVATE_HASHES,
    "gates": gates, "generator": GENERATOR, "model_repo": CFG["repo"], "model_revision": REV, "role": CFG["role"],
    "dtype": CFG["dtype"], "decoding": generation.DECODING, "seeding": "per batch (deviation 2)",
    "embedder": {"repo": EMBED_REPO, "revision": EMBED_REV, "cosine_threshold": COSINE_THRESHOLD},
    "records_01_sha256": RECORDS_01_SHA256, "phishbench_commit": CODE_COMMIT,
    "requests": len(requests), "kept": len(final), "batches": len(batches), "new_tokens": new_tokens,
    "runtime_seconds": round(time.time() - T0, 1), "gpus": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
    "params": PARAMS, "environment": ENV, "selftest": SELFTEST, "files": manifest.file_hashes(SAFE),
})
log("gates", gates)
log("attrition flags (reported, not a gate)", ATTRITION)
assert gates["privacy_no_text_in_safe_outputs"], "Privacy gate failure: outputs must not be used downstream"
if not gates["every_task_attempted"]:
    log("PARTIAL run: outputs kept for a continuation; not usable downstream as a complete cell set")
"""),
]
write_notebook(OUT, cells, gpu=True)
print("wrote", OUT)
