"""Dependency- and slot-aware Kaggle pipeline: build, push, wait, collect, commit, then start the next step.

For each step:
  1. Build the notebook with its builder at the current pushed HEAD commit.
  2. Write kernel-metadata.json and the EXACT notebook into kaggle_kernels/<step>/. Committing both lets anyone
     reproduce the run with `kaggle kernels push -p kaggle_kernels/<step>`.
  3. Push once a GPU slot is free (the free tier allows 2 concurrent batch GPU sessions).
  4. When the run ends: download the outputs to the private folder, check that the run manifest says COMPLETED,
     copy ONLY the safe folder into results/, then git commit and push.
  5. A failed step stops its dependants, and the reason is logged. Steps are never retried blindly.
State lives in <private>/pipeline_state.json, so the runner can be stopped and resumed.

Usage: python scripts/pipeline.py [--only step1,step2]
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PRIVATE = Path(os.environ.get("PHISH_PRIVATE", REPO.parent / "AI-Generated-Phishing-Detection_private"))
_VENV_CLI = REPO.parent / "AI-Generated-Phishing-Detection_venv" / "Scripts" / "kaggle.exe"
CLI = os.environ.get("KAGGLE_CLI") or (str(_VENV_CLI) if _VENV_CLI.exists() else "kaggle")
LOCK = PRIVATE / "pipeline.lock"   # heartbeat: refreshed every poll; a second runner exits while it is fresh
OWNER = "ddipra"
MAX_SLOTS = 2
POLL = 90
sys.path.insert(0, str(REPO / "scripts" / "notebook_builders"))
from common import kernel_metadata  # noqa: E402

K01 = f"{OWNER}/01-data-sources-audit-and-locked-cells"
GEN = {g: f"{OWNER}/03-generation-{g.replace('.', '-')}" for g in ("qwen2.5-7b", "phi-3.5-mini", "olmo-2-7b")}
# Deviation 12: the Qwen kernel finished all generation, but a builder-level gate (not in the protocol) failed. Its exact
# outputs are frozen as a private dataset (content hashes in results/03_generation/qwen2.5-7b/private_files_sha256.json),
# so downstream steps read Qwen from the dataset, not from the kernel.
QWEN_DS = f"{OWNER}/phishbench-03-qwen2-5-7b-outputs"
GEN_SRC = {g: k for g, k in GEN.items() if g != "qwen2.5-7b"}

STEPS = {
    "02": dict(builder=["build_02.py"], nb="02_Study1_Exploratory_Reproduction.ipynb", slug=f"{OWNER}/02-study1-exploratory-reproduction",
               deps=[], sources=[], safe="safe_02", results="results/02_study1"),
    **{f"03-{g}": dict(builder=["build_03.py", g], nb="03_Graded_AI_Assistance_Generation.ipynb", slug=GEN[g], deps=[],
                       sources=[K01], safe=f"safe_03/{g}", results=f"results/03_generation/{g}") for g in GEN},
    "05-classical": dict(builder=["build_05.py", "classical"], nb="05_Detector_Training_and_Sealed_Scoring.ipynb",
                         slug=f"{OWNER}/05-training-classical", deps=[f"03-{g}" for g in GEN], sources=[K01, *GEN_SRC.values()], datasets=[QWEN_DS],
                         safe="safe_05/classical", results="results/05_training/classical"),
    "05-transformers": dict(builder=["build_05.py", "transformers"], nb="05_Detector_Training_and_Sealed_Scoring.ipynb",
                            slug=f"{OWNER}/05-training-transformers", deps=[f"03-{g}" for g in GEN], sources=[K01, *GEN_SRC.values()], datasets=[QWEN_DS],
                            safe="safe_05/transformers", results="results/05_training/transformers"),
    "04-kit": dict(builder=["build_04.py", "kit"], nb="04_Human_Validation.ipynb", slug=f"{OWNER}/04-human-validation-kit",
                   deps=["03-qwen2.5-7b", "03-phi-3.5-mini"], sources=[K01, GEN["phi-3.5-mini"]], datasets=[QWEN_DS],
                   safe="safe_04/kit", results="results/04_human_validation/kit"),
    # 04-score waits until both raters' answers and the adjudication are committed (docs/HUMAN_VALIDATION_PROTOCOL.md)
    "04-score": dict(builder=["build_04.py", "score"], nb="04_Human_Validation.ipynb", slug=f"{OWNER}/04-human-validation-score",
                     deps=["04-kit"], sources=[f"{OWNER}/04-human-validation-kit"], safe="safe_04/score",
                     results="results/04_human_validation/score",
                     requires=[f"results/04_human_validation/ratings/{n}" for n in ("rater_A.csv", "rater_B.csv", "adjudication.csv")]),
    "06": dict(builder=["build_06.py"], nb="06_Zero_Shot_LLM_Judge.ipynb", slug=f"{OWNER}/06-zero-shot-llm-judge",
               deps=["03-qwen2.5-7b", "03-phi-3.5-mini"], sources=[K01, GEN["phi-3.5-mini"]], datasets=[QWEN_DS],
               safe="safe_06", results="results/06_judge"),
    "07": dict(builder=["build_07.py"], nb="07_Confirmatory_Evaluation.ipynb", slug=f"{OWNER}/07-confirmatory-evaluation",
               deps=["05-classical", "05-transformers", "06"],
               datasets=[QWEN_DS], sources=[K01, GEN["phi-3.5-mini"], f"{OWNER}/05-training-classical",
                        f"{OWNER}/05-training-transformers", f"{OWNER}/06-zero-shot-llm-judge"],
               safe="safe_07", results="results/07_confirmatory"),
}
ORDER = ["02", "03-qwen2.5-7b", "03-phi-3.5-mini", "03-olmo-2-7b", "04-kit", "06", "05-classical", "05-transformers", "07",
         "04-score"]


def sh(*args, cwd=REPO, check=True) -> str:
    out = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True)
    if check and out.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}\n{out.stdout}\n{out.stderr}")
    return (out.stdout + out.stderr).strip()


def log(msg: str) -> None:
    line = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}Z {msg}"
    print(line, flush=True)
    with (PRIVATE / "pipeline.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state() -> dict:
    p = PRIVATE / "pipeline_state.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_state(st: dict) -> None:
    (PRIVATE / "pipeline_state.json").write_text(json.dumps(st, indent=2), encoding="utf-8")


def kstatus(slug: str) -> str:
    s = sh(CLI, "kernels", "status", slug, check=False)
    for k in ("COMPLETE", "ERROR", "CANCEL", "RUNNING", "QUEUED"):
        if k in s:
            return k
    return "UNKNOWN"


def git_sync_commit(paths: list[str], message: str) -> str:
    sh("git", "add", *paths)
    if not sh("git", "diff", "--cached", "--name-only"):
        return sh("git", "rev-parse", "HEAD")
    sh("git", "commit", "-q", "-m", message + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    sh("git", "pull", "--rebase", "--autostash", "-q", "origin", "main")
    sh("git", "push", "-q", "origin", "main")
    return sh("git", "rev-parse", "HEAD")


def available(name: str) -> bool:
    """The step's builder exists and every committed input it requires is present (tracked by git, not just on disk)."""
    s = STEPS[name]
    if not (REPO / "scripts" / "notebook_builders" / s["builder"][0]).exists():
        return False
    return all(sh("git", "ls-files", r, check=False) for r in s.get("requires", []))


