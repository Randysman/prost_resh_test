from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.models import PriceRecord


class PriceRecordRepository:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all_by_ticker(self, ticker: str) -> list[PriceRecord]:
        result = await self._session.execute(
            select(PriceRecord)
            .where(PriceRecord.ticker == ticker)
            .order_by(PriceRecord.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_latest_by_ticker(self, ticker: str) -> PriceRecord | None:
        result = await self._session.execute(
            select(PriceRecord)
            .where(PriceRecord.ticker == ticker)
            .order_by(PriceRecord.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_ticker_and_date_range(
        self,
        ticker: str,
        from_timestamp: int,
        to_timestamp: int,
    ) -> list[PriceRecord]:
        result = await self._session.execute(
            select(PriceRecord)
            .where(
                PriceRecord.ticker == ticker,
                PriceRecord.timestamp >= from_timestamp,
                PriceRecord.timestamp <= to_timestamp,
            )
            .order_by(PriceRecord.timestamp.desc())
        )
        return list(result.scalars().all())


class SyncPriceRecordRepository:

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, ticker: str, price: Decimal, timestamp: int) -> PriceRecord:
        record = PriceRecord(ticker=ticker, price=price, timestamp=timestamp)
        self._session.add(record)
        self._session.flush()
        return record