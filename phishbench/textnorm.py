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
