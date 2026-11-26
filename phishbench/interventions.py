"""H4 cue interventions on LEGITIMATE emails only, using the exact texts from pre-registration §6.

None of these edits can turn a legitimate email into phishing: the URL is a fixed, inert example.com address.
"""

from __future__ import annotations

import re

from .textnorm import URL_RE

I1_LINE = "More information: https://www.example.com/info"
I3_SIGNATURE = "Best regards,\nJordan Lee\nOperations Coordinator\nNorthfield Partners Ltd."
I5_FOOTER = "You are receiving this email because you subscribed to updates. To unsubscribe, click here."
_GREETING = re.compile(r"^\s*(hi|hello|dear|hey|good (morning|afternoon|evening)|greetings)\b[^\n]{0,60}\n", re.IGNORECASE)
_SIGNOFF = re.compile(r"\n\s*(best|regards|kind regards|best regards|thanks|thank you|cheers|sincerely|warm regards)"
                      r"[,!.]?\s*\n?[^\n]{0,60}\s*$", re.IGNORECASE)


def apply(kind: str, body: str) -> str:
    b = (body or "").rstrip()
    if kind == "I1":
        return f"{b}\n\n{I1_LINE}"
    if kind == "I2":
        return re.sub(r"[ \t]{2,}", " ", URL_RE.sub("", b)).strip()
    if kind == "I3":
        return f"{b}\n\n{I3_SIGNATURE}"
    if kind == "I4":
        return _SIGNOFF.sub("", _GREETING.sub("", b, count=1)).strip()
    if kind == "I5":
        return f"{b}\n\n{I5_FOOTER}"
    if kind == "I6":
        words = b.split()
        return " ".join(words[: max(1, len(words) // 2)])
    raise ValueError(kind)


KINDS = ("I1", "I2", "I3", "I4", "I5", "I6")
