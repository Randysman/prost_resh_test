from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import PriceRecordRepository
from app.db.session import get_db_session
from app.services.price_serice import PriceService


async def get_price_repository(
        session: AsyncSession = Depends(get_db_session),
) -> PriceRecordRepository:
    return PriceRecordRepository(session)


async def get_price_service(
        repository: PriceRecordRepository = Depends(get_price_repository),
) -> PriceService:
    return PriceService(repository)