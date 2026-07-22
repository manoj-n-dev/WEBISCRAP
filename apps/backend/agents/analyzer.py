import json
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any
from .base import BaseAgent
from ai.router import ai_router
from prompts.analyzer_prompt import ANALYZER_SYSTEM_PROMPT
from loguru import logger

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AnalyzerAgent")
        
    async def _fetch_html_snippet(self, url: str) -> str:
        """Fetches the page statically to get the initial HTML snippet."""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Use BeautifulSoup to extract head and a portion of body
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style tags to save tokens, unless they indicate SPA
                for script in soup(["style"]):
                    script.decompose()
                    
                body_content = soup.body.prettify()[:5000] if soup.body else ""
                head_content = soup.head.prettify()[:2000] if soup.head else ""
                
                return f"<head>\n{head_content}\n</head>\n<body>\n{body_content}\n</body>"
        except Exception as e:
            logger.warning(f"Static fetch failed for {url}: {e}")
            return "<html><body>Static fetch failed. JS rendering likely required.</body></html>"

    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        target_url = input_data.get("target_url")
        if not target_url:
            return {"analysis": "No URL provided."}
            
        # Fetch static HTML snippet
        html_snippet = await self._fetch_html_snippet(target_url)
        
        prompt = f"Target URL: '{target_url}'\nHTML Snippet:\n```html\n{html_snippet}\n```\nAnalyze the structure."
        
        # Route to analysis model (Gemini)
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
            logger.error(f"[{session_id}] Analyzer failed to output valid JSON. Output: {response_text}")
            raise ValueError("Analyzer output was not valid JSON.") from e

analyzer_agent = AnalyzerAgent()
