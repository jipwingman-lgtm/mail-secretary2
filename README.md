# Mail Secretary 2

Mail Secretary 2 is an open-source, privacy-first Gmail triage and reply-drafting CLI.

It is designed as a generic tool. The repository contains no bundled mailbox, no preconfigured Gmail account, no OAuth token, no API key, and no real email content.

## What it does

- Connects to a user's Gmail account through that user's own local OAuth setup.
- Requests Gmail read-only access.
- Reads unread inbox messages.
- Locally redacts common identifiers before model calls.
- Produces a priority, summary, next action, and optional reply suggestion.
- Never sends, deletes, archives, labels, or marks email as read.

## Privacy model

Before selected email text is sent to the configured OpenAI API model, the tool locally replaces common identifiers:

- email addresses
- phone numbers
- long numeric identifiers
- IPv4 addresses
- optional user-defined sensitive terms

Users can provide extra private terms locally:

    export MAIL_SECRETARY_REDACT_TERMS="Customer Name,Project Codename"

The remote model then receives placeholders such as:

    [REDACTED_EMAIL]
    [REDACTED_PHONE]
    [REDACTED_NUMBER]
    [REDACTED_IP]
    [REDACTED_TERM]

Redaction reduces accidental exposure, but it cannot guarantee detection of every type of confidential information.

## Installation

Requirements:

- Python 3.10+
- a Google Cloud OAuth Desktop client configured by the user
- an OpenAI API key configured by the user

Install for development:

    git clone https://github.com/jipwingman-lgtm/mail-secretary2.git
    cd mail-secretary2
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"

On Windows PowerShell:

    .venv\Scripts\Activate.ps1
    pip install -e ".[dev]"

## Gmail setup

Each user supplies their own Google OAuth credentials.

1. Create a Google Cloud project.
2. Enable the Gmail API.
3. Configure an OAuth consent screen.
4. Create an OAuth client for a Desktop app.
5. Download the OAuth client file.
6. Save it locally as credentials.json.
7. Run the CLI.
8. Approve the Gmail read-only permission in the browser.

The generated local token is stored as token.json.

Both credentials.json and token.json are excluded from Git by default.

## OpenAI setup

Set the API key locally:

    export OPENAI_API_KEY="your-key"

The default model is gpt-5.6-luna. It can be overridden:

    export OPENAI_MODEL="gpt-5.6-luna"

## Usage

Analyze up to five unread messages:

    mail-secretary triage --limit 5

The command prints local JSON results containing:

- message id
- subject
- date
- priority
- summary
- recommended next action
- whether a reply is needed
- suggested reply text

The tool does not write those results back to Gmail.

## Security boundaries

Current Gmail scope:

    https://www.googleapis.com/auth/gmail.readonly

The project intentionally has no send-mail, delete-mail, archive, label, or draft-writing code in the initial release.

Email content is treated as untrusted input. Instructions inside an email are never treated as application instructions.

## Development

Run tests:

    pytest

The test suite uses only synthetic data. It verifies that common identifiers are removed before the model client receives input.

## Roadmap

- [x] Read-only Gmail OAuth
- [x] Local identifier redaction
- [x] Unread inbox triage
- [x] Synthetic privacy tests
- [x] CI tests
- [ ] Thread-aware summaries
- [ ] Configurable sender allow/deny rules
- [ ] Local-only evaluation dataset
- [ ] Optional pluggable redaction providers
- [ ] User-approved draft creation as a separate, explicitly permissioned feature

## Contributing

See CONTRIBUTING.md.

Never include real email content, credentials, access tokens, or API keys in issues, pull requests, examples, or tests.

## License

MIT
