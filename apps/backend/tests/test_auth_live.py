import asyncio
import sys
import os
import uuid
import httpx
from datetime import datetime

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from sqlmodel import select, delete
from database.connection import get_session
from models.user import User

async def run_auth_tests():
    test_id = uuid.uuid4().hex[:8]
    test_email = f"authtest_{test_id}@example.com"
    test_password = "Password123!"
    test_name = f"Auth Tester {test_id}"
    created_user_ids = []

    print(f"\n==========================================")
    print(f"STARTING COMPREHENSIVE AUTH SYSTEM TESTS")
    print(f"Target: In-Process FastAPI App with LIVE Neon PostgreSQL & Upstash Redis")
    print(f"Test Email: {test_email}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"==========================================\n")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        # 1. Health check
        print("[TEST 1] Backend Health Check")
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.status_code} {res.text}"
        print(f"  --> PASSED: {res.json()}")

        # 2. Password Validation Tests
        print("\n[TEST 2] Password Validation Rules")
        weak_passwords = [
            ("short1", "Password must be at least 8 characters long."),
            ("nouppercase123", "Password must contain at least one uppercase letter."),
            ("NoNumberPass", "Password must contain at least one number."),
        ]
        for weak_pwd, expected_err in weak_passwords:
            res = await client.post("/api/auth/register", json={
                "email": f"weak_{test_id}@example.com",
                "password": weak_pwd,
                "full_name": "Weak Pwd"
            })
            assert res.status_code == 400, f"Expected 400 for '{weak_pwd}', got {res.status_code}"
            assert expected_err in res.json().get("detail", ""), f"Unexpected error detail: {res.json()}"
            print(f"  --> Rejected '{weak_pwd}': '{res.json()['detail']}'")

        # 3. User Registration
        print("\n[TEST 3] Valid User Registration")
        reg_payload = {
            "email": test_email,
            "password": test_password,
            "full_name": test_name
        }
        res = await client.post("/api/auth/register", json=reg_payload)
        assert res.status_code == 200, f"Registration failed: {res.status_code} {res.text}"
        user_data = res.json()
        assert user_data["email"] == test_email
        assert user_data["full_name"] == test_name
        assert "hashed_password" not in user_data or user_data["hashed_password"] is None
        user_id = user_data["id"]
        created_user_ids.append(user_id)
        print(f"  --> PASSED: Registered user ID: {user_id}, Email: {user_data['email']}")

        # 4. Duplicate Registration Prevention
        print("\n[TEST 4] Duplicate Registration Prevention")
        res = await client.post("/api/auth/register", json=reg_payload)
        assert res.status_code == 400, f"Expected 400 for duplicate, got {res.status_code}"
        assert "already exists" in res.json().get("detail", "").lower()
        print(f"  --> PASSED: Correctly rejected duplicate email: {res.json()['detail']}")

        # 5. Login with Bad Credentials
        print("\n[TEST 5] Login with Incorrect Password")
        res = await client.post("/api/auth/login", data={
            "username": test_email,
            "password": "WrongPassword123!"
        })
        assert res.status_code == 400, f"Expected 400, got {res.status_code}"
        assert "incorrect" in res.json().get("detail", "").lower()
        print(f"  --> PASSED: Rejected bad password: {res.json()['detail']}")

        print("\n[TEST 6] Login with Non-Existent Email")
        res = await client.post("/api/auth/login", data={
            "username": f"nonexistent_{test_id}@example.com",
            "password": test_password
        })
        assert res.status_code == 400, f"Expected 400, got {res.status_code}"
        assert "incorrect" in res.json().get("detail", "").lower()
        print(f"  --> PASSED: Rejected non-existent user: {res.json()['detail']}")

        # 6. Successful Login
        print("\n[TEST 7] Login with Valid Credentials")
        res = await client.post("/api/auth/login?remember_me=true", data={
            "username": test_email,
            "password": test_password
        })
        assert res.status_code == 200, f"Login failed: {res.status_code} {res.text}"
        login_data = res.json()
        access_token = login_data.get("access_token")
        assert access_token, "No access token in response"
        assert login_data.get("token_type") == "bearer"
        
        refresh_cookie = client.cookies.get("refresh_token")
        assert refresh_cookie, "No refresh_token cookie set in response headers"
        print(f"  --> PASSED: Received access token ({len(access_token)} chars)")
        print(f"  --> Refresh cookie received: {refresh_cookie[:15]}...")

        # 7. Access Protected Route (/api/auth/me)
        print("\n[TEST 8] Verify Current User (/api/auth/me)")
        headers = {"Authorization": f"Bearer {access_token}"}
        res = await client.get("/api/auth/me", headers=headers)
        assert res.status_code == 200, f"/me failed: {res.status_code} {res.text}"
        me_data = res.json()
        assert me_data["id"] == user_id
        assert me_data["email"] == test_email
        print(f"  --> PASSED: Authenticated as {me_data['email']} (ID: {me_data['id']})")

        # 8. Token Refresh
        print("\n[TEST 9] Token Refresh (/api/auth/refresh)")
        res = await client.post("/api/auth/refresh")
        assert res.status_code == 200, f"Refresh failed: {res.status_code} {res.text}"
        new_token_data = res.json()
        new_access_token = new_token_data.get("access_token")
        assert new_access_token, "No new access token"
        print(f"  --> PASSED: New access token acquired: {new_access_token[:20]}...")

        # 9. Verify New Token Works on /me
        print("\n[TEST 10] Verify New Token Works on /api/auth/me")
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        res = await client.get("/api/auth/me", headers=new_headers)
        assert res.status_code == 200
        assert res.json()["id"] == user_id
        print(f"  --> PASSED: New token successfully verified")

        # 10. Guest Login
        print("\n[TEST 11] Guest User Login (/api/auth/guest)")
        async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as guest_client:
            res = await guest_client.post("/api/auth/guest")
            assert res.status_code == 200, f"Guest login failed: {res.status_code} {res.text}"
            guest_token = res.json().get("access_token")
            assert guest_token, "No guest access token"
            guest_cookie = guest_client.cookies.get("refresh_token")
            assert guest_cookie, "No guest refresh cookie"

            # Check /me for guest
            res_me = await guest_client.get("/api/auth/me", headers={"Authorization": f"Bearer {guest_token}"})
            assert res_me.status_code == 200
            guest_user = res_me.json()
            assert guest_user.get("is_guest") is True
            created_user_ids.append(guest_user["id"])
            print(f"  --> PASSED: Guest created with ID: {guest_user['id']}, is_guest: {guest_user['is_guest']}")

        # 11. Forgot Password Endpoint
        print("\n[TEST 12] Forgot Password Service")
        res = await client.post("/api/auth/forgot-password", json={"email": test_email})
        assert res.status_code == 200
        assert "message" in res.json()
        print(f"  --> PASSED (Existing user): {res.json()['message']}")

        res = await client.post("/api/auth/forgot-password", json={"email": "nobody@example.com"})
        assert res.status_code == 200
        assert "message" in res.json()
        print(f"  --> PASSED (Non-existing user anti-enumeration): {res.json()['message']}")

        # 12. Logout and Refresh Revocation
        print("\n[TEST 13] Logout & Refresh Token Revocation")
        res = await client.post("/api/auth/logout", headers=new_headers)
        assert res.status_code == 200, f"Logout failed: {res.status_code} {res.text}"
        print(f"  --> PASSED: Logout successful: {res.json()['message']}")

        # After logout, cookie is deleted or invalidated, attempting refresh should fail
        res = await client.post("/api/auth/refresh")
        assert res.status_code == 401, f"Expected 401 on refreshed revoked session, got {res.status_code}"
        print(f"  --> PASSED: Revoked token rejected with 401: {res.json().get('detail')}")

    # 13. Database Cleanup
    print("\n[TEST 14] Database Cleanup")
    cleaned_count = 0
    async for db in get_session():
        for uid in created_user_ids:
            statement = select(User).where(User.id == uid)
            result = await db.exec(statement)
            u = result.first()
            if u:
                await db.delete(u)
                cleaned_count += 1
        await db.commit()
        break
    print(f"  --> PASSED: Cleaned up {cleaned_count} test users from Neon PostgreSQL")

    print("\n==========================================")
    print("ALL 14 LIVE AUTHENTICATION TESTS PASSED 100%!")
    print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(run_auth_tests())
