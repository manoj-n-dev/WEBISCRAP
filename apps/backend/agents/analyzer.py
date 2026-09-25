import re
from typing import Any, Dict

from bs4 import BeautifulSoup
from loguru import logger

from ai.router import ai_router
from core.config import settings
from core.llm_json import extract_json
from prompts.analyzer_prompt import ANALYZER_SYSTEM_PROMPT
from .base import BaseAgent, ssrf_safe_fetch

_SPA_MARKERS = ('id="root"', "id='root'", 'id="app"', "id='app'", "__NEXT_DATA__", "data-reactroot", "ng-app", "ng-version", "__NUXT__")


import urllib.parse


def is_known_private_platform_url(url: str) -> bool:
    """Identify URLs belonging to known authenticated-only user services."""
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = (parsed.netloc or "").lower()
        path = (parsed.path or "").lower()
        # ChatGPT / OpenAI private conversation sessions
        if ("chatgpt.com" in netloc or "openai.com" in netloc) and path.startswith("/c/"):
            return True
        # Claude private conversation sessions
        if "claude.ai" in netloc and path.startswith("/chat/"):
            return True
        # Webmail / private app dashboards
        if netloc in ("mail.google.com", "outlook.live.com", "mail.yahoo.com", "app.slack.com", "discord.com"):
            return True
        return False
    except Exception:
        return False


def heuristic_analysis(html_text: str, target_url: str = "") -> Dict[str, Any]:
    """Zero-LLM page analysis (saves ~3K tokens + 2-4 s per scrape). Static rendering is chosen ONLY when the
    raw HTML already contains a lot of visible text AND many repeating items; otherwise Playwright is used."""
    known_private = is_known_private_platform_url(target_url) if target_url else False
    if not html_text:
        return {
            "requires_js_rendering": True,
            "pagination_type": "none",
            "login_required": known_private,
            "url_access_issue": "private_auth" if known_private else None,
            "analysis_notes": "Static fetch failed; using a real browser."
        }
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text_len = len(soup.get_text(" ", strip=True))
    repeating = len(soup.find_all(["li", "tr", "article"]))
    spa = any(m in html_text for m in _SPA_MARKERS)
    static_ok = text_len >= 2500 and repeating >= 15 and not (spa and text_len < 6000)
    nxt = soup.find("a", attrs={"rel": re.compile("next", re.I)}) or soup.find("link", attrs={"rel": re.compile("next", re.I)})
    pagination = {"pagination_type": "link", "pagination_selector": "a[rel='next']"} if nxt else {"pagination_type": "none"}
    login = known_private or (bool(soup.find("input", attrs={"type": "password"})) and text_len < 1500)
    url_access_issue = "private_auth" if login else None
    return {
        "requires_js_rendering": (not static_ok) or bool(nxt),
        "login_required": login,
        "url_access_issue": url_access_issue,
        "analysis_notes": f"heuristic: {text_len} chars text, {repeating} repeating items, spa={spa}",
        **pagination
    }


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AnalyzerAgent")

    async def _fetch_html_snippet(self, url: str) -> str:
        """C4: static fetch via the SSRF-safe fetcher, trimmed for the (optional) LLM analysis."""
        response_text = await ssrf_safe_fetch(url)
        if not response_text:
            return "<html><body>Static fetch failed. JS rendering likely required.</body></html>"
        try:
            soup = BeautifulSoup(response_text, "html.parser")
            for script in soup(["style"]):
                script.decompose()
            body_content = soup.body.prettify()[:5000] if soup.body else ""
            head_content = soup.head.prettify()[:2000] if soup.head else ""
            return f"<head>\n{head_content}\n</head>\n<body>\n{body_content}\n</body>"
        except Exception as e:
            logger.warning(f"HTML snippet parsing failed for {url}: {e}")
            return "<html><body>Static fetch failed. JS rendering likely required.</body></html>"

    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        target_url = input_data.get("target_url")
        if not target_url:
            input_data["analysis"] = {"requires_js_rendering": False, "note": "No URL provided."}
            return input_data

        if settings.ANALYZER_MODE.lower() != "llm":
            html_text = await ssrf_safe_fetch(target_url)
            analysis = heuristic_analysis(html_text or "", target_url=target_url)
            logger.info(f"[{session_id}] Analyzer (heuristic): {analysis}")
            input_data["analysis"] = analysis          # NOTE: the planner's JS guess no longer forces a browser
            if analysis.get("url_access_issue"):
                input_data["url_access_issue"] = analysis["url_access_issue"]
            return input_data

        html_snippet = await self._fetch_html_snippet(target_url)
        prompt = f"""
        Target URL: '{target_url}'

        <untrusted_source_content>
        {html_snippet}
        </untrusted_source_content>

        Analyze the structure according to your task guidelines.
        """
        response_text = await ai_router.generate(
            task_category="analysis", prompt=prompt, system_prompt=ANALYZER_SYSTEM_PROMPT, temperature=0.2)
        analysis = extract_json(response_text, "object")
        analysis["requires_js_rendering"] = bool(analysis.get("requires_js_rendering")) or bool(input_data.get("requires_browser", False))
        logger.info(f"[{session_id}] Analyzer generated plan: {analysis}")
        input_data["analysis"] = analysis
        return input_data


analyzer_agent = AnalyzerAgent()
