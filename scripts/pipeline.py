"""Dependency- and slot-aware Kaggle pipeline: build, push, wait, collect, commit, then start the next step.

For each step:
  1. Build the notebook with its builder at the current pushed HEAD commit.
  2. Write kernel-metadata.json and the EXACT notebook into kaggle_kernels/<step>/. Committing both lets anyone
     reproduce the run with `kaggle kernels push -p kaggle_kernels/<step>`.
  3. Push once a GPU slot is free (the free tier allows 2 concurrent batch GPU sessions).
  4. When the run ends: download the outputs to the private folder, check that the run manifest says COMPLETED,
     copy ONLY the safe folder into results/, then git commit and push.
  5. A failed step stops its dependants, and the reason is logged. Steps are never retried blindly.
State and log live in pipeline_state/ (committed; step names, states and Kaggle messages only, never text), so any runner
can stop and resume.

Usage:
  python scripts/pipeline.py --once            one tick (what the scheduled GitHub Actions workflow runs; D027)
  python scripts/pipeline.py [--only a,b]      a local loop that polls every 90 s (never while the workflow is enabled)
With PIPELINE_SAFE_ONLY=1 (the cloud runner), a finished kernel's outputs are downloaded for its safe folder ONLY,
so private files (email text, generated text, rater keys) never leave Kaggle.
"""

from __future__ import annotations

import json
import os
import re
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
STATE_DIR = REPO / "pipeline_state"   # committed, so the cloud runner and a local runner share one state
SAFE_ONLY = os.environ.get("PIPELINE_SAFE_ONLY") == "1"
LOCK = PRIVATE / "pipeline.lock"   # local loop only: refreshed every poll; a second local runner exits while it is fresh
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
# Deviation 14: Phi run 1 stopped at the time guard (and lost tasks to an OOM-recovery bug); a continuation kernel keeps its
# outputs and redoes only the technically failed tasks. Downstream steps read Phi from the continuation, never from run 1.
PHI_CONT = f"{OWNER}/03-generation-phi-3-5-mini-cont"
GEN_SRC["phi-3.5-mini"] = PHI_CONT
GEN_STEP = {"qwen2.5-7b": "03-qwen2.5-7b", "phi-3.5-mini": "03-phi-3.5-mini-cont", "olmo-2-7b": "03-olmo-2-7b"}

STEPS = {
    "02": dict(builder=["build_02.py"], nb="02_Study1_Exploratory_Reproduction.ipynb", slug=f"{OWNER}/02-study1-exploratory-reproduction",
               deps=[], sources=[], safe="safe_02", results="results/02_study1"),
    **{f"03-{g}": dict(builder=["build_03.py", g], nb="03_Graded_AI_Assistance_Generation.ipynb", slug=GEN[g], deps=[],
                       sources=[K01], safe=f"safe_03/{g}", results=f"results/03_generation/{g}") for g in GEN},
    "05-classical": dict(builder=["build_05.py", "classical"], nb="05_Detector_Training_and_Sealed_Scoring.ipynb",
                         slug=f"{OWNER}/05-training-classical", deps=list(GEN_STEP.values()), sources=[K01, *GEN_SRC.values()], datasets=[QWEN_DS],
                         safe="safe_05/classical", results="results/05_training/classical"),
    **{f"05-{part}": dict(builder=["build_05.py", part], nb="05_Detector_Training_and_Sealed_Scoring.ipynb",
                          slug=f"{OWNER}/05-training-{part}", deps=list(GEN_STEP.values()), sources=[K01, *GEN_SRC.values()],
                          datasets=[QWEN_DS], safe=f"safe_05/{part}", results=f"results/05_training/{part}")
       for part in ("transformers-a", "transformers-b")},   # D019: two shards of the pre-registered transformer plan
    "04-kit": dict(builder=["build_04.py", "kit"], nb="04_Human_Validation.ipynb", slug=f"{OWNER}/04-human-validation-kit",
                   deps=["03-qwen2.5-7b", "03-phi-3.5-mini-cont"], sources=[K01, PHI_CONT], datasets=[QWEN_DS],
                   safe="safe_04/kit", results="results/04_human_validation/kit"),
    # 04-score waits until both raters' answers and the adjudication are committed (docs/HUMAN_VALIDATION_PROTOCOL.md)
    "04-score": dict(builder=["build_04.py", "score"], nb="04_Human_Validation.ipynb", slug=f"{OWNER}/04-human-validation-score",
                     deps=["04-kit"], sources=[f"{OWNER}/04-human-validation-kit"], safe="safe_04/score",
                     results="results/04_human_validation/score",
                     requires=[f"results/04_human_validation/ratings/{n}" for n in ("rater_A.csv", "rater_B.csv", "adjudication.csv")]),
    "06": dict(builder=["build_06.py"], nb="06_Zero_Shot_LLM_Judge.ipynb", slug=f"{OWNER}/06-zero-shot-llm-judge",
               deps=["03-qwen2.5-7b", "03-phi-3.5-mini-cont"], sources=[K01, PHI_CONT], datasets=[QWEN_DS],
               safe="safe_06", results="results/06_judge"),
    "08": dict(builder=["build_08.py"], nb="08_Paper_Tables_Figures_and_Reproducibility.ipynb",
               slug=f"{OWNER}/08-paper-tables-figures-reproducibility", deps=["07"], datasets=[QWEN_DS],
               sources=[K01, PHI_CONT, GEN["olmo-2-7b"]], safe="safe_08", results="results/08_paper", gpu=False),
    "07": dict(builder=["build_07.py"], nb="07_Confirmatory_Evaluation.ipynb", slug=f"{OWNER}/07-confirmatory-evaluation",
               deps=["05-classical", "05-transformers-a", "05-transformers-b", "06", "04-score"],   # §3.5 decisions first
               datasets=[QWEN_DS], sources=[K01, PHI_CONT, f"{OWNER}/05-training-classical",
                        f"{OWNER}/05-training-transformers-a", f"{OWNER}/05-training-transformers-b",
                        f"{OWNER}/06-zero-shot-llm-judge"],
               safe="safe_07", results="results/07_confirmatory"),
}
# CPU-only steps run in CPU sessions (same pinned image, no GPU quota, not counted against the 2 GPU slots; D018)
for _n in ("04-kit", "04-score", "05-classical", "07"):
    STEPS[_n]["gpu"] = False
