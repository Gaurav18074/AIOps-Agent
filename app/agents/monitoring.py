"""Monitoring agent — performs HTTP health checks."""
import time
import httpx
import logging
from datetime import datetime
from app.database import SessionLocal
from app.models import Site, Check
from app.services.dedup import should_create_incident
from app.agents.graph import run_pipeline

logger = logging.getLogger("aiops.monitoring")


def check_site(site_id: int):
    """Perform one health check for a site; trigger agent pipeline on failure."""
    db = SessionLocal()
    try:
        site = db.get(Site, site_id)
        if not site or not site.enabled:
            return

        start = time.time()
        status_code = None
        success = False
        error = None

        try:
            r = httpx.get(site.url, timeout=10.0, follow_redirects=True)
            status_code = r.status_code
            success = 200 <= r.status_code < 400
            if not success:
                error = f"HTTP {r.status_code}"
        except httpx.TimeoutException:
            error = "Request timeout after 10s"
        except httpx.ConnectError as e:
            error = f"Connection error: {str(e)[:200]}"
        except Exception as e:
            error = f"{type(e).__name__}: {str(e)[:200]}"

        elapsed_ms = (time.time() - start) * 1000

        check = Check(
            site_id=site.id,
            status_code=status_code,
            response_time_ms=elapsed_ms,
            success=success,
            error=error,
            checked_at=datetime.utcnow(),
        )
        db.add(check)
        db.commit()

        logger.info(
            f"Checked {site.name} ({site.url}): "
            f"success={success} status={status_code} time={elapsed_ms:.0f}ms"
        )

        # Trigger pipeline on failure (deduped)
        if not success:
            signature = error or f"http_{status_code}"
            if should_create_incident(site.id, signature):
                logger.warning(f"Failure for {site.name}, triggering pipeline")
                run_pipeline(site_id=site.id, check_id=check.id)
            else:
                logger.info(f"Failure for {site.name} suppressed by dedup")
    finally:
        db.close()
