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
    escaped_email = _html.escape(user_email)
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    expire_minutes = settings.RESET_TOKEN_EXPIRE_MINUTES
    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Reset Your WEBISCRAP Password</title>
</head>
<body style="margin: 0; padding: 0; background-color: #06080d; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #06080d; padding: 40px 16px;">
    <tr>
      <td align="center">
        <!-- Main Container Card -->
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 560px; background-color: #0d1117; border: 1px solid #21262d; border-radius: 12px; overflow: hidden; box-shadow: 0 16px 40px rgba(0,0,0,0.5);">
          <!-- Top Cyber Glow Accent Line -->
          <tr>
            <td height="3" style="background-color: #1477f5; background-image: linear-gradient(90deg, #1477f5, #00d2ff, #1477f5); font-size: 0; line-height: 0;">&nbsp;</td>
          </tr>
          <!-- Content Area -->
          <tr>
            <td style="padding: 36px 36px 32px 36px;">
              <!-- Header with Logo and Badge -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 28px;">
                <tr>
                  <td align="left" valign="middle">
                    <img src="{frontend_url}/logo-mark.png" width="32" height="32" alt="WEBISCRAP" style="vertical-align: middle; margin-right: 10px; display: inline-block; border: 0;" />
                    <span style="font-size: 18px; font-weight: 700; letter-spacing: 1.5px; color: #ffffff; vertical-align: middle; display: inline-block;">WEBISCRAP</span>
                  </td>
                  <td align="right" valign="middle">
                    <span style="display: inline-block; padding: 4px 10px; font-family: monospace, Consolas, Courier; font-size: 10.5px; font-weight: 600; color: #4fd8ff; background-color: rgba(0, 210, 255, 0.08); border: 1px solid rgba(0, 210, 255, 0.25); border-radius: 4px; text-transform: uppercase; letter-spacing: 0.8px;">SECURITY NOTICE</span>
                  </td>
                </tr>
              </table>

              <!-- Heading -->
              <h1 style="margin: 0 0 16px 0; font-size: 22px; font-weight: 600; color: #ffffff; letter-spacing: -0.3px; line-height: 1.3;">Password Reset Request</h1>
              
              <p style="margin: 0 0 14px 0; font-size: 14px; line-height: 1.6; color: #c9d1d9;">Hello,</p>
              
              <p style="margin: 0 0 20px 0; font-size: 14px; line-height: 1.6; color: #8b949e;">
                We received an authorized request to reset the password for your account associated with <strong style="color: #ffffff;">{escaped_email}</strong>.
              </p>

              <!-- Expiration Notice Callout -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #071324; border: 1px solid #143560; border-radius: 8px; margin-bottom: 26px;">
                <tr>
                  <td style="padding: 12px 16px; font-size: 13px; color: #79c0ff; line-height: 1.5;">
                    <strong style="color: #ffffff;">&#9201; Security Window:</strong> This password reset link will expire in <strong>{expire_minutes} minutes</strong>.
                  </td>
                </tr>
              </table>

              <!-- Action Button -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="margin: 0 0 28px 0;">
                <tr>
                  <td align="center" bgcolor="#1477f5" style="border-radius: 8px; background-color: #1477f5; box-shadow: 0 4px 16px rgba(20, 119, 245, 0.35);">
                    <a href="{reset_url}" target="_blank" style="font-size: 14px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #ffffff; text-decoration: none; padding: 13px 32px; display: inline-block; border-radius: 8px; letter-spacing: 0.2px;">Reset Password &rarr;</a>
                  </td>
                </tr>
              </table>

              <!-- Fallback Section -->
              <p style="margin: 0 0 8px 0; font-size: 12.5px; color: #8b949e; line-height: 1.5;">
                If the button above does not work, copy and paste this link into your browser:
              </p>
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #05070a; border: 1px solid #1b2230; border-radius: 6px; margin-bottom: 24px;">
                <tr>
                  <td style="padding: 12px 14px; word-break: break-all; font-family: monospace, Consolas, Courier; font-size: 11.5px; line-height: 1.5; color: #4fd8ff;">
                    <a href="{reset_url}" target="_blank" style="color: #4fd8ff; text-decoration: underline;">{reset_url}</a>
                  </td>
                </tr>
              </table>

              <!-- Reassurance Note -->
              <p style="margin: 0 0 24px 0; font-size: 12.5px; line-height: 1.6; color: #6e7681;">
                If you did not request a password reset, you can safely ignore this email. Your account credentials remain secure and no changes have been made.
              </p>

              <!-- Footer Divider -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td style="border-top: 1px solid #21262d; padding-top: 20px;">
                    <p style="margin: 0 0 6px 0; font-size: 11.5px; color: #484f58; line-height: 1.5;">
                      WEBISCRAP &bull; Autonomous Web Scraping &amp; AI Extraction Engine
                    </p>
                    <p style="margin: 0; font-size: 11px; color: #484f58;">
                      <a href="{frontend_url}/privacy" style="color: #6e7681; text-decoration: none; margin-right: 12px;">Privacy Policy</a>
                      <a href="{frontend_url}/terms" style="color: #6e7681; text-decoration: none; margin-right: 12px;">Terms of Service</a>
                      <a href="{frontend_url}/docs" style="color: #6e7681; text-decoration: none;">Documentation</a>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

