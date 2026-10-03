"""
Access / bot-wall / login classification for scraped pages.

PURE functions only (no network, no Playwright, no I/O) so they are trivially unit-testable.
Result codes (url_access_issue):
  private_auth      STRONG  - known private app URL, HTTP 401, or redirect to a real login route. Skips extraction.
  login_suspected   WEAK    - login-like DOM signals only. NEVER skips extraction; used only to pick the message.
  access_blocked    STRONG  - HTTP 403 or bot-wall page (Cloudflare / Akamai / PerimeterX / DataDome ...).
  captcha           STRONG  - CAPTCHA / "are you a robot" interstitial.
  rate_limited      STRONG  - HTTP 429.
  server_error      WEAK    - HTTP 5xx with no usable content.
  unreachable_*     (set by navigation-error classifier)
"""
import re
import urllib.parse
from typing import Optional, Tuple

STRONG_ISSUES = {"private_auth", "access_blocked", "captcha", "rate_limited"}

_LOGIN_SEGMENTS = {"login", "signin", "sign-in", "log-in", "sign_in", "log_in", "sso"}
_LOGIN_PREFIXES = ("/accounts/login", "/ap/signin", "/account/login", "/session/new", "/checkpoint")

_CAPTCHA_MARKERS = (
    "enter the characters you see below",          # Amazon robot check
    "sorry, we just need to make sure you're not a robot",
    "type the characters you see in this image",
    "are you a human",                              # generic / Flipkart-style interstitial
    "verify you are human",
    "verify you are a human",
    "please verify you are a human",
    "unusual traffic from your computer",
    "complete the security check",
    "press & hold",                                  # PerimeterX
    "g-recaptcha", "h-captcha", "hcaptcha", "cf-turnstile", "px-captcha",
)
_BLOCK_MARKERS = (
    "access denied",                                 # Akamai ("Reference #18.xxxx")
    "you don't have permission to access",
    "request blocked",
    "the request could not be satisfied",           # CloudFront
    "checking your browser before accessing",
    "enable javascript and cookies to continue",
    "attention required! | cloudflare",
    "just a moment...",
    "security check",
    "pardon our interruption",                       # Distil/Imperva
    "datadome",
    "incapsula incident",
)
_BLOCK_TITLES = ("access denied", "just a moment...", "attention required! | cloudflare", "security check",
                 "robot check", "pardon our interruption", "403 forbidden", "captcha")


def _host(url: str) -> str:
    try:
        return (urllib.parse.urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def host_matches(host: str, domain: str) -> bool:
    """Exact host or true subdomain (NOT substring): 'notclaude.ai' must not match 'claude.ai'."""
    return host == domain or host.endswith("." + domain)


# (domain, path-prefix or None for whole host, service label used for guidance)
_PRIVATE_RULES = (
    ("chatgpt.com", "/c/", "chatgpt"),
    ("chat.openai.com", "/c/", "chatgpt"),
    ("claude.ai", "/chat/", "claude"),
    ("claude.ai", "/chats", "claude"),
    ("gemini.google.com", "/app", "gemini"),
    ("mail.google.com", None, "webmail"),
    ("outlook.live.com", "/mail", "webmail"),
    ("outlook.office.com", "/mail", "webmail"),
    ("mail.yahoo.com", None, "webmail"),
    ("app.slack.com", None, "slack"),
    ("discord.com", "/channels", "discord"),
    ("web.whatsapp.com", None, "whatsapp"),
)


def private_platform_service(url: str) -> Optional[str]:
    """Return a service label if the URL is a KNOWN logged-in-only area, else None."""
    if not url:
        return None
    try:
        p = urllib.parse.urlparse(url)
        host, path = (p.hostname or "").lower(), (p.path or "").lower()
        for domain, prefix, label in _PRIVATE_RULES:
            if host_matches(host, domain) and (prefix is None or path.startswith(prefix)):
                return label
    except Exception:
        pass
    return None


def is_known_private_platform_url(url: str) -> bool:
    return private_platform_service(url) is not None


def is_login_route(path: str) -> bool:
    """Segment-based (not substring) so '/signing-day' and '/blog/login-tips' are NOT login routes."""
    path = (path or "").lower()
    if any(path.startswith(pref) for pref in _LOGIN_PREFIXES):
        return True
    segs = [s for s in path.split("/") if s]
    return any(s in _LOGIN_SEGMENTS for s in segs[:2])      # login routes sit at the top of the path


def classify_http_status(status: Optional[int]) -> Optional[str]:
    if status == 401:
        return "private_auth"
    if status == 403:
        return "access_blocked"
    if status == 429:
        return "rate_limited"
    return None


def classify_page(status: Optional[int], target_url: str, final_url: str, title: str,
                  body_text: str, has_visible_password: bool, repeating_items: int) -> Tuple[Optional[str], str]:
    """Return (issue_code | None, reason). Order = strongest evidence first. A rich page (many repeating items)
    is never classified as a login wall."""
    title_l = (title or "").lower().strip()
    sample = (body_text or "")[:3000].lower()
    body_len = len((body_text or "").strip())

    rich = body_len >= 4000 and repeating_items >= 8          # plenty of real content: trust the content, not the status
    by_status = classify_http_status(status)
    if by_status and not rich:
        return by_status, f"http {status}"

    if any(m in sample for m in _CAPTCHA_MARKERS) and body_len < 4000:
        return "captcha", "captcha marker in short page"
    if (any(t == title_l or title_l.startswith(t) for t in _BLOCK_TITLES) and body_len < 4000) or \
       (any(m in sample for m in _BLOCK_MARKERS) and body_len < 1500):
        return "access_blocked", "bot-wall title/marker on short page"
    if status in (500, 502, 503, 504) and body_len < 800:
        return "server_error", f"http {status} with almost no content"

    o, f = urllib.parse.urlparse(target_url), urllib.parse.urlparse(final_url or target_url)
    if is_login_route(f.path) and not is_login_route(o.path) and repeating_items < 8:
        return "private_auth", "redirected to a login route"

    login_words = ("log in", "sign in", "login", "signin", "sign-in", "authentication required")
    if has_visible_password and repeating_items < 8 and (body_len < 800 or any(w in title_l for w in login_words)):
        return "login_suspected", "visible password field on a thin page"
    return None, "ok"


def classify_navigation_error(err: str) -> Optional[str]:
    """Map Playwright/Chromium error text to an issue code (previously only timeout/DNS were mapped)."""
    e = (err or "").lower()
    if "timeout" in e:
        return "unreachable_timeout"
    if "err_name_not_resolved" in e or "err_name_resolution_failed" in e:
        return "unreachable_dns"
    if any(k in e for k in ("err_http2_protocol_error", "err_connection_reset", "err_empty_response",
                            "err_access_denied", "err_blocked_by_response", "err_http_response_code_failure",
                            "err_connection_closed", "err_quic_protocol_error")):
        return "access_blocked"          # typical of CDN/WAF resetting automated clients
    if any(k in e for k in ("err_connection_refused", "err_connection_timed_out", "err_address_unreachable",
                            "err_internet_disconnected", "err_network_changed")):
        return "unreachable"
    if "err_cert" in e or "err_ssl" in e:
        return "tls_error"
    if "err_too_many_redirects" in e:
        return "redirect_loop"
    return None
