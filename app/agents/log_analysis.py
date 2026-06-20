"""Log Analysis Agent — collects recent check history and shapes it for the LLM."""
import logging
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Site, Check

logger = logging.getLogger("aiops.log_analysis")


def analyze(site_id: int, check_id: int) -> dict:
    """Build a structured context bundle for the root-cause LLM."""
    db = SessionLocal()
    try:
        site = db.get(Site, site_id)
        failing_check = db.get(Check, check_id)
        if not site or not failing_check:
            return {}

        # Recent history — last hour
        cutoff = datetime.utcnow() - timedelta(hours=1)
        recent = (
            db.query(Check)
            .filter(Check.site_id == site_id, Check.checked_at >= cutoff)
            .order_by(Check.checked_at.desc())
            .limit(50)
            .all()
        )

        total = len(recent)
        failed = sum(1 for c in recent if not c.success)
        avg_response = (
            sum(c.response_time_ms for c in recent if c.response_time_ms) / max(total, 1)
        )

        context = {
            "site": {"name": site.name, "url": site.url},
            "failure": {
                "status_code": failing_check.status_code,
                "response_time_ms": failing_check.response_time_ms,
                "error": failing_check.error,
                "timestamp": failing_check.checked_at.isoformat(),
            },
            "history_last_hour": {
                "total_checks": total,
                "failed_checks": failed,
                "failure_rate": round(failed / max(total, 1), 3),
                "avg_response_time_ms": round(avg_response, 1),
            },
            "recent_errors": [
                {"time": c.checked_at.isoformat(), "error": c.error, "status": c.status_code}
                for c in recent if not c.success
            ][:10],
        }
        logger.info(f"Built context for site={site.name} failures={failed}/{total}")
        return context
    finally:
        db.close()
