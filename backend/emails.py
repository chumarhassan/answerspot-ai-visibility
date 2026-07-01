from __future__ import annotations
import logging
import httpx
from config import get_settings
logger = logging.getLogger("answerspot.emails")
settings = get_settings()
class EmailError(Exception): pass
async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    if not settings.resend_configured:
        logger.info("Email (MOCK): To: %s | Subject: %s | Content length: %d", to_email, subject, len(html_content))
        return True
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {settings.resend_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "from": settings.resend_from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code not in (200, 201):
                logger.error("Resend delivery failed: %s %s", resp.status_code, resp.text)
                return False
            logger.info("Email sent to %s via Resend.", to_email)
            return True
    except Exception as exc:
        logger.exception("Email delivery exception: %s", exc)
        return False
def build_weekly_report_html(business_name: str, summary: str, current_date: str) -> str:
    return f