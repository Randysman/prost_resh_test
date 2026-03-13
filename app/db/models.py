from sqlalchemy import BigInteger, Column, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class PriceRecord(Base):
    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    price = Column(Numeric(precision=20, scale=8), nullable=False)
    timestamp = Column(BigInteger, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<PriceRecord(ticker={self.ticker}, price={self.price}, timestamp={self.timestamp})>"