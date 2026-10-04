import asyncio
import random
import uuid
from dataclasses import dataclass
from decimal import Decimal

from database.core.config import settings


@dataclass
class ChargeResult:
    success: bool
    transaction_id: str | None = None
    reason: str | None = None


class MockPaymentProvider:
    name = "mock"

    async def charge(self, order_id: uuid.UUID, amount: Decimal) -> ChargeResult:
        await asyncio.sleep(settings.payment.delay_seconds)  # имитация сети
        if random.random() < settings.payment.success_rate:
            return ChargeResult(True, transaction_id=f"mock_{uuid.uuid4().hex}")
        return ChargeResult(False, reason="card declined")

    async def refund(self, order_id: uuid.UUID, amount: Decimal) -> None:
        await asyncio.sleep(settings.payment.delay_seconds)