"""State extraction and normalization helpers."""

from __future__ import annotations

import datetime as dt
from typing import Any


def _dig(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _value_or_wrapped(value: Any) -> Any:
    if isinstance(value, dict):
        if "value" in value:
            return value["value"]
        if "_value" in value:
            return value["_value"]
    return value


def extract_feeds_from_state(initial_state: dict[str, Any]) -> list[dict[str, Any]]:
    """Return normalized feed cards from an XHS initial-state object."""
    feeds = _value_or_wrapped(_dig(initial_state, "feed", "feeds"))
    if not isinstance(feeds, list):
        return []
    return [normalize_feed_card(feed) for feed in feeds if isinstance(feed, dict)]


def normalize_feed_card(feed: dict[str, Any]) -> dict[str, Any]:
    note = feed.get("noteCard") if isinstance(feed.get("noteCard"), dict) else {}
    user = note.get("user") if isinstance(note.get("user"), dict) else {}
    interact = note.get("interactInfo") if isinstance(note.get("interactInfo"), dict) else {}
    cover = note.get("cover") if isinstance(note.get("cover"), dict) else {}
    video = note.get("video") if isinstance(note.get("video"), dict) else None
    normalized: dict[str, Any] = {
        "id": str(feed.get("id") or ""),
        "xsecToken": str(feed.get("xsecToken") or ""),
        "modelType": str(feed.get("modelType") or ""),
        "index": feed.get("index", 0),
        "displayTitle": str(note.get("displayTitle") or ""),
        "type": str(note.get("type") or ""),
        "user": {
            "userId": str(user.get("userId") or ""),
            "nickname": str(user.get("nickname") or user.get("nickName") or ""),
        },
        "interactInfo": {
            "likedCount": str(interact.get("likedCount") or ""),
            "collectedCount": str(interact.get("collectedCount") or ""),
            "commentCount": str(interact.get("commentCount") or ""),
            "sharedCount": str(interact.get("sharedCount") or ""),
        },
    }
    cover_url = cover.get("url") or cover.get("urlDefault")
    if cover_url:
        normalized["cover"] = str(cover_url)
    if isinstance(video, dict):
        duration = _dig(video, "capa", "duration") or 0
        normalized["video"] = {"duration": duration}
    return normalized


def extract_detail_from_state(
    initial_state: dict[str, Any],
    feed_id: str,
) -> dict[str, Any] | None:
    """Return a note detail entry for a feed id from an initial-state object."""
    detail_map = _dig(initial_state, "note", "noteDetailMap")
    if not isinstance(detail_map, dict):
        return None
    direct = detail_map.get(feed_id)
    if isinstance(direct, dict):
        return direct
    for candidate in detail_map.values():
        if not isinstance(candidate, dict):
            continue
        note = candidate.get("note")
        if isinstance(note, dict) and note.get("noteId") == feed_id:
            return candidate
    return None


def format_posted_at(time_value: Any) -> str:
    """Convert seconds or milliseconds since epoch to UTC ISO 8601."""
    if not time_value:
        return ""
    try:
        timestamp = int(time_value)
    except (TypeError, ValueError):
        return ""
    if timestamp <= 0:
        return ""
    if timestamp > 10_000_000_000:
        timestamp //= 1000
    try:
        return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).isoformat()
    except (OSError, OverflowError, ValueError):
        return ""


def build_detail_payload(feed_id: str, xsec_token: str, detail_entry: dict[str, Any]) -> dict[str, Any]:
    """Normalize a detail-map entry into a monitor-friendly payload."""
    note = detail_entry.get("note") if isinstance(detail_entry.get("note"), dict) else {}
    user = note.get("user") if isinstance(note.get("user"), dict) else {}
    interact = note.get("interactInfo") if isinstance(note.get("interactInfo"), dict) else {}
    posted_at = format_posted_at(note.get("time"))
    return {
        "id": feed_id,
        "xsecToken": xsec_token,
        "displayTitle": str(note.get("title") or note.get("desc") or ""),
        "monitor_source": "detail_recheck",
        "posted_at": posted_at,
        "time": posted_at,
        "ipLocation": str(note.get("ipLocation") or ""),
        "user": {
            "userId": str(user.get("userId") or ""),
            "nickname": str(user.get("nickname") or user.get("nickName") or ""),
        },
        "interactInfo": {
            "likedCount": str(interact.get("likedCount") or ""),
            "collectedCount": str(interact.get("collectedCount") or ""),
            "commentCount": str(interact.get("commentCount") or ""),
            "sharedCount": str(interact.get("sharedCount") or ""),
        },
        "url": f"https://www.xiaohongshu.com/explore/{feed_id}",
    }