def prepare(name: str) -> Path:
    s = STEPS[name]
    commit = sh("git", "rev-parse", "HEAD")
    kdir = REPO / "kaggle_kernels" / name
    kernel_metadata(kdir, s["slug"].split("/")[1], s["nb"], gpu=True, kernel_sources=s["sources"],
                    dataset_sources=s.get("datasets", []))
    sh(sys.executable, str(REPO / "scripts" / "notebook_builders" / s["builder"][0]), str(kdir / s["nb"]), commit, *s["builder"][1:])
    git_sync_commit([str(kdir.relative_to(REPO))], f"run({name}): exact notebook and kernel metadata pushed to Kaggle [skip ci]")
    return kdir


def collect(name: str) -> bool:
    s = STEPS[name]
    out = PRIVATE / f"{name}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    out.mkdir(parents=True, exist_ok=True)
    sh(CLI, "kernels", "output", s["slug"], "-p", str(out), check=False)
    man = out / s["safe"] / "run_manifest.json"
    if not man.exists():
        log(f"{name}: no run manifest in outputs ({out})")
        return False
    m = json.loads(man.read_text(encoding="utf-8"))
    if m.get("status") != "COMPLETED":
        log(f"{name}: status {m.get('status')} gates {m.get('gates')}")
        return False
    dst = REPO / s["results"]
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(out / s["safe"], dst)
    head = git_sync_commit([s["results"]], f"results({name}): {m.get('notebook')} COMPLETED, all gates PASS "
                                            f"(runtime {m.get('runtime_seconds')} s)")
    log(f"{name}: COMPLETED -> {s['results']} committed at {head[:8]}")
    return True


