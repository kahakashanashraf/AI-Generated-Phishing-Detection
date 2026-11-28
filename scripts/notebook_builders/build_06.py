"""Builds notebooks/06_Zero_Shot_LLM_Judge.ipynb (D6: Granite-3.1-8B-Instruct, zero-shot, sealed scoring)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import code, env_cell, header, md, params_cell, selftest_cell, write_notebook  # noqa: E402

OUT, COMMIT = Path(sys.argv[1]), sys.argv[2]
PARAMS = {
    "REPO_URL": "https://github.com/kahakashanashraf/AI-Generated-Phishing-Detection.git",
    "CODE_COMMIT": COMMIT,
    "SEED": 2026,
    "EXPECTED_VERSIONS": {"sklearn": "1.6.1", "transformers": "5.20.2"},
    "JUDGE_REPO": "ibm-granite/granite-3.1-8b-instruct",
    "JUDGE_PROMPT": ("Classify the following email as phishing or legitimate. Phishing means it tries to trick the "
                     "recipient into revealing credentials, paying, opening a malicious link or attachment, or "
                     "otherwise acting against their interest. Answer with exactly one word: phishing or legitimate."
                     "\n\n{email}"),
    "LABEL_WORDS": {"phishing": "phishing", "legitimate": "legitimate"},
    "EMAIL_MAX_TOKENS": 1536, "EMAIL_HEAD_TOKENS": 1024,
    "TOKEN_BUDGET": 12000, "MAX_BATCH": 16,
    "FPR_TARGETS": {"tau5": 0.05, "tau1": 0.01},
    "TEST_GENERATORS": ["qwen2.5-7b", "phi-3.5-mini"],
    "EXTENSION_INPUTS": ["records_ext3", "generated_qwen2.5-7b__ext3", "generated_phi-3.5-mini__ext3", "generated_qwen2.5-14b"],   # deviation 15
    "INPUT_ROOT": "/kaggle/input",
}
cells = [
    header("06", "Zero-shot LLM judge (D6) with sealed scoring",
           "Score every cell with a zero-shot instruction model from a family different from every generator (deviation 8 fixes the "
           "truncation and scoring details before any scoring). Score = P(phishing) from the first-token logits of the two label words. "
           "τ5/τ1 come from R1 validation with the same rule as D1–D5. Locked-cell scores are **sealed** (deviation 7).",
           "§4 (D6), deviations 7–8",
           ["01 records", "03 generated test cells (Qwen, Phi)"],
           ["`safe_06/` (committed): registry (validation metrics, τ), seal manifest, run manifest",
            "`private_06/scores/D6.csv.gz` (sealed)"],
           ["model revision pinned and recorded", "validation FPR at τ5 ≤ 0.05", "every cell scored"],
           "Kaggle GPU T4×2 (8B model in fp16 split across both GPUs), about 1–2 hours"),
    params_cell(PARAMS),
    env_cell("""import numpy as np, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import HfApi, snapshot_download
from phishbench import stats
SAFE, PRIVATE = WORK / "safe_06", WORK / "private_06"
(PRIVATE / "scores").mkdir(parents=True, exist_ok=True); SAFE.mkdir(parents=True, exist_ok=True)"""),
    selftest_cell(),
    md("## 1. Inputs and the cells to score (identical to 05, without the H4 cells)"),
    code("""
read_gz = manifest.read_jsonl          # .jsonl.gz from kernel outputs, .jsonl from Kaggle datasets (deviation 12)
INPUTS = {"01": manifest.find_artifact(INPUT_ROOT, "records"),
          **{g: manifest.find_artifact(INPUT_ROOT, f"generated_{g}") for g in TEST_GENERATORS},
          **{stem: manifest.find_artifact(INPUT_ROOT, stem) for stem in EXTENSION_INPUTS}}   # deviation 15
INPUT_SHA256 = {k: manifest.content_sha256(v) for k, v in INPUTS.items()}
by_cell = defaultdict(list)
for p in INPUTS.values():
    for r in read_gz(p):
        by_cell[r["cell"]].append(r)
ROLE_KEYS = {"train_r1", "val_r1", "train_r1_rw", "val_r1_rw", "train_r2_extra", "val_r2_extra", "train_r2_sens_nigerian"}
SCORE_CELLS = sorted(c for c in by_cell if c not in ROLE_KEYS and not c.startswith("train_r1-"))
log("cells", len(SCORE_CELLS), "rows", sum(len(by_cell[c]) for c in SCORE_CELLS))
"""),
    md("## 2. Load the judge (pinned revision, fp16 across both T4s) and define the scoring rule"),
    code("""