def _build_verification_email_html(verify_url: str, user_email: str) -> str:
    escaped_email = _html.escape(user_email)
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Verify Your WEBISCRAP Email</title>
</head>
<body style="margin: 0; padding: 0; background-color: #06080d; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #06080d; padding: 40px 16px;">
    <tr>
      <td align="center">
        <!-- Main Container Card -->
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 560px; background-color: #0d1117; border: 1px solid #21262d; border-radius: 12px; overflow: hidden; box-shadow: 0 16px 40px rgba(0,0,0,0.5);">
          <!-- Top Cyber Glow Accent Line -->
          <tr>
            <td height="3" style="background-color: #1477f5; background-image: linear-gradient(90deg, #1477f5, #00d2ff, #1477f5); font-size: 0; line-height: 0;">&nbsp;</td>
          </tr>
          <!-- Content Area -->
          <tr>
            <td style="padding: 36px 36px 32px 36px;">
              <!-- Header with Logo and Badge -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 28px;">
                <tr>
                  <td align="left" valign="middle">
                    <img src="{frontend_url}/logo-mark.png" width="32" height="32" alt="WEBISCRAP" style="vertical-align: middle; margin-right: 10px; display: inline-block; border: 0;" />
                    <span style="font-size: 18px; font-weight: 700; letter-spacing: 1.5px; color: #ffffff; vertical-align: middle; display: inline-block;">WEBISCRAP</span>
                  </td>
                  <td align="right" valign="middle">
                    <span style="display: inline-block; padding: 4px 10px; font-family: monospace, Consolas, Courier; font-size: 10.5px; font-weight: 600; color: #4fd8ff; background-color: rgba(0, 210, 255, 0.08); border: 1px solid rgba(0, 210, 255, 0.25); border-radius: 4px; text-transform: uppercase; letter-spacing: 0.8px;">ACCOUNT ACTIVATION</span>
                  </td>
                </tr>
              </table>

              <!-- Heading -->
              <h1 style="margin: 0 0 16px 0; font-size: 22px; font-weight: 600; color: #ffffff; letter-spacing: -0.3px; line-height: 1.3;">Verify Your Email Address</h1>
              
              <p style="margin: 0 0 14px 0; font-size: 14px; line-height: 1.6; color: #c9d1d9;">Welcome to WEBISCRAP!</p>
              
              <p style="margin: 0 0 20px 0; font-size: 14px; line-height: 1.6; color: #8b949e;">
                Please confirm your email address (<strong style="color: #ffffff;">{escaped_email}</strong>) to activate your account and start extracting structured data from any website.
              </p>

              <!-- Expiration Notice Callout -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #071324; border: 1px solid #143560; border-radius: 8px; margin-bottom: 26px;">
                <tr>
                  <td style="padding: 12px 16px; font-size: 13px; color: #79c0ff; line-height: 1.5;">
                    <strong style="color: #ffffff;">&#9201; Expiration:</strong> This activation link will remain active for <strong>24 hours</strong>.
                  </td>
                </tr>
              </table>

              <!-- Action Button -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="margin: 0 0 28px 0;">
                <tr>
                  <td align="center" bgcolor="#1477f5" style="border-radius: 8px; background-color: #1477f5; box-shadow: 0 4px 16px rgba(20, 119, 245, 0.35);">
                    <a href="{verify_url}" target="_blank" style="font-size: 14px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #ffffff; text-decoration: none; padding: 13px 32px; display: inline-block; border-radius: 8px; letter-spacing: 0.2px;">Verify Email Address &rarr;</a>
                  </td>
                </tr>
              </table>

              <!-- Fallback Section -->
              <p style="margin: 0 0 8px 0; font-size: 12.5px; color: #8b949e; line-height: 1.5;">
                If the button above does not work, copy and paste this link into your browser:
              </p>
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #05070a; border: 1px solid #1b2230; border-radius: 6px; margin-bottom: 24px;">
                <tr>
                  <td style="padding: 12px 14px; word-break: break-all; font-family: monospace, Consolas, Courier; font-size: 11.5px; line-height: 1.5; color: #4fd8ff;">
                    <a href="{verify_url}" target="_blank" style="color: #4fd8ff; text-decoration: underline;">{verify_url}</a>
                  </td>
                </tr>
              </table>

              <!-- Reassurance Note -->
              <p style="margin: 0 0 24px 0; font-size: 12.5px; line-height: 1.6; color: #6e7681;">
                If you did not register for an account on WEBISCRAP, please disregard this email.
              </p>

              <!-- Footer Divider -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td style="border-top: 1px solid #21262d; padding-top: 20px;">
                    <p style="margin: 0 0 6px 0; font-size: 11.5px; color: #484f58; line-height: 1.5;">
                      WEBISCRAP &bull; Autonomous Web Scraping &amp; AI Extraction Engine
                    </p>
                    <p style="margin: 0; font-size: 11px; color: #484f58;">
                      <a href="{frontend_url}/privacy" style="color: #6e7681; text-decoration: none; margin-right: 12px;">Privacy Policy</a>
                      <a href="{frontend_url}/terms" style="color: #6e7681; text-decoration: none; margin-right: 12px;">Terms of Service</a>
                      <a href="{frontend_url}/docs" style="color: #6e7681; text-decoration: none;">Documentation</a>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

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
