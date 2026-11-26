"""Human validation of the generated emails (pre-registration §3.5, deviation 9).

A blinded sample of L3 rewrites (RW) and L4 compositions (DN) is drawn from the test generators. Each rater
answers fixed questions in their own copy of a workbook. This module covers four jobs:
  - draw the sample;
  - build the blinded items and the private key;
  - read the answers back WITHOUT any email text;
  - compute agreement (Cohen's kappa) and preservation rates (Wilson CIs).
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict

import numpy as np

from .freeze import seeded_order
from .stats import wilson_ci

LABEL_NAME = {0: "legitimate", 1: "phishing"}

QUESTIONS = {
    "RW": {
        "intent_preserved": ("yes", "no"),
        "security_element_changed": ("no", "added", "removed", "added_and_removed"),
        "rewrite_label": ("phishing", "legitimate", "unsure"),
    },
    "DN": {
        "plausible_legitimate": ("yes", "no"),
    },
}
ANSWER_COLUMNS = [q for task in QUESTIONS.values() for q in task]

QUESTION_TEXT = {
    "intent_preserved": "(a) Does the rewrite keep the intent of the original: the same purpose and the same requests of the reader?",
    "security_element_changed": "(b) Compared with the original, did the rewrite ADD or REMOVE any security-relevant element: "
                                "a request (credentials, payment, an action), a link, an attachment, or a deadline?",
    "rewrite_label": "(c) Judging the REWRITE on its own, is it a phishing email or a legitimate email? Use 'unsure' only if "
                     "you genuinely cannot decide.",
    "plausible_legitimate": "Would this email pass as a plausible, ordinary legitimate email?",
}

INSTRUCTIONS = [
    "Human validation of AI-assisted emails (protocol: docs/PREREGISTRATION_V2.md §3.5 and deviation 9)",
    "",
    "Work ALONE. Do not discuss items with the other rater until both workbooks are complete.",
    "Do not open the private key file (key.csv). It reveals which model wrote each item.",
    "Links are defanged ('hxxp'). Do not visit any link, and do not copy any text out of this workbook.",
    "",
    "Sheet RW: each row shows an ORIGINAL email and an AI REWRITE of it. Answer three questions:",
    "  " + QUESTION_TEXT["intent_preserved"] + "  Answers: yes / no",
    "  " + QUESTION_TEXT["security_element_changed"] + "  Answers: no / added / removed / added_and_removed",
    "  " + QUESTION_TEXT["rewrite_label"] + "  Answers: phishing / legitimate / unsure",
    "Sheet DN: each row shows ONE email that an AI composed from a subject line. Answer one question:",
    "  " + QUESTION_TEXT["plausible_legitimate"] + "  Answers: yes / no",
    "",
    "Use the drop-down lists. Every answer cell must be filled. The 'comment' column is optional and is never published;",
    "do not paste email text into it.",
    "Placeholders, unusual names and formatting are NOT reasons by themselves to call an email phishing.",
    "Phishing means: the email tries to deceive the reader into revealing information, paying, or taking a harmful action.",
]


def _seed(*parts) -> int:
    """A stable 32-bit seed derived from labelled parts (independent of Python's hash randomisation)."""
    return int(hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()[:8], 16)


_HTTP = re.compile(r"(?i)\bhttp(s?)://")
_WWW = re.compile(r"(?i)\bwww\.")


def defang(text: str) -> str:
    """Make links non-clickable for raters (http -> hxxp, www. -> www[.]). Applied to every item alike."""
    return _WWW.sub("www[.]", _HTTP.sub(lambda m: "hxxp" + m.group(1) + "://", text or ""))


def source_of(rec: dict) -> str:
    return rec["cell"].split("-")[0]


def draw_sample(generated: list[dict], generators: list[str], sources=("EXT", "IN"), rw_per_stratum: int = 50,
                dn_per_stratum: int = 25, seed: int = 2026) -> tuple[list[dict], list[dict], list[dict]]:
    """Stratified, seeded draw.

    RW strata: generator x source x label, using L3 outputs. Within a source and label, the generators get
    disjoint parents where possible, so no rater sees the same original twice in one stratum pair.
    DN strata: generator x source, using L4 outputs (legitimate only).
    Returns (rw_rows, dn_rows, report).
    """
    by = defaultdict(list)
    for r in generated:
        if r["generator"] in generators:
            by[(r["generator"], source_of(r), int(r["label"]), r["level"])].append(r)
    rw, dn, report = [], [], []
    for src in sources:
        for label in (0, 1):
            used: set[str] = set()
            for g in generators:
                pool = seeded_order(by[(g, src, label, "L3")], _seed(seed, "RW", g, src, label))
                pick = [r for r in pool if r["native_id"] not in used][:rw_per_stratum]
                reuse = 0
                if len(pick) < rw_per_stratum:   # fall back to parents already used by another generator, and report it
                    taken = {r["sample_id"] for r in pick}
                    extra = [r for r in pool if r["sample_id"] not in taken][: rw_per_stratum - len(pick)]
                    reuse, pick = len(extra), pick + extra
                used.update(r["native_id"] for r in pick)
                rw += pick
                report.append({"task": "RW", "generator": g, "source": src, "label": label, "available": len(pool),
                               "target": rw_per_stratum, "drawn": len(pick), "parent_reuse": reuse})
        for g in generators:
            pool = seeded_order(by[(g, src, 0, "L4")], _seed(seed, "DN", g, src))
            pick = pool[:dn_per_stratum]
            dn += pick
            report.append({"task": "DN", "generator": g, "source": src, "label": 0, "available": len(pool),
                           "target": dn_per_stratum, "drawn": len(pick), "parent_reuse": 0})
    return rw, dn, report


def make_items(rw: list[dict], dn: list[dict], parents: dict[str, dict], seed: int = 2026) -> tuple[list[dict], list[dict]]:
    """Blind the sample: opaque item IDs in a seeded order. Returns (items with text, key without text)."""
    items, key = [], []
    for task, rows in (("RW", rw), ("DN", dn)):
        for i, r in enumerate(seeded_order(rows, _seed(seed, task, "items")), 1):
            iid = f"{task}-{i:03d}"
            item = {"item_id": iid, "task": task, "subject": defang(r["subject"]), "body": defang(r["body"])}
            if task == "RW":
                p = parents[r["native_id"]]
                item.update(original_subject=defang(p["subject"]), original_body=defang(p["body"]))
            items.append(item)
            key.append({"item_id": iid, "task": task, "sample_id": r["sample_id"], "parent_id": r["native_id"],
                        "generator": r["generator"], "source": source_of(r), "label": int(r["label"]),
                        "level": r["level"], "cell": r["cell"]})
    return items, key


def rater_order(items: list[dict], rater: str, seed: int = 2026) -> list[dict]:
    """Each rater gets their own seeded order within each task (item IDs stay the same)."""
    out = []
    for task in QUESTIONS:
        rows = sorted((x for x in items if x["task"] == task), key=lambda x: x["item_id"])
        perm = np.random.default_rng(_seed(seed, "rater", rater, task)).permutation(len(rows))
        out += [rows[i] for i in perm]
    return out


def items_digest(items: list[dict]) -> str:
    """SHA-256 of the canonical item content (stable across runs, unlike workbook bytes)."""
    blob = json.dumps(sorted(items, key=lambda x: x["item_id"]), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def write_workbook(path, items: list[dict], rater: str) -> None:
    """One rater's workbook: Instructions, RW and DN sheets, with drop-down validation on every answer cell."""
    from datetime import datetime

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    wb.properties.creator = "phishbench"
    wb.properties.created = wb.properties.modified = datetime(2026, 1, 1)
    ws = wb.active
    ws.title = "Instructions"
    ws.append([f"Rater {rater}"])
    for line in INSTRUCTIONS:
        ws.append([line])
    ws["A1"].font = Font(bold=True)
    ws.column_dimensions["A"].width = 160
    layout = {
        "RW": (["item_id", "original_subject", "original_body", "rewrite_subject", "rewrite_body", *QUESTIONS["RW"], "comment"],
               lambda x: [x["item_id"], x["original_subject"], x["original_body"], x["subject"], x["body"]],
               [10, 28, 70, 28, 70, 16, 22, 16, 30]),
        "DN": (["item_id", "subject", "body", *QUESTIONS["DN"], "comment"],
               lambda x: [x["item_id"], x["subject"], x["body"]], [10, 34, 100, 18, 30]),
    }
    for task, (cols, row_of, widths) in layout.items():
        sh = wb.create_sheet(task)
        sh.append(cols)
        for c in sh[1]:
            c.font = Font(bold=True)
        rows = [x for x in items if x["task"] == task]
        for x in rows:
            sh.append(row_of(x) + [None] * (len(cols) - len(row_of(x))))
        for i, w in enumerate(widths):
            sh.column_dimensions[chr(65 + i)].width = w
        for r in sh.iter_rows(min_row=2):
            for c in r:
                c.alignment = Alignment(wrap_text=True, vertical="top")
        sh.freeze_panes = "B2"
        for q, allowed in QUESTIONS[task].items():
            col = chr(65 + cols.index(q))
            dv = DataValidation(type="list", formula1='"' + ",".join(allowed) + '"', allow_blank=True,
                                showErrorMessage=True, errorTitle="Invalid answer", error="Choose one value from the list.")
            sh.add_data_validation(dv)
            if rows:
                dv.add(f"{col}2:{col}{len(rows) + 1}")
    wb.save(path)


def workbook_item_ids(path) -> list[str]:
    """Item IDs present in a workbook (any answer state); used to check a freshly written workbook."""
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True)
    ids = [str(row[0]) for task in QUESTIONS for row in wb[task].iter_rows(min_row=2, max_col=1, values_only=True) if row[0]]
    wb.close()
    return ids


def read_workbook(path) -> list[dict]:
    """Read ONLY item IDs and answers (never text) from a completed workbook, and validate every answer."""
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    out, problems = [], []
    for task, qs in QUESTIONS.items():
        rows = wb[task].iter_rows(values_only=True)
        header = [str(h).strip() if h is not None else "" for h in next(rows)]
        idx = {h: i for i, h in enumerate(header)}
        for row in rows:
            if row is None or row[idx["item_id"]] in (None, ""):
                continue
            rec = {"item_id": str(row[idx["item_id"]]).strip(), "task": task}
            for q, allowed in qs.items():
                v = row[idx[q]]
                v = "" if v is None else str(v).strip().lower()
                if v not in allowed:
                    problems.append(f"{rec['item_id']}: {q}={v!r}")
                rec[q] = v
            out.append(rec)
    wb.close()
    if problems:
        raise ValueError(f"{len(problems)} missing or invalid answers, for example: " + "; ".join(problems[:10]))
    return out


def disagreements(ratings_a: list[dict], ratings_b: list[dict]) -> list[dict]:
    """Rows needing adjudication: one row per item and question where the two raters differ."""
    a = {r["item_id"]: r for r in ratings_a}
    b = {r["item_id"]: r for r in ratings_b}
    if set(a) != set(b):
        raise ValueError(f"Raters cover different items: {sorted(set(a) ^ set(b))[:10]}")
    out = []
    for iid in sorted(a):
        for q in QUESTIONS[a[iid]["task"]]:
            if a[iid][q] != b[iid][q]:
                out.append({"item_id": iid, "question": q, "rater_A": a[iid][q], "rater_B": b[iid][q], "resolved": "", "note": ""})
    return out


def cohen_kappa(a, b, categories=None) -> float:
    """Cohen's kappa for two raters. NaN when chance agreement is 1 (both raters used one single category)."""
    a, b = list(a), list(b)
    n = len(a)
    if n == 0 or n != len(b):
        raise ValueError("kappa needs two equal-length, non-empty rating lists")
    cats = list(categories) if categories else sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[c] * cb[c] for c in cats) / (n * n)
    return float("nan") if pe >= 1.0 else (po - pe) / (1 - pe)


