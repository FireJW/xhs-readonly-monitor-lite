from __future__ import annotations

from typing import Any

from xhs_readonly_monitor import cli


class DummyBrowser:
    def __init__(self, port: int) -> None:
        self.port = port
        self.page = object()
        self.closed = False
        self.closed_pages: list[object] = []

    def new_page(self) -> object:
        return self.page

    def close_page(self, page: object) -> None:
        self.closed_pages.append(page)

    def close(self) -> None:
        self.closed = True


def test_run_list_feeds_marks_tracked_and_closes_task_page(monkeypatch: Any) -> None:
    created: list[DummyBrowser] = []

    def fake_browser(port: int) -> DummyBrowser:
        browser = DummyBrowser(port)
        created.append(browser)
        return browser

    def fake_list_feeds(page: object, scroll_pages: int = 0) -> list[dict[str, str]]:
        assert page is created[0].page
        assert scroll_pages == 3
        return [{"id": "tracked"}, {"id": "new"}]

    monkeypatch.setattr(cli, "Browser", fake_browser)
    monkeypatch.setattr(cli, "list_feeds", fake_list_feeds)

    result = cli.run_list_feeds(
        3347,
        tracked_posts=[{"feed_id": "tracked"}],
        scroll_pages=3,
    )

    assert created[0].port == 3347
    assert created[0].closed_pages == [created[0].page]
    assert created[0].closed is True
    assert result["tracked_count"] == 1
    assert result["discovery_count"] == 1
    assert result["feeds"][0]["monitor_source"] == "tracked"
    assert result["feeds"][1]["monitor_source"] == "discovery"


def test_run_recheck_skips_malformed_items_and_closes_task_page(monkeypatch: Any) -> None:
    created: list[DummyBrowser] = []

    def fake_browser(port: int) -> DummyBrowser:
        browser = DummyBrowser(port)
        created.append(browser)
        return browser

    def fake_get_feed_detail(page: object, feed_id: str, xsec_token: str) -> dict[str, str]:
        assert page is created[0].page
        return {"id": feed_id, "xsecToken": xsec_token}

    monkeypatch.setattr(cli, "Browser", fake_browser)
    monkeypatch.setattr(cli, "get_feed_detail", fake_get_feed_detail)

    result = cli.run_recheck(
        9222,
        [{"feed_id": "feed-1", "xsec_token": "tok"}, {"feed_id": ""}],
        10,
    )

    assert result["feeds"] == [{"id": "feed-1", "xsecToken": "tok"}]
    assert result["skipped"] == [{"feed_id": "", "reason": "missing_feed_id_or_xsec_token"}]
    assert created[0].closed_pages == [created[0].page]
    assert created[0].closed is True
