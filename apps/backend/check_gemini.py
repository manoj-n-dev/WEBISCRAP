import google.generativeai as genai
import os

from dotenv import load_dotenv
load_dotenv()

key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=key)

try:
    models = list(genai.list_models())
    print("Available Models:")
    for m in models:
        print(f" - {m.name} (methods: {m.supported_generation_methods})")
    if not models:
        print("No models available for this key.")
except Exception as e:
    print(f"Error: {e}")
