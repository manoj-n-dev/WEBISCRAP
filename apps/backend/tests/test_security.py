import unittest
import sys
import os
import uuid
from datetime import timedelta

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from auth.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)

class TestSecurity(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        """Test that passwords hash uniquely and verify accurately."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword123!", hashed))

    def test_access_token_lifecycle(self):
        """Test creating and decoding a standard JWT access token."""
        user_id = str(uuid.uuid4())
        token = create_access_token(user_id)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 20)

        payload = decode_access_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("sub"), user_id)
        self.assertIn("exp", payload)

    def test_refresh_token_lifecycle(self):
        """Test creating and decoding a JWT refresh token with unique JTI."""
        user_id = str(uuid.uuid4())
        token = create_refresh_token(user_id)
        self.assertIsInstance(token, str)

        payload = decode_refresh_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("sub"), user_id)
        self.assertEqual(payload.get("type"), "refresh")
        self.assertIn("jti", payload)
        self.assertTrue(len(payload["jti"]) > 0)

    def test_token_cross_validation_rejection(self):
        """Test that decode_access_token rejects refresh tokens and vice-versa."""
        user_id = str(uuid.uuid4())
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        # Access token decoder must reject refresh tokens
        self.assertIsNone(decode_access_token(refresh_token))

        # Refresh token decoder must reject standard access tokens
        self.assertIsNone(decode_refresh_token(access_token))

    def test_invalid_token_decoding(self):
        """Test that malformed or forged tokens return None."""
        self.assertIsNone(decode_access_token("not.a.valid.jwt"))
        self.assertIsNone(decode_refresh_token("random_garbage_string"))

if __name__ == "__main__":
    unittest.main()
