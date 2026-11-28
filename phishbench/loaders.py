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


# ---- EXT3 (deviation 15): public Apache Software Foundation mailing lists, thread starters, 2019-01 to 2022-10 ----
APACHE_AUTO_SENDER_RE = re.compile(r"(\bjira\b|\bgit(hub)?\b|\bbot\b|notification|no-?reply|jenkins|buildbot|\bcommits\b)", re.IGNORECASE)
APACHE_AUTO_SUBJECT_RE = re.compile(r"^\s*\[(jira|github|ci|vote|result)\]", re.IGNORECASE)
APACHE_PATCH_RE = re.compile(r"(^diff --git |^--- a/|^\+\+\+ b/|^@@ -\d)", re.MULTILINE)
APACHE_CODE_LINE_RE = re.compile(r"(^\s+at [\w$.]+\(|^\s*[{}]\s*$|;\s*$|^\s*(def|class|import|public|private|return)\s|"
                                 r"^\s*[\w.\[\]]+\s*=\s*[\w\"'(\[]|^\s*\$ |^>>> |^\s*<[/\w][^>]*>\s*$)")
APACHE_FOOTER_RE = re.compile(r"\n-{20,}\s*\n\s*To unsubscribe.*\Z", re.IGNORECASE | re.DOTALL)
APACHE_FOOTER_LINE_RE = re.compile(r"^(To unsubscribe, e-mail:|For additional commands, e-mail:).*$", re.IGNORECASE | re.MULTILINE)


def apache_body_reason(body: str) -> str | None:
    """None when the body is ordinary human prose; otherwise the exclusion reason (deviation 15)."""
    if APACHE_PATCH_RE.search(body):
        return "patch_or_diff"
    lines = [ln for ln in body.splitlines() if ln.strip()]
    if lines and sum(bool(APACHE_CODE_LINE_RE.search(ln)) for ln in lines) / len(lines) > 0.30:
        return "code_or_trace"
    return None


def strip_list_footer(body: str) -> str:
    """Remove the footer the list software appends (not written by the sender), so every EXT3 email does not share it."""
    body = APACHE_FOOTER_RE.sub("", body or "")
    return APACHE_FOOTER_LINE_RE.sub("", body).strip()


def load_apache_mbox(path: Path, list_name: str, start: str = "2019-01", end: str = "2022-10") -> tuple[list[dict], dict]:
    """Thread-starting human messages from one month of one public Apache list. Returns (records, exclusion counts).

    Sample IDs are EXT3: plus SHA-1(Message-ID)[:16], so no address appears in an identifier.
    """
    import hashlib
    from collections import Counter
    from email.utils import parsedate_to_datetime

    out, why = [], Counter()
    box = mailbox.mbox(str(path), create=False)
    try:
        for msg in box:
            mid = (msg.get("Message-ID") or "").strip()
            if not mid:
                why["no_message_id"] += 1; continue
            try:
                dt = parsedate_to_datetime(msg.get("Date"))
                ym = f"{dt.year:04d}-{dt.month:02d}"
            except Exception:
                why["no_date"] += 1; continue
            if not (start <= ym <= end):
                why["outside_window"] += 1; continue
            if msg.get("In-Reply-To") or msg.get("References"):
                why["reply"] += 1; continue
            sender, subject = _hdr(msg.get("From")), _hdr(msg.get("Subject"))
            if APACHE_AUTO_SENDER_RE.search(sender or ""):
                why["automated_sender"] += 1; continue
            if APACHE_AUTO_SUBJECT_RE.search(subject or ""):
                why["automated_or_vote_subject"] += 1; continue
            body = strip_list_footer(message_body(msg))
            if not body:
                why["no_body"] += 1; continue
            r = apache_body_reason(body)
            if r:
                why[r] += 1; continue
            sid = "EXT3:" + hashlib.sha1(mid.encode("utf-8", "replace")).hexdigest()[:16]
            rec = record(sid, "apache", sid.split(":", 1)[1], subject, body, 0, "human", year=dt.year)
            rec.update(cell="EXT3-legit-L0", list=list_name, month=ym)
            out.append(rec)
            why["candidate"] += 1
    finally:
        box.close()
    return out, dict(why)
