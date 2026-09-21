import asyncio
import html as _html
import smtplib
import ssl
from typing import Optional, Tuple

import httpx
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger
from core.config import settings

def _build_reset_email_html(reset_url: str, user_email: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Reset Your WEBISCRAP Password</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #0d0f12;
      color: #e6edf3;
      margin: 0;
      padding: 30px;
    }}
    .container {{
      max-width: 520px;
      margin: 0 auto;
      background-color: #161b22;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 36px;
    }}
    .logo {{
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0.5px;
      color: #58a6ff;
      margin-bottom: 24px;
    }}
    h1 {{
      font-size: 22px;
      margin: 0 0 16px;
      color: #ffffff;
    }}
    p {{
      font-size: 14px;
      line-height: 1.6;
      color: #8b949e;
      margin: 0 0 24px;
    }}
    .button {{
      display: inline-block;
      background-color: #238636;
      color: #ffffff !important;
      text-decoration: none;
      font-weight: 600;
      font-size: 14px;
      padding: 12px 28px;
      border-radius: 6px;
      margin-bottom: 24px;
    }}
    .link-alt {{
      font-size: 12px;
      word-break: break-all;
      color: #58a6ff;
    }}
    .footer {{
      margin-top: 32px;
      padding-top: 20px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 12px;
      color: #484f58;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo"><img src="{settings.FRONTEND_URL.rstrip('/')}/logo-mark.png" width="32" height="32" alt="" style="vertical-align:middle;margin-right:8px"> WEBISCRAP</div>
    <h1>Password Reset Request</h1>
    <p>Hello,</p>
    <p>We received a request to reset your password for your account associated with <strong>{_html.escape(user_email)}</strong>. This link will expire in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
    <div>
      <a href="{reset_url}" class="button" target="_blank">Reset Password</a>
    </div>
    <p>If the button doesn't work, copy and paste this link into your browser:</p>
    <p class="link-alt">{reset_url}</p>
    <div class="footer">
      If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged.
    </div>
  </div>
</body>
</html>
"""

def _build_verification_email_html(verify_url: str, user_email: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Verify Your WEBISCRAP Email</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #0d0f12;
      color: #e6edf3;
      margin: 0;
      padding: 30px;
    }}
    .container {{
      max-width: 520px;
      margin: 0 auto;
      background-color: #161b22;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 36px;
    }}
    .logo {{
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0.5px;
      color: #58a6ff;
      margin-bottom: 24px;
    }}
    h1 {{
      font-size: 22px;
      margin: 0 0 16px;
      color: #ffffff;
    }}
    p {{
      font-size: 14px;
      line-height: 1.6;
      color: #8b949e;
      margin: 0 0 24px;
    }}
    .button {{
      display: inline-block;
      background-color: #1f6feb;
      color: #ffffff !important;
      text-decoration: none;
      font-weight: 600;
      font-size: 14px;
      padding: 12px 28px;
      border-radius: 6px;
      margin-bottom: 24px;
    }}
    .link-alt {{
      font-size: 12px;
      word-break: break-all;
      color: #58a6ff;
    }}
    .footer {{
      margin-top: 32px;
      padding-top: 20px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 12px;
      color: #484f58;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo"><img src="{settings.FRONTEND_URL.rstrip('/')}/logo-mark.png" width="32" height="32" alt="" style="vertical-align:middle;margin-right:8px"> WEBISCRAP</div>
    <h1>Verify Your Email Address</h1>
    <p>Welcome to WEBISCRAP!</p>
    <p>Please confirm your email address (<strong>{_html.escape(user_email)}</strong>) to activate your account and access intelligent web scraping and extraction.</p>
    <div>
      <a href="{verify_url}" class="button" target="_blank">Verify Email Address</a>
    </div>
    <p>If the button doesn't work, copy and paste this link into your browser:</p>
    <p class="link-alt">{verify_url}</p>
    <div class="footer">
      This verification link will expire in 24 hours. If you did not create a WEBISCRAP account, please ignore this email.
    </div>
  </div>
</body>
</html>
"""

def _plain_text(intro: str, url: str, note: str) -> str:
    return f"{intro}\n\n{url}\n\n{note}\n\n— WEBISCRAP"


def _provider() -> str:
    p = (settings.EMAIL_PROVIDER or "auto").lower()
    if p != "auto":
        return p
    if settings.BREVO_API_KEY:
        return "brevo"
    if settings.RESEND_API_KEY:
        return "resend"
    if settings.SMTP_HOST and settings.SMTP_USER:
        return "smtp"
    return "none"


async def _post_json(url: str, headers: dict, payload: dict) -> Tuple[bool, Optional[str]]:
    """HTTPS (port 443) delivery - works on hosts that block SMTP ports (Render free blocks 25/465/587)."""
    last: Optional[str] = None
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(url, headers=headers, json=payload)
            if r.status_code < 300:
                return True, None
            last = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code < 500:
                break                                   # 4xx = config problem (bad key / unverified sender): don't retry
        except httpx.HTTPError as e:
            last = f"{type(e).__name__}: {e}"
        await asyncio.sleep(1.0)
    return False, last


async def _send_brevo(recipient: str, subject: str, html_content: str, text: str):
    return await _post_json(
        "https://api.brevo.com/v3/smtp/email",
        {"api-key": settings.BREVO_API_KEY, "accept": "application/json", "content-type": "application/json"},
        {"sender": {"name": settings.EMAILS_FROM_NAME, "email": settings.EMAILS_FROM_EMAIL},
         "to": [{"email": recipient}], "subject": subject, "htmlContent": html_content, "textContent": text})


async def _send_resend(recipient: str, subject: str, html_content: str, text: str):
    return await _post_json(
        "https://api.resend.com/emails",
        {"Authorization": f"Bearer {settings.RESEND_API_KEY}", "Content-Type": "application/json"},
        {"from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>", "to": [recipient],
         "subject": subject, "html": html_content, "text": text})


def _send_sync_smtp(recipient: str, subject: str, html_content: str, text: str = "") -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    user = (settings.SMTP_USER or "").strip().strip('"\'')
    password = (settings.SMTP_PASSWORD or "").strip().strip('"\'')
    from_email = (settings.EMAILS_FROM_EMAIL or user).strip().strip('"\'')
    host = (settings.SMTP_HOST or "").strip().strip('"\'')
    port = settings.SMTP_PORT

    # Gmail SMTP strict rules: From must match authenticated user, and port 2525 is invalid
    if "gmail.com" in host.lower():
        if from_email != user:
            logger.info(f"Gmail SMTP: adjusting From header from '{from_email}' to authenticated user '{user}'")
            from_email = user
        if port == 2525:
            logger.info("Gmail SMTP does not support port 2525; auto-switching to standard port 587")
            port = 587

    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{from_email}>"
    msg["To"] = recipient
    if text:
        msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=10, context=ssl.create_default_context())
        else:
            server = smtplib.SMTP(host, port, timeout=10)
        with server:
            if settings.SMTP_TLS and port != 465:
                server.starttls(context=ssl.create_default_context())
            if user and password:
                server.login(user, password)
            server.sendmail(from_email, [recipient], msg.as_string())
        logger.info(f"Email '{subject}' sent via SMTP to {recipient}")
        return True
    except Exception as e:
        logger.error(f"SMTP delivery failed ({type(e).__name__}): {e}")
        return False


async def _deliver(recipient: str, subject: str, html_content: str, text: str) -> dict:
    provider = _provider()
    if provider == "brevo":
        ok, err = await _send_brevo(recipient, subject, html_content, text)
    elif provider == "resend":
        ok, err = await _send_resend(recipient, subject, html_content, text)
    elif provider == "smtp":
        loop = asyncio.get_running_loop()
        ok = await loop.run_in_executor(None, _send_sync_smtp, recipient, subject, html_content, text)
        err = None if ok else "SMTP send failed (on Render free web services SMTP ports 25/465/587 are blocked - use EMAIL_PROVIDER=brevo|resend)"
    else:
        return {"sent": False, "method": "none", "error": "No email provider configured"}
    if ok:
        logger.info(f"Email '{subject}' delivered via {provider}")
    else:
        logger.error(f"Email '{subject}' FAILED via {provider}: {err}")
    return {"sent": ok, "method": provider, "error": err}


async def send_password_reset_email(recipient: str, reset_url: str) -> dict:
    """Production never logs or returns the bearer URL. Dev/test without a provider logs it and returns it."""
    subject = "Reset your WEBISCRAP password"
    html_content = _build_reset_email_html(reset_url, recipient)
    text = _plain_text("Reset your WEBISCRAP password using this link:", reset_url,
                       f"It expires in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes. If you didn't request it, ignore this email.")
    if _provider() != "none":
        return await _deliver(recipient, subject, html_content, text)
    if settings.ENVIRONMENT == "production":
        logger.error("No email provider configured in production. Password reset email NOT delivered.")
        return {"sent": False, "method": "none", "error": "No email provider configured"}
    logger.info(f"[DEV EMAIL MOCK] Password reset link for {recipient}: {reset_url}")
    return {"sent": True, "method": "dev_logged", "reset_url": reset_url}


async def send_verification_email(recipient: str, verify_url: str) -> dict:
    subject = "Verify your WEBISCRAP email address"
    html_content = _build_verification_email_html(verify_url, recipient)
    text = _plain_text("Confirm your email to activate your WEBISCRAP account:", verify_url,
                       "This link expires in 24 hours. If you didn't create an account, ignore this email.")
    if _provider() != "none":
        return await _deliver(recipient, subject, html_content, text)
    if settings.ENVIRONMENT == "production":
        logger.error("No email provider configured in production. Verification email NOT delivered.")
        return {"sent": False, "method": "none", "error": "No email provider configured"}
    logger.info(f"[DEV EMAIL MOCK] Email verification link for {recipient}: {verify_url}")
    return {"sent": True, "method": "dev_logged", "verify_url": verify_url}