def gwet_ac1(a, b, categories) -> float:
    """Gwet's AC1 (supplementary to kappa; robust to the high-prevalence 'kappa paradox')."""
    a, b = list(a), list(b)
    n, cats = len(a), list(categories)
    if n == 0 or n != len(b) or len(cats) < 2:
        raise ValueError("AC1 needs two equal-length, non-empty rating lists and at least two categories")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(((ca[c] + cb[c]) / (2 * n)) * (1 - (ca[c] + cb[c]) / (2 * n)) for c in cats) / (len(cats) - 1)
    return (po - pe) / (1 - pe)


def kappa_bootstrap_ci(a, b, categories=None, iterations: int = 2000, seed: int = 2026) -> tuple[float, float]:
    """Percentile 95% CI for kappa from an item bootstrap (NaN draws are dropped)."""
    a, b = np.asarray(a, dtype=object), np.asarray(b, dtype=object)
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(iterations):
        i = rng.integers(0, len(a), len(a))
        k = cohen_kappa(a[i], b[i], categories)
        if not np.isnan(k):
            draws.append(k)
    if not draws:
        return (float("nan"), float("nan"))
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return (float(lo), float(hi))


def final_answers(ratings_a: list[dict], ratings_b: list[dict], adjudication: list[dict]) -> dict[str, dict]:
    """Final answer per item and question: the shared answer, or the adjudicated one. Every disagreement must be resolved."""
    a = {r["item_id"]: r for r in ratings_a}
    b = {r["item_id"]: r for r in ratings_b}
    res = {(r["item_id"], r["question"]): str(r.get("resolved", "")).strip().lower() for r in adjudication}
    out, missing = {}, []
    for iid in sorted(a):
        task = a[iid]["task"]
        out[iid] = {"task": task}
        for q, allowed in QUESTIONS[task].items():
            if a[iid][q] == b[iid][q]:
                out[iid][q] = a[iid][q]
            elif res.get((iid, q), "") in allowed:
                out[iid][q] = res[(iid, q)]
            else:
                missing.append(f"{iid}:{q}")
    if missing:
        raise ValueError(f"{len(missing)} disagreements have no valid resolution, for example: {missing[:10]}")
    return out


