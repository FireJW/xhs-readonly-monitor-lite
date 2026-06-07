# Demo Runbook

Use this runbook to demo the repository without personal browser data.

## Local Parser Demo

Run the unit tests:

```bash
python -m pytest -q
```

The tests use synthetic initial-state payloads and do not open a browser.

## Live Read-Only Demo

1. Start Chrome with a DevTools port in a test environment.
2. Open only pages you are comfortable inspecting.
3. Run `xhs-readonly-monitor list-feeds --port 9222`.
4. Review JSON output before saving or sharing it.
5. Close the browser session when done.

Do not publish, comment, like, favorite, follow, message, log in, export cookies, or capture private account data during a public demo.
