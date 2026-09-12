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
from sqlmodel import select
from database.connection import get_session
from models.user import User
from auth.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    create_verification_token,
    decode_access_token,
    decode_refresh_token,
    decode_reset_token,
    decode_verification_token,
)
from memory.session_store import redis_store

async def run_production_auth_tests():
    test_id = uuid.uuid4().hex[:8]
    test_email = f"prod_auth_{test_id}@example.com"
    password = "StrongPassword123!"
    created_user_ids = []

    print("\n============================================================")
    print("WEBISCRAP PHASE 1: PRODUCTION AUTHENTICATION TEST SUITE")
    print(f"Test Run ID: {test_id}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("============================================================\n")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:

        # ------------------------------------------------------------------
        # TEST 1: Registration Mass-Assignment & Privilege Escalation Attack
        # ------------------------------------------------------------------
        print("[TEST 1] Testing Registration Mass-Assignment Prevention")
        # Attacker attempts to inject privileged fields into registration
        malicious_payload = {
            "email": test_email,
            "password": password,
            "full_name": f"Privilege Attacker {test_id}",
            "is_superuser": True,
            "is_active": True,
            "is_guest": True,
            "is_verified": True,
            "token_version": 99
        }
        reg_res = await client.post("/api/auth/register", json=malicious_payload)
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        reg_data = reg_res.json()
        user_id = reg_data["id"]
        created_user_ids.append(user_id)

        # Inspect DB directly to verify privileged fields were NOT accepted
        async for db in get_session():
            st = select(User).where(User.id == user_id)
            res = await db.exec(st)
            db_user = res.first()
            assert db_user is not None
            assert db_user.is_superuser is False, "CRITICAL: is_superuser was injected!"
            assert db_user.is_guest is False, "CRITICAL: is_guest was injected!"
            assert db_user.is_verified is False, "CRITICAL: is_verified was injected!"
            assert db_user.token_version == 1, "CRITICAL: token_version was injected!"
            break
        print("  --> PASSED: Mass-assignment prevented! All privileged fields forced to safe defaults.")

        # ------------------------------------------------------------------
        # TEST 2: Login Guard Blocks Unverified Users
        # ------------------------------------------------------------------
        print("\n[TEST 2] Testing Login Verification Guard (Unverified User Must Be Blocked)")
        unverified_login = await client.post("/api/auth/login", data={
            "username": test_email,
            "password": password
        })
        assert unverified_login.status_code == 403, f"Expected 403 for unverified user, got {unverified_login.status_code}"
        assert "not verified" in unverified_login.json().get("detail", "").lower()
        print(f"  --> PASSED: Unverified login blocked with HTTP 403: '{unverified_login.json()['detail']}'")

        # ------------------------------------------------------------------
        # TEST 3: JWT Positive Token Type Isolation & Cross-Token Confusion
        # ------------------------------------------------------------------
        print("\n[TEST 3] Testing JWT Token Type Confusion Defense")
        # Generate tokens of various purposes
        access_tok = create_access_token(user_id)
        refresh_tok = create_refresh_token(user_id)
        reset_tok = create_reset_token(user_id)
        verify_tok = create_verification_token(user_id)

        # 3a. Verify internal decoders enforce positive types
        assert decode_access_token(access_tok) is not None, "Valid access token should decode"
        assert decode_access_token(refresh_tok) is None, "Refresh token must NOT decode as access token"
        assert decode_access_token(reset_tok) is None, "Reset token must NOT decode as access token"
        assert decode_access_token(verify_tok) is None, "Verify token must NOT decode as access token"

        assert decode_refresh_token(refresh_tok) is not None, "Valid refresh token should decode"
        assert decode_refresh_token(access_tok) is None, "Access token must NOT decode as refresh token"
        assert decode_refresh_token(reset_tok) is None, "Reset token must NOT decode as refresh token"

        assert decode_reset_token(reset_tok) is not None, "Valid reset token should decode"
        assert decode_reset_token(access_tok) is None, "Access token must NOT decode as reset token"

        assert decode_verification_token(verify_tok) is not None, "Valid verification token should decode"
        assert decode_verification_token(access_tok) is None, "Access token must NOT decode as verify token"

        # 3b. Test cross-token attacks against live API endpoints
        # Cross attack: Using refresh token on /api/auth/me (expects access token)
        me_with_refresh = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {refresh_tok}"})
        assert me_with_refresh.status_code == 401, f"Expected 401 using refresh token as access, got {me_with_refresh.status_code}"

        # Cross attack: Using reset token on /api/auth/me
        me_with_reset = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {reset_tok}"})
        assert me_with_reset.status_code == 401, f"Expected 401 using reset token as access, got {me_with_reset.status_code}"

        # Cross attack: Using verify token on /api/auth/me
        me_with_verify = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {verify_tok}"})
        assert me_with_verify.status_code == 401, f"Expected 401 using verify token as access, got {me_with_verify.status_code}"

        print("  --> PASSED: Cross-token attacks rejected! Token purpose is strictly isolated.")

        # ------------------------------------------------------------------
        # TEST 4: Email Verification Flow & Single-Use Enforcement
        # ------------------------------------------------------------------
        print("\n[TEST 4] Testing Email Verification Lifecycle")
        dev_verify_url = reg_data.get("dev_verify_url")
        assert dev_verify_url, "dev_verify_url should be provided in non-production mode"
        raw_token = dev_verify_url.split("token=")[-1]

        # 4a. Verify account with valid token
        verify_res = await client.get(f"/api/auth/verify-email?token={raw_token}")
        assert verify_res.status_code == 200, f"Verification failed: {verify_res.text}"
        print(f"  --> Account verified: {verify_res.json()['message']}")

        # 4b. Verify token cannot be reused (Single-use token enforcement via Redis JTI blacklist)
        reuse_verify = await client.get(f"/api/auth/verify-email?token={raw_token}")
        assert reuse_verify.status_code == 400, f"Expected 400 on token reuse, got {reuse_verify.status_code}"
        assert "already been used" in reuse_verify.json().get("detail", "").lower()
        print("  --> PASSED: Reused verification token rejected.")

        # 4c. Verified user can now log in
        login_res = await client.post("/api/auth/login", data={
            "username": test_email,
            "password": password
        })
        assert login_res.status_code == 200, f"Login failed for verified user: {login_res.text}"
        session_a_tokens = login_res.json()
        session_a_access = session_a_tokens["access_token"]
        session_a_cookie = login_res.cookies.get("refresh_token")
        print("  --> PASSED: Verified user logged in successfully (Session A created).")

        # ------------------------------------------------------------------
        # TEST 5: Password Reset Session Revocation (Section 10 / C-03)
        # ------------------------------------------------------------------
        print("\n[TEST 5] Testing Password Reset Global Session Invalidation")
        # Session A can access /api/auth/me
        me_res = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {session_a_access}"})
        assert me_res.status_code == 200, f"Session A me failed: {me_res.text}"

        # Request password reset
        forgot_res = await client.post("/api/auth/forgot-password", json={"email": test_email})
        assert forgot_res.status_code == 200
        reset_token = forgot_res.json()["dev_reset_url"].split("token=")[-1]

        # Perform password reset to new password
        new_password = "BrandNewPassword999!"
        reset_res = await client.post("/api/auth/reset-password", json={
            "token": reset_token,
            "new_password": new_password
        })
        assert reset_res.status_code == 200, f"Reset failed: {reset_res.text}"
        print(f"  --> Password reset completed: {reset_res.json()['message']}")

        # Verify Session A access token is NOW INVALIDATED
        me_after_reset = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {session_a_access}"})
        assert me_after_reset.status_code == 401, f"Expected 401 for old session after password reset, got {me_after_reset.status_code}"
        print("  --> PASSED: Old Session A access token successfully rejected with HTTP 401!")

        # Verify Session A refresh token is NOW INVALIDATED
        assert session_a_cookie is not None, "session_a_cookie should be present"
        refresh_client = httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0)
        refresh_client.cookies.set("refresh_token", session_a_cookie)
        refresh_after_reset = await refresh_client.post("/api/auth/refresh")
        assert refresh_after_reset.status_code == 401, f"Expected 401 for old refresh token, got {refresh_after_reset.status_code}"
        print("  --> PASSED: Old Session A refresh token successfully rejected with HTTP 401!")
        await refresh_client.aclose()

        # Login with new password succeeds (Session B)
        new_login = await client.post("/api/auth/login", data={
            "username": test_email,
            "password": new_password
        })
        assert new_login.status_code == 200
        print("  --> PASSED: Login with new password succeeded (Session B created).")

        # ------------------------------------------------------------------
        # TEST 6: Guest Account Creation & Conversion
        # ------------------------------------------------------------------
        print("\n[TEST 6] Testing Guest Account Creation & Permanent Conversion")
        guest_res = await client.post("/api/auth/guest")
        assert guest_res.status_code == 200, f"Guest creation failed: {guest_res.text}"
        guest_data = guest_res.json()
        guest_user_id = guest_data["user_id"]
        guest_access = guest_data["access_token"]
        created_user_ids.append(guest_user_id)

        # Convert guest account into permanent user
        guest_convert_email = f"converted_guest_{test_id}@example.com"
        convert_res = await client.post(
            "/api/auth/convert-guest",
            headers={"Authorization": f"Bearer {guest_access}"},
            json={
                "email": guest_convert_email,
                "password": "ConvertedPassword123!",
                "full_name": "Converted Guest User"
            }
        )
        assert convert_res.status_code == 200, f"Guest conversion failed: {convert_res.text}"

        # Verify guest was converted in DB and preserved same user ID
        async for db in get_session():
            st = select(User).where(User.id == guest_user_id)
            res = await db.exec(st)
            converted_user = res.first()
            assert converted_user is not None
            assert converted_user.email == guest_convert_email
            assert converted_user.is_guest is False, "User should no longer be a guest"
            assert converted_user.is_verified is False, "Newly converted account requires email verification"
            break
        print("  --> PASSED: Guest converted seamlessly to permanent account with ownership preserved.")

    # ------------------------------------------------------------------
    # DATABASE CLEANUP
    # ------------------------------------------------------------------
    print("\n[CLEANUP] Cleaning up test users from Neon PostgreSQL...")
    async for db in get_session():
        for uid in created_user_ids:
            st = select(User).where(User.id == uid)
            res = await db.exec(st)
            u = res.first()
            if u:
                await db.delete(u)
        await db.commit()
        break
    print("  --> PASSED: Test users cleaned up successfully.")

    print("\n============================================================")
    print("ALL PHASE 1 PRODUCTION AUTHENTICATION TESTS PASSED 100%!")
    print("============================================================\n")

if __name__ == "__main__":
    asyncio.run(run_production_auth_tests())
