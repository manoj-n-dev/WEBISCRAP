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

async def run_reset_password_tests():
    test_id = uuid.uuid4().hex[:8]
    test_email = f"reset_test_{test_id}@example.com"
    old_password = "OldPassword123!"
    new_password = "BrandNewPassword456!"
    created_user_ids = []

    print("\n==========================================")
    print("STARTING PASSWORD RESET & VERIFICATION TESTS")
    print(f"Test Email: {test_email}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("==========================================\n")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        # 1. Register test user
        print("[TEST 1] Registering Test User with Initial Password")
        reg_res = await client.post("/api/auth/register", json={
            "email": test_email,
            "password": old_password,
            "full_name": f"Reset Tester {test_id}"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        user_id = reg_res.json()["id"]
        created_user_ids.append(user_id)
        print(f"  --> Registered user {test_email} (ID: {user_id})")

        # 1b. Verify user starts unverified and login is blocked with 403
        unverified_res = await client.post("/api/auth/login", data={"username": test_email, "password": old_password})
        assert unverified_res.status_code == 403, f"Expected 403 for unverified user, got {unverified_res.status_code}"
        dev_verify = reg_res.json().get("dev_verify_url")
        assert dev_verify, "dev_verify_url should be returned in dev mode"
        v_tok = dev_verify.split("token=")[-1]
        v_res = await client.get(f"/api/auth/verify-email?token={v_tok}")
        assert v_res.status_code == 200, f"Verification failed: {v_res.text}"
        print(f"  --> Verified user {test_email}")

        # 2. Request password reset
        print("\n[TEST 2] Requesting Password Reset Link (/api/auth/forgot-password)")
        forgot_res = await client.post("/api/auth/forgot-password", json={"email": test_email})
        assert forgot_res.status_code == 200, f"Forgot password failed: {forgot_res.text}"
        forgot_data = forgot_res.json()
        assert "message" in forgot_data
        dev_url = forgot_data.get("dev_reset_url")
        assert dev_url, "dev_reset_url not returned in response during dev mode"
        reset_token = dev_url.split("token=")[-1]
        assert reset_token, "Could not parse reset token from URL"
        print(f"  --> Received reset token ({len(reset_token)} chars)")

        # 3. Test Old Password Rejection (User requirement: verifying with old password)
        print("\n[TEST 3] Rejection When New Password Equals Old Password")
        same_pwd_res = await client.post("/api/auth/reset-password", json={
            "token": reset_token,
            "new_password": old_password
        })
        assert same_pwd_res.status_code == 400, f"Expected 400 for duplicate old password, got {same_pwd_res.status_code}"
        assert "cannot be the same as your old password" in same_pwd_res.json().get("detail", "").lower()
        print(f"  --> PASSED: Correctly rejected duplicate password: '{same_pwd_res.json()['detail']}'")

        # 4. Test Weak Password Rejection
        print("\n[TEST 4] Rejection When New Password Is Weak (< 8 chars, no uppercase, no number)")
        weak_res = await client.post("/api/auth/reset-password", json={
            "token": reset_token,
            "new_password": "weak"
        })
        assert weak_res.status_code == 400
        print(f"  --> PASSED: Correctly rejected weak password: '{weak_res.json()['detail']}'")

        # 5. Successfully Update to Brand New Password
        print("\n[TEST 5] Successfully Reset Password with Valid Strong New Password")
        update_res = await client.post("/api/auth/reset-password", json={
            "token": reset_token,
            "new_password": new_password
        })
        assert update_res.status_code == 200, f"Reset password failed: {update_res.text}"
        print(f"  --> PASSED: {update_res.json()['message']}")

        # 6. Verify Old Password Fails Login
        print("\n[TEST 6] Login with Old Password Must Now Fail")
        old_login_res = await client.post("/api/auth/login", data={
            "username": test_email,
            "password": old_password
        })
        assert old_login_res.status_code == 400, f"Expected 400 for old password, got {old_login_res.status_code}"
        assert "incorrect" in old_login_res.json().get("detail", "").lower()
        print(f"  --> PASSED: Old password rejected as expected")

        # 7. Verify New Password Succeeds Login
        print("\n[TEST 7] Login with New Password Must Now Succeed")
        new_login_res = await client.post("/api/auth/login", data={
            "username": test_email,
            "password": new_password
        })
        assert new_login_res.status_code == 200, f"Login with new password failed: {new_login_res.text}"
        login_tokens = new_login_res.json()
        assert "access_token" in login_tokens
        print(f"  --> PASSED: Login with new password succeeded! Received access token")

        # 8. Verify Token Cannot Be Reused (Blacklisted JTI)
        print("\n[TEST 8] Used Reset Token Cannot Be Reused")
        reuse_res = await client.post("/api/auth/reset-password", json={
            "token": reset_token,
            "new_password": "AnotherNewPassword789!"
        })
        assert reuse_res.status_code == 400, f"Expected 400 on token reuse, got {reuse_res.status_code}"
        print(f"  --> PASSED: Reused reset token rejected: '{reuse_res.json()['detail']}'")

    # 9. Cleanup database
    print("\n[TEST 9] Database Cleanup")
    async for db in get_session():
        for uid in created_user_ids:
            st = select(User).where(User.id == uid)
            res = await db.exec(st)
            u = res.first()
            if u:
                await db.delete(u)
        await db.commit()
        break
    print(f"  --> PASSED: Cleaned up test user from Neon PostgreSQL")

    print("\n==========================================")
    print("ALL 9 PASSWORD RESET & VERIFICATION TESTS PASSED 100%!")
    print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(run_reset_password_tests())
