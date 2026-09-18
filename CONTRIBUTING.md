# Contributing

Contributions are welcome.

## Project principles

- Keep Gmail access read-only unless a future feature clearly requires more.
- Keep consequential actions under explicit user control.
- Redact common identifiers locally before remote model calls.
- Treat email content as untrusted input.
- Use synthetic data in tests, issues, and documentation.
- Never commit OAuth credentials, tokens, API keys, or real private email content.

## Development

    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    pytest

Please add tests for privacy-sensitive behavior.
