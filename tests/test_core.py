import base64
import json

from mail_secretary.assistant import build_model_input, triage_message
from mail_secretary.gmail_client import _decode, _extract_text
from mail_secretary.models import EmailMessage
from mail_secretary.redaction import redact_text


def _b64(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")


def test_decode_urlsafe_base64():
    assert _decode(_b64("hello")) == "hello"


def test_extract_text_prefers_plain_text():
    payload = {
        "mimeType": "multipart/alternative",
        "parts": [
            {"mimeType": "text/plain", "body": {"data": _b64("plain")}},
            {"mimeType": "text/html", "body": {"data": _b64("<b>html</b>")}},
        ],
    }
    assert _extract_text(payload) == "plain"


def test_redact_common_identifiers():
    original = (
        "Contact alice@example.com, phone +1 202-555-0123, "
        "reference 123456789012, host 192.168.10.25."
    )

    result = redact_text(original)

    assert "alice@example.com" not in result
    assert "+1 202-555-0123" not in result
    assert "123456789012" not in result
    assert "192.168.10.25" not in result
    assert "[REDACTED_EMAIL]" in result
    assert "[REDACTED_PHONE]" in result
    assert "[REDACTED_NUMBER]" in result
    assert "[REDACTED_IP]" in result


def test_custom_redaction_terms():
    result = redact_text(
        "Internal project codename BlueLighthouse",
        extra_terms=["BlueLighthouse"],
    )
    assert "BlueLighthouse" not in result
    assert "[REDACTED_TERM]" in result


def test_model_input_is_redacted():
    message = EmailMessage(
        id="m1",
        thread_id="t1",
        sender="Alice <alice@example.com>",
        subject="Reference 123456789012",
        date="2026-01-01",
        body="Call +1 202-555-0123 from 192.168.10.25.",
    )

    prompt = build_model_input(message)

    assert "alice@example.com" not in prompt
    assert "123456789012" not in prompt
    assert "+1 202-555-0123" not in prompt
    assert "192.168.10.25" not in prompt


class _FakeResponse:
    output_text = json.dumps(
        {
            "priority": "normal",
            "summary": "A routine message.",
            "action": "Review when convenient.",
            "needs_reply": False,
            "suggested_reply": "",
        }
    )


class _FakeResponses:
    def __init__(self):
        self.last_input = ""

    def create(self, **kwargs):
        self.last_input = kwargs["input"]
        return _FakeResponse()


class _FakeClient:
    def __init__(self):
        self.responses = _FakeResponses()


def test_remote_model_receives_only_redacted_input():
    client = _FakeClient()
    message = EmailMessage(
        id="m2",
        thread_id="t2",
        sender="Bob <bob@example.com>",
        subject="Account 987654321012",
        date="2026-01-01",
        body="Reach me at +44 20 7946 0958.",
    )

    result = triage_message(message, model="test-model", client=client)

    assert result.priority == "normal"
    assert "bob@example.com" not in client.responses.last_input
    assert "987654321012" not in client.responses.last_input
    assert "+44 20 7946 0958" not in client.responses.last_input
