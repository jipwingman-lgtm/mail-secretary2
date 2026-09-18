"""Privacy-first email triage utilities."""

from .models import EmailMessage, TriageResult
from .redaction import redact_text

__all__ = ["EmailMessage", "TriageResult", "redact_text"]
__version__ = "0.1.0"
