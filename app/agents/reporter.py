"""Incident Report Agent — persists structured incidents."""
import logging
from app.database import SessionLocal
from app.models import Incident

logger = logging.getLogger("aiops.reporter")


def create_incident(site_id: int, context: dict, analysis: dict) -> int:
    """Create an incident row from agent outputs. Returns incident ID."""
    db = SessionLocal()
    try:
        summary = (
            f"Site {context['site']['name']} ({context['site']['url']}) "
            f"failed with: {context['failure']['error']}. "
            f"Failure rate (last hour): {context['history_last_hour']['failure_rate'] * 100:.0f}%."
        )
        inc = Incident(
            site_id=site_id,
            severity=analysis["severity"],
            title=analysis["title"],
            summary=summary,
            root_cause=analysis["root_cause"],
            suggested_fix=analysis["suggested_fix"],
            confidence=analysis["confidence"],
            raw_context=context,
            status="open",
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        logger.info(f"Created incident #{inc.id} severity={inc.severity}")
        return inc.id
    finally:
        db.close()