def heartbeat() -> None:
    LOCK.write_text(f"{os.getpid()} {datetime.now(timezone.utc).isoformat()}", encoding="utf-8")


def main(only: list[str] | None) -> int:
    PRIVATE.mkdir(parents=True, exist_ok=True)
    if LOCK.exists() and time.time() - LOCK.stat().st_mtime < 3 * POLL:
        log(f"another runner is active ({LOCK.read_text(encoding='utf-8')}); exiting")
        return 1
    heartbeat()
    st = load_state()
    todo = [n for n in ORDER if (not only or n in only)]
    for n in todo:
        st.setdefault(n, {"state": "pending"})
    save_state(st)
    while True:
        running = [n for n in todo if st[n]["state"] == "running"]
        for n in running:
            k = kstatus(STEPS[n]["slug"])
            if k in ("COMPLETE", "ERROR", "CANCEL"):
                ok = k == "COMPLETE" and collect(n)
                st[n]["state"] = "done" if ok else "failed"
                st[n]["finished"] = datetime.now(timezone.utc).isoformat()
                log(f"{n}: kernel {k} -> {st[n]['state']}")
                save_state(st)
        running = [n for n in todo if st[n]["state"] == "running"]
        for n in todo:
            if st[n]["state"] != "pending" or len(running) >= MAX_SLOTS:
                continue
            deps = STEPS[n]["deps"]
            if any(st.get(d, {}).get("state") == "failed" for d in deps):
                st[n]["state"] = "blocked"; log(f"{n}: blocked by a failed dependency"); save_state(st); continue
            if not all(st.get(d, {}).get("state") == "done" for d in deps):
                continue
            if not available(n):
                continue   # builder or required committed inputs (for example ratings) not there yet; the step waits
            if kstatus(STEPS[n]["slug"]) in ("RUNNING", "QUEUED") and st[n].get("adopt", True):
                st[n].update(state="running", adopted=True); log(f"{n}: adopted an already running kernel"); save_state(st)
                running.append(n); continue
            kdir = prepare(n)
            out = sh(CLI, "kernels", "push", "-p", str(kdir), check=False)
            if "successfully" in out:
                st[n].update(state="running", pushed=datetime.now(timezone.utc).isoformat(), commit=sh("git", "rev-parse", "HEAD"))
                log(f"{n}: pushed ({out.splitlines()[-1][:90]})"); running.append(n)
            else:
                log(f"{n}: push deferred: {out.splitlines()[-1][:120] if out else 'no output'}")
            save_state(st)
        if all(st[n]["state"] in ("done", "failed", "blocked") for n in todo):
            break
        if not any(st[n]["state"] == "running" for n in todo) and not any(
                st[n]["state"] == "pending" and all(st.get(d, {}).get("state") == "done" for d in STEPS[n]["deps"])
                and available(n) for n in todo):
            log("nothing runnable: waiting for builders or dependencies"); break
        heartbeat()
        time.sleep(POLL)
    log("pipeline stop: " + json.dumps({n: st[n]["state"] for n in todo}))
    LOCK.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    sys.exit(main(only))
