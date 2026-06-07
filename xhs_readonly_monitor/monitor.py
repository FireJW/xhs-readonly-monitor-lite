"""Read-only browser monitor routines."""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import quote, urlencode

from .cdp import Page
from .errors import NoFeedDetailError, NoFeedsError
from .state import build_detail_payload, extract_detail_from_state, extract_feeds_from_state

HOME_URL = "https://www.xiaohongshu.com"

_INITIAL_STATE_JS = """
(() => {
  if (window.__INITIAL_STATE__) {
    return JSON.stringify(window.__INITIAL_STATE__);
  }
  return "";
})()
"""


def _read_initial_state(page: Page) -> dict[str, Any]:
    result = page.evaluate(_INITIAL_STATE_JS)
    if not result:
        return {}
    payload = json.loads(result)
    return payload if isinstance(payload, dict) else {}


def list_feeds(page: Page, scroll_pages: int = 0, scroll_pause: float = 1.0) -> list[dict[str, Any]]:
    """Open the home feed and return normalized feed cards."""
    page.navigate(HOME_URL)
    page.wait_for_load()
    page.wait_dom_stable()
    time.sleep(0.5)
    for _ in range(max(0, int(scroll_pages or 0))):
        try:
            page.dispatch_wheel_event(1200)
            page.scroll_by(0, max(1200, page.get_viewport_height()))
        except Exception:
            page.scroll_by(0, 1200)
        time.sleep(max(0.2, scroll_pause))
        page.wait_dom_stable(timeout=3.0, interval=0.4)
    feeds = extract_feeds_from_state(_read_initial_state(page))
    if not feeds:
        raise NoFeedsError("No feed cards found in page initial state")
    return feeds


def get_feed_detail(page: Page, feed_id: str, xsec_token: str) -> dict[str, Any]:
    """Open a note detail page and return normalized metrics."""
    safe_feed_id = quote(str(feed_id).strip(), safe="")
    query = urlencode({"xsec_token": str(xsec_token).strip(), "xsec_source": "pc_feed"})
    url = f"https://www.xiaohongshu.com/explore/{safe_feed_id}?{query}"
    page.navigate(url)
    page.wait_for_load()
    page.wait_dom_stable()
    time.sleep(0.5)
    state = _read_initial_state(page)
    detail = extract_detail_from_state(state, str(feed_id).strip())
    if not detail:
        raise NoFeedDetailError("No note detail found in page initial state")
    return build_detail_payload(str(feed_id).strip(), str(xsec_token).strip(), detail)