# Deviation 15: pre-specified exploratory extensions E1 (EXT3, newer human email) and E2 (Qwen2.5-14B, scale)
K01B = f"{OWNER}/01b-extension-newer-human-email"
EXT_KERNELS = {"03-ext3-qwen2.5-7b": f"{OWNER}/03-ext3-generation-qwen2-5-7b", "03-ext3-phi-3.5-mini": f"{OWNER}/03-ext3-generation-phi-3-5-mini",
               "03-e2-qwen2.5-14b": f"{OWNER}/03-e2-generation-qwen2-5-14b"}
STEPS["01b-ext3"] = dict(builder=["build_01b.py"], nb="01b_Extension_Newer_Human_Email.ipynb", slug=K01B, deps=[], sources=[K01],
                         safe="safe_01b", results="results/01b_ext3", gpu=False)
for _g in ("qwen2.5-7b", "phi-3.5-mini"):
    STEPS[f"03-ext3-{_g}"] = dict(builder=["build_03.py", _g, "ext3"], nb="03_Graded_AI_Assistance_Generation.ipynb",
                                  slug=EXT_KERNELS[f"03-ext3-{_g}"], deps=["01b-ext3"], sources=[K01, K01B],
                                  safe=f"safe_03/{_g}__ext3", results=f"results/03_generation/{_g}__ext3")
STEPS["03-e2-qwen2.5-14b"] = dict(builder=["build_03.py", "qwen2.5-14b", "e2"], nb="03_Graded_AI_Assistance_Generation.ipynb",
                                  slug=EXT_KERNELS["03-e2-qwen2.5-14b"], deps=[], sources=[K01],
                                  safe="safe_03/qwen2.5-14b", results="results/03_generation/qwen2.5-14b")
EXT_SRC = [K01B, *EXT_KERNELS.values()]
for _n in ("05-classical", "05-transformers-a", "05-transformers-b", "06"):   # one sealed scoring run covers the extension cells
    STEPS[_n]["deps"] = STEPS[_n]["deps"] + ["01b-ext3", *EXT_KERNELS]
    STEPS[_n]["sources"] = STEPS[_n]["sources"] + EXT_SRC
STEPS["07"]["sources"] = STEPS["07"]["sources"] + EXT_SRC
STEPS["03-phi-3.5-mini-cont"] = dict(
    builder=["build_03.py", "phi-3.5-mini", "cont"], nb="03_Graded_AI_Assistance_Generation.ipynb", slug=PHI_CONT, deps=[],
    sources=[K01, GEN["phi-3.5-mini"]], safe="safe_03/phi-3.5-mini", results="results/03_generation/phi-3.5-mini")
ORDER = ["02", "03-qwen2.5-7b", "03-phi-3.5-mini", "03-phi-3.5-mini-cont", "03-olmo-2-7b",
         "01b-ext3", "03-ext3-qwen2.5-7b", "03-ext3-phi-3.5-mini", "03-e2-qwen2.5-14b", "04-kit", "06", "05-classical", "05-transformers-a", "05-transformers-b", "07",
         "04-score", "08"]


def sh(*args, cwd=REPO, check=True) -> str:
    out = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True)
    if check and out.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}\n{out.stdout}\n{out.stderr}")
    return (out.stdout + out.stderr).strip()


