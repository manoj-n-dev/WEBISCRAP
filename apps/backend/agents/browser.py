import asyncio
import sys
from typing import Dict, Any, List
from .base import BaseAgent
from loguru import logger
from bs4 import BeautifulSoup
import httpx
import re


# Configurable limits
MAX_SCROLL_ATTEMPTS = 20       # Up to 20 scrolls for infinite scroll pages
MAX_PAGINATION_CLICKS = 10     # Up to 10 "next page" clicks
SCROLL_WAIT_MS = 2500          # Wait after each scroll for lazy content to load
PAGE_LOAD_TIMEOUT_MS = 30000   # Timeout for initial page load
MAX_HTML_CHARS = 20000         # Max chars per snapshot to fit within Groq's 32K token context window


def minify_html(html_content: str, max_chars: int = MAX_HTML_CHARS) -> str:
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        # Remove non-content tags aggressively to maximize useful data per snapshot
        for tag in soup(['script', 'style', 'noscript', 'svg', 'iframe', 'path', 'link', 'meta', 'img', 'video', 'audio', 'canvas', 'map', 'source', 'picture']):
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
    Runs Playwright in a synchronous context via asyncio.to_thread()
    to avoid uvicorn's event loop conflicts on Windows.
    
    Handles:
    - Infinite scroll (smart detection, up to MAX_SCROLL_ATTEMPTS)
    - Button/link pagination (up to MAX_PAGINATION_CLICKS)
    - Load-more buttons
    - Single page fallback
    """
    from playwright.sync_api import sync_playwright

    dom_snapshots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            page.goto(target_url, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT_MS)

            pagination_type = (analysis.get("pagination_type") or "").lower()

            if pagination_type == "infinite_scroll":
                # Smart infinite scroll: keep scrolling until no new content loads
                content = _smart_scroll(page)
                dom_snapshots.append(minify_html(content))

            elif pagination_type in ("button", "link", "numbered") and analysis.get("pagination_selector"):
                # Click-based pagination: grab each page
                dom_snapshots = _paginate_by_clicking(page, analysis.get("pagination_selector"))

            else:
                # No pagination detected by analyzer — auto-detect
                dom_snapshots = _auto_detect_and_extract(page)

        except Exception as e:
            logger.error(f"Playwright navigation failed: {e}")
            # Try to capture whatever is on the page
            try:
                content = page.content()
                if content:
                    dom_snapshots.append(minify_html(content))
            except Exception:
                pass
        finally:
            browser.close()

    return dom_snapshots


def _smart_scroll(page) -> str:
    """
    Scrolls the page intelligently, stopping when no new content loads.
    Returns the final full page HTML.
    """
    previous_height = 0
    stale_count = 0

    for i in range(MAX_SCROLL_ATTEMPTS):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(SCROLL_WAIT_MS)

        current_height = page.evaluate("document.body.scrollHeight")

        if current_height == previous_height:
            stale_count += 1
            if stale_count >= 3:
                # No new content loaded after 3 consecutive scrolls — we're at the bottom
                logger.info(f"Smart scroll: stopped after {i+1} scrolls (no new content)")
                break
        else:
            stale_count = 0

        previous_height = current_height

    return page.content()


def _paginate_by_clicking(page, selector: str) -> List[str]:
    """
    Clicks a pagination button/link repeatedly to collect data from multiple pages.
    """
    dom_snapshots = []

    # Capture first page
    content = page.content()
    dom_snapshots.append(minify_html(content))

    for i in range(MAX_PAGINATION_CLICKS):
        try:
            next_btn = page.query_selector(selector)
            if not next_btn or not next_btn.is_visible():
                logger.info(f"Pagination: no more pages after {i+1} clicks")
                break

            next_btn.click()
            page.wait_for_load_state("networkidle", timeout=15000)
            page.wait_for_timeout(1500)

            content = page.content()
            dom_snapshots.append(minify_html(content))

        except Exception as e:
            logger.warning(f"Pagination click {i+1} failed: {e}")
            break

    return dom_snapshots


def _auto_detect_and_extract(page) -> List[str]:
    """
    When the analyzer didn't detect pagination, try common patterns automatically:
    1. Look for common "Next" / "Load More" buttons
    2. Try infinite scroll detection
    3. Fall back to single page
    """
    dom_snapshots = []

    # Common pagination selectors for e-commerce sites
    common_next_selectors = [
        "a._1LKTO3",                        # Flipkart next button
        "a[class*='next']",                  # Generic next links
        "button[class*='next']",             # Generic next buttons
        "a[aria-label='Next']",
        "a[rel='next']",
        "li.next > a",
        ".pagination a:last-child",
        "nav[aria-label='Pagination'] a:last-child",
        "a:has-text('Next')",
        "a:has-text('next')",
        "button:has-text('Next')",
        "button:has-text('Load More')",
        "button:has-text('Show More')",
    ]

    # Try to find a working next/pagination button
    found_pagination = False
    for selector in common_next_selectors:
        try:
            btn = page.query_selector(selector)
            if btn and btn.is_visible():
                logger.info(f"Auto-detected pagination with selector: {selector}")
                dom_snapshots = _paginate_by_clicking(page, selector)
                found_pagination = True
                break
        except Exception:
            continue

    if not found_pagination:
        # Try smart scroll (might be infinite scroll that analyzer missed)
        initial_height = page.evaluate("document.body.scrollHeight")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(SCROLL_WAIT_MS)
        new_height = page.evaluate("document.body.scrollHeight")

        if new_height > initial_height:
            # Page has infinite scroll
            logger.info("Auto-detected infinite scroll")
            content = _smart_scroll(page)
            dom_snapshots.append(minify_html(content))
        else:
            # Single page — just grab everything
            logger.info("Single page detected, capturing full content")
            content = page.content()
            dom_snapshots.append(minify_html(content))

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
            # Static fetch is sufficient — fast path
            logger.info(f"[{session_id}] BrowserAgent using static HTTP fetch for {target_url}")
            html = await _fetch_static_html(target_url)
            if html:
                input_data["dom_snapshots"] = [minify_html(html)]
            else:
                input_data["dom_snapshots"] = []
            return input_data

        # JS rendering required — use Playwright in a separate thread
        logger.info(f"[{session_id}] BrowserAgent starting Playwright (threaded) for {target_url}")

        try:
            dom_snapshots = await asyncio.to_thread(
                _run_playwright_sync, target_url, analysis
            )
            logger.info(f"[{session_id}] BrowserAgent captured {len(dom_snapshots)} page snapshots")
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
