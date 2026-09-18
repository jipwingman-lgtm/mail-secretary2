from __future__ import annotations

import os
import re


EMAIL_RE = re.compile(
    r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])",
    re.IGNORECASE,
)
PHONE_RE = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{2,4}(?!\w)"
)
LONG_NUMBER_RE = re.compile(r"(?<!\w)\d{8,}(?!\w)")
IPV4_RE = re.compile(
    r"(?<!\d)(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|1?\d?\d)(?!\d)"
)


def _looks_like_phone(candidate: str) -> bool:
    digits = re.sub(r"\D", "", candidate)
    return 7 <= len(digits) <= 15


def configured_terms() -> list[str]:
    raw = os.getenv("MAIL_SECRETARY_REDACT_TERMS", "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def redact_text(text: str, extra_terms: list[str] | None = None) -> str:
    """Replace common identifiers before text is sent to a remote model."""
    if not text:
        return text

    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    redacted = IPV4_RE.sub("[REDACTED_IP]", redacted)
    redacted = LONG_NUMBER_RE.sub("[REDACTED_NUMBER]", redacted)

    def replace_phone(match: re.Match[str]) -> str:
        value = match.group(0)
        return "[REDACTED_PHONE]" if _looks_like_phone(value) else value

    redacted = PHONE_RE.sub(replace_phone, redacted)

    terms = configured_terms() if extra_terms is None else extra_terms
    for term in sorted(set(terms), key=len, reverse=True):
        redacted = re.sub(
            re.escape(term),
            "[REDACTED_TERM]",
            redacted,
            flags=re.IGNORECASE,
        )

    return redacted