def log(msg: str) -> None:
    for local, label in ((str(PRIVATE), "<private>"), (str(REPO.parent), "<root>"), (str(Path.home()), "<home>")):
        msg = msg.replace(local, label)   # the log is committed to a public repository: no machine paths in it
    line = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}Z {msg}"
    print(line, flush=True)
    with (STATE_DIR / "pipeline.log").open("a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")


def load_state() -> dict:
    p = STATE_DIR / "state.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_state(st: dict) -> None:
    (STATE_DIR / "state.json").write_bytes((json.dumps(st, indent=2) + "\n").encode("utf-8"))


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
    kernel_metadata(kdir, s["slug"].split("/")[1], s["nb"], gpu=s.get("gpu", True), kernel_sources=s["sources"],
                    dataset_sources=s.get("datasets", []))
    sh(sys.executable, str(REPO / "scripts" / "notebook_builders" / s["builder"][0]), str(kdir / s["nb"]), commit, *s["builder"][1:])
    git_sync_commit([str(kdir.relative_to(REPO))], f"run({name}): exact notebook and kernel metadata pushed to Kaggle [skip ci]")
    return kdir


def collect(name: str) -> bool:
    s = STEPS[name]
    out = PRIVATE / f"{name}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    out.mkdir(parents=True, exist_ok=True)
    only_safe = ["--file-pattern", "^" + re.escape(s["safe"]) + "/"] if SAFE_ONLY else []
    sh(CLI, "kernels", "output", s["slug"], "-p", str(out), "-q", *only_safe, check=False)
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


def not_yet(step: dict) -> bool:
    """True while a step's optional "not_before" time (UTC, ISO 8601) lies in the future (for example a quota reset)."""
    nb = step.get("not_before")
    return bool(nb) and datetime.now(timezone.utc) < datetime.fromisoformat(nb)


def heartbeat() -> None:
    LOCK.write_text(f"{os.getpid()} {datetime.now(timezone.utc).isoformat()}", encoding="utf-8")


def commit_state() -> None:
    git_sync_commit([str(STATE_DIR.relative_to(REPO))], "pipeline: state and log [skip ci]")


def tick(st: dict, todo: list[str]) -> None:
    """One pass: collect every finished kernel, then push each step whose dependencies are done while a slot is free."""
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
        gpu_running = [m for m in running if STEPS[m].get("gpu", True)]
        if st[n]["state"] != "pending" or (STEPS[n].get("gpu", True) and len(gpu_running) >= MAX_SLOTS) or not_yet(st[n]):
            continue
        deps = STEPS[n]["deps"]
        if any(st.get(d, {}).get("state") == "failed" for d in deps):
            st[n]["state"] = "blocked"; log(f"{n}: blocked by a failed dependency"); save_state(st); continue
        if not all(st.get(d, {}).get("state") == "done" for d in deps):
            continue
        if not available(n):
            continue   # builder or required committed inputs (for example ratings) not there yet; the step waits
        if kstatus(STEPS[n]["slug"]) in ("RUNNING", "QUEUED"):
            if not st[n].get("adopt", True):
                continue   # an older, unwanted run is still active (for example awaiting cancellation): wait
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


def main(only: list[str] | None, once: bool = False) -> int:
    PRIVATE.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if once:
        # the scheduled cloud runner: do nothing at all unless Kaggle answers for a known, finished kernel
        if not os.environ.get("KAGGLE_API_TOKEN") and not (Path.home() / ".kaggle").is_dir():
            print("no Kaggle credentials (repository secret KAGGLE_API_TOKEN is not set): runner inactive, nothing changed")
            return 0
        if kstatus(K01) != "COMPLETE":
            print("Kaggle API not reachable or not authenticated: nothing changed")
            return 1
        sh("git", "pull", "--rebase", "--autostash", "-q", "origin", "main")
    else:
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
        tick(st, todo)
        commit_state()
        if once:
            return 0
        if all(st[n]["state"] in ("done", "failed", "blocked") for n in todo):
            break
        if not any(st[n]["state"] == "running" for n in todo) and not any(
                st[n]["state"] == "pending" and all(st.get(d, {}).get("state") == "done" for d in STEPS[n]["deps"])
                and available(n) for n in todo) and not any(
                st[n]["state"] == "pending" and not_yet(st[n]) for n in todo):
            log("nothing runnable: waiting for builders or dependencies"); break
        heartbeat()
        time.sleep(POLL)
    log("pipeline stop: " + json.dumps({n: st[n]["state"] for n in todo}))
    commit_state()
    LOCK.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    once = "--once" in sys.argv
    try:
        sys.exit(main(only, once))
    except Exception:   # record the reason (committed, so the cloud runner's crash is visible too), release the lock
        import traceback
        log("CRASH: " + " | ".join(traceback.format_exc().splitlines())[-1500:])
        try:
            commit_state()
        except Exception:
            pass
        LOCK.unlink(missing_ok=True)
        sys.exit(2)
