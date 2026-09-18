# Security

Mail Secretary handles email content and OAuth credentials, so secret handling is part of the project design.

## Never commit

- credentials.json
- token.json
- .env
- API keys
- private keys
- real private email contents

The repository gitignore covers the standard local credential paths.

## Runtime privacy

The tool requests Gmail read-only access. Common identifiers are locally replaced before the selected email text is sent to the configured model.

Local redaction reduces accidental exposure, but it cannot guarantee detection of every confidential value. Users should configure MAIL_SECRETARY_REDACT_TERMS for names, project codenames, customer identifiers, or other private terms that matter to them.

## Reporting

Do not include real credentials or private email contents in public issues. Use synthetic examples.
