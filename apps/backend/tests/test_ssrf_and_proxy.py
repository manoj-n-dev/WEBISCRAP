import unittest
import sys
import os
from unittest.mock import MagicMock

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from agents.base import validate_resolved_ip, validate_target_url
from core.config import settings, get_client_ip

class TestSSRFAndProxy(unittest.TestCase):
    def test_ssrf_ip_validation_blocks_private_and_internal(self):
        """Test that validate_resolved_ip blocks private, loopback, link-local, and reserved IPs."""
        # Loopback
        self.assertFalse(validate_resolved_ip("127.0.0.1"))
        self.assertFalse(validate_resolved_ip("127.0.1.1"))

        # Private RFC 1918
        self.assertFalse(validate_resolved_ip("10.0.0.1"))
        self.assertFalse(validate_resolved_ip("172.16.0.1"))
        self.assertFalse(validate_resolved_ip("192.168.1.1"))

        # Cloud metadata / Link-local (169.254.x.x)
        self.assertFalse(validate_resolved_ip("169.254.169.254"))

        # Unspecified (0.0.0.0)
        self.assertFalse(validate_resolved_ip("0.0.0.0"))

        # Invalid IP strings
        self.assertFalse(validate_resolved_ip("invalid_ip"))

    def test_ssrf_ip_validation_allows_public(self):
        """Test that validate_resolved_ip allows legitimate public IPs."""
        self.assertTrue(validate_resolved_ip("8.8.8.8"))
        self.assertTrue(validate_resolved_ip("1.1.1.1"))
        self.assertTrue(validate_resolved_ip("93.184.216.34")) # example.com

    def test_validate_target_url(self):
        """Test URL scheme and destination validation."""
        # Invalid schemes
        self.assertFalse(validate_target_url("file:///etc/passwd"))
        self.assertFalse(validate_target_url("ftp://ftp.example.com"))
        self.assertFalse(validate_target_url("javascript:alert(1)"))
        self.assertFalse(validate_target_url(""))

        # Localhost / internal hostnames
        self.assertFalse(validate_target_url("http://localhost:8000"))
        self.assertFalse(validate_target_url("http://127.0.0.1:3000"))
        self.assertFalse(validate_target_url("http://169.254.169.254/latest/meta-data/"))

        # Legitimate public URLs
        self.assertTrue(validate_target_url("https://example.com"))
        self.assertTrue(validate_target_url("https://httpbin.org/get"))

    def test_proxy_ip_handling_default_safe(self):
        """Test FIX 15: When TRUST_PROXY_HEADERS=False, X-Forwarded-For is ignored (anti-spoofing)."""
        settings.TRUST_PROXY_HEADERS = False

        req = MagicMock()
        req.headers = {"X-Forwarded-For": "203.0.113.195, 70.41.3.18"}
        req.client.host = "192.168.1.50"

        extracted = get_client_ip(req)
        # Should return direct connection host to prevent spoofing
        self.assertEqual(extracted, "192.168.1.50")

    def test_proxy_ip_handling_behind_trusted_proxy(self):
        """Test FIX 15: When TRUST_PROXY_HEADERS=True, X-Forwarded-For client IP is parsed."""
        try:
            settings.TRUST_PROXY_HEADERS = True

            req = MagicMock()
            req.headers = {"X-Forwarded-For": "203.0.113.195, 70.41.3.18"}
            req.client.host = "10.0.0.2"

            extracted = get_client_ip(req)
            self.assertEqual(extracted, "203.0.113.195")
        finally:
            settings.TRUST_PROXY_HEADERS = False

if __name__ == "__main__":
    unittest.main()
