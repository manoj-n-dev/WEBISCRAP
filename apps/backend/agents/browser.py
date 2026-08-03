import asyncio
import sys
from typing import Dict, Any, List
from .base import BaseAgent
from loguru import logger
from bs4 import BeautifulSoup
import httpx
import re


def minify_html(html_content: str, max_chars: int = 25000) -> str:
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        for tag in soup(['script', 'style', 'noscript', 'svg', 'iframe', 'path', 'header', 'footer']):
            tag.decompose()
        text = str(soup)
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > max_chars:
            text = text[:max_chars] + " <!-- TRUNCATED -->"
        return text
    except Exception as e:
        logger.warning(f"Failed to minify HTML: {e}")
        return html_content[:max_chars]


def _run_playwright_sync(target_url: str, analysis: dict) -> List[str]:
    """
    Runs Playwright in a synchronous context. This function is designed to be
    called via asyncio.to_thread() so it runs in a separate OS thread,
    avoiding event loop conflicts with uvicorn on Windows.
    """
    from playwright.sync_api import sync_playwright

    dom_snapshots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            page.goto(target_url, wait_until="networkidle", timeout=30000)

            pagination_type = analysis.get("pagination_type", "none")

            if pagination_type == "infinite_scroll":
                for _ in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2000)
                content = page.content()
                dom_snapshots.append(minify_html(content))

            elif pagination_type == "button" and analysis.get("pagination_selector"):
                content = page.content()
                dom_snapshots.append(minify_html(content))
                selector = analysis.get("pagination_selector")
                for _ in range(2):
                    try:
                        next_btn = page.query_selector(selector)
                        if next_btn:
                            next_btn.click()
                            page.wait_for_timeout(2000)
                            content = page.content()
                            dom_snapshots.append(minify_html(content))
                        else:
                            break
                    except Exception:
                        break
            else:
                content = page.content()
                dom_snapshots.append(minify_html(content))

        except Exception as e:
            logger.error(f"Playwright navigation failed: {e}")
        finally:
            browser.close()

    return dom_snapshots


async def _fetch_static_html(target_url: str) -> str:
    """Fetch page HTML using httpx (no browser needed)."""
    try:
        async with httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        ) as client:
            response = await client.get(target_url)
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.warning(f"Static HTTP fetch failed for {target_url}: {e}")
        return ""


class BrowserAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="BrowserAgent")

    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        target_url = input_data.get("target_url")
        analysis = input_data.get("analysis", {})

        if not target_url:
            return input_data

        requires_js = analysis.get("requires_js_rendering", True)

        if not requires_js:
            # Static fetch is sufficient — fast path, no browser needed
            logger.info(f"[{session_id}] BrowserAgent using static HTTP fetch for {target_url}")
            html = await _fetch_static_html(target_url)
            if html:
                input_data["dom_snapshots"] = [minify_html(html)]
            else:
                input_data["dom_snapshots"] = []
            return input_data

        # JS rendering required — use Playwright
        logger.info(f"[{session_id}] BrowserAgent starting Playwright (threaded) for {target_url}")

        try:
            # Run Playwright in a separate thread to avoid Windows event loop issues
            dom_snapshots = await asyncio.to_thread(
                _run_playwright_sync, target_url, analysis
            )
            input_data["dom_snapshots"] = dom_snapshots
        except Exception as e:
            logger.error(f"[{session_id}] Playwright threaded execution failed: {e}")
            # Fallback to static fetch
            logger.info(f"[{session_id}] Falling back to static HTTP fetch")
            html = await _fetch_static_html(target_url)
            if html:
                input_data["dom_snapshots"] = [minify_html(html)]
            else:
                input_data["dom_snapshots"] = []

        return input_data


browser_agent = BrowserAgent()
