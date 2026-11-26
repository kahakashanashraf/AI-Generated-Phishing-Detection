"""Push a suite notebook to Kaggle, wait for it, download its outputs privately and report its status.

Usage:
  python scripts/kaggle_run.py push  <kernel_dir> <notebook.ipynb>
  python scripts/kaggle_run.py wait  <owner/slug> <private_out_dir> [--poll 60]
  python scripts/kaggle_run.py collect <private_out_dir> <safe_subdir> <repo_results_dir>

'collect' copies ONLY the safe (aggregate, text-free) folder into the repository. Private folders are never copied.
Set KAGGLE_CLI to the kaggle executable if it is not on PATH.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CLI = os.environ.get("KAGGLE_CLI", "kaggle")


def run(*args: str) -> str:
    out = subprocess.run([CLI, *args], capture_output=True, text=True)
    return (out.stdout + out.stderr).strip()


def push(kernel_dir: str, notebook: str) -> None:
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(Path(kernel_dir) / "kernel-metadata.json", d)
        shutil.copy(notebook, d)
        print(run("kernels", "push", "-p", d))


def wait(slug: str, out_dir: str, poll: int = 60) -> int:
    t0 = time.time()
    while True:
        s = run("kernels", "status", slug)
        if any(k in s for k in ("COMPLETE", "ERROR", "CANCEL")):
            break
        time.sleep(poll)
    print(f"{s}  (waited {round((time.time() - t0) / 60, 1)} min)")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    run("kernels", "output", slug, "-p", str(out))
    for m in sorted(out.rglob("run_manifest.json")):
        try:
            j = json.loads(m.read_text(encoding="utf-8"))
            print(f"[{m.relative_to(out)}] status={j.get('status')} gates={j.get('gates')}")
        except Exception as e:  # report, never hide
            print(f"[{m}] unreadable: {e}")
    logs = sorted(out.glob("*.log"))
    if logs:
        try:
            text = "".join(x.get("data", "") for x in json.loads(logs[0].read_text(encoding="utf-8")))
        except Exception:
            text = logs[0].read_text(encoding="utf-8", errors="replace")
        print("---- log tail ----\n" + text[-3000:])
    return 0 if "COMPLETE" in s else 1


def collect(out_dir: str, safe_subdir: str, repo_results_dir: str) -> None:
    src = Path(out_dir) / safe_subdir
    if not src.is_dir():
        raise SystemExit(f"No safe folder at {src}")
    dst = Path(repo_results_dir)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"copied {sum(1 for p in dst.rglob('*') if p.is_file())} safe files -> {dst}")


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    if cmd == "push":
        push(*rest)
    elif cmd == "wait":
        poll = int(rest[rest.index("--poll") + 1]) if "--poll" in rest else 60
        sys.exit(wait(rest[0], rest[1], poll))
    elif cmd == "collect":
        collect(*rest)
    else:
        raise SystemExit(__doc__)
