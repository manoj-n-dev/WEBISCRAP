import asyncio
import os
import sys
import json
from loguru import logger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from agents.orchestrator import orchestrator

async def run_test(name: str, url: str, prompt: str):
    logger.info(f"--- Running Test: {name} ---")
    logger.info(f"URL: {url}")
    logger.info(f"Prompt: {prompt}")
    
    session_id = f"test_session_{name.lower().replace(' ', '_')}"
    
    try:
        result = await orchestrator.execute_pipeline(
            user_request=prompt,
            target_url=url,
            session_id=session_id
        )
        
        if result["status"] == "success":
            logger.success(f"Test {name} completed successfully!")
            
            # Print some highlights
            data = result.get("data", {})
            cleaned_data = data.get("cleaned_data", [])
            validation = data.get("validation", {})
            conversation_response = data.get("answer", "")
            
            print(f"\n[{name}] Validation Score: {validation.get('score', 'N/A')}")
            print(f"[{name}] Extracted Items Count: {len(cleaned_data)}")
            print(f"[{name}] Extracted Sample (first item): {json.dumps(cleaned_data[0] if cleaned_data else {}, indent=2)}")
            print(f"[{name}] Final Answer:\n{conversation_response}\n")
            
        else:
            logger.error(f"Test {name} failed: {result['message']}")
            
    except Exception as e:
        logger.error(f"Test {name} threw an exception: {e}")

async def main():
    logger.info("Initializing Orchestrator Test...")
    
    # Test 1: Static Site
    await run_test(
        name="Static HackerNews",
        url="https://news.ycombinator.com/",
        prompt="Extract the titles, points, and usernames of the top 5 articles on this page."
    )
    
    # Test 2: Dynamic Site (JavaScript required)
    await run_test(
        name="Dynamic Quotes",
        url="https://quotes.toscrape.com/js/",
        prompt="Extract all the quotes and the authors from this page."
    )

if __name__ == "__main__":
    asyncio.run(main())
