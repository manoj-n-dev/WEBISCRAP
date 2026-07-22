import asyncio
from typing import Dict, Any, List
from playwright.async_api import async_playwright
from .base import BaseAgent
from loguru import logger
from bs4 import BeautifulSoup

def minify_html(html_content: str, max_chars: int = 25000) -> str:
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        # Remove useless tags for extraction
        for tag in soup(['script', 'style', 'noscript', 'svg', 'iframe', 'path', 'header', 'footer']):
            tag.decompose()
        # Minify
        text = str(soup)
        # Remove extra whitespace
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        # Truncate
        if len(text) > max_chars:
            text = text[:max_chars] + " <!-- TRUNCATED -->"
        return text
    except Exception as e:
        logger.warning(f"Failed to minify HTML: {e}")
        return html_content[:max_chars]

class BrowserAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="BrowserAgent")
        
    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        target_url = input_data.get("target_url")
        analysis = input_data.get("analysis", {})
        
        if not target_url:
            return input_data
            
        requires_js = analysis.get("requires_js_rendering", True)
        
        # If JS is not required, we can skip full browser automation 
        # and just use the static HTML fetched earlier if available.
        # But for reliability, we can fetch the full DOM anyway if preferred.
        # In this implementation, if requires_js is false, we just return the input.
        if not requires_js and "analysis" in input_data:
            logger.info(f"[{session_id}] BrowserAgent skipping Playwright as JS rendering is not required.")
            # Assume static parser will handle it later or Analyzer already got enough
            input_data["dom_snapshots"] = [input_data["analysis"]] # Pass static through
            return input_data

        logger.info(f"[{session_id}] BrowserAgent starting Playwright for {target_url}")
        
        dom_snapshots = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Basic stealth setup
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })
                
                await page.goto(target_url, wait_until="networkidle", timeout=30000)
                
                pagination_type = analysis.get("pagination_type", "none")
                
                if pagination_type == "infinite_scroll":
                    # Scroll down multiple times
                    for _ in range(3): # Limit to 3 scrolls for safety
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await page.wait_for_timeout(2000)
                    
                    content = await page.content()
                    dom_snapshots.append(minify_html(content))
                    
                elif pagination_type == "button" and analysis.get("pagination_selector"):
                    # Get first page
                    content = await page.content()
                    dom_snapshots.append(minify_html(content))
                    
                    # Try to click next button up to 2 times
                    selector = analysis.get("pagination_selector")
                    for _ in range(2):
                        try:
                            next_btn = await page.query_selector(selector)
                            if next_btn:
                                await next_btn.click()
                                await page.wait_for_timeout(2000)
                                content = await page.content()
                                dom_snapshots.append(minify_html(content))
                            else:
                                break
                        except Exception as e:
                            logger.warning(f"[{session_id}] Pagination click failed: {e}")
                            break
                else:
                    # Default: just grab the single page
                    content = await page.content()
                    dom_snapshots.append(minify_html(content))
                    
            except Exception as e:
                logger.error(f"[{session_id}] Playwright navigation failed: {e}")
                # We still try to return whatever we have
            finally:
                await browser.close()
                
        input_data["dom_snapshots"] = dom_snapshots
        return input_data

browser_agent = BrowserAgent()
