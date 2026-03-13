from app.core.exceptions import PriceNotFoundError, UnsupportedTickerError
from app.core.config import settings
from app.db.repository import PriceRecordRepository
from app.db.models import PriceRecord


class PriceService:
    def __init__(self, repository: PriceRecordRepository) -> None:
        self._repository = repository

    def _validate_ticker(self, ticker: str) -> str:
        normalized = ticker.lower()
        if normalized not in settings.supported_tickers:
            raise UnsupportedTickerError(
                f"Ticker '{ticker}' is not supported. "
                f"Supported tickers: {settings.supported_tickers}"
            )
        return normalized

    async def get_all_prices(self, ticker: str) -> list[PriceRecord]:
        normalized = self._validate_ticker(ticker)
        return await self._repository.get_all_by_ticker(normalized)

    async def get_latest_price(self, ticker: str) -> PriceRecord:
        normalized = self._validate_ticker(ticker)
        record = await self._repository.get_latest_by_ticker(normalized)
        if record is None:
            raise PriceNotFoundError(f"No price data found for ticker '{ticker}'.")
        return record

    async def get_prices_in_range(
        self,
        ticker: str,
        from_timestamp: int,
        to_timestamp: int,
    ) -> list[PriceRecord]:
        normalized = self._validate_ticker(ticker)
        if from_timestamp > to_timestamp:
            raise ValueError("'from_timestamp' must be less than or equal to 'to_timestamp'.")
        return await self._repository.get_by_ticker_and_date_range(
            normalized, from_timestamp, to_timestamp
        )