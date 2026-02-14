"""
ReOrder AI — Background job scheduler.
Runs forecast refresh on a configurable interval using APScheduler.
Also provides a helper to trigger forecasts after a sync completes.
"""

import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.core.config import get_settings

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


def _run_all_forecasts():
    """
    Background job: find all stores that have normalized data and run forecasts.
    This runs inside its own DB session (not request-scoped).
    """
    from src.db.session import get_session
    from src.db.models import PipelineStoreConfig
    from src.core.forecast import get_provider
    from src.core.forecast.runner import run_forecasts

    provider = get_provider()

    with get_session() as db:
        stores = db.query(PipelineStoreConfig.store_id).all()
        store_ids = [s.store_id for s in stores]

    if not store_ids:
        logger.info("Scheduler: no stores configured, skipping forecast run")
        return

    for store_id in store_ids:
        try:
            with get_session() as db:
                summary = run_forecasts(db, store_id, provider, horizon_days=30)
                logger.info(
                    "Scheduler: forecasted store %s — %d SKUs, %d skipped",
                    store_id, summary.skus_forecasted, summary.skus_skipped,
                )
        except Exception as e:
            logger.error("Scheduler: forecast failed for store %s: %s", store_id, e)


def run_forecast_for_store(store_id: str):
    """
    Trigger a one-off forecast for a specific store.
    Call this after a sync completes.
    """
    from src.db.session import get_session
    from src.core.forecast import get_provider
    from src.core.forecast.runner import run_forecasts

    provider = get_provider()

    try:
        with get_session() as db:
            summary = run_forecasts(db, store_id, provider, horizon_days=30)
            logger.info(
                "Post-sync forecast for store %s: %d SKUs, %d skipped",
                store_id, summary.skus_forecasted, summary.skus_skipped,
            )
            return summary
    except Exception as e:
        logger.error("Post-sync forecast failed for store %s: %s", store_id, e)
        raise


def start_scheduler():
    """
    Start the background scheduler. Call once from FastAPI startup.
    Interval is controlled by FORECAST_REFRESH_HOURS (default: 24).
    """
    global _scheduler
    if _scheduler is not None:
        return  # already running

    settings = get_settings()
    hours = getattr(settings, "forecast_refresh_hours", 24)

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        _run_all_forecasts,
        trigger=IntervalTrigger(hours=hours),
        id="forecast_refresh",
        name="Refresh demand forecasts for all stores",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Background scheduler started: forecasts refresh every %d hours", hours)


def stop_scheduler():
    """Shut down the scheduler gracefully."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Background scheduler stopped")
