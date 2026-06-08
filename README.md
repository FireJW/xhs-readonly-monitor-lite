# XHS Readonly Monitor Lite

Public-safe extraction of read-only Chrome DevTools helpers for inspecting Xiaohongshu feed cards and note detail metrics.

This repository is intentionally narrow. It does not publish posts, send comments, like, favorite, manage cookies, log in, scrape private accounts, or store browser sessions. It only demonstrates how to connect to an existing DevTools endpoint, open task-scoped tabs, read page initial state, normalize public feed/detail fields, and close the tabs it opened.

## What It Demonstrates

- Minimal synchronous Chrome DevTools Protocol client.
- Read-only home-feed card extraction from `window.__INITIAL_STATE__`.
- Read-only note detail metric recheck for watchlist items.
- Task-scoped tab cleanup with `Target.closeTarget`.
- Synthetic fixture tests for parsing and monitor orchestration.
- Public documentation that separates monitoring from account-changing automation.

## Install

```bash
python -m pip install -e .
```

For development:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

## Usage

Start Chrome with a DevTools port in your own environment:

```bash
chrome --remote-debugging-port=9222
```

List feed cards:

```bash
xhs-readonly-monitor list-feeds --port 9222 --scroll-pages 2
```

Mark current feed cards against a prior watchlist:

```bash
xhs-readonly-monitor list-feeds \
  --port 9222 \
  --tracked-posts-file tracked-posts.json
```

Recheck detail metrics:

```bash
xhs-readonly-monitor recheck-details \
  --port 9222 \
  --watchlist-file watchlist.json \
  --limit 20
```

`watchlist.json` can be either a list or an object with a `watchlist` array:

```json
{
  "watchlist": [
    {
      "feed_id": "sample-note-id",
      "xsec_token": "sample-token"
    }
  ]
}
```

## Output Shape

`list-feeds` returns:

- `feeds`: normalized feed cards.
- `tracked_feeds`: cards whose ids were already in the supplied watchlist.
- `discovery_feeds`: cards not found in the watchlist.
- count fields for each bucket.

`recheck-details` returns:

- `feeds`: normalized detail metrics.
- `errors`: per-note read failures.
- `skipped`: malformed watchlist entries.
- `requested_count`: number of input watchlist items.

## Safety Boundary

This repo is designed for public portfolio review and safe local experimentation.

It deliberately excludes:

- login and cookie management;
- publishing workflows;
- comment, reply, like, favorite, follow, or message actions;
- browser profile management;
- account identifiers, real watchlists, tokens, or saved sessions.

Use only synthetic fixtures in tests and public demos. Review any live output before sharing it because public pages can still contain personal or creator information.

## Portfolio Context

This project was extracted from a broader private automation codebase into a small public repo with a safer surface area. The point is to show engineering judgment: useful read-only monitoring can be packaged without exposing account-changing automation or private browser state.

## Documentation

- [Portfolio overview](https://firejw.github.io/xhs-readonly-monitor-lite/)
- [Safety model](docs/security-and-privacy.md)
- [Demo runbook](docs/demo-runbook.md)
- [Demo transcript](docs/demo-transcript.md)

## License

MIT License. See [LICENSE](LICENSE).
