from decimal import Decimal
from pydantic import BaseModel, Field


class PriceRecordSchema(BaseModel):
    id: int
    ticker: str
    price: Decimal
    timestamp: int = Field(description="Unix timestamp in seconds")

    model_config = {"from_attributes": True}


class PriceListResponse(BaseModel):
    ticker: str
    count: int
    records: list[PriceRecordSchema]


class LatestPriceResponse(BaseModel):
    ticker: str
    price: Decimal
    timestamp: int = Field(description="Unix timestamp in seconds")


class ErrorResponse(BaseModel):
    detail: str