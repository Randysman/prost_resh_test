from dataclasses import dataclass
from decimal import Decimal

import aiohttp

from app.core.config import settings
from app.core.exceptions import DeribitClientError


@dataclass(frozen=True)
class IndexPriceResult:
    ticker: str
    index_price: Decimal
    timestamp: int


class DeribitClient:

    _INDEX_PRICE_ENDPOINT = "/public/get_index_price"

    def __init__(
        self,
        base_url: str = settings.deribit_base_url,
        timeout_seconds: int = settings.deribit_request_timeout,
    ) -> None:
        self._base_url = base_url
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async def get_index_price(self, ticker: str) -> IndexPriceResult:
        index_name = ticker.lower().replace("_", "")
        url = f"{self._base_url}{self._INDEX_PRICE_ENDPOINT}"
        params = {"index_name": index_name}

        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.get(url, params=params) as response:
                payload = await response.json()

        if "error" in payload:
            raise DeribitClientError(
                f"Deribit API error for ticker '{ticker}': {payload['error']}"
            )

        result = payload.get("result", {})
        index_price = result.get("index_price")
        timestamp_ms = payload.get("usOut")  # microseconds

        if index_price is None or timestamp_ms is None:
            raise DeribitClientError(
                f"Unexpected response format from Deribit for ticker '{ticker}': {payload}"
            )

        timestamp_unix = int(timestamp_ms) // 1_000_000  # microseconds → seconds

        return IndexPriceResult(
            ticker=ticker.lower(),
            index_price=Decimal(str(index_price)),
            timestamp=timestamp_unix,
        )