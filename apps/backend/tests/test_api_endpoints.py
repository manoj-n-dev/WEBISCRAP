import unittest
import sys
import os
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from memory.session_store import redis_store
from database.connection import engine
from auth.security import create_verification_token

class TestApiEndpoints(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=self.transport, base_url="http://testserver")
        await redis_store.connect()
        # Reset rate limit key for test client so tests don't exhaust the quota
        await redis_store.delete("rate_limit:127.0.0.1", "rate_limit:testclient", "rate_limit:unknown")

        # Unique user credentials for isolation
        suffix = uuid.uuid4().hex[:6]
        self.email = f"testuser_{suffix}@example.com"
        self.password = "StrongPass123!"
        self.user_token = None
        self.refresh_token = None

    async def asyncTearDown(self):
        await redis_store.delete("rate_limit:127.0.0.1", "rate_limit:testclient", "rate_limit:unknown")
        await self.client.aclose()
        await redis_store.close()
        await engine.dispose()

    async def test_health_check(self):
        """Test GET /health returns ok."""
        res = await self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")

    async def test_auth_full_lifecycle(self):
        """
        Comprehensive test of Auth flow:
        1. Register user
        2. Prevent weak password
        3. Prevent duplicate registration (FIX 9: returns 400 Bad Request, not 500)
        4. Login (returns access_token + refresh cookie)
        5. Access /api/auth/me with Bearer token
        6. Access /api/auth/me without token -> 401
        7. Refresh access token (FIX 6: verifies token rotation & JTI blacklisting)
        8. Replay attack rejection with old refresh token
        9. Logout
        """
        # 1. Weak password rejected
        weak_res = await self.client.post("/api/auth/register", json={
            "email": f"weak_{uuid.uuid4().hex[:6]}@example.com",
            "password": "weak"
        })
        self.assertEqual(weak_res.status_code, 400)

        # 2. Valid Registration
        reg_res = await self.client.post("/api/auth/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": "Test User"
        })
        self.assertEqual(reg_res.status_code, 200)
        reg_data = reg_res.json()
        self.assertEqual(reg_data["email"], self.email)
        self.assertIn("id", reg_data)

        # 3. Duplicate Registration (FIX 9: must return 400 Bad Request instead of 500 IntegrityError)
        dup_res = await self.client.post("/api/auth/register", json={
            "email": self.email,
            "password": self.password
        })
        self.assertEqual(dup_res.status_code, 400)
        self.assertIn("already exists", dup_res.json()["detail"])

        # Unverified user cannot login -> 403 Forbidden
        unverified_login = await self.client.post("/api/auth/login", data={
            "username": self.email,
            "password": self.password
        })
        self.assertEqual(unverified_login.status_code, 403)

        # Verify email using single-use verification token
        verify_token = create_verification_token(uuid.UUID(reg_data["id"]))
        verify_res = await self.client.get(f"/api/auth/verify-email?token={verify_token}")
        self.assertEqual(verify_res.status_code, 200)

        # 4. Login after verification
        login_res = await self.client.post("/api/auth/login", data={
            "username": self.email,
            "password": self.password
        })
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.json()
        self.assertIn("access_token", login_data)
        self.user_token = login_data["access_token"]
        
        # Verify refresh cookie was set
        cookies = login_res.cookies
        self.assertIn("refresh_token", cookies)
        old_refresh_token = cookies["refresh_token"]

        # 5. Access /api/auth/me
        me_res = await self.client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {self.user_token}"
        })
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["email"], self.email)

        # 6. Access /api/auth/me without token -> 401
        unauth_res = await self.client.get("/api/auth/me")
        self.assertEqual(unauth_res.status_code, 401)

        # 7. Refresh token rotation (FIX 6)
        refresh_res = await self.client.post(
            "/api/auth/refresh",
            cookies={"refresh_token": old_refresh_token}
        )
        self.assertEqual(refresh_res.status_code, 200)
        new_token_data = refresh_res.json()
        self.assertIn("access_token", new_token_data)
        new_refresh_cookie = refresh_res.cookies.get("refresh_token")
        self.assertIsNotNone(new_refresh_cookie)

        # 8. Replay attack rejection: Using old_refresh_token again MUST FAIL (401)
        replay_res = await self.client.post(
            "/api/auth/refresh",
            cookies={"refresh_token": old_refresh_token}
        )
        self.assertEqual(replay_res.status_code, 401)
        self.assertIn("revoked", replay_res.json()["detail"])

        # 9. Logout
        logout_res = await self.client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {new_token_data['access_token']}"},
            cookies={"refresh_token": new_refresh_cookie}
        )
        self.assertEqual(logout_res.status_code, 200)

        # 10. Verify refresh token is revoked after logout
        post_logout_refresh = await self.client.post(
            "/api/auth/refresh",
            cookies={"refresh_token": new_refresh_cookie}
        )
        self.assertEqual(post_logout_refresh.status_code, 401)

    async def test_guest_user_creation(self):
        """Test creating an ephemeral guest user."""
        res = await self.client.post("/api/auth/guest")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertIn("user_id", data)

    async def test_chat_idor_protection_fail_closed(self):
        """
        Test FIX 5: Fail-closed IDOR protection in chat.py
        - If User A creates a session, User B is blocked (403).
        - If a session has no owner, User B is blocked (403).
        - User A can access their own session.
        """
        # Register User A and verify email
        user_a_email = f"user_a_{uuid.uuid4().hex[:6]}@example.com"
        reg_a = await self.client.post("/api/auth/register", json={"email": user_a_email, "password": "UserPass123!"})
        user_a_id = reg_a.json()["id"]
        token_a_verify = create_verification_token(uuid.UUID(user_a_id))
        await self.client.get(f"/api/auth/verify-email?token={token_a_verify}")

        login_a = await self.client.post("/api/auth/login", data={"username": user_a_email, "password": "UserPass123!"})
        token_a = login_a.json()["access_token"]

        # Register User B and verify email
        user_b_email = f"user_b_{uuid.uuid4().hex[:6]}@example.com"
        reg_b = await self.client.post("/api/auth/register", json={"email": user_b_email, "password": "UserPass123!"})
        user_b_id = reg_b.json()["id"]
        token_b_verify = create_verification_token(uuid.UUID(user_b_id))
        await self.client.get(f"/api/auth/verify-email?token={token_b_verify}")

        login_b = await self.client.post("/api/auth/login", data={"username": user_b_email, "password": "UserPass123!"})
        token_b = login_b.json()["access_token"]

        # Setup a session owned by User A
        test_session_id = f"idor_test_{uuid.uuid4().hex[:8]}"
        await redis_store.set_session_owner(test_session_id, str(user_a_id))
        await redis_store.add_user_session(str(user_a_id), test_session_id)
        await redis_store.set_pipeline_progress(test_session_id, "browse")

        # 1. User A checks progress -> 200 OK
        res_a_progress = await self.client.get(
            f"/api/chat/{test_session_id}/progress",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        self.assertEqual(res_a_progress.status_code, 200)
        self.assertEqual(res_a_progress.json()["step"], "browse")

        # 2. User B tries to access User A's progress -> 403 Forbidden!
        res_b_progress = await self.client.get(
            f"/api/chat/{test_session_id}/progress",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        self.assertEqual(res_b_progress.status_code, 403)

        # 3. User B tries to access User A's history -> 403 Forbidden!
        res_b_history = await self.client.get(
            f"/api/chat/{test_session_id}/history",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        self.assertEqual(res_b_history.status_code, 403)

        # 4. User B tries to post a message into User A's session -> 403 Forbidden!
        res_b_chat = await self.client.post(
            "/api/chat/",
            json={"session_id": test_session_id, "message": "Malicious attempt"},
            headers={"Authorization": f"Bearer {token_b}"}
        )
        self.assertEqual(res_b_chat.status_code, 403)

        # 5. Missing owner session test -> must fail-closed (403 Forbidden!)
        orphan_session = f"orphan_{uuid.uuid4().hex[:8]}"
        res_orphan = await self.client.get(
            f"/api/chat/{orphan_session}/progress",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        self.assertEqual(res_orphan.status_code, 403)

        # Clean up
        await redis_store.delete(
            f"session:{test_session_id}:owner",
            f"pipeline_progress:{test_session_id}",
            f"user_sessions:{user_a_id}"
        )

    async def test_file_upload_validation_and_session_association(self):
        """Test FIX 13: File upload validation, size check, and session association."""
        # Create guest user for upload
        guest_res = await self.client.post("/api/auth/guest")
        token = guest_res.json()["access_token"]
        session_id = f"upload_sess_{uuid.uuid4().hex[:6]}"

        # 1. Reject invalid file extension (.exe)
        invalid_file = ("bad.exe", b"malicious binary content", "application/octet-stream")
        res_invalid = await self.client.post(
            "/api/upload/",
            files={"file": invalid_file},
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res_invalid.status_code, 400)
        self.assertIn("Unsupported file extension", res_invalid.json()["detail"])

        # 2. Upload valid CSV file with session_id query param (FIX 13)
        csv_content = b"Name,Price,Qty\nWidget,19.99,100\nGadget,29.99,50"
        valid_file = ("inventory.csv", csv_content, "text/csv")
        res_valid = await self.client.post(
            f"/api/upload/?session_id={session_id}",
            files={"file": valid_file},
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res_valid.status_code, 200)
        upload_data = res_valid.json()
        self.assertEqual(upload_data["status"], "success")
        file_id = upload_data["file_id"]

        # 3. Verify Redis stored uploaded context associated with session_id (FIX 13)
        cached_context = await redis_store.get_uploaded_context(session_id, file_id)
        self.assertIsNotNone(cached_context)
        self.assertIn("Widget", cached_context)
        self.assertIn("Gadget", cached_context)

    async def test_export_download_security(self):
        """Test Export API path traversal protection and authorization check."""
        guest_res = await self.client.post("/api/auth/guest")
        token = guest_res.json()["access_token"]

        # 1. Path traversal attempt must be rejected (400)
        res_traversal = await self.client.get(
            "/api/export/download/../../etc/passwd",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertIn(res_traversal.status_code, [400, 404])

        # 2. Downloading another user's file prefix must be rejected (403)
        foreign_filename = "different_user_prefix_webiscrap_2026.csv"
        res_foreign = await self.client.get(
            f"/api/export/download/{foreign_filename}",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res_foreign.status_code, 403)

if __name__ == "__main__":
    unittest.main()
