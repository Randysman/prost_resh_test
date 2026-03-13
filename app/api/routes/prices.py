from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_price_service
from app.api.scemas import (
    ErrorResponse,
    LatestPriceResponse,
    PriceListResponse,
    PriceRecordSchema,
)
from app.core.exceptions import PriceNotFoundError, UnsupportedTickerError
from app.services.price_serice import PriceService


router = APIRouter(prefix="/prices", tags=["prices"])


@router.get(
    "/",
    response_model=PriceListResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Get all stored prices for a ticker",
)
async def get_all_prices(
    ticker: str = Query(..., description="Currency ticker, e.g. btc_usd"),
    service: PriceService = Depends(get_price_service),
) -> PriceListResponse:
    try:
        records = await service.get_all_prices(ticker)
    except UnsupportedTickerError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return PriceListResponse(
        ticker=ticker.lower(),
        count=len(records),
        records=[PriceRecordSchema.model_validate(r) for r in records],
    )


@router.get(
    "/latest",
    response_model=LatestPriceResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Get the most recent price for a ticker",
)
async def get_latest_price(
    ticker: str = Query(..., description="Currency ticker, e.g. btc_usd"),
    service: PriceService = Depends(get_price_service),
) -> LatestPriceResponse:
    try:
        record = await service.get_latest_price(ticker)
    except UnsupportedTickerError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except PriceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return LatestPriceResponse(
        ticker=record.ticker,
        price=record.price,
        timestamp=record.timestamp,
    )


@router.get(
    "/range",
    response_model=PriceListResponse,
    responses={
        400: {"model": ErrorResponse},
    },
    summary="Get prices for a ticker filtered by Unix timestamp range",
)
async def get_prices_in_range(
    ticker: str = Query(..., description="Currency ticker, e.g. btc_usd"),
    from_timestamp: int = Query(..., description="Start of range as Unix timestamp (seconds)", ge=0),
    to_timestamp: int = Query(..., description="End of range as Unix timestamp (seconds)", ge=0),
    service: PriceService = Depends(get_price_service),
) -> PriceListResponse:
    try:
        records = await service.get_prices_in_range(ticker, from_timestamp, to_timestamp)
    except UnsupportedTickerError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return PriceListResponse(
        ticker=ticker.lower(),
        count=len(records),
        records=[PriceRecordSchema.model_validate(r) for r in records],
    )