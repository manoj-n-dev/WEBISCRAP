import smtplib
import asyncio
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
    <div class="logo">⚡ WEBISCRAP</div>
    <h1>Password Reset Request</h1>
    <p>Hello,</p>
    <p>We received a request to reset your password for your account associated with <strong>{user_email}</strong>. This link will expire in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
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
    <div class="logo">⚡ WEBISCRAP</div>
    <h1>Verify Your Email Address</h1>
    <p>Welcome to WEBISCRAP!</p>
    <p>Please confirm your email address (<strong>{user_email}</strong>) to activate your account and access intelligent web scraping and extraction.</p>
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

def _send_sync_smtp(recipient: str, subject: str, html_content: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = recipient

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, [recipient], msg.as_string())
        logger.info(f"Email '{subject}' sent successfully via SMTP to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via SMTP to {recipient}: {e}")
        return False

async def send_password_reset_email(recipient: str, reset_url: str) -> dict:
    """
    Sends password reset email.
    In PRODUCTION:
      - Uses real SMTP.
      - Never logs the bearer reset URL.
      - Never exposes the reset URL in the return dictionary.
    In DEVELOPMENT / TEST:
      - Uses SMTP if configured.
      - Otherwise falls back to mock logger and returns reset_url for local testing convenience.
    """
    subject = "Reset your WEBISCRAP password"
    html_content = _build_reset_email_html(reset_url, recipient)

    if settings.SMTP_HOST and settings.SMTP_USER:
        loop = asyncio.get_running_loop()
        success = await loop.run_in_executor(None, _send_sync_smtp, recipient, subject, html_content)
        return {"sent": success, "method": "smtp"}
    
    if settings.ENVIRONMENT == "production":
        logger.error(f"SMTP is not configured in production. Failed to deliver password reset to {recipient}.")
        return {"sent": False, "method": "smtp_unconfigured"}
    else:
        logger.info(f"[DEV EMAIL MOCK] Password reset link for {recipient}: {reset_url}")
        return {"sent": True, "method": "dev_logged", "reset_url": reset_url}

async def send_verification_email(recipient: str, verify_url: str) -> dict:
    """
    Sends email verification message.
    In PRODUCTION:
      - Uses real SMTP.
      - Never logs the verification URL.
      - Never exposes the verification URL in the return dictionary.
    In DEVELOPMENT / TEST:
      - Uses SMTP if configured.
      - Otherwise falls back to mock logger and returns verify_url for local testing convenience.
    """
    subject = "Verify your WEBISCRAP email address"
    html_content = _build_verification_email_html(verify_url, recipient)

    if settings.SMTP_HOST and settings.SMTP_USER:
        loop = asyncio.get_running_loop()
        success = await loop.run_in_executor(None, _send_sync_smtp, recipient, subject, html_content)
        return {"sent": success, "method": "smtp"}
    
    if settings.ENVIRONMENT == "production":
        logger.error(f"SMTP is not configured in production. Failed to deliver verification to {recipient}.")
        return {"sent": False, "method": "smtp_unconfigured"}
    else:
        logger.info(f"[DEV EMAIL MOCK] Email verification link for {recipient}: {verify_url}")
        return {"sent": True, "method": "dev_logged", "verify_url": verify_url}