REV = HfApi().model_info(JUDGE_REPO).sha
path = snapshot_download(JUDGE_REPO, revision=REV, allow_patterns=["*.json", "*.safetensors", "*.txt", "tokenizer*", "*.model"])
tok = AutoTokenizer.from_pretrained(path); tok.padding_side = "left"
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float16, device_map="auto").eval()
first = lambda w: tok(w, add_special_tokens=False)["input_ids"][0]
LABEL_IDS = {k: sorted({first(w), first(" " + w), first(w.capitalize())}) for k, w in LABEL_WORDS.items()}
assert not (set(LABEL_IDS["phishing"]) & set(LABEL_IDS["legitimate"])), "label words share a first token"
def email_text(r):
    ids = tok(textnorm.detector_input(r["subject"], r["body"]), add_special_tokens=False)["input_ids"]
    if len(ids) > EMAIL_MAX_TOKENS:
        ids = ids[:EMAIL_HEAD_TOKENS] + ids[-(EMAIL_MAX_TOKENS - EMAIL_HEAD_TOKENS):]
    return tok.decode(ids)
def chat(r):
    return tok.apply_chat_template([{"role": "user", "content": JUDGE_PROMPT.format(email=email_text(r))}],
                                   add_generation_prompt=True, tokenize=False)
@torch.no_grad()
def score(rows):
    prompts = [chat(r) for r in rows]
    lens = [len(tok(p, add_special_tokens=False)["input_ids"]) for p in prompts]
    order = np.argsort(lens, kind="stable"); out = np.zeros(len(rows)); i = 0
    while i < len(order):
        j = i
        while j < len(order) and (j - i + 1) * lens[order[j]] <= TOKEN_BUDGET and j - i < MAX_BATCH:
            j += 1
        j = max(j, i + 1); idx = order[i:j]
        enc = tok([prompts[k] for k in idx], return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        logits = model(**enc).logits[:, -1, :].float()
        lp = torch.logsumexp(logits[:, LABEL_IDS["phishing"]], -1); ll = torch.logsumexp(logits[:, LABEL_IDS["legitimate"]], -1)
        out[idx] = torch.sigmoid(lp - ll).cpu().numpy(); i = j
    return out
log("judge", JUDGE_REPO, REV, "| label ids", LABEL_IDS)
"""),
    md("## 3. Validation thresholds, then sealed scoring of every cell"),
    code("""
from sklearn.metrics import average_precision_score, roc_auc_score
va = by_cell["val_r1"]; yv = np.array([r["label"] for r in va]); sv = score(va)
taus = {k: stats.threshold_at_fpr(yv, sv, v) for k, v in FPR_TARGETS.items()}
REG = {"model_id": "D6|zero-shot|M0|s0", "repo": JUDGE_REPO, "revision": REV, "val_ap": average_precision_score(yv, sv),
       "val_auroc": roc_auc_score(yv, sv), **taus, "val_fpr_at_tau5": float(np.mean(sv[yv == 0] >= taus["tau5"])),
       "val_recall_at_tau5": float(np.mean(sv[yv == 1] >= taus["tau5"])), "argmax_val_fpr": float(np.mean(sv[yv == 0] >= 0.5))}
log("validation", REG)
spath = PRIVATE / "scores" / "D6__zero-shot__M0__s0.csv.gz"
with gzip.open(spath, "wt", encoding="utf-8", newline="") as f:          # SEALED (deviation 7)
    wr = csv.writer(f, lineterminator="\\n"); wr.writerow(["model_id", "cell", "sample_id", "score"])
    for c in SCORE_CELLS:
        for r, s in zip(by_cell[c], score(by_cell[c])):
            wr.writerow([REG["model_id"], c, r["sample_id"], f"{float(s):.8f}"])
        log("  scored", c, len(by_cell[c]))
    for r, s in zip(va, sv):
        wr.writerow([REG["model_id"], "VALIDATION", r["sample_id"], f"{float(s):.8f}"])
SEAL = {spath.name: manifest.sha256_file(spath)}
manifest.write_json(SAFE / "seal_manifest.json", {"part": "judge", "files": SEAL})
with (SAFE / "model_registry.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(REG.keys()), lineterminator="\\n"); wr.writeheader(); wr.writerow(REG)
GATES = {"validation_fpr_at_tau5_le_0.05": REG["val_fpr_at_tau5"] <= 0.05 + 1e-12, "sealed": len(SEAL) == 1}
manifest.write_json(SAFE / "run_manifest.json", {"notebook": "06_Zero_Shot_LLM_Judge", "status": "COMPLETED" if all(GATES.values()) else "COMPLETED_WITH_GATE_FAILURES",
                    "gates": GATES, "input_sha256": INPUT_SHA256, "params": PARAMS, "environment": ENV, "selftest": SELFTEST,
                    "runtime_seconds": round(time.time() - T0, 1), "files": manifest.file_hashes(SAFE)})
log("gates", GATES); assert all(GATES.values())
"""),
]
write_notebook(OUT, cells, gpu=True)
print("wrote", OUT)
