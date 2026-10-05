import asyncio
import logging

from database.core.config import settings
from database.orm.db_helper import db_helper
from messaging.broker import broker
from messaging.events import StockReservationExpired
from service.reservation import ReservationService

log = logging.getLogger(__name__)


async def run_expiration_worker() -> None:
    cfg = settings.reservation
    while True:
        try:
            async with db_helper.session_factory() as session:
                order_ids = await ReservationService(session).expire_stale(cfg.ttl_seconds)
            for order_id in order_ids:
                await broker.publish(
                    "stock.reservation_expired",
                    StockReservationExpired(order_id=order_id),
                )
            if order_ids:
                log.warning("Expired reservations for %s order(s)", len(order_ids))
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Expiration worker failed")
        await asyncio.sleep(cfg.scan_interval_seconds)