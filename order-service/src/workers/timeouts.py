import asyncio
import logging

from database.core.config import settings
from database.orm.db_helper import db_helper
from messaging.broker import broker
from repositories.order import OrderRepository
from service.saga import OrderSagaService

log = logging.getLogger(__name__)


async def run_timeout_worker() -> None:
    cfg = settings.saga
    while True:
        try:
            async with db_helper.session_factory() as session:
                repo = OrderRepository(session)
                saga = OrderSagaService(repo, broker)  # без cart_client
                for order_id in await repo.find_stale_pending(cfg.pending_timeout_seconds):
                    await saga.cancel(order_id, "order timed out")
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Timeout worker failed")
        await asyncio.sleep(cfg.scan_interval_seconds)