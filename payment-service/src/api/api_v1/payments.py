import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import TokenUser, get_current_user
from database.orm.db_helper import db_helper
from repositories.payment import PaymentRepository
from schemas.payment import PaymentRead

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/order/{order_id}", response_model=PaymentRead)
async def get_payment(
    order_id: uuid.UUID,
    user: Annotated[TokenUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    payment = await PaymentRepository(session).get_for_user(order_id, user.id)
    if payment is None:
        raise HTTPException(404, "Payment not found")
    return payment