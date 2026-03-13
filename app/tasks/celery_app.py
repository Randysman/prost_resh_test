import asyncio
import logging
import time

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.exceptions import DeribitClientError
from app.db.repository import SyncPriceRecordRepository
from app.db.sync_session import get_sync_db_session
from app.services.derebit_client import DeribitClient

logger = logging.getLogger(__name__)

celery_app = Celery(
    "deribit_tracker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "fetch-prices-every-minute": {
            "task": "app.tasks.celery_app.fetch_and_store_all_prices",
            "schedule": settings.price_fetch_interval_seconds,
        },
    },
)


@celery_app.task(name="app.tasks.celery_app.fetch_and_store_all_prices", bind=True, max_retries=3)
def fetch_and_store_all_prices(self) -> dict:
    client = DeribitClient()
    results = {"success": [], "failed": []}

    for ticker in settings.supported_tickers:
        try:
            price_result = asyncio.run(client.get_index_price(ticker))
            with get_sync_db_session() as session:
                repo = SyncPriceRecordRepository(session)
                repo.save(
                    ticker=price_result.ticker,
                    price=price_result.index_price,
                    timestamp=price_result.timestamp,
                )
            logger.info(
                "Stored price for %s: %s at %s",
                ticker,
                price_result.index_price,
                price_result.timestamp,
            )
            results["success"].append(ticker)
        except DeribitClientError as exc:
            logger.error("Failed to fetch price for %s: %s", ticker, exc)
            results["failed"].append({"ticker": ticker, "error": str(exc)})
        except Exception as exc:
            logger.exception("Unexpected error for ticker %s: %s", ticker, exc)
            results["failed"].append({"ticker": ticker, "error": str(exc)})

    return results