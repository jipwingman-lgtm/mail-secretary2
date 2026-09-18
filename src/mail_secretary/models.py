from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EmailMessage:
    id: str
    thread_id: str
    sender: str
    subject: str
    date: str
    body: str


@dataclass(slots=True)
class TriageResult:
    priority: str
    summary: str
    action: str
    needs_reply: bool
    suggested_reply: str
