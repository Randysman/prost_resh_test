from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv


load_dotenv()

class Settings(BaseSettings):
    database_url_sync: str = os.getenv("DATABASE_URL_SYNC")

    deribit_base_url: str = "https://www.deribit.com/api/v2"
    deribit_request_timeout: int = 10

    supported_tickers: list[str] = ["btc_usd", "eth_usd"]

    price_fetch_interval_seconds: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
