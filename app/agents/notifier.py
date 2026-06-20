"""Notification Agent — sends incident alerts to Slack."""
import logging
import httpx
from app.config import settings
from app.database import SessionLocal
from app.models import Incident

logger = logging.getLogger("aiops.notifier")


def notify(incident_id: int):
    if not settings.slack_webhook_url:
        logger.info("Slack webhook not configured, skipping notification")
        return

    db = SessionLocal()
    try:
        inc = db.get(Incident, incident_id)
        if not inc:
            return

        emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(inc.severity, "⚠️")
        text = (
            f"{emoji} *Incident #{inc.id}* — {inc.title}\n"
            f"*Severity:* {inc.severity} (confidence: {inc.confidence:.0%})\n"
            f"*Summary:* {inc.summary}\n"
            f"*Root cause:* {inc.root_cause}\n"
            f"*Suggested fix:* {inc.suggested_fix}"
        )
        try:
            httpx.post(settings.slack_webhook_url, json={"text": text}, timeout=5.0)
            logger.info(f"Slack notification sent for incident #{inc.id}")
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
    finally:
        db.close()
