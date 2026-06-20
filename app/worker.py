"""Background scheduler — polls sites and triggers checks."""
import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings
from app.database import SessionLocal
from app.models import Site
from app.agents.monitoring import check_site

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("aiops.worker")

scheduler = BackgroundScheduler()
_scheduled_ids: set[int] = set()


def sync_jobs():
    """Add jobs for new sites; remove jobs for deleted sites."""
    db = SessionLocal()
    try:
        sites = db.query(Site).filter(Site.enabled == True).all()
        current = {s.id for s in sites}

        # Remove old
        for sid in _scheduled_ids - current:
            try:
                scheduler.remove_job(f"site-{sid}")
                logger.info(f"Removed job for site {sid}")
            except Exception:
                pass

        # Add new
        for site in sites:
            job_id = f"site-{site.id}"
            if site.id not in _scheduled_ids:
                scheduler.add_job(
                    check_site,
                    trigger=IntervalTrigger(seconds=site.check_interval_seconds),
                    args=[site.id],
                    id=job_id,
                    replace_existing=True,
                )
                logger.info(
                    f"Scheduled site {site.id} ({site.name}) "
                    f"every {site.check_interval_seconds}s"
                )

        _scheduled_ids.clear()
        _scheduled_ids.update(current)
    finally:
        db.close()


def main():
    logger.info("AIOps worker starting")
    scheduler.start()
    # Re-sync sites every 30 seconds (handles add/delete)
    scheduler.add_job(sync_jobs, IntervalTrigger(seconds=30), id="sync", replace_existing=True)
    sync_jobs()
    logger.info("Scheduler started")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()
