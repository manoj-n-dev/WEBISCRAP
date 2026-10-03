import os, sys, unittest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from agents.access_classifier import (
    classify_page, classify_navigation_error, classify_http_status, is_login_route,
    is_known_private_platform_url, private_platform_service, host_matches,
)


class TestAccessClassifier(unittest.TestCase):
    U = "https://www.amazon.in/s?k=laptop"

    def c(self, status=200, final=None, title="", body="", pw=False, rep=0, url=None):
        return classify_page(status, url or self.U, final or url or self.U, title, body, pw, rep)[0]

    def test_http_statuses(self):
        self.assertEqual(self.c(status=401), "private_auth")
        self.assertEqual(self.c(status=403), "access_blocked")
        self.assertEqual(self.c(status=429), "rate_limited")
        self.assertEqual(self.c(status=503, body="x" * 100), "server_error")
        self.assertIsNone(self.c(status=503, body="x" * 5000))

    def test_rich_page_despite_403_is_not_blocked(self):
        self.assertIsNone(self.c(status=403, title="Products", body="x" * 6000, rep=30))
        self.assertEqual(self.c(status=403, title="Forbidden", body="no", rep=0), "access_blocked")

    def test_amazon_robot_check_with_200(self):
        body = "Enter the characters you see below. Sorry, we just need to make sure you're not a robot."
        self.assertEqual(self.c(title="Robot Check", body=body), "captcha")

    def test_akamai_access_denied_with_200(self):
        self.assertEqual(self.c(title="Access Denied", body="You don't have permission to access this server. Reference #18.abc"), "access_blocked")

    def test_cloudflare_challenge(self):
        self.assertEqual(self.c(title="Just a moment...", body="Checking your browser before accessing"), "access_blocked")

    def test_rich_page_with_login_modal_is_not_private(self):
        self.assertIsNone(self.c(title="Lenovo Loq - Buy Online", body="x" * 6000, pw=True, rep=40))
        self.assertIsNone(self.c(title="Search", body="y" * 300, pw=True, rep=12))   # thin but many repeating items

    def test_real_login_wall(self):
        self.assertEqual(self.c(title="Sign in", body="Email Password Forgot?", pw=True, rep=0), "login_suspected")
        self.assertEqual(self.c(final="https://www.amazon.in/ap/signin?openid=x", body="z" * 50), "private_auth")

    def test_login_route_is_segment_based(self):
        self.assertTrue(is_login_route("/login"))
        self.assertTrue(is_login_route("/account/login"))
        self.assertTrue(is_login_route("/ap/signin"))
        self.assertFalse(is_login_route("/signing-day"))
        self.assertFalse(is_login_route("/blog/login-tips"))
        self.assertFalse(is_login_route("/loginpage-reviews"))
        self.assertFalse(is_login_route("/s"))

    def test_private_platforms(self):
        yes = ["https://chatgpt.com/c/abc", "https://chat.openai.com/c/1", "https://claude.ai/chat/abc",
               "https://mail.google.com/mail/u/0/#inbox", "https://app.slack.com/client/T1/C1", "https://discord.com/channels/@me",
               "https://CHATGPT.com:443/c/1"]
        no = ["https://chatgpt.com/share/abc", "https://claude.ai/share/abc", "https://claude.ai/", "https://chatgpt.com/",
              "https://discord.com/", "https://discord.com/invite/x", "https://notclaude.ai/chat/x", "https://evilopenai.com/c/x",
              "https://openai.com/research", "https://www.flipkart.com/q/lenovo-loq", "https://www.amazon.in/s?k=laptop", ""]
        for u in yes: self.assertTrue(is_known_private_platform_url(u), u)
        for u in no: self.assertFalse(is_known_private_platform_url(u), u)
        self.assertEqual(private_platform_service("https://chatgpt.com/c/1"), "chatgpt")
        self.assertEqual(private_platform_service("https://claude.ai/chat/1"), "claude")

    def test_host_matching(self):
        self.assertTrue(host_matches("a.claude.ai", "claude.ai"))
        self.assertFalse(host_matches("notclaude.ai", "claude.ai"))

    def test_navigation_errors(self):
        self.assertEqual(classify_navigation_error("Page.goto: net::ERR_HTTP2_PROTOCOL_ERROR at https://x"), "access_blocked")
        self.assertEqual(classify_navigation_error("net::ERR_CONNECTION_RESET"), "access_blocked")
        self.assertEqual(classify_navigation_error("Timeout 25000ms exceeded"), "unreachable_timeout")
        self.assertEqual(classify_navigation_error("net::ERR_NAME_NOT_RESOLVED"), "unreachable_dns")
        self.assertEqual(classify_navigation_error("net::ERR_CERT_AUTHORITY_INVALID"), "tls_error")
        self.assertIsNone(classify_navigation_error("something else entirely"))

    def test_status_helper(self):
        self.assertIsNone(classify_http_status(200))


if __name__ == "__main__":
    unittest.main()
