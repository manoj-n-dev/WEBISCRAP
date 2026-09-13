import unittest
import sys
import os
import httpx

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app

class TestAuthProviders(unittest.IsolatedAsyncioTestCase):
    async def test_oauth_endpoints(self):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=10.0) as client:
            # Test invalid Google token
            res = await client.post("/api/auth/google", json={"id_token": "invalid_fake_google_token"})
            self.assertEqual(res.status_code, 400)

            # Test invalid Phone token
            res = await client.post("/api/auth/phone", json={"id_token": "invalid_fake_phone_token"})
            self.assertEqual(res.status_code, 400)

if __name__ == "__main__":
    unittest.main()
