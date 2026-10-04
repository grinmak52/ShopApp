import asyncio
import logging

from database.core.config import settings
from database.orm.db_helper import db_helper
from service.reservation import ReservationService

log = logging.getLogger(__name__)


async def run_expiration_worker() -> None:
    cfg = settings.reservation
    while True:
        try:
            async with db_helper.session_factory() as session:
                count = await ReservationService(session).expire_stale(cfg.ttl_seconds)
            if count:
                log.warning("Expired %s stale reservations", count)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Expiration worker failed")
        await asyncio.sleep(cfg.scan_interval_seconds)