"""Text normalisation, keys, simple filters and placeholder locking (pre-registration §3)."""

from __future__ import annotations

import hashlib
import html
import re
from html.parser import HTMLParser

_WS = re.compile(r"\s+")
_WORD = re.compile(r"\b\w+\b", re.UNICODE)

URL_RE = re.compile(r"""(?:https?://|www\.)[^\s<>"'\])]+""", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
PLACEHOLDER_RE = re.compile(r"\[(URL|EMAIL|PHONE)_(\d+)\]")

REFUSAL_RE = re.compile(r"\b(I can't|I cannot|I can not|As an AI|I'm sorry|I am sorry|I won't|I will not)\b",
                        re.IGNORECASE)


def normalize(text: str) -> str:
    """Casefold and collapse whitespace. This is the normalisation used by N05 and §3.3."""
    return _WS.sub(" ", (text or "").casefold()).strip()


def text_key(subject: str, body: str) -> str:
    """sha256 of the normalised subject + newline + body."""
    return hashlib.sha256(normalize(f"{subject or ''}\n{body or ''}").encode("utf-8")).hexdigest()


def word_count(text: str) -> int:
    return len(_WORD.findall(text or ""))


def detector_input(subject: str, body: str) -> str:
    """Canonical detector input for Study 2 (§4)."""
    return f"Subject: {(subject or '').strip()}\n\n{(body or '').strip()}"


def split_subject(text: str) -> tuple[str, str]:
    """Split a single 'text' field into (subject, body) if it starts with a Subject line."""
    t = (text or "").lstrip("﻿").strip()
    m = re.match(r"(?is)^\s*subject\s*:\s*(.*?)(?:\r?\n)(.*)$", t)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return "", t


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head"):
            self._skip += 1
        elif tag in ("br", "p", "div", "tr", "li", "h1", "h2", "h3", "table"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def html_to_text(markup: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(markup or "")
        parser.close()
    except Exception:  # malformed HTML: fall back to a crude tag strip
        return html.unescape(re.sub(r"<[^>]+>", " ", markup or ""))
    text = "".join(parser.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def lock_placeholders(text: str) -> tuple[str, dict[str, str]]:
    """Replace URLs, email addresses and phone numbers with indexed placeholders.

    Returns (locked_text, mapping). Identical strings share one placeholder. URLs are replaced
    before email addresses so that addresses inside URLs stay part of the URL.
    """
    mapping: dict[str, str] = {}
    reverse: dict[tuple[str, str], str] = {}
    counters = {"URL": 0, "EMAIL": 0, "PHONE": 0}

    def make_sub(kind: str):
        def sub(m: re.Match) -> str:
            value = m.group(0)
            key = (kind, value)
            if key not in reverse:
                counters[kind] += 1
                token = f"[{kind}_{counters[kind]}]"
                reverse[key] = token
                mapping[token] = value
            return reverse[key]
        return sub

    out = URL_RE.sub(make_sub("URL"), text or "")
    out = EMAIL_RE.sub(make_sub("EMAIL"), out)
    out = PHONE_RE.sub(make_sub("PHONE"), out)
    return out, mapping


def restore_placeholders(text: str, mapping: dict[str, str]) -> str:
    return PLACEHOLDER_RE.sub(lambda m: mapping.get(m.group(0), m.group(0)), text or "")


def placeholders_preserved(source_locked: str, output: str) -> bool:
    """§3.4: every input placeholder appears in the output and no new placeholder is introduced."""
    src = set(PLACEHOLDER_RE.findall(source_locked or ""))
    out = set(PLACEHOLDER_RE.findall(output or ""))
    return src == out


def is_refusal(text: str) -> bool:
    return bool(REFUSAL_RE.search((text or "")[:400]))


_LANG_READY = False


def detect_language(text: str) -> str | None:
    """langdetect with a fixed seed (deterministic). Returns None when undetectable."""
    global _LANG_READY
    from langdetect import DetectorFactory, detect  # imported lazily: optional dependency
    if not _LANG_READY:
        DetectorFactory.seed = 0
        _LANG_READY = True
    sample = (text or "")[:2000]
    if word_count(sample) < 3:
        return None
    try:
        return detect(sample)
    except Exception:
        return None


# ---- M4: artifact normalisation (pre-registration §5), applied identically at training and test time ----
DATE_RE = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|"
                     r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+\d{1,2}\s+[A-Z][a-z]{2,8}\s+\d{4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)\b")
NUM_RE = re.compile(r"\b\d[\d,.:]*\b")
QUOTE_START_RE = re.compile(r"^\s*(-{2,}\s*Original Message\s*-{2,}|-{2,}\s*Forwarded by|On .{3,80} wrote:\s*$|From:\s.+$)",
                            re.IGNORECASE | re.MULTILINE)
FOOTER_LINE_RE = re.compile(r"^.*(unsubscribe|opt[- ]out|privacy policy|confidentiality notice|this e-?mail (and any|is) "
                            r"(confidential|intended)|all rights reserved).*$", re.IGNORECASE | re.MULTILINE)


def artifact_normalize(text: str) -> str:
    """Mask URL, email, date and number tokens; strip quoted replies and boilerplate footer lines."""
    t = text or ""
    m = QUOTE_START_RE.search(t, pos=min(len(t), 20))   # keep a leading header line such as "Subject:"
    if m:
        t = t[:m.start()]
    t = "\n".join(l for l in t.splitlines() if not l.lstrip().startswith(">"))
    t = FOOTER_LINE_RE.sub("", t)
    t = URL_RE.sub(" <URL> ", t)
    t = EMAIL_RE.sub(" <EMAIL> ", t)
    t = DATE_RE.sub(" <DATE> ", t)
    t = NUM_RE.sub(" <NUM> ", t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()
