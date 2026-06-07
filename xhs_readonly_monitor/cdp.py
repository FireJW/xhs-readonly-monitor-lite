"""Minimal read-only Chrome DevTools Protocol client."""

from __future__ import annotations

import json
import time
from typing import Any

import requests
import websockets.sync.client as ws_client

from .errors import CDPError


class CDPClient:
    """Small synchronous CDP WebSocket client."""

    def __init__(self, ws_url: str) -> None:
        self._ws = ws_client.connect(ws_url, max_size=50 * 1024 * 1024)
        self._id = 0

    def send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._id += 1
        message: dict[str, Any] = {"id": self._id, "method": method}
        if params:
            message["params"] = params
        self._ws.send(json.dumps(message))
        return self._wait_for(self._id)

    def _wait_for(self, message_id: int, timeout: float = 30.0) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                raw = self._ws.recv(timeout=max(0.1, deadline - time.monotonic()))
            except TimeoutError:
                break
            data = json.loads(raw)
            if data.get("id") == message_id:
                if "error" in data:
                    raise CDPError(f"CDP error: {data['error']}")
                result = data.get("result", {})
                return result if isinstance(result, dict) else {}
        raise CDPError(f"Timed out waiting for CDP response id={message_id}")

    def close(self) -> None:
        self._ws.close()


class Page:
    """Read-only page wrapper.

    The wrapper intentionally omits click, keyboard, file upload, cookie, and
    storage mutation helpers. It can open pages, evaluate state, scroll, and
    close its own task tab.
    """

    def __init__(self, cdp: CDPClient, target_id: str, session_id: str) -> None:
        self._cdp = cdp
        self._ws = cdp._ws
        self.target_id = target_id
        self.session_id = session_id
        self._id = 1000

    def _send_session(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        self._id += 1
        message: dict[str, Any] = {
            "id": self._id,
            "method": method,
            "sessionId": self.session_id,
        }
        if params:
            message["params"] = params
        self._ws.send(json.dumps(message))
        return self._wait_session(self._id, timeout=timeout)

    def _wait_session(self, message_id: int, timeout: float = 60.0) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                raw = self._ws.recv(timeout=max(0.1, deadline - time.monotonic()))
            except TimeoutError:
                break
            data = json.loads(raw)
            if data.get("id") == message_id:
                if "error" in data:
                    raise CDPError(f"CDP session error: {data['error']}")
                result = data.get("result", {})
                return result if isinstance(result, dict) else {}
        raise CDPError(f"Timed out waiting for CDP session response id={message_id}")

    def enable(self) -> None:
        self._send_session("Page.enable")
        self._send_session("Runtime.enable")

    def navigate(self, url: str) -> None:
        self._send_session("Page.navigate", {"url": url})

    def wait_for_load(self, timeout: float = 45.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                if self.evaluate("document.readyState") == "complete":
                    return
            except CDPError:
                pass
            time.sleep(0.4)

    def wait_dom_stable(self, timeout: float = 8.0, interval: float = 0.4) -> None:
        previous = None
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            current = self.evaluate("document.body ? document.body.innerHTML.length : 0")
            if current and current == previous:
                return
            previous = current
            time.sleep(interval)

    def evaluate(self, expression: str) -> Any:
        result = self._send_session(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": False,
            },
        )
        if "exceptionDetails" in result:
            raise CDPError(f"JavaScript evaluation failed: {result['exceptionDetails']}")
        remote = result.get("result", {})
        return remote.get("value") if isinstance(remote, dict) else None

    def scroll_by(self, x: int, y: int) -> None:
        self.evaluate(f"window.scrollBy({int(x)}, {int(y)})")

    def dispatch_wheel_event(self, delta_y: float) -> None:
        self.evaluate(
            """
            (() => {
              const target = document.querySelector('.note-scroller')
                || document.querySelector('.interaction-container')
                || document.documentElement;
              target.dispatchEvent(new WheelEvent('wheel', {
                deltaY: %s,
                deltaMode: 0,
                bubbles: true,
                cancelable: true,
                view: window
              }));
            })()
            """
            % float(delta_y)
        )

    def get_viewport_height(self) -> int:
        value = self.evaluate("window.innerHeight")
        return int(value) if value else 768


class Browser:
    """Connects to an existing Chrome DevTools endpoint."""

    def __init__(self, host: str = "127.0.0.1", port: int = 9222) -> None:
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self._cdp: CDPClient | None = None

    def connect(self) -> None:
        response = requests.get(f"{self.base_url}/json/version", timeout=5)
        response.raise_for_status()
        self._cdp = CDPClient(response.json()["webSocketDebuggerUrl"])

    def new_page(self, url: str = "about:blank") -> Page:
        if not self._cdp:
            self.connect()
        assert self._cdp is not None
        target = self._cdp.send("Target.createTarget", {"url": url})["targetId"]
        session = self._cdp.send(
            "Target.attachToTarget",
            {"targetId": target, "flatten": True},
        )["sessionId"]
        page = Page(self._cdp, target, session)
        page.enable()
        return page

    def close_page(self, page: Page) -> None:
        if self._cdp:
            self._cdp.send("Target.closeTarget", {"targetId": page.target_id})

    def close(self) -> None:
        if self._cdp:
            self._cdp.close()
            self._cdp = None
