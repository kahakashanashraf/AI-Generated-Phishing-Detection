# Environment evidence

`cpu_session_image_probe.json` is the output of a one-off private Kaggle kernel, `zz-cpu-image-probe`, run on 2026-11-27. It ran in a CPU
session with the pinned image. It shows the same image digest (`fc720c15…`), the same package versions and no CUDA, which supports
D018: CPU-only steps run in CPU sessions with the same image. The probe kernel itself was deleted on 2026-11-28 (D022), after this
output had been committed.

`package_probe_bitsandbytes.json` is the output of a one-off private kernel, `zz-bnb-probe`, run on 2026-11-28 in a CPU session with the
pinned image. It shows that bitsandbytes is **not** included, while accelerate 1.15.0 and transformers 5.20.2 are. For that reason the E2
kernel installs `bitsandbytes==0.50.2` (D025). The probe kernel was deleted after this output had been committed.
