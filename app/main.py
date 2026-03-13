from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.prices import router as prices_router
from app.db.models import Base
from app.db.session import _engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Deribit Price Tracker API",
        description="Stores and exposes BTC/ETH index prices fetched from Deribit.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.include_router(prices_router, prefix="/api/v1")
    return app


app = create_app()