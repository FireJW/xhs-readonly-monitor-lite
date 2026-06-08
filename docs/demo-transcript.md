# Demo Transcript

This transcript is intentionally public-safe. It uses package help output and
synthetic fixture tests only; it does not open a browser, log in, read cookies,
save a session, publish content, or inspect a real account.

## Local Fixture Test

```bash
python -m pytest -q -p no:cacheprovider
```

Expected output:

```text
.....                                                                    [100%]
5 passed in 0.89s
```

What this covers:

- feed-card parsing from synthetic `window.__INITIAL_STATE__` payloads
- note-detail metric normalization from synthetic payloads
- malformed watchlist entries are skipped
- task-opened tabs are closed after list and recheck flows
- browser connections are closed by the orchestration layer

## CLI Help

```bash
python -m xhs_readonly_monitor --help
```

Expected output shape:

```text
usage: __main__.py [-h] {list-feeds,recheck-details} ...

Read-only XHS monitor helpers.

positional arguments:
  {list-feeds,recheck-details}
    list-feeds          Read the home feed via CDP.
    recheck-details     Read detail metrics for notes.
```

## Read-Only Commands

```bash
python -m xhs_readonly_monitor list-feeds --help
python -m xhs_readonly_monitor recheck-details --help
```

The public command surface is limited to:

- `list-feeds`: inspect feed cards through an existing DevTools endpoint
- `recheck-details`: inspect metrics for supplied watchlist entries

There are no commands for login, posting, commenting, replying, liking,
favoriting, following, messaging, cookie export, or browser profile management.

## Live Demo Rule

For a live local demo, start Chrome with a DevTools port in a test environment,
run only the read-only commands, and review JSON output before saving or
sharing it. Do not commit live watchlists, tracked-post exports, screenshots
from logged-in pages, cookies, profiles, sessions, or account identifiers.
