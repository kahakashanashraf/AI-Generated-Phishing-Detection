# Phi-3.5-mini, run 1 (partial; superseded by the continuation)

Kernel `ddipra/03-generation-phi-3-5-mini`, version 2, float16. The 10.5-hour time guard stopped the run (`PARTIAL_TIME_LIMIT`).

| What | Count |
|---|---|
| Tasks requested | 4,845 |
| Kept after §3.4 | 2,915 |
| Not run (time guard) | 766 |
| Lost to an out-of-memory recovery bug | 374 |

The 766 + 374 = 1,140 lost tasks are technical failures, never §3.4 quality exclusions. The continuation kernel
`03-generation-phi-3-5-mini-cont` (deviation 14) keeps every record and §3.4 exclusion from this run and generates only those
1,140 tasks. The final Phi outputs are in `../phi-3.5-mini/`. These files are kept for transparency only.
