import asyncio
import sys
import os
import httpx

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app

async def test_oauth_endpoints():
    print("\n--- Testing Google & Phone Auth Endpoint Guards ---")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=10.0) as client:
        # Test invalid Google token
        res = await client.post("/api/auth/google", json={"id_token": "invalid_fake_google_token"})
        assert res.status_code == 400, f"Expected 400 for fake token, got {res.status_code}"
        print(f"  --> Google invalid token rejected: {res.json()['detail']}")

        # Test invalid Phone token
        res = await client.post("/api/auth/phone", json={"id_token": "invalid_fake_phone_token"})
        assert res.status_code == 400, f"Expected 400 for fake phone token, got {res.status_code}"
        print(f"  --> Phone invalid token rejected: {res.json()['detail']}")

    print("--- Google & Phone Endpoint Guards PASSED ---\n")

if __name__ == "__main__":
    asyncio.run(test_oauth_endpoints())
