import asyncio
import os
from groq import AsyncGroq

from dotenv import load_dotenv
load_dotenv()

key = os.environ.get("GROQ_API_KEY")

async def check_models():
    try:
        client = AsyncGroq(api_key=key)
        models = await client.models.list()
        print("Available Groq Models:")
        for m in models.data:
            print(f" - {m.id}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_models())
