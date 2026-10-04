import logging

from sqlalchemy.exc import IntegrityError

from database.orm.models import Payment, PaymentStatus
from messaging.events import StockReserved
from providers.mock import MockPaymentProvider
from repositories.payment import PaymentRepository

log = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, repo: PaymentRepository, provider: MockPaymentProvider):
        self.repo = repo
        self.provider = provider

    async def process(self, event: StockReserved) -> Payment:
        # идемпотентность: платёж по заказу уже есть, возвращаем прежний итог
        existing = await self.repo.get_by_order(event.order_id)
        if existing:
            log.info("Order %s already has payment %s", event.order_id, existing.status)
            return existing

        result = await self.provider.charge(event.order_id, event.total_price)
        payment = Payment(
            order_id=event.order_id,
            user_id=event.user_id,
            amount=event.total_price,
            status=PaymentStatus.SUCCEEDED if result.success else PaymentStatus.FAILED,
            provider=self.provider.name,
            transaction_id=result.transaction_id,
            failure_reason=result.reason,
        )
        try:
            return await self.repo.create(payment)
        except IntegrityError:
            await self.repo.session.rollback()
            return await self.repo.get_by_order(event.order_id)