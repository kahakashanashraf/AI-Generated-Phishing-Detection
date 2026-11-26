"""Prompts, output parsing and quality filters for graded AI assistance (pre-registration §3.2, §3.4).

The prompt texts are frozen and must match PREREGISTRATION_V2.md exactly. Tests assert the key phrases.
"""

from __future__ import annotations

import hashlib
import re

from .textnorm import (detect_language, is_refusal, lock_placeholders, normalize, placeholders_preserved,
                       restore_placeholders, word_count)

DN_URL = "https://www.example.com/info"

PROMPTS = {
    "L1": ("Correct only the spelling, grammar and punctuation of the following email. Do not change wording "
           "otherwise, and keep every placeholder token in square brackets exactly as written. Return only the "
           "corrected email: the first line must be \"Subject: ...\" followed by the body.\n\n"
           "Subject: {subject}\n\n{body}"),
    "L2": ("Polish the following email so that it is clear, fluent and professional. Keep the same content, "
           "intent, requests, facts, names, numbers, structure, and every placeholder token in square brackets "
           "exactly as written. Return only the polished email: the first line must be \"Subject: ...\" "
           "followed by the body.\n\nSubject: {subject}\n\n{body}"),
    "L3": ("Rewrite the following email so that it reads as if you had written it yourself. Keep the same sender "
           "intent, requests, facts, names, numbers, and every placeholder token in square brackets exactly as "
           "written (for example [URL_1], [EMAIL_1], [PHONE_1]). Do not add or remove links, attachments, "
           "requests, or deadlines. Return only the rewritten email: the first line must be \"Subject: ...\" "
           "followed by the body.\n\nSubject: {subject}\n\n{body}"),
    "L4": ("Write a realistic, legitimate email with the subject line below, as an ordinary sender would write "
           "it. Use 80–250 words. If the email would naturally include a link, write the placeholder [URL_1] "
           "instead of a real address. Return only the email: the first line must be \"Subject: ...\" followed "
           "by the body.\n\nSubject: {subject}"),
}

DECODING = {"temperature": 0.7, "top_p": 0.95, "max_new_tokens": 2048, "do_sample": True}  # deviation 3: 700 -> 2048


def build_request(parent: dict, level: str) -> dict:
    """Return the prompt plus the placeholder mapping needed to restore and check the output."""
    if level == "L4":
        return {"prompt": PROMPTS["L4"].format(subject=parent["subject"].strip()), "mapping": {}, "locked_body": ""}
    # Lock subject and body jointly so placeholder indices are unique across both.
    joint, mapping = lock_placeholders(parent["subject"] + "\n⁣\n" + parent["body"])
    locked_subject, locked_body = joint.split("\n⁣\n", 1)
    return {"prompt": PROMPTS[level].format(subject=locked_subject.strip(), body=locked_body.strip()),
            "mapping": mapping, "locked_body": locked_subject + "\n" + locked_body}


_FENCE = re.compile(r"^```[a-zA-Z]*\s*|\s*```$")


def parse_output(text: str) -> tuple[str, str] | None:
    t = _FENCE.sub("", (text or "").strip()).strip()
    m = re.match(r"(?is)^\**\s*subject\s*:\**\s*(.*?)\r?\n(.*)$", t)
    if not m:
        return None
    subject = m.group(1).strip().strip("*").strip()
    body = m.group(2).strip()
    return (subject, body) if body else None


def batch_seed(sample_ids: list[str]) -> int:
    """Deviation 2: one seed per batch, derived from the sorted member IDs (row-level seeds are impossible)."""
    return int(hashlib.sha256("\n".join(sorted(sample_ids)).encode()).hexdigest()[:8], 16)


def quality_check(parent: dict, level: str, request: dict, raw_output: str, check_language: bool = True
                  ) -> tuple[dict | None, str | None]:
    """Apply the §3.4 filters (with deviation 1 for L1). Return (restored_subject_body, reason_if_rejected).

    The cosine-similarity filter (L1–L3) runs later, in batch, on the returned texts.
    """
    if is_refusal(raw_output):
        return None, "refusal"
    parsed = parse_output(raw_output)
    if parsed is None:
        return None, "unparseable"
    subject, body = parsed
    if level == "L4":
        body = body.replace("[URL_1]", DN_URL)
        if not 40 <= word_count(body) <= 400:
            return None, "length_out_of_bounds"
    else:
        if not placeholders_preserved(request["locked_body"], subject + "\n" + body):
            return None, "placeholders_changed"
        ratio = word_count(body) / max(1, word_count(parent["body"]))
        if not 0.5 <= ratio <= 2.0:
            return None, "length_ratio"
        subject = restore_placeholders(subject, request["mapping"])
        body = restore_placeholders(body, request["mapping"])
        # Compare after restoring placeholders, so emails that contain URLs are compared like with like.
        if level in ("L2", "L3") and normalize(subject + "\n" + body) == normalize(parent["subject"] + "\n" + parent["body"]):
            return None, "identical_to_input"  # deviation 1: not applied to L1
    if check_language and detect_language(subject + "\n" + body) != "en":
        return None, "not_english"
    return {"subject": subject, "body": body}, None
