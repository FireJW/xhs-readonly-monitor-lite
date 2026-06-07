from __future__ import annotations

from xhs_readonly_monitor.state import (
    build_detail_payload,
    extract_detail_from_state,
    extract_feeds_from_state,
    format_posted_at,
)


def test_extract_feeds_from_wrapped_initial_state() -> None:
    state = {
        "feed": {
            "feeds": {
                "value": [
                    {
                        "id": "feed-1",
                        "xsecToken": "tok",
                        "modelType": "note",
                        "index": 2,
                        "noteCard": {
                            "displayTitle": "Title",
                            "type": "normal",
                            "user": {"userId": "u1", "nickname": "Alice"},
                            "interactInfo": {
                                "likedCount": "10",
                                "collectedCount": "3",
                                "commentCount": "2",
                                "sharedCount": "1",
                            },
                            "cover": {"urlDefault": "https://example.invalid/cover.jpg"},
                        },
                    }
                ]
            }
        }
    }

    feeds = extract_feeds_from_state(state)

    assert feeds == [
        {
            "id": "feed-1",
            "xsecToken": "tok",
            "modelType": "note",
            "index": 2,
            "displayTitle": "Title",
            "type": "normal",
            "user": {"userId": "u1", "nickname": "Alice"},
            "interactInfo": {
                "likedCount": "10",
                "collectedCount": "3",
                "commentCount": "2",
                "sharedCount": "1",
            },
            "cover": "https://example.invalid/cover.jpg",
        }
    ]


def test_extract_detail_from_state_falls_back_to_note_id() -> None:
    state = {
        "note": {
            "noteDetailMap": {
                "other-key": {
                    "note": {
                        "noteId": "feed-2",
                        "title": "Detail",
                        "time": 1_700_000_000_000,
                        "ipLocation": "Shanghai",
                        "user": {"userId": "u2", "nickName": "Bob"},
                        "interactInfo": {"likedCount": "8"},
                    }
                }
            }
        }
    }

    detail = extract_detail_from_state(state, "feed-2")

    assert detail is not None
    payload = build_detail_payload("feed-2", "tok-2", detail)
    assert payload["displayTitle"] == "Detail"
    assert payload["posted_at"].startswith("2023-")
    assert payload["ipLocation"] == "Shanghai"
    assert payload["user"]["nickname"] == "Bob"
    assert payload["interactInfo"]["likedCount"] == "8"


def test_format_posted_at_accepts_seconds_and_rejects_invalid_values() -> None:
    assert format_posted_at(1_700_000_000).startswith("2023-")
    assert format_posted_at(1_700_000_000_000).startswith("2023-")
    assert format_posted_at(0) == ""
    assert format_posted_at("not-a-number") == ""