def _rate(k: int, n: int) -> dict:
    lo, hi = wilson_ci(k, n)
    return {"n": n, "k": k, "rate": round(k / n, 4) if n else None, "ci95_low": round(lo, 4), "ci95_high": round(hi, 4)}


def summarize(key: list[dict], ratings_a: list[dict], ratings_b: list[dict], adjudication: list[dict],
              preservation_min: float = 0.90, kappa_target: float = 0.60, iterations: int = 2000, seed: int = 2026) -> dict:
    """Every §3.5 statistic.

    The statistics are:
      - agreement: raw agreement and kappa with a bootstrap CI, from independent ratings;
      - label preservation per generator: Wilson CI from the final answers, where 'unsure' counts as NOT preserved;
      - the §3.5 decision rule;
      - intent, security-element and DN plausibility rates.
    """
    meta = {k["item_id"]: k for k in key}
    a = {r["item_id"]: r for r in ratings_a}
    b = {r["item_id"]: r for r in ratings_b}
    if set(a) != set(meta) or set(b) != set(meta):
        raise ValueError("ratings do not cover exactly the items in the key")
    final = final_answers(ratings_a, ratings_b, adjudication)

    agreement = []
    for task, qs in QUESTIONS.items():
        for q, cats in qs.items():
            groups = {"all": [i for i in sorted(meta) if meta[i]["task"] == task]}
            if q == "rewrite_label":
                for lab in (0, 1):
                    groups[f"original_{LABEL_NAME[lab]}"] = [i for i in groups["all"] if meta[i]["label"] == lab]
            for gname, ids in groups.items():
                xa, xb = [a[i][q] for i in ids], [b[i][q] for i in ids]
                k = cohen_kappa(xa, xb, cats)
                lo, hi = kappa_bootstrap_ci(xa, xb, cats, iterations, _seed(seed, "kappa", q, gname))
                agreement.append({"task": task, "question": q, "subset": gname, "n": len(ids),
                                  "raw_agreement": round(sum(x == y for x, y in zip(xa, xb)) / len(ids), 4),
                                  "kappa": None if np.isnan(k) else round(k, 4),
                                  "kappa_ci95_low": None if np.isnan(lo) else round(lo, 4),
                                  "kappa_ci95_high": None if np.isnan(hi) else round(hi, 4),
                                  "gwet_ac1": round(gwet_ac1(xa, xb, cats), 4)})

    rates, decisions = [], {}
    gens = sorted({m["generator"] for m in meta.values()})
    for g in gens:
        rw = [i for i in sorted(meta) if meta[i]["task"] == "RW" and meta[i]["generator"] == g]
        for subset, ids in [("all", rw)] + [(f"original_{LABEL_NAME[lab]}", [i for i in rw if meta[i]["label"] == lab]) for lab in (0, 1)] \
                + [(f"source_{s}", [i for i in rw if meta[i]["source"] == s]) for s in sorted({meta[i]["source"] for i in rw})]:
            kept = sum(final[i]["rewrite_label"] == LABEL_NAME[meta[i]["label"]] for i in ids)
            unsure = sum(final[i]["rewrite_label"] == "unsure" for i in ids)
            rates.append({"generator": g, "measure": "label_preserved", "subset": subset, **_rate(kept, len(ids)), "unsure": unsure})
            rates.append({"generator": g, "measure": "intent_preserved", "subset": subset,
                          **_rate(sum(final[i]["intent_preserved"] == "yes" for i in ids), len(ids)), "unsure": None})
            rates.append({"generator": g, "measure": "security_element_changed", "subset": subset,
                          **_rate(sum(final[i]["security_element_changed"] != "no" for i in ids), len(ids)), "unsure": None})
        dn = [i for i in sorted(meta) if meta[i]["task"] == "DN" and meta[i]["generator"] == g]
        rates.append({"generator": g, "measure": "dn_plausible_legitimate", "subset": "all",
                      **_rate(sum(final[i]["plausible_legitimate"] == "yes" for i in dn), len(dn)), "unsure": None})
        lp = next(r for r in rates if r["generator"] == g and r["measure"] == "label_preserved" and r["subset"] == "all")
        decisions[g] = {"label_preservation": lp["rate"], "ci95": [lp["ci95_low"], lp["ci95_high"]],
                        "rw_results_role": "primary" if lp["rate"] is not None and lp["rate"] >= preservation_min else "sensitivity_only"}

    k_c = next(r for r in agreement if r["question"] == "rewrite_label" and r["subset"] == "all")
    items = [{**{k: meta[i][k] for k in ("item_id", "task", "sample_id", "parent_id", "generator", "source", "label", "level", "cell")},
              **{f"A_{q}": a[i][q] for q in QUESTIONS[meta[i]["task"]]},
              **{f"B_{q}": b[i][q] for q in QUESTIONS[meta[i]["task"]]},
              **{f"final_{q}": final[i][q] for q in QUESTIONS[meta[i]["task"]]}} for i in sorted(meta)]
    return {"agreement": agreement, "rates": rates, "decisions": decisions, "items": items,
            "kappa_rewrite_label": k_c["kappa"], "kappa_target": kappa_target,
            "kappa_target_met": k_c["kappa"] is not None and k_c["kappa"] >= kappa_target,
            "n_disagreements": sum(1 for i in meta for q in QUESTIONS[meta[i]["task"]] if a[i][q] != b[i][q]),
            "preservation_min": preservation_min}
