import json
from bs4 import BeautifulSoup
from typing import Dict, Any
from .base import BaseAgent, ssrf_safe_fetch
from ai.router import ai_router
from prompts.analyzer_prompt import ANALYZER_SYSTEM_PROMPT
from loguru import logger

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AnalyzerAgent")
        
    async def _fetch_html_snippet(self, url: str) -> str:
        """C4: Fetches the page statically using SSRF-safe redirect-walking fetcher."""
        response_text = await ssrf_safe_fetch(url)
        if not response_text:
            return "<html><body>Static fetch failed. JS rendering likely required.</body></html>"
        
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Remove style tags to save tokens
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
            return {"analysis": "No URL provided."}
            
        # Fetch static HTML snippet
        html_snippet = await self._fetch_html_snippet(target_url)
        
        prompt = f"Target URL: '{target_url}'\nHTML Snippet:\n```html\n{html_snippet}\n```\nAnalyze the structure."
        
        # Route to analysis model
        response_text = await ai_router.generate(
            task_category="analysis",
            prompt=prompt,
            system_prompt=ANALYZER_SYSTEM_PROMPT,
            temperature=0.2
        )
        
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            analysis = json.loads(response_text)
            
            # Merge planner knowledge with analyzer knowledge
            planner_said_js = input_data.get("requires_browser", False)
            analysis["requires_js_rendering"] = analysis.get("requires_js_rendering") or planner_said_js
            
            logger.info(f"[{session_id}] Analyzer generated plan: {analysis}")
            
            # Combine previous input data with analysis
            input_data.update({"analysis": analysis})
            return input_data
            
        except json.JSONDecodeError as e:
            logger.error(f"[{session_id}] Analyzer failed to output valid JSON. Error: {e}. Snippet: {response_text[:200]}")
            raise ValueError("Analyzer output was not valid JSON.") from e

analyzer_agent = AnalyzerAgent()
