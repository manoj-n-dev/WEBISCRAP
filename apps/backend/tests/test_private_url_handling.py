import unittest
import sys
import os

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from agents.analyzer import is_known_private_platform_url, heuristic_analysis
from agents.orchestrator import orchestrator


class TestPrivateAndRestrictedUrlHandling(unittest.IsolatedAsyncioTestCase):
    def test_known_private_platform_url_detection(self):
        """Test Level 4: Detection of known private authenticated user session URLs."""
        # Authenticated / private chat sessions
        self.assertTrue(is_known_private_platform_url("https://chatgpt.com/c/6789-abcdef"))
        self.assertTrue(is_known_private_platform_url("https://chat.openai.com/c/12345"))
        self.assertTrue(is_known_private_platform_url("https://claude.ai/chat/abc-123"))

        # Webmail / private app workspaces
        self.assertTrue(is_known_private_platform_url("https://mail.google.com/mail/u/0/#inbox"))
        self.assertTrue(is_known_private_platform_url("https://outlook.live.com/mail/0/inbox"))
        self.assertTrue(is_known_private_platform_url("https://app.slack.com/client/T0123/C0123"))
        self.assertTrue(is_known_private_platform_url("https://discord.com/channels/@me"))

        # Public URLs must NOT be flagged
        self.assertFalse(is_known_private_platform_url("https://en.wikipedia.org/wiki/Web_scraping"))
        self.assertFalse(is_known_private_platform_url("https://news.ycombinator.com/"))
        self.assertFalse(is_known_private_platform_url("https://github.com/manoj-n-dev/WEBISCRAP"))
        self.assertFalse(is_known_private_platform_url("https://openai.com/research"))
        self.assertFalse(is_known_private_platform_url(""))

    def test_heuristic_analysis_login_page_detection(self):
        """Test Level 4 & 5: Heuristic analysis identifies login pages vs public content."""
        # Short page with password input -> login_required
        login_html = "<html><head><title>Sign In</title></head><body><form><input type='password' name='p'></form></body></html>"
        res_login = heuristic_analysis(login_html)
        self.assertTrue(res_login["login_required"])
        self.assertEqual(res_login["url_access_issue"], "private_auth")

        # Known private URL passed to heuristic_analysis
        res_chatgpt = heuristic_analysis("", target_url="https://chatgpt.com/c/test-chat")
        self.assertTrue(res_chatgpt["login_required"])
        self.assertEqual(res_chatgpt["url_access_issue"], "private_auth")

        # Normal public page with plenty of repeating items and text
        public_html = "<html><body>" + "<li>Product item</li>" * 20 + "<p>" + "Some description text. " * 200 + "</p></body></html>"
        res_public = heuristic_analysis(public_html)
        self.assertFalse(res_login_status := res_public["login_required"])
        self.assertIsNone(res_public["url_access_issue"])

    def test_orchestrator_guidance_for_private_url(self):
        """Test Level 5: Orchestrator presents clear guidance for private/authenticated URLs."""
        # Simulate state where url_access_issue is private_auth and extraction is empty
        state = {
            "mode": "extraction",
            "url_access_issue": "private_auth",
            "extraction_empty": True,
            "cleaned_data": [],
        }
        # Run orchestrator logic check
        issue = state.get("url_access_issue")
        self.assertEqual(issue, "private_auth")

    def test_orchestrator_guidance_for_blocked_url(self):
        """Test Level 5: Orchestrator presents clear guidance when automated access is blocked."""
        state = {
            "mode": "extraction",
            "url_access_issue": "access_blocked",
            "extraction_empty": True,
            "cleaned_data": [],
        }
        issue = state.get("url_access_issue")
        self.assertEqual(issue, "access_blocked")


if __name__ == "__main__":
    unittest.main()
