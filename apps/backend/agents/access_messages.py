"""User-facing explanations for why a URL produced no data. PURE (no I/O). Never claim more certainty than we have."""
from typing import Any, Dict, Optional

_UPLOAD_HINT = "open the page yourself, save it as a PDF (or copy the table into a CSV/Excel file) and attach the file here"

_PRIVATE_HINTS = {
    "chatgpt": "For a ChatGPT conversation, use its Share option to create a public link and paste that link, or copy the conversation / save it as a PDF and attach the file here.",
    "claude": "For a Claude conversation, use its Share option to create a public link and paste that link, or copy the conversation / save it as a PDF and attach the file here.",
    "gemini": "Copy the conversation or save it as a PDF and attach the file here.",
    "webmail": "Export or copy the message text, or save it as a PDF, and attach the file here.",
}


def build_access_message(issue: Optional[str], service: Optional[str] = None,
                         browse_stats: Optional[Dict[str, Any]] = None) -> str:
    if issue == "private_auth":
        hint = _PRIVATE_HINTS.get(service or "", f"If you need this content, {_UPLOAD_HINT}.")
        return ("This looks like a private page that needs you to be logged in, and WEBISCRAP can only read public pages. "
                + hint)
    if issue == "login_suspected":
        return ("This page looks like it may need a login and no public data was found on it. "
                f"If it is private, {_UPLOAD_HINT}.")
    if issue == "access_blocked":
        return ("The website refused automated access (bot protection). This is common on large shopping, social and "
                f"streaming sites and is not something you did wrong. Try a different public page, or {_UPLOAD_HINT}.")
    if issue == "captcha":
        return ("The website showed a human-verification (CAPTCHA) page instead of its content, so it could not be read "
                f"automatically. Try again later or with a different page, or {_UPLOAD_HINT}.")
    if issue == "rate_limited":
        return "The website is limiting requests right now (too many requests). Please wait a few minutes and try again."
    if issue == "server_error":
        return "The website returned a server error and showed no content. Please try again in a little while."
    if issue in ("unreachable_timeout", "unreachable_dns", "unreachable"):
        return ("We couldn't connect to this URL. The website took too long to respond or is temporarily "
                "unavailable. Please check that the URL is active and try again.")
    if issue == "tls_error":
        return "The website's security certificate could not be verified, so the page was not opened."
    if issue == "redirect_loop":
        return "The website kept redirecting in a loop, so the page could not be opened."
    snaps = int((browse_stats or {}).get("snapshots") or 0)
    if snaps > 0:
        return ("We opened the page but couldn't find data that matches your request. Try naming the fields you want, "
                "or use a more specific page (for example a listing or search-results URL).")
    return ("We couldn't read any content from this URL. The site may block automated browsers or be loading very "
            f"slowly. Try again, use a more specific URL, or {_UPLOAD_HINT}.")
