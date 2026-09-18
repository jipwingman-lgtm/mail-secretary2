from __future__ import annotations

import base64
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .models import EmailMessage


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _decode(data: str | None) -> str:
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii")).decode(
        "utf-8", errors="replace"
    )


def _extract_text(payload: dict) -> str:
    mime_type = payload.get("mimeType", "")
    body = payload.get("body", {})

    if mime_type == "text/plain" and body.get("data"):
        return _decode(body["data"])

    plain_parts: list[str] = []
    html_parts: list[str] = []

    for part in payload.get("parts", []) or []:
        text = _extract_text(part)
        if not text:
            continue
        if part.get("mimeType") == "text/plain":
            plain_parts.append(text)
        elif part.get("mimeType") == "text/html":
            html_parts.append(text)
        else:
            plain_parts.append(text)

    if plain_parts:
        return "\n".join(plain_parts)
    if html_parts:
        return "\n".join(html_parts)
    return _decode(body.get("data"))


def _headers(payload: dict) -> dict[str, str]:
    return {
        item.get("name", "").lower(): item.get("value", "")
        for item in payload.get("headers", [])
    }


class GmailClient:
    """Minimal Gmail client that requests read-only access."""

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
    ) -> None:
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)

    def _credentials(self) -> Credentials:
        creds: Credentials | None = None

        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if not creds or not creds.valid:
            if not self.credentials_path.exists():
                raise FileNotFoundError(
                    "OAuth client file was not found. Create a Google OAuth "
                    "Desktop app credential and save it as credentials.json."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)
            self.token_path.write_text(creds.to_json(), encoding="utf-8")

        return creds

    def service(self):
        return build("gmail", "v1", credentials=self._credentials())

    def unread(self, limit: int = 10) -> list[EmailMessage]:
        service = self.service()
        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                q="in:inbox is:unread",
                maxResults=limit,
            )
            .execute()
        )

        messages: list[EmailMessage] = []

        for item in response.get("messages", []):
            raw = (
                service.users()
                .messages()
                .get(userId="me", id=item["id"], format="full")
                .execute()
            )
            payload = raw.get("payload", {})
            headers = _headers(payload)

            messages.append(
                EmailMessage(
                    id=raw["id"],
                    thread_id=raw.get("threadId", ""),
                    sender=headers.get("from", ""),
                    subject=headers.get("subject", "(no subject)"),
                    date=headers.get("date", ""),
                    body=_extract_text(payload).strip(),
                )
            )

        return messages
