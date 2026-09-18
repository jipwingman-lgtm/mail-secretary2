from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .assistant import triage_message
from .gmail_client import GmailClient


def _triage(args: argparse.Namespace) -> None:
    gmail = GmailClient(
        credentials_path=args.credentials,
        token_path=args.token,
    )
    messages = gmail.unread(limit=args.limit)

    if not messages:
        print("No unread inbox messages found.")
        return

    for message in messages:
        result = triage_message(message, model=args.model)
        output = {
            "message": {
                "id": message.id,
                "subject": message.subject,
                "date": message.date,
            },
            "triage": asdict(result),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mail-secretary",
        description=(
            "Read-only Gmail triage with local identifier redaction "
            "before model calls."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    triage = subparsers.add_parser(
        "triage",
        help="Analyze unread inbox messages without modifying Gmail.",
    )
    triage.add_argument("--limit", type=int, default=10)
    triage.add_argument("--model")
    triage.add_argument("--credentials", default="credentials.json")
    triage.add_argument("--token", default="token.json")
    triage.set_defaults(func=_triage)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
