import asyncio
import os
from loguru import logger
import sys

# Add the apps/backend directory to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from ai.key_manager import ai_manager
from ai.providers.groq_client import GroqClient
from ai.providers.groq_client import GroqClient
from agents.planner import planner_agent
from agents.analyzer import analyzer_agent

async def test_api_keys():
    logger.info("Testing Groq Client...")
    try:
        groq_client = GroqClient()
        response = await groq_client.generate_response(
            prompt="Hello, are you working?",
            system_prompt="You are a helpful assistant. Reply with a short JSON like {'status': 'ok'}.",
            temperature=0.1
        )
        logger.success(f"Groq Response: {response}")
    except Exception as e:
        import tenacity
        real_e = e
        if isinstance(e, tenacity.RetryError):
            real_e = e.last_attempt.exception()
            
        logger.error(f"Groq Test Failed: {type(real_e).__name__}: {real_e}")
        if hasattr(real_e, 'response'):
            logger.error(f"Groq Error Body: {real_e.response.text}")
        elif hasattr(real_e, 'body'):
            logger.error(f"Groq Error Body: {real_e.body}")



async def test_agents():
    from agents.browser import browser_agent
    from agents.extractor import extractor_agent
    from agents.cleaner import cleaner_agent
    from agents.validator import validator_agent

    logger.info("Testing Planner Agent...")
    input_data = {
        "user_request": "Scrape the names and prices of all laptops from example.com/laptops.",
        "target_url": "https://example.com/laptops"
    }
    
    try:
        data = await planner_agent.run(input_data, session_id="test_session_1")
        logger.success(f"Planner Output: {data}")
    except Exception as e:
        logger.error(f"Planner Test Failed: {e}")
        return

    logger.info("Testing Analyzer Agent...")
    try:
        # Give a small fake HTML for analyzer
        data["target_url"] = "https://example.com/laptops"
        data["analysis"] = "<html><body><div class='product'>Laptop</div></body></html>"
        data = await analyzer_agent.run(data, session_id="test_session_1")
        logger.success(f"Analyzer Output: {data.get('analysis')}")
    except Exception as e:
        logger.error(f"Analyzer Test Failed: {e}")
        return

    logger.info("Testing Browser Agent (Playwright)...")
    try:
        data = await browser_agent.run(data, session_id="test_session_1")
        logger.success(f"Browser Output Snapshot Count: {len(data.get('dom_snapshots', []))}")
    except Exception as e:
        logger.error(f"Browser Test Failed: {e}")
        return

    logger.info("Testing Extractor Agent...")
    try:
        data = await extractor_agent.run(data, session_id="test_session_1")
        logger.success(f"Extractor Output Items: {len(data.get('extracted_data', []))}")
    except Exception as e:
        logger.error(f"Extractor Test Failed: {e}")
        return

    logger.info("Testing Cleaner Agent...")
    try:
        data["base_url"] = "https://example.com"
        data = await cleaner_agent.run(data, session_id="test_session_1")
        logger.success(f"Cleaner Output Items: {len(data.get('cleaned_data', []))}")
    except Exception as e:
        logger.error(f"Cleaner Test Failed: {e}")
        return

    logger.info("Testing Validator Agent...")
    try:
        data = await validator_agent.run(data, session_id="test_session_1")
        logger.success(f"Validator Output: {data.get('validation')}")
    except Exception as e:
        logger.error(f"Validator Test Failed: {e}")
        return

    logger.success("All agents successfully tested!")

async def main():
    logger.info("Loaded GROQ Keys: " + str(len(settings.GROQ_API_KEYS)))
    
    await test_api_keys()
    await test_agents()

if __name__ == "__main__":
    asyncio.run(main())
