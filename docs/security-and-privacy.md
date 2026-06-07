# Security and Privacy

This repository is intentionally read-only. It should not contain browser profile data, cookies, login helpers, publishing commands, social-interaction commands, private watchlists, or saved sessions.

## Included

- Read-only Chrome DevTools connection helpers.
- Feed card extraction from page initial state.
- Note detail metric extraction from page initial state.
- Synthetic fixture tests.
- Demo documentation for safe public review.

## Excluded

- Login, cookie, session, profile, and account-switching code.
- Publish, comment, reply, like, favorite, follow, or message actions.
- Real account identifiers, private watchlists, personal browser data, and notification endpoints.
- Any stored credentials or API keys.

## Demo Rules

- Use synthetic payloads for tests and screenshots.
- Do not commit live output from personal accounts.
- Do not include private watchlist files in issues, pull requests, or docs.
- Review public page content before sharing screenshots.
