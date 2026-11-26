"""Loaders that turn every Study 2 source into one record schema.

Record fields: sample_id, source, native_id, parent_id, subject, body, label (0 legitimate,
1 phishing, None excluded), authorship ('human', 'ai' or 'unknown'), generator, level, year.
Sample IDs are pseudonymous but derivable from the public source (row index or message index).
"""

from __future__ import annotations

import csv
import json
import mailbox
import re
from email.header import decode_header, make_header
from pathlib import Path

from .textnorm import html_to_text, split_subject

csv.field_size_limit(2 ** 31 - 1)

MAIL_SYSTEM_RE = re.compile(
    r"(FOLDER INTERNAL DATA|Mail delivery failed|Undeliverable|Undelivered Mail|"
    r"Delivery Status Notification|Returned mail|Mail System Error)", re.IGNORECASE)

FOIA_LINE_RE = re.compile(
    r"^.*(UNCLASSIFIED|U\.S\. Department of State|Case No\.|Doc No\.|RELEASE IN (FULL|PART)|"
    r"SUBJECT TO AGREEMENT ON SENSITIVE INFORMATION|PRODUCED TO HOUSE SELECT|STATE DEPT\.).*$",
    re.IGNORECASE | re.MULTILINE)


def record(sample_id, source, native_id, subject, body, label, authorship, *, parent_id=None,
           generator=None, level="L0", year=None) -> dict:
    return {"sample_id": sample_id, "source": source, "native_id": str(native_id),
            "parent_id": parent_id or sample_id, "subject": subject or "", "body": body or "",
            "label": label, "authorship": authorship, "generator": generator, "level": level, "year": year}


def _int_label(x):
    try:
        return int(float(str(x).strip()))
    except (TypeError, ValueError):
        return None


def load_d1_csv(path: Path, source: str, keep_label: int) -> list[dict]:
    """D1 curated CSV. Keeps only rows whose label equals keep_label (0 means ham, i.e. legitimate).

    Label 1 in the spam/ham corpora (Enron, SpamAssassin, CEAS) is spam, which never maps to
    phishing (decision D001). Callers therefore pass keep_label=0 for those files.
    """
    out = []
    with Path(path).open(encoding="utf-8", errors="replace", newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if _int_label(row.get("label")) != keep_label:
                continue
            lab = 0 if keep_label == 0 else 1
            out.append(record(f"{source}:{i}", source, i, row.get("subject"), row.get("body"), lab, "human"))
    return out


def _hdr(v) -> str:
    try:
        return str(make_header(decode_header(v or "")))
    except Exception:
        return str(v or "")


def _payload_text(part) -> str:
    payload = part.get_payload(decode=True)
    if payload is None:
        return ""
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except LookupError:
        return payload.decode("utf-8", errors="replace")


def message_body(msg) -> str:
    plain, htmls = [], []
    for part in (msg.walk() if msg.is_multipart() else [msg]):
        if part.is_multipart():
            continue
        if "attachment" in (part.get("Content-Disposition") or "").lower():
            continue
        ctype = part.get_content_type()
        if ctype == "text/plain":
            plain.append(_payload_text(part))
        elif ctype == "text/html":
            htmls.append(_payload_text(part))
    if any(p.strip() for p in plain):
        return "\n".join(plain).strip()
    if htmls:
        return html_to_text("\n".join(htmls))
    return ""


def load_nazario_mbox(path: Path, year: int) -> tuple[list[dict], int]:
    """Nazario yearly mbox (phishing). Returns (records, number_of_mail_system_notices_removed)."""
    out, removed = [], 0
    box = mailbox.mbox(str(path), create=False)
    try:
        for i, msg in enumerate(box):
            subject = _hdr(msg.get("Subject"))
            if MAIL_SYSTEM_RE.search(subject or ""):
                removed += 1
                continue
            body = message_body(msg)
            authorship = "human" if year <= 2022 else "unknown"
            out.append(record(f"nazario{year}:{i}", f"nazario{year}", i, subject, body, 1, authorship, year=year))
    finally:
        box.close()
    return out, removed


def load_llmgen(path: Path) -> list[dict]:
    out = []
    with Path(path).open(encoding="utf-8-sig", errors="replace", newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            text = row.get("content") or row.get("﻿content") or ""
            lab = _int_label(row.get("label"))
            if lab not in (0, 1):
                continue
            s, b = split_subject(text)
            out.append(record(f"llmgen:{i}", "llmgen", i, s, b, lab, "ai", generator="openai(card)"))
    return out


def greco_rows(path: Path) -> list[str]:
    """Rows of a Greco24 file: one physical line per email, with the last comma-separated field as the label.

    legit.csv is quoted CSV, but phishing.csv is *unquoted* even though its text contains commas,
    so a standard CSV reader splits that text into many fields (deviation 4). Each file has
    exactly one email per line, so we take everything before the last comma as the text. Its
    'label' column is the authorship label (1 = LLM), not the phishing label; the phishing label
    comes from the file name.
    """
    lines = Path(path).read_bytes().decode("utf-8", errors="replace").splitlines()
    if not lines or not lines[0].strip().lower().startswith("text"):
        raise ValueError(f"Unexpected Greco24 header in {path}")
    texts = []
    for line in lines[1:]:
        if not line.strip():
            continue
        text, _, lab = line.rpartition(",")
        if lab.strip() not in ("0", "1"):
            raise ValueError(f"Unexpected Greco24 label field in {path}: {lab[:20]!r}")
        text = text.strip()
        if len(text) >= 2 and text[0] == text[-1] == '"':
            text = text[1:-1].replace('""', '"')
        texts.append(text)
    return texts


def load_greco_llm(folder: Path) -> list[dict]:
    """Greco et al. 2024 (Kaggle, CC-BY-NC-SA-4.0): only the llm-generated legit and phishing files."""
    out = []
    for fname, lab in (("legit.csv", 0), ("phishing.csv", 1)):
        matches = sorted(Path(folder).rglob(f"llm-generated/{fname}"))
        if not matches:
            raise FileNotFoundError(f"Greco llm-generated/{fname} not found under {folder}")
        for i, text in enumerate(greco_rows(matches[0])):
            s, b = split_subject(text)
            out.append(record(f"greco24_{'legit' if lab == 0 else 'phish'}:{i}", "greco24", i, s, b, lab,
                              "ai", generator="greco24(paper)"))
    return out


def clean_foia(body: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", FOIA_LINE_RE.sub("", body or "")).strip()


def load_clinton(path: Path) -> list[dict]:
    out = []
    with Path(path).open(encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            sid = row.get("Id")
            subject = row.get("ExtractedSubject") or row.get("MetadataSubject") or ""
            body = clean_foia(row.get("ExtractedBodyText") or "")
            out.append(record(f"clinton:{sid}", "clinton", sid, subject, body, 0, "human"))
    return out


def load_ephish(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as f:
        data = json.load(f)
    out = []
    for i, r in enumerate(data):
        if str(r.get("Language", "")).strip().lower() != "en":
            continue
        lab = _int_label(r.get("type"))
        out.append(record(f"ephish:{i}", "ephish", i, r.get("Subject"), r.get("Body"), lab, "ai",
                          generator="ephishgen(paper)"))
    return out
