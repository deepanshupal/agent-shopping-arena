"""Shared Playwright executor: one headless Chromium, screenshot-in / action-out.

Both model adapters translate their vendor's action vocabulary into the
normalized action dicts this executor runs, so the browser affordances are
identical across models. Sequential, polite: one browser, no parallelism.
"""
from __future__ import annotations
import base64, time
from playwright.sync_api import sync_playwright

VIEWPORT = {"width": 1280, "height": 720}

class BrowserExecutor:
    def __init__(self, viewport=VIEWPORT, settle_ms=1200):
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=True)
        self.context = self.browser.new_context(viewport=viewport)
        self.page = self.context.new_page()
        self.settle_ms = settle_ms

    def screenshot_b64(self) -> str:
        time.sleep(self.settle_ms / 1000)
        return base64.b64encode(self.page.screenshot(type="png")).decode()

    def url(self) -> str:
        return self.page.url

    def act(self, action: dict) -> str:
        """Run one normalized action. Returns a short outcome string for the log."""
        kind = action["type"]
        if kind == "goto":
            self.page.goto(action["url"], timeout=30000, wait_until="domcontentloaded")
            return f"goto {self.page.url}"
        if kind == "click":
            self.page.mouse.click(action["x"], action["y"])
            return f"click {action['x']},{action['y']}"
        if kind == "dblclick":
            self.page.mouse.dblclick(action["x"], action["y"])
            return f"dblclick {action['x']},{action['y']}"
        if kind == "type":
            self.page.keyboard.type(action["text"], delay=20)
            return f"type {action['text'][:40]!r}"
        if kind == "key":
            self.page.keyboard.press(action["key"])
            return f"key {action['key']}"
        if kind == "scroll":
            self.page.mouse.wheel(action.get("dx", 0), action.get("dy", 0))
            return f"scroll {action.get('dx',0)},{action.get('dy',0)}"
        if kind == "wait":
            time.sleep(action.get("ms", 1000) / 1000)
            return "wait"
        raise ValueError(f"unknown action {kind!r}")

    def close(self):
        self.context.close(); self.browser.close(); self._pw.stop()
