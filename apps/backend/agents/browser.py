import asyncio
import sys
from typing import Dict, Any, List
from .base import BaseAgent, validate_target_url, validate_resolved_ip, ssrf_safe_fetch
from loguru import logger
from bs4 import BeautifulSoup
import httpx
import re
import socket
import urllib.parse
from core.config import settings


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

    # C2 & H-12: Validate the target URL against SSRF before launching Chromium
    if not validate_target_url(target_url):
        raise ValueError(f"Blocked SSRF attempt: {target_url} failed security validation")

    target_hostname = urllib.parse.urlparse(target_url).hostname
    resolved_ip = None
    if target_hostname:
        try:
            addr_infos = socket.getaddrinfo(target_hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            if addr_infos:
                resolved_ip = addr_infos[0][4][0]
        except socket.gaierror as e:
            logger.warning(f"Failed to resolve target hostname {target_hostname}: {e}")

    with sync_playwright() as p:
        launch_args = []
        if target_hostname and resolved_ip:
            launch_args.append(f"--host-resolver-rules=MAP {target_hostname} {resolved_ip}")

        # H-10: Do NOT ignore HTTPS certificate errors by default in production
        allow_insecure_ssl = getattr(settings, "ALLOW_INSECURE_SSL", False) and settings.ENVIRONMENT.lower() == "development"

        browser = p.chromium.launch(headless=True, args=launch_args)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=allow_insecure_ssl,
        )
        page = context.new_page()

        try:
            # C2 & H-11 & H-12: SSRF and DNS rebinding protection for subresources (Fail-Closed)
            def ssrf_route_handler(route):
                """Abort requests to internal/private IPs for subresources (Fail-Closed)."""
                request_url = route.request.url
                try:
                    hostname = urllib.parse.urlparse(request_url).hostname
                    if hostname:
                        # H-12: Validate all addresses returned for this host
                        addr_infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
                        for addr_info in addr_infos:
                            ip_addr: str = str(addr_info[4][0])  # typeshed: str|int; str() is safe
                            if not validate_resolved_ip(ip_addr):
                                logger.warning(f"Playwright SSRF block: {request_url} resolved to unsafe IP {ip_addr}")
                                route.abort()
                                return
                    route.continue_()
                except Exception as e:
                    # H-11: Fail-closed on unexpected errors or DNS failures
                    logger.warning(f"SSRF route handler error for {request_url}, aborting (fail-closed): {e}")
                    try:
                        route.abort()
                    except Exception:
                        pass
            
            page.route("**/*", ssrf_route_handler)
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


# H-09: Forbidden dangerous action keywords for browser automation clicking
DANGEROUS_CLICK_KEYWORDS = {
    "submit", "buy", "cart", "checkout", "pay", "order", "purchase",
    "delete", "remove", "drop", "destroy", "logout", "log out", "sign out",
    "login", "log in", "sign in", "register", "signup", "cancel", "terminate",
    "post", "send", "publish", "update", "modify"
}

def _is_safe_pagination_element(page, element, selector: str) -> bool:
    """
    H-09: Enforce strict guardrails against arbitrary state-changing button clicks.
    Validates that a candidate element is exclusively a benign navigation or pagination control.
    """
    selector_lower = selector.lower()
    for forbidden in DANGEROUS_CLICK_KEYWORDS:
        if forbidden in selector_lower:
            logger.warning(f"[Browser Guardrail] Rejected dangerous selector containing '{forbidden}': {selector}")
            return False

    try:
        tag_name = page.evaluate("(el) => el.tagName", element)
        btn_type = page.evaluate("(el) => (el.getAttribute('type') || '').toLowerCase()", element)
        if btn_type == "submit":
            logger.warning(f"[Browser Guardrail] Rejected element with type='submit': {selector}")
            return False

        text_content = (page.evaluate("(el) => el.textContent || ''", element) or "").strip().lower()
        aria_label = (page.evaluate("(el) => el.getAttribute('aria-label') || ''", element) or "").strip().lower()
        title_attr = (page.evaluate("(el) => el.getAttribute('title') || ''", element) or "").strip().lower()

        combined_text = f"{text_content} {aria_label} {title_attr}"

        # Check for forbidden state-changing action keywords in element text
        for forbidden in DANGEROUS_CLICK_KEYWORDS:
            # Word boundary or standalone match
            if f" {forbidden} " in f" {combined_text} " or combined_text == forbidden:
                logger.warning(f"[Browser Guardrail] Rejected element containing forbidden action '{forbidden}': '{combined_text}'")
                return False

        # Positive indicator: must resemble pagination/navigation
        safe_indicators = ["next", "more", "load more", "show more", ">", "»", "›", "page", "weiter", "suivant", "siguiente"]
        has_safe_indicator = any(ind in combined_text for ind in safe_indicators)
        is_page_number = text_content.isdigit() or (len(text_content) <= 4 and text_content.strip().isdigit())

        if not (has_safe_indicator or is_page_number):
            logger.warning(f"[Browser Guardrail] Rejected element lacking pagination indicators: '{combined_text}' (selector: {selector})")
            return False

        return True
    except Exception as e:
        logger.warning(f"[Browser Guardrail] Element safety inspection failed: {e}")
        return False


def _paginate_by_clicking(page, selector: str) -> List[str]:
    """
    Clicks a pagination button/link repeatedly to collect data from multiple pages.
    Guarded by H-09 safe pagination element verification.
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

            # H-09: Validate element safety before clicking
            if not _is_safe_pagination_element(page, next_btn, selector):
                logger.warning(f"Pagination halted: element at '{selector}' is not a verified safe pagination control.")
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

    # Common pagination selectors for universal pagination detection
    common_next_selectors = [
        "a[class*='next']",                  # Generic next links
        "button[class*='next']",             # Generic next buttons
        "a[aria-label*='Next' i]",
        "a[rel='next']",
        "li.next > a",
        ".pagination a:last-child",
        "nav[aria-label*='Pagination' i] a:last-child",
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
    """C4: Fetch page HTML using SSRF-safe redirect-walking fetcher."""
    result = await ssrf_safe_fetch(target_url)
    return result or ""


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
