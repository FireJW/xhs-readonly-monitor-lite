"""Command line interface for read-only XHS monitoring."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .cdp import Browser
from .monitor import get_feed_detail, list_feeds


def load_json_items(path: str | Path, preferred_key: str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get(preferred_key), list):
        return [item for item in payload[preferred_key] if isinstance(item, dict)]
    return []


def run_list_feeds(
    port: int,
    tracked_posts: list[dict[str, Any]] | None = None,
    scroll_pages: int = 0,
) -> dict[str, Any]:
    browser = Browser(port=port)
    page = None
    try:
        page = browser.new_page()
        tracked_ids = {
            str(item.get("feed_id") or item.get("id") or "").strip()
            for item in (tracked_posts or [])
            if str(item.get("feed_id") or item.get("id") or "").strip()
        }
        feeds = []
        tracked = []
        discovery = []
        for feed in list_feeds(page, scroll_pages=scroll_pages):
            feed_id = str(feed.get("id") or "").strip()
            feed["monitor_source"] = "tracked" if feed_id in tracked_ids else "discovery"
            feeds.append(feed)
            (tracked if feed["monitor_source"] == "tracked" else discovery).append(feed)
        return {
            "feeds": feeds,
            "count": len(feeds),
            "tracked_feeds": tracked,
            "tracked_count": len(tracked),
            "tracked_watchlist_count": len(tracked_ids),
            "discovery_feeds": discovery,
            "discovery_count": len(discovery),
        }
    finally:
        if page is not None:
            browser.close_page(page)
        browser.close()


def run_recheck(port: int, watchlist: list[dict[str, Any]], limit: int) -> dict[str, Any]:
    browser = Browser(port=port)
    page = None
    feeds: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    try:
        page = browser.new_page()
        for item in watchlist[: max(0, int(limit))]:
            feed_id = str(item.get("feed_id") or item.get("id") or "").strip()
            xsec_token = str(item.get("xsec_token") or item.get("xsecToken") or "").strip()
            if not feed_id or not xsec_token:
                skipped.append({"feed_id": feed_id, "reason": "missing_feed_id_or_xsec_token"})
                continue
            try:
                feeds.append(get_feed_detail(page, feed_id, xsec_token))
            except Exception as exc:
                errors.append(
                    {
                        "feed_id": feed_id,
                        "reason": type(exc).__name__,
                        "message": str(exc),
                    }
                )
        return {
            "feeds": feeds,
            "errors": errors,
            "skipped": skipped,
            "requested_count": len(watchlist),
        }
    finally:
        if page is not None:
            browser.close_page(page)
        browser.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only XHS monitor helpers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-feeds", help="Read the home feed via CDP.")
    list_parser.add_argument("--port", type=int, default=9222, help="Chrome DevTools port.")
    list_parser.add_argument("--scroll-pages", type=int, default=0)
    list_parser.add_argument("--tracked-posts-file", default="")

    detail_parser = subparsers.add_parser("recheck-details", help="Read detail metrics for notes.")
    detail_parser.add_argument("--port", type=int, default=9222, help="Chrome DevTools port.")
    detail_parser.add_argument("--watchlist-file", required=True)
    detail_parser.add_argument("--limit", type=int, default=20)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "list-feeds":
        tracked = (
            load_json_items(args.tracked_posts_file, "tracked_posts")
            if args.tracked_posts_file
            else []
        )
        result = run_list_feeds(args.port, tracked_posts=tracked, scroll_pages=args.scroll_pages)
    else:
        watchlist = load_json_items(args.watchlist_file, "watchlist")
        result = run_recheck(args.port, watchlist, args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
